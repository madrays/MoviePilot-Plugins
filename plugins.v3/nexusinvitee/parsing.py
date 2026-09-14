"""后宫成员列表的跨站点清洗与分享率归一化。"""
import re
from typing import Any, Dict, List, Optional, Tuple


_HEADER_WORDS = {
    "用户名", "用户", "邮箱", "邮件", "分享率", "上传", "下载", "状态",
    "username", "user", "email", "ratio", "uploaded", "downloaded", "status",
}
_SIZE_RE = re.compile(r"([\d.,]+)\s*([KMGTPE]?i?B)\b", re.IGNORECASE)
_UNITS = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3,
          "TB": 1024 ** 4, "PB": 1024 ** 5, "EB": 1024 ** 6}


def _size_to_bytes(value: Any) -> Optional[float]:
    match = _SIZE_RE.search(str(value or ""))
    if not match:
        return None
    try:
        number = float(match.group(1).replace(",", ""))
        unit = match.group(2).upper().replace("I", "")
        return number * _UNITS.get(unit, 1)
    except ValueError:
        return None


def _ratio(value: Any) -> Optional[float]:
    text = str(value or "").strip()
    if not text or text.lower() in _HEADER_WORDS or _SIZE_RE.search(text):
        return None
    if text.lower() in {"∞", "inf", "inf.", "infinite", "无限"}:
        return float("inf")
    match = re.search(r"-?\d+(?:[.,]\d+)?", text.replace(",", "."))
    try:
        return float(match.group(0)) if match else None
    except ValueError:
        return None


def _ratio_label(value: Optional[float]) -> Tuple[str, List[str]]:
    if value is None:
        return "neutral", ["无数据", "text-grey"]
    if value == float("inf"):
        return "excellent", ["分享率无限", "text-success"]
    if value >= 1:
        return "good", ["正常", "text-success"]
    if value >= 0.4:
        return "warning", ["较低", "text-warning"]
    if value > 0:
        return "danger", ["危险", "text-error"]
    return "neutral", ["无数据", "text-grey"]


def sanitize_invitees(invitees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """丢弃误抓表头、修正错列分享率，并为界面补齐健康状态。"""
    cleaned = []
    for invitee in invitees or []:
        if not isinstance(invitee, dict):
            continue
        username = str(invitee.get("username") or "").strip()
        if not username or username.lower() in _HEADER_WORDS:
            continue

        ratio = _ratio(invitee.get("ratio"))
        if ratio is None:
            uploaded = _size_to_bytes(invitee.get("uploaded"))
            downloaded = _size_to_bytes(invitee.get("downloaded"))
            if uploaded is not None and downloaded is not None:
                ratio = float("inf") if downloaded == 0 and uploaded > 0 else (
                    uploaded / downloaded if downloaded > 0 else None
                )
                if ratio is not None:
                    invitee["ratio"] = "∞" if ratio == float("inf") else f"{ratio:.3f}"
            elif _SIZE_RE.search(str(invitee.get("ratio") or "")):
                invitee["ratio"] = ""

        health, label = _ratio_label(ratio)
        invitee["ratio_health"] = health
        invitee["ratio_label"] = label
        cleaned.append(invitee)
    return cleaned

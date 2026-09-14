"""Gazelle 体系站点的邀请与被邀请人解析。"""
import re
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from . import _ISiteHandler
from ..site_access import classify, get


class GazelleHandler(_ISiteHandler):
    site_schema = "gazelle"

    @classmethod
    def match(cls, site_url: str) -> bool:
        return any(domain in (site_url or "").lower() for domain in ("redacted", "orpheus", "opsfet"))

    @staticmethod
    def _result() -> Dict[str, Any]:
        return {"invite_status": {"can_invite": False, "reason": "", "permanent_count": 0,
                                  "temporary_count": 0, "bonus": 0,
                                  "permanent_invite_price": 0, "temporary_invite_price": 0},
                "invitees": []}

    @staticmethod
    def _invitees(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        for table in soup.select("table"):
            headers = [cell.get_text(strip=True) for cell in table.select("tr:first-child th, tr:first-child td")]
            if not any("user" in header.lower() or "用户" in header for header in headers):
                continue
            def col(*names):
                return next((i for i, value in enumerate(headers)
                             if any(name.lower() in value.lower() for name in names)), None)
            user, email, uploaded, downloaded, ratio = (
                col("username", "用户名", "user"), col("email", "邮箱"),
                col("uploaded", "上传"), col("downloaded", "下载"), col("ratio", "分享率"),
            )
            invitees = []
            for row in table.select("tr")[1:]:
                cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
                if not cells:
                    continue
                value = lambda index: cells[index] if index is not None and index < len(cells) else ""
                if value(user):
                    invitees.append({"username": value(user), "email": value(email),
                                     "uploaded": value(uploaded), "downloaded": value(downloaded),
                                     "ratio": value(ratio), "enabled": "Yes", "status": "已确认"})
            if invitees:
                return invitees
        return []

    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        result, url = self._result(), site_info.get("url", "")
        try:
            page = get(session, url, "user.php?action=invite")
        except requests.RequestException as err:
            result["invite_status"]["reason"] = f"访问邀请页面失败：{err}"
            return result
        reason = classify(page)
        if reason:
            result["invite_status"]["reason"] = reason
            return result
        soup = BeautifulSoup(page.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" "))
        count = re.search(r"(?:邀请|invites?)\s*[:：]?\s*(\d+)", text, re.IGNORECASE)
        permanent = int(count.group(1)) if count else 0
        result["invite_status"].update({"permanent_count": permanent,
                                         "can_invite": permanent > 0 and bool(soup.select_one("input[name='email']")),
                                         "reason": f"可用邀请数: 永久={permanent}" if permanent else "当前没有可用邀请名额"})
        result["invitees"] = self._invitees(soup)
        return result

"""站点访问与响应分类；只识别 Cloudflare 挑战，不尝试绕过。"""
import re
from typing import Optional
from urllib.parse import urljoin

import requests


CF_CHALLENGE_REASON = "检测到 Cloudflare 验证页，请在站点中正常完成验证后更新 Cookie"
COOKIE_EXPIRED_REASON = "Cookie 已失效，请重新登录站点更新 Cookie"
_CF_MARKERS = ("just a moment", "checking your browser", "cf-browser-verification",
               "challenge-platform", "cf_chl_opt", "attention required! | cloudflare")
_LOGIN_MARKERS = ("takelogin.php", "action=login", "name=\"password\"", "name='password'")


def get(session: requests.Session, base_url: str, path: str, **kwargs) -> requests.Response:
    """所有专用处理器统一使用的相对路径请求。"""
    response = session.get(urljoin(base_url, path.lstrip("/")), timeout=(10, 30), **kwargs)
    _fix_encoding(response)
    return response


def _fix_encoding(response: requests.Response) -> None:
    """修正未声明编码的旧 PT 页面，避免中文表头解析失败。"""
    if (response.encoding or "").lower() not in ("", "iso-8859-1", "ascii"):
        return
    match = re.search(rb'charset=["\']?\s*([\w-]+)', response.content[:4096], re.IGNORECASE)
    if match:
        try:
            response.encoding = match.group(1).decode("ascii")
            return
        except UnicodeDecodeError:
            pass
    response.encoding = response.apparent_encoding or "utf-8"


def classify(response: requests.Response) -> Optional[str]:
    """将防护页、Cookie 失效和 HTTP 错误转换为用户可处理的原因。"""
    body = (response.text or "")[:8000].lower()
    if response.status_code in (403, 429, 503) and any(mark in body for mark in _CF_MARKERS):
        return CF_CHALLENGE_REASON
    if any(mark in body for mark in _LOGIN_MARKERS) or any(
        marker in (response.url or "").lower() for marker in ("login.php", "takelogin.php")
    ):
        return COOKIE_EXPIRED_REASON
    if response.status_code >= 500:
        return f"站点服务异常（HTTP {response.status_code}）"
    if response.status_code == 403:
        return "站点返回 403，可能是 Cookie 已失效或触发访问限制"
    if response.status_code >= 400:
        return f"请求失败（HTTP {response.status_code}）"
    return None


def detect_schema(html: str, site_url: str) -> Optional[str]:
    """根据域名与页面特征识别非 NexusPHP 站点体系。"""
    host = (site_url or "").lower()
    body = (html or "")[:200000].lower()
    if "totheglory.im" in host:
        return "ttg"
    if "unit3d" in body or ("livewire" in body and "/users/" in body):
        return "unit3d"
    if "gazelle" in body or ("user.php?action=" in body and "torrents.php" in body):
        return "gazelle"
    return None

"""UNIT3D 体系站点邀请页解析。"""
import re
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from . import _ISiteHandler
from ..site_access import classify, get


class Unit3dHandler(_ISiteHandler):
    site_schema = "unit3d"
    _DOMAINS = ("aither.cc", "hawke.uno", "blutopia.", "fearnopeer.com", "reelflix.xyz",
                "onlyencodes.cc", "upload.cx", "lst.gg", "seedpool.org", "cinematik.net")

    @classmethod
    def match(cls, site_url: str) -> bool:
        return any(domain in (site_url or "").lower() for domain in cls._DOMAINS)

    @staticmethod
    def _username(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        node = soup.select_one("a.top-nav__username, a[href*='/general-settings'], a[href*='/hub/settings']")
        if node and node.get("href"):
            matched = re.search(r"/users/([^/?#]+)", node["href"])
            if matched:
                return matched.group(1)
        names = re.findall(r"/users/([^/'\"?#]+)", html)
        return max(set(names), key=names.count) if names else None

    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        result = {"invite_status": {"can_invite": False, "reason": "", "permanent_count": 0,
                                     "temporary_count": 0, "bonus": 0, "permanent_invite_price": 0,
                                     "temporary_invite_price": 0}, "invitees": []}
        url = site_info.get("url", "")
        try:
            home = get(session, url, "/")
        except requests.RequestException as err:
            result["invite_status"]["reason"] = f"访问首页失败：{err}"
            return result
        reason = classify(home)
        if reason:
            result["invite_status"]["reason"] = reason
            return result
        username = self._username(home.text)
        if not username:
            result["invite_status"]["reason"] = "页面里找不到当前登录用户，Cookie 可能已失效"
            return result
        invite_page = None
        for path in (f"/users/{username}/invites", f"/users/{username}/hub/invites", "/invites"):
            try:
                candidate = get(session, url, path)
            except requests.RequestException:
                continue
            if candidate.status_code == 200 and classify(candidate) is None:
                invite_page = candidate
                break
        if invite_page is None:
            result["invite_status"]["reason"] = "该 UNIT3D 站点未开放邀请页面"
            return result
        soup = BeautifulSoup(invite_page.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" "))
        count = re.search(r"(?:邀请|invites?)\s*[:：]?\s*(\d+)", text, re.IGNORECASE)
        permanent = int(count.group(1)) if count else 0
        result["invite_status"].update({"permanent_count": permanent, "can_invite": permanent > 0,
                                         "reason": f"可用邀请数: 永久={permanent}" if permanent else "当前没有可用邀请名额"})
        for row in soup.select("table tbody tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
            if len(cells) >= 2 and any("@" in cell for cell in cells):
                email = next(cell for cell in cells if "@" in cell)
                result["invitees"].append({"username": email, "email": email, "uploaded": "", "downloaded": "",
                                           "ratio": "", "enabled": "Yes", "status": "已发送"})
        return result

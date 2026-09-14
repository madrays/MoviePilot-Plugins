"""TTG（totheglory.im）邀请页解析。"""
import re
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from . import _ISiteHandler
from ..site_access import classify, get


class TtgHandler(_ISiteHandler):
    site_schema = "ttg"

    @classmethod
    def match(cls, site_url: str) -> bool:
        return "totheglory.im" in (site_url or "").lower()

    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        result = {"invite_status": {"can_invite": False, "reason": "", "permanent_count": 0,
                                     "temporary_count": 0, "bonus": 0, "permanent_invite_price": 0,
                                     "temporary_invite_price": 0}, "invitees": []}
        try:
            page = get(session, site_info.get("url", ""), "invite.php")
        except requests.RequestException as err:
            result["invite_status"]["reason"] = f"访问邀请页面失败：{err}"
            return result
        reason = classify(page)
        if reason:
            result["invite_status"]["reason"] = reason
            return result
        soup = BeautifulSoup(page.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" "))
        count = re.search(r"(?:邀请|invites?)\s*[:：]\s*(\d+)", text, re.IGNORECASE)
        permanent = int(count.group(1)) if count else 0
        result["invite_status"].update({"permanent_count": permanent, "can_invite": permanent > 0,
                                         "reason": f"可用邀请数: 永久={permanent}" if permanent else "当前没有可用邀请名额"})
        for table in soup.select("table"):
            headers = [cell.get_text(strip=True) for cell in table.select("tr:first-child td, tr:first-child th")]
            if not any("用户名" in item or "username" in item.lower() for item in headers):
                continue
            user_index = next((i for i, item in enumerate(headers) if "用户名" in item or "username" in item.lower()), None)
            for row in table.select("tr")[1:]:
                cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
                if user_index is not None and user_index < len(cells) and cells[user_index]:
                    result["invitees"].append({"username": cells[user_index], "email": "", "uploaded": "",
                                               "downloaded": "", "ratio": "", "enabled": "Yes", "status": "已确认"})
            if result["invitees"]:
                break
        return result

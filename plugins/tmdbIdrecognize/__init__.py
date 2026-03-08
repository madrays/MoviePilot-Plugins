"""
TMDB ID 直通识别插件 (V2)

模仿 Emby 刮削策略：
  文件名含 {tmdbid=23155} → 直接查 TMDB API → 拿到标准名称 + 年份 → 返回给 MP

解决命名如：
  空之境界 第五章 矛盾螺旋 （2008） {tmdbid=23155}
  进击的巨人 最终季 完结篇（后篇）（2023）{tmdbid=888888}
"""
import re
from typing import Any, List, Dict, Tuple, Optional

from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import ChainEventType


class TmdbIdRecognize(_PluginBase):
    # ---- 插件元信息 ----
    plugin_name = "TMDB ID 直通识别"
    plugin_desc = "模仿 Emby 刮削策略，从文件名提取 {tmdbid=xxx} 直接查询 TMDB，精准识别媒体。"
    plugin_icon = "Themoviedb_A.png"
    plugin_version = "2.0"
    plugin_author = "sakezerto"
    author_url = "https://github.com/sakezerto/MoviePilot-Plugins"
    plugin_config_prefix = "tmdbidrecognize_"
    plugin_order = 0       # 越小越先执行，抢在 ChatGPT 识别之前
    auth_level = 1

    # ---- 配置属性 ----
    _enabled = False

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled", False)

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enabled",
                                            "label": "启用插件",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12},
                                "content": [
                                    {
                                        "component": "VAlert",
                                        "props": {
                                            "type": "info",
                                            "variant": "tonal",
                                            "text": "工作原理（模仿 Emby 刮削策略）：\n"
                                            "1. 从文件名提取 {tmdbid=xxx}\n"
                                            "2. 直接调 TMDB API 用 ID 查询精确的影片信息\n"
                                            "3. 把 TMDB 返回的标准名称+年份告诉 MoviePilot\n"
                                            "4. MoviePilot 拿着标准名称轻松匹配 ✅\n\n"
                                            "支持格式：{tmdbid=23155}  {tmdb-23155}  [tmdbid:23155]\n"
                                            "注意：仅在 MoviePilot 内置识别失败时触发。",
                                        },
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        ], {
            "enabled": False,
        }

    # ==========================================================
    #   核心：V2 链式事件 —— 名称识别
    #   只有 MP 内置识别器搞不定时才会触发
    # ==========================================================

    @eventmanager.register(ChainEventType.NameRecognize)
    def name_recognize(self, event: Event):
        """
        拦截名称识别链式事件。
        策略：
          1. 提取文件名中的 tmdbid
          2. 用 tmdbid 直接调 TMDB API 拿到标准信息
          3. 把标准名称+年份写回 event_data，MP 后续用它再走一遍匹配就能命中
        """
        if not self._enabled:
            return

        event_data = event.event_data
        if not event_data:
            return

        title = event_data.get("title", "")
        if not title:
            return

        # ---- Step 1: 提取 tmdbid ----
        tmdbid = self._extract_tmdbid(title)
        if not tmdbid:
            # 没有 tmdbid 标签，做个基础的全角转半角清洗就走
            cleaned = self._normalize_and_clean(title)
            if cleaned and cleaned != title:
                name, year = self._split_name_year(cleaned)
                if name:
                    event_data["name"] = name
                if year:
                    event_data["year"] = year
            return

        logger.info(f"TMDB直通识别 - 从文件名提取到 tmdbid={tmdbid}，原始: {title}")

        # ---- Step 2: 用 tmdbid 查 TMDB ----
        tmdb_info = self._query_tmdb(tmdbid)

        if not tmdb_info:
            logger.warning(f"TMDB直通识别 - tmdbid={tmdbid} 查 TMDB 失败，做基础清洗兜底")
            cleaned = self._normalize_and_clean(title)
            name, year = self._split_name_year(cleaned)
            if name:
                event_data["name"] = name
            if year:
                event_data["year"] = year
            return

        # ---- Step 3: 从 TMDB 数据提取标准名称 + 年份 ----
        tmdb_name = self._pick_best_title(tmdb_info)
        tmdb_year = self._pick_year(tmdb_info)

        logger.info(
            f"TMDB直通识别 - TMDB 返回: "
            f"name=「{tmdb_name}」, year={tmdb_year}"
        )

        # ---- Step 4: 写回 event_data ----
        if tmdb_name:
            event_data["name"] = tmdb_name
        if tmdb_year:
            event_data["year"] = tmdb_year

        # 补充提取季/集（tmdb 查的是影片级别的信息，季集还是得从文件名来）
        season, episode = self._extract_season_episode(title)
        if season is not None:
            event_data["season"] = season
        if episode is not None:
            event_data["episode"] = episode

    # ==========================================================
    #   TMDB 查询 —— 用 MP 内置模块，复用代理/缓存/API Key
    # ==========================================================

    @staticmethod
    def _query_tmdb(tmdbid: int) -> Optional[dict]:
        """
        通过 tmdbid 查询 TMDB，先查电影，再查电视剧。
        使用 MoviePilot 内置的 TmdbApi，自动走代理和缓存。
        """
        try:
            from app.modules.themoviedb.tmdbapi import TmdbApi
            tmdb = TmdbApi()

            # 先查电影
            info = tmdb.movie_detail(tmdbid)
            if info and info.get("id"):
                logger.debug(f"TMDB直通识别 - tmdbid={tmdbid} 匹配到电影")
                return info

            # 再查电视剧
            info = tmdb.tv_detail(tmdbid)
            if info and info.get("id"):
                logger.debug(f"TMDB直通识别 - tmdbid={tmdbid} 匹配到电视剧")
                return info

            logger.warning(f"TMDB直通识别 - tmdbid={tmdbid} 在 TMDB 中未找到")
            return None

        except Exception as e:
            logger.error(f"TMDB直通识别 - 查询 TMDB 异常: {e}")
            return None

    # ==========================================================
    #   文件名解析工具
    # ==========================================================

    @staticmethod
    def _extract_tmdbid(title: str) -> Optional[int]:
        """
        从文件名中提取 tmdbid。
        支持：{tmdbid=23155}  {tmdb-23155}  [tmdbid:23155]  (tmdbid=23155)
        """
        patterns = [
            r'[\{\[\(]tmdbid[=\-:\s]*(\d+)[\}\]\)]',
            r'[\{\[\(]tmdb[=\-:\s]*(\d+)[\}\]\)]',
        ]
        for p in patterns:
            m = re.search(p, title, re.IGNORECASE)
            if m:
                return int(m.group(1))
        return None

    @staticmethod
    def _pick_best_title(info: dict) -> Optional[str]:
        """
        从 TMDB 返回数据中选最佳标题。
        zh-CN 请求返回的 title/name 就是中文（如果有的话）。
        """
        # 电影用 title，电视剧用 name
        return (
            info.get("title")
            or info.get("name")
            or info.get("original_title")
            or info.get("original_name")
        )

    @staticmethod
    def _pick_year(info: dict) -> Optional[str]:
        """从 TMDB 返回数据中提取年份"""
        date = info.get("release_date") or info.get("first_air_date") or ""
        return date[:4] if len(date) >= 4 else None

    @staticmethod
    def _extract_season_episode(title: str) -> Tuple[Optional[int], Optional[int]]:
        """从文件名中提取季/集号"""
        season = episode = None

        # S01E02
        m = re.search(r'[Ss](\d{1,3})[Ee](\d{1,4})', title)
        if m:
            return int(m.group(1)), int(m.group(2))

        # 仅 S01
        m = re.search(r'[Ss](\d{1,3})(?!\d)', title)
        if m:
            season = int(m.group(1))

        # 仅 E01 / EP01
        m = re.search(r'[Ee][Pp]?(\d{1,4})(?!\d)', title)
        if m:
            episode = int(m.group(1))

        # 第X季 / 第X集
        m = re.search(r'第\s*(\d+)\s*季', title)
        if m and season is None:
            season = int(m.group(1))
        m = re.search(r'第\s*(\d+)\s*[集话話]', title)
        if m and episode is None:
            episode = int(m.group(1))

        return season, episode

    @staticmethod
    def _normalize_and_clean(title: str) -> str:
        """
        全角转半角 + 移除 {tmdbid=xxx} + 移除编码格式噪音
        """
        out = []
        for ch in title:
            c = ord(ch)
            if c == 0x3000:
                out.append(' ')
            elif ch == '（':
                out.append('(')
            elif ch == '）':
                out.append(')')
            elif ch == '【':
                out.append('[')
            elif ch == '】':
                out.append(']')
            elif 0xFF01 <= c <= 0xFF5E:
                out.append(chr(c - 0xFEE0))
            else:
                out.append(ch)
        text = ''.join(out)

        # 移除 tmdbid 标签
        text = re.sub(r'[\{\[\(]tmdb(?:id)?[=\-:\s]*\d+[\}\]\)]', '', text, flags=re.IGNORECASE)
        # 移除编码格式噪音
        text = re.sub(
            r'(?:1080[pPiI]|720[pPiI]|2160[pPiI]|4[kK]|REMUX|'
            r'BluRay|BDRip|WEB-?DL|WEBRip|HDRip|HDTV|'
            r'x26[45]|H\.?26[45]|HEVC|AVC|AAC|FLAC|DTS|AC3|'
            r'10bit|HDR|Dolby|ATMOS)',
            ' ', text, flags=re.IGNORECASE
        )
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def _split_name_year(title: str) -> Tuple[str, Optional[str]]:
        """从清洗后的标题中分离名称和年份"""
        year = None
        cleaned = title
        for p in [r'\((\d{4})\)', r'\[(\d{4})\]',
                   r'[\s._-]+(\d{4})(?=[\s._\-\[\]{}()$]|$)']:
            m = re.search(p, cleaned)
            if m:
                y = int(m.group(1))
                if 1900 <= y <= 2099:
                    year = str(y)
                    cleaned = (cleaned[:m.start()] + cleaned[m.end():]).strip()
                    break
        return cleaned, year

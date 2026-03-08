"""
TMDB ID 直通识别插件

核心策略：通过 get_module 劫持 recognize_media，
在 MP 内置识别器运行之前拦截。
如果文件名含 {tmdbid=xxx}，直接用 ID 调底层 TMDB 模块查询，
跳过 MP 的文件名猜测（它会把"空之境界 第五章"错误匹配到 2013 年同名日剧）。
"""
import re
from typing import Any, List, Dict, Tuple, Optional

from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import ChainEventType


class TmdbIdRecognize(_PluginBase):
    plugin_name = "TMDB ID 直通识别"
    plugin_desc = "模仿 Emby 刮削策略，从文件名提取 {tmdbid=xxx} 直接查询 TMDB，在内置识别之前拦截。"
    plugin_icon = "Themoviedb_A.png"
    plugin_version = "3.0"
    plugin_author = "sakezerto"
    author_url = "https://github.com/sakezerto"
    plugin_config_prefix = "tmdbidrecognize_"
    plugin_order = 0
    auth_level = 1

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
                                            "text": "本插件通过 get_module 劫持 recognize_media，"
                                            "在内置识别器运行之前拦截。\n\n"
                                            "当文件名包含 {tmdbid=23155} 时：\n"
                                            "→ 直接用 tmdbid 调 TMDB 底层模块\n"
                                            "→ 跳过 MP 的文件名猜测（避免匹配到同名错误作品）\n\n"
                                            "当文件名不含 tmdbid 时：\n"
                                            "→ 完全不干涉，走 MP 默认识别流程",
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
    #   核心：get_module 劫持 recognize_media
    #   在 MP 内置识别之前运行！不是事后补救！
    # ==========================================================

    def get_module(self) -> Dict[str, Any]:
        """
        劫持 recognize_media。
        处理链执行顺序：插件方法 → 系统模块方法
        - 返回非 None → 使用插件结果，系统模块不再执行
        - 返回 None → 继续执行系统模块（默认识别流程）
        """
        if not self._enabled:
            return {}
        return {
            "recognize_media": self._recognize_media,
        }

    def _recognize_media(self, meta, mtype=None, tmdbid=None, **kwargs):
        """
        劫持入口：
        1. 已有 tmdbid 参数 → return None（不干涉）
        2. 文件名无 {tmdbid=xxx} → return None（不干涉）
        3. 文件名有 {tmdbid=xxx} → 直接调底层 TheMovieDbModule.recognize_media
           带上 tmdbid 参数，跳过文件名猜测

        注意：直接调底层模块，不经过 chain 层，所以不会递归！
        """
        if tmdbid:
            return None

        org_string = self._get_org_string(meta)
        if not org_string:
            return None

        extracted_id = self._extract_tmdbid(org_string)
        if not extracted_id:
            return None

        logger.info(
            f"TMDB直通识别 - 拦截! 文件名含 tmdbid={extracted_id}，"
            f"跳过内置识别，直接查 TMDB。原始: {org_string}"
        )

        # ====== 直接调用底层 TMDB 模块（不走 chain，无递归） ======
        try:
            from app.modules.themoviedb import TheMovieDbModule
            tmdb_module = TheMovieDbModule()
            result = tmdb_module.recognize_media(
                meta=meta,
                mtype=mtype,
                tmdbid=extracted_id,
                **kwargs
            )
            if result:
                logger.info(
                    f"TMDB直通识别 - 成功! tmdbid={extracted_id} → "
                    f"{getattr(result, 'title', '?')} "
                    f"({getattr(result, 'year', '?')})"
                )
                return result
            else:
                logger.warning(f"TMDB直通识别 - tmdbid={extracted_id} 底层模块返回空")
                return None
        except Exception as e:
            logger.error(f"TMDB直通识别 - 底层模块调用失败: {e}，尝试备用方案")

        # ====== 备用：通过 ModuleManager 找 TMDB 模块实例 ======
        try:
            from app.core.module import ModuleManager
            for module in ModuleManager().get_modules("recognize_media"):
                cls_name = module.__class__.__name__
                if "themoviedb" in cls_name.lower() or "tmdb" in cls_name.lower():
                    logger.info(f"TMDB直通识别 - 备用方案: 通过 {cls_name} 查询")
                    result = module.recognize_media(
                        meta=meta, mtype=mtype, tmdbid=extracted_id, **kwargs
                    )
                    if result:
                        logger.info(f"TMDB直通识别 - 备用方案成功!")
                        return result
        except Exception as e2:
            logger.error(f"TMDB直通识别 - 备用方案也失败: {e2}")

        return None

    # ==========================================================
    #   兜底：NameRecognize 链式事件
    #   万一 get_module 不生效（MP版本不支持），识别失败时还能补救
    # ==========================================================

    @eventmanager.register(ChainEventType.NameRecognize)
    def name_recognize(self, event: Event):
        if not self._enabled:
            return

        event_data = event.event_data
        if not event_data:
            return

        title = event_data.get("title", "")
        if not title:
            return

        tmdbid = self._extract_tmdbid(title)
        if not tmdbid:
            return

        logger.info(f"TMDB直通识别 [兜底事件] - 提取到 tmdbid={tmdbid}")

        tmdb_info = self._query_tmdb_raw(tmdbid)
        if not tmdb_info:
            return

        name = self._pick_title(tmdb_info)
        year = self._pick_year(tmdb_info)

        if name:
            event_data["name"] = name
        if year:
            event_data["year"] = year

        season, episode = self._extract_season_episode(title)
        if season is not None:
            event_data["season"] = season
        if episode is not None:
            event_data["episode"] = episode

    # ==========================================================
    #   工具函数
    # ==========================================================

    @staticmethod
    def _get_org_string(meta) -> Optional[str]:
        for attr in ["org_string", "_org_string", "title", "rev_string", "name"]:
            val = getattr(meta, attr, None)
            if val and isinstance(val, str) and len(val) > 2:
                return val
        try:
            s = str(meta)
            return s if s and len(s) > 3 else None
        except Exception:
            return None

    @staticmethod
    def _extract_tmdbid(title: str) -> Optional[int]:
        for p in [r'[\{\[\(]tmdbid[=\-:\s]*(\d+)[\}\]\)]',
                   r'[\{\[\(]tmdb[=\-:\s]*(\d+)[\}\]\)]']:
            m = re.search(p, title, re.IGNORECASE)
            if m:
                return int(m.group(1))
        return None

    @staticmethod
    def _query_tmdb_raw(tmdbid: int) -> Optional[dict]:
        try:
            from app.modules.themoviedb.tmdbapi import TmdbApi
            tmdb = TmdbApi()
            info = tmdb.movie_detail(tmdbid)
            if info and info.get("id"):
                return info
            info = tmdb.tv_detail(tmdbid)
            if info and info.get("id"):
                return info
            return None
        except Exception as e:
            logger.error(f"TMDB直通识别 - TmdbApi 异常: {e}")
            return None

    @staticmethod
    def _pick_title(info: dict) -> Optional[str]:
        return info.get("title") or info.get("name") or info.get("original_title") or info.get("original_name")

    @staticmethod
    def _pick_year(info: dict) -> Optional[str]:
        date = info.get("release_date") or info.get("first_air_date") or ""
        return date[:4] if len(date) >= 4 else None

    @staticmethod
    def _extract_season_episode(title: str) -> Tuple[Optional[int], Optional[int]]:
        season = episode = None
        m = re.search(r'[Ss](\d{1,3})[Ee](\d{1,4})', title)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.search(r'[Ss](\d{1,3})(?!\d)', title)
        if m:
            season = int(m.group(1))
        m = re.search(r'[Ee][Pp]?(\d{1,4})(?!\d)', title)
        if m:
            episode = int(m.group(1))
        m = re.search(r'第\s*(\d+)\s*季', title)
        if m and season is None:
            season = int(m.group(1))
        m = re.search(r'第\s*(\d+)\s*[集话話]', title)
        if m and episode is None:
            episode = int(m.group(1))
        return season, episode

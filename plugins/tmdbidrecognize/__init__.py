"""
TMDB ID 直通识别插件 v5.1

当文件名包含 {tmdbid=xxx} 等标记时，直接用 ID 分别查询 TMDB 电影和电视剧，
通过年份和标题消歧，彻底解决系统无法判断类型而放弃识别的问题。
"""
import contextvars
from contextlib import contextmanager
from typing import Any, Optional, Dict, List, Tuple

from app.core.context import MediaInfo
from app.core.meta.metabase import MetaBase
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import MediaType


class TmdbIdRecognize(_PluginBase):
    plugin_name = "TMDB ID 直通识别"
    plugin_desc = "从文件名提取 {tmdbid=xxx} 直接查询 TMDB，分别尝试电影/电视剧并自动消歧。"
    plugin_icon = "Themoviedb_A.png"
    plugin_version = "5.1"
    plugin_author = "sakezerto"
    author_url = "https://github.com/sakezerto"
    plugin_config_prefix = "tmdbidrecognize_"
    plugin_order = 1
    auth_level = 1

    _contextvars = contextvars.ContextVar("tmdbid_recognize_flag", default=False)
    _enabled: bool = False

    @contextmanager
    def no_recursion(self):
        token = self._contextvars.set(True)
        try:
            yield
        finally:
            self._contextvars.reset(token)

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

    def get_service(self) -> List[Dict[str, Any]]:
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
                                            "text": "TMDB ID 直通识别 v5.1\n\n"
                                            "文件名含 {tmdbid=23155} 等标记时，"
                                            "分别以电影和电视剧类型查询 TMDB，"
                                            "再通过年份和标题自动消歧。\n\n"
                                            "解决系统遇到同 ID 同时存在电影和电视剧时"
                                            "直接放弃识别的问题。\n"
                                            "无 tmdbid 标签的文件不受影响，走默认识别流程。",
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
    #   get_module 劫持
    # ==========================================================

    def get_module(self) -> Dict[str, Any]:
        return {
            "recognize_media": self.on_recognize_media,
            "async_recognize_media": self.on_recognize_media,
        }

    def on_recognize_media(
        self,
        meta: MetaBase = None,
        mtype: MediaType = None,
        tmdbid: Optional[int] = None,
        episode_group: Optional[str] = None,
        cache: Optional[bool] = True,
        **kwargs,
    ) -> Optional[MediaInfo]:

        # 防递归：在内部 chain 调用时跳过
        if self._contextvars.get():
            return None

        if not self._enabled:
            return None

        # 获取 tmdbid：参数 > meta属性
        target_id = tmdbid
        if not target_id and meta and meta.tmdbid:
            target_id = meta.tmdbid
        if not target_id:
            return None

        # 确保是整数
        try:
            target_id = int(target_id)
        except (ValueError, TypeError):
            return None

        logger.info(f"TMDB直通识别 - 拦截! tmdbid={target_id}，"
                     f"meta.name={meta.name if meta else 'N/A'}，"
                     f"meta.year={meta.year if meta else 'N/A'}")

        # 分别尝试电影和电视剧
        with self.no_recursion():
            movie_info = self.chain.recognize_media(
                meta=meta,
                tmdbid=target_id,
                mtype=MediaType.MOVIE,
                episode_group=episode_group,
                cache=cache,
            )
            tv_info = self.chain.recognize_media(
                meta=meta,
                tmdbid=target_id,
                mtype=MediaType.TV,
                episode_group=episode_group,
                cache=cache,
            )

        # 消歧
        if movie_info and tv_info:
            result = self._disambiguate(meta, movie_info, tv_info, target_id)
        elif movie_info:
            result = movie_info
        elif tv_info:
            result = tv_info
        else:
            logger.warning(f"TMDB直通识别 - tmdbid={target_id} 电影和电视剧均未查到")
            return False

        logger.info(f"TMDB直通识别 - 成功! tmdbid={target_id} → "
                     f"{result.type.value} {result.title} ({result.year}) "
                     f"TMDB={result.tmdb_id}")
        return result

    # ==========================================================
    #   消歧逻辑
    # ==========================================================

    @staticmethod
    def _disambiguate(
        meta: MetaBase,
        movie_info: MediaInfo,
        tv_info: MediaInfo,
        target_id: int,
    ) -> MediaInfo:
        """
        同一 tmdbid 同时匹配到电影和电视剧时，按年份 → 标题进行消歧。
        """
        # 1. 年份消歧
        if meta and meta.year:
            movie_year_match = str(movie_info.year) == str(meta.year)
            tv_year_match = str(tv_info.year) == str(meta.year)
            if movie_year_match and not tv_year_match:
                logger.info(f"TMDB直通识别 - 年份匹配电影: {movie_info.title} ({movie_info.year})")
                return movie_info
            if tv_year_match and not movie_year_match:
                logger.info(f"TMDB直通识别 - 年份匹配电视剧: {tv_info.title} ({tv_info.year})")
                return tv_info

        # 2. 标题消歧
        if meta and meta.name:
            name = meta.name
            movie_title = movie_info.title or ""
            tv_title = tv_info.title or ""
            movie_match = name in movie_title or movie_title in name
            tv_match = name in tv_title or tv_title in name
            if movie_match and not tv_match:
                logger.info(f"TMDB直通识别 - 标题匹配电影: {movie_title}")
                return movie_info
            if tv_match and not movie_match:
                logger.info(f"TMDB直通识别 - 标题匹配电视剧: {tv_title}")
                return tv_info

        # 3. 无法消歧，默认电影
        logger.warn(f"TMDB直通识别 - tmdbid={target_id} 同时匹配电影和电视剧，"
                     f"无法通过年份/标题消歧，默认使用电影")
        return movie_info


"""
TMDB ID 直通识别插件 v4.1 (调试版)

参考 wikrin/CureTMDbAnime 的实现方式
"""
import contextvars
import re
from contextlib import contextmanager
from typing import Any, Optional, Dict, List, Tuple

from app.core.context import MediaInfo
from app.core.meta.metabase import MetaBase
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import MediaType


class TmdbIdRecognize(_PluginBase):
    plugin_name = "TMDB ID 直通识别"
    plugin_desc = "模仿 Emby 策略，从文件名提取 {tmdbid=xxx} 直接查询 TMDB，跳过内置文件名猜测。"
    plugin_icon = "Themoviedb_A.png"
    plugin_version = "4.1"
    plugin_author = "sakezerto"
    author_url = "https://github.com/sakezerto"
    plugin_config_prefix = "tmdbidrecognize_"
    plugin_order = 25
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
                                            "text": "模仿 Emby 刮削策略：\n"
                                            "文件名含 {tmdbid=23155} → 直接用 ID 查 TMDB → 精准匹配\n\n"
                                            "解决 MP 把「空之境界 第五章」错误匹配到同名日剧的问题。\n"
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

        # 防递归
        if self._contextvars.get():
            return None

        if not self._enabled:
            return None

        # 已有 tmdbid，不干涉
        if tmdbid:
            return None

        if not meta:
            return None

        # ====== 调试：打印 meta 的所有属性 ======
        extracted_id = None
        source_attr = None

        # 遍历所有可能含有原始文件名的属性
        candidates = {}
        for attr in dir(meta):
            if attr.startswith('__'):
                continue
            try:
                val = getattr(meta, attr)
                if isinstance(val, str) and len(val) > 2:
                    candidates[attr] = val
                    # 尝试从每个字符串属性中提取 tmdbid
                    tid = self._extract_tmdbid(val)
                    if tid and not extracted_id:
                        extracted_id = tid
                        source_attr = attr
            except Exception:
                pass

        # 打印调试信息
        logger.info(
            f"TMDB直通识别 [DEBUG] meta 字符串属性: "
            f"{', '.join(f'{k}={repr(v[:80])}' for k, v in candidates.items())}"
        )

        if extracted_id:
            logger.info(
                f"TMDB直通识别 - 从 meta.{source_attr} 提取到 tmdbid={extracted_id}"
            )
        else:
            # 最后尝试：str(meta)
            meta_str = str(meta) if meta else ""
            logger.info(f"TMDB直通识别 [DEBUG] str(meta)={repr(meta_str[:100])}")
            extracted_id = self._extract_tmdbid(meta_str)
            if extracted_id:
                source_attr = "str(meta)"
                logger.info(
                    f"TMDB直通识别 - 从 str(meta) 提取到 tmdbid={extracted_id}"
                )

        if not extracted_id:
            logger.debug("TMDB直通识别 - 未找到 tmdbid，不干涉")
            return None

        # ====== 核心：防递归调用 chain ======
        logger.info(
            f"TMDB直通识别 - 拦截! tmdbid={extracted_id}，"
            f"来源属性: {source_attr}"
        )

        with self.no_recursion():
            media_info = self.chain.recognize_media(
                meta=meta,
                tmdbid=extracted_id,
                mtype=mtype,
                episode_group=episode_group,
                cache=cache,
                **kwargs,
            )

        if media_info is None:
            logger.warning(
                f"TMDB直通识别 - tmdbid={extracted_id} 识别失败"
            )
            return False

        logger.info(
            f"TMDB直通识别 - 成功! "
            f"tmdbid={extracted_id} → "
            f"{media_info.title} ({media_info.year}) "
            f"TMDB={media_info.tmdb_id}"
        )
        return media_info

    # ==========================================================
    #   工具函数
    # ==========================================================

    @staticmethod
    def _extract_tmdbid(title: str) -> Optional[int]:
        """从任意字符串提取 tmdbid"""
        for p in [
            r'[\{\[\(]tmdbid[=\-:\s]*(\d+)[\}\]\)]',
            r'[\{\[\(]tmdb[=\-:\s]*(\d+)[\}\]\)]',
            # 兜底：不限定括号类型，直接匹配 tmdbid=数字
            r'tmdbid[=\-:\s]*(\d+)',
            r'tmdb[=\-:\s]*(\d+)',
        ]:
            m = re.search(p, title, re.IGNORECASE)
            if m:
                return int(m.group(1))
        return None

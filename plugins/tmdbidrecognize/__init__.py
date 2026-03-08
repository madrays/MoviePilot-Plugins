"""
TMDB ID 直通识别插件

参考 wikrin/CureTMDbAnime 的实现方式：
- get_module 劫持 recognize_media，开局拦截
- contextvars 防递归
- self.chain.recognize_media(tmdbid=xxx) 回调原始识别流程

解决：空之境界 第五章 矛盾螺旋 (2008) {tmdbid=23155} 被错误匹配到 2013 年同名日剧
"""
import contextvars
import re
from typing import Any, Optional, Dict, List, Tuple

from app.core.context import MediaInfo
from app.core.meta.metabase import MetaBase
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import MediaType


class TmdbIdRecognize(_PluginBase):
    # 插件名称
    plugin_name = "TMDB ID 直通识别"
    # 插件描述
    plugin_desc = "模仿 Emby 策略，从文件名提取 {tmdbid=xxx} 直接查询 TMDB，跳过内置文件名猜测。"
    # 插件图标
    plugin_icon = "Themoviedb_A.png"
    # 插件版本
    plugin_version = "4.0"
    # 插件作者
    plugin_author = "sakezerto"
    # 作者主页
    author_url = "https://github.com/sakezerto"
    # 插件配置项ID前缀
    plugin_config_prefix = "tmdbidrecognize_"
    # 加载顺序
    plugin_order = 25
    # 可使用的用户级别
    auth_level = 1

    # 防递归标志（参考 CureTMDbAnime）
    _contextvars = contextvars.ContextVar("tmdbid_recognize_flag", default=False)

    # 配置属性
    _enabled: bool = False

    def no_recursion(self):
        """防递归上下文管理器"""
        from contextlib import contextmanager

        @contextmanager
        def _no_recursion():
            token = self._contextvars.set(True)
            try:
                yield
            finally:
                self._contextvars.reset(token)

        return _no_recursion()

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
                                            "无 tmdbid 标签的文件不受影响，走默认识别流程。\n\n"
                                            "支持格式：{tmdbid=23155} {tmdb-23155} [tmdbid:23155]",
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
    #   核心：get_module 劫持（参考 CureTMDbAnime）
    # ==========================================================

    def get_module(self) -> Dict[str, Any]:
        """
        劫持 recognize_media 和 async_recognize_media
        """
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
        """
        劫持 recognize_media 方法。

        逻辑：
        1. 递归调用 → return None（让系统模块执行）
        2. 插件未启用 → return None
        3. 已有 tmdbid → return None（不需要插手）
        4. 文件名无 {tmdbid=xxx} → return None（不干涉）
        5. 文件名有 {tmdbid=xxx} → 提取 ID，
           在防递归上下文中调用 self.chain.recognize_media(tmdbid=提取的ID)
           返回结果；如果结果为 None 则 return False 阻止后续模块执行
        """
        # 防递归：第二次进入时直接放行给系统模块
        if self._contextvars.get():
            return None

        # 插件未启用
        if not self._enabled:
            return None

        # 上游已经传了 tmdbid，不需要插手
        if tmdbid:
            return None

        # 没有 meta 对象
        if not meta:
            return None

        # 从 meta 获取原始文件名
        org_string = self._get_org_string(meta)
        if not org_string:
            return None

        # 提取 tmdbid
        extracted_id = self._extract_tmdbid(org_string)
        if not extracted_id:
            # 文件名没有 tmdbid 标签，完全不干涉
            return None

        logger.info(
            f"TMDB直通识别 - 拦截! "
            f"从「{org_string}」提取到 tmdbid={extracted_id}"
        )

        # ====== 核心：在防递归上下文中调用 chain 层 ======
        # self.chain 是 _PluginBase 提供的，指向处理链
        # no_recursion() 确保 chain 再次触发 get_module 时，
        # _contextvars 为 True → return None → 走系统默认模块
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
            # 即使用了正确的 tmdbid 也识别失败
            # 返回 False 阻止 run_module 继续执行其他模块（参考 CureTMDbAnime）
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
    def _get_org_string(meta: MetaBase) -> Optional[str]:
        """从 MetaBase 获取原始文件名"""
        # MetaBase 的 org_string 属性存储原始输入字符串
        for attr in ["org_string", "_org_string"]:
            val = getattr(meta, attr, None)
            if val and isinstance(val, str):
                return val
        # 回退：尝试 title
        val = getattr(meta, "title", None)
        if val and isinstance(val, str):
            return val
        return None

    @staticmethod
    def _extract_tmdbid(title: str) -> Optional[int]:
        """
        从文件名提取 tmdbid。
        支持：{tmdbid=23155} {tmdb-23155} [tmdbid:23155] (tmdbid=23155)
        """
        for p in [
            r'[\{\[\(]tmdbid[=\-:\s]*(\d+)[\}\]\)]',
            r'[\{\[\(]tmdb[=\-:\s]*(\d+)[\}\]\)]',
        ]:
            m = re.search(p, title, re.IGNORECASE)
            if m:
                return int(m.group(1))
        return None

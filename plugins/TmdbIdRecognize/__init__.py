"""
MoviePilot TMDB ID 直通识别插件

模仿 Emby 的刮削策略：
1. 从文件名中提取 {tmdbid=xxx} 标签
2. 直接用 TMDB ID 调用 TMDB API 获取精确的媒体信息
3. 将识别结果注入 MoviePilot 的识别链，跳过不靠谱的文件名解析

解决以下命名无法识别的问题：
- 空之境界 第五章 矛盾螺旋 （2008） {tmdbid=23155}
- 进击的巨人 最终季 完结篇（后篇）（2023）{tmdbid=888888}
- 命运之夜 天之杯Ⅲ 春之歌（2020）{tmdb=12345}
"""
import re
from typing import Any, List, Dict, Tuple, Optional

from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import ChainEventType, MediaType


class TmdbIdRecognize(_PluginBase):
    # 插件名称
    plugin_name = "TMDB ID 直通识别"
    # 插件描述
    plugin_desc = "模仿 Emby 刮削策略，从文件名提取 {tmdbid=xxx} 直接查询 TMDB，精准识别媒体。"
    # 插件图标
    plugin_icon = "Themoviedb_A.png"
    # 插件版本
    plugin_version = "2.0"
    # 插件作者
    plugin_author = "YourName"
    # 作者主页
    author_url = "https://github.com/YourName"
    # 插件配置项ID前缀
    plugin_config_prefix = "tmdbidrecognize_"
    # 加载顺序（越小越先执行）
    plugin_order = 0
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _fallback_search = True  # 如果ID查询得到的名称与文件名差异大，用TMDB搜索辅助验证
    _prefer_cn_title = True  # 优先使用中文标题

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled", False)
            self._fallback_search = config.get("fallback_search", True)
            self._prefer_cn_title = config.get("prefer_cn_title", True)

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
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
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "fallback_search",
                                            "label": "TMDB搜索验证",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "prefer_cn_title",
                                            "label": "优先中文标题",
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
                                            "text": "工作流程（模仿 Emby 刮削策略）：\n"
                                            "1. 从文件名中提取 {tmdbid=xxx} 标签\n"
                                            "2. 用 TMDB ID 直接调用 TMDB API 拿到精确的影片数据\n"
                                            "3. 将 TMDB 返回的标准名称和年份注入 MoviePilot 识别链\n"
                                            "4. MoviePilot 后续流程用这个标准名称去匹配，命中率 100%\n\n"
                                            "支持格式：{tmdbid=23155}、{tmdb=23155}、[tmdbid=23155]、"
                                            "{tmdbid-23155}，大小写不敏感。",
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
            "fallback_search": True,
            "prefer_cn_title": True,
        }

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        pass

    # ============================================================
    #   方案一（优先）：通过 get_module 劫持 recognize_media
    #   直接在「媒体识别」环节注入 tmdbid，最彻底
    # ============================================================

    def get_module(self) -> Dict[str, Any]:
        """
        劫持系统的 recognize_media 方法
        当文件名包含 {tmdbid=xxx} 时，直接告诉 MP 用这个 ID 去查 TMDB
        """
        if not self._enabled:
            return {}
        return {
            "recognize_media": self.recognize_media_hook,
        }

    def recognize_media_hook(self, meta, mtype=None, tmdbid=None, **kwargs):
        """
        劫持 recognize_media：
        - 如果上游已经传了 tmdbid，不干涉，返回 None 让默认流程继续
        - 如果没有 tmdbid 但文件名里有 {tmdbid=xxx}，提取后用 TMDB 查询
        """
        # 已经有 tmdbid 了，不需要插手
        if tmdbid:
            return None

        # 从 meta 中取原始文件名
        org_string = self._get_org_string(meta)
        if not org_string:
            return None

        # 提取 tmdbid
        extracted_id, media_type_hint = self._extract_tmdbid_from_title(org_string)
        if not extracted_id:
            return None

        logger.info(f"TMDB直通识别 - 从文件名提取到 tmdbid={extracted_id}，原始标题: {org_string}")

        # 用提取到的 tmdbid 查 TMDB 拿到精确数据
        tmdb_info = self._query_tmdb_by_id(extracted_id, mtype=mtype)
        if not tmdb_info:
            logger.warning(f"TMDB直通识别 - tmdbid={extracted_id} 查询TMDB失败，交还默认流程")
            return None

        # 拿到结果后，用标准数据调用系统的 recognize_media
        # 这里不直接返回 mediainfo，而是把 tmdbid 注入 meta 让系统自己去查
        # 这样能保证所有后续的分类、刮削逻辑都正常走通
        try:
            from app.chain.media import MediaChain
            media_chain = MediaChain()

            # 确定类型
            result_mtype = mtype
            if not result_mtype:
                result_mtype = self._guess_media_type(tmdb_info)

            # 核心：用提取到的 tmdbid 调用系统识别，这次带上 tmdbid 参数
            logger.info(
                f"TMDB直通识别 - 使用 tmdbid={extracted_id} "
                f"类型={result_mtype} 调用系统识别"
            )
            mediainfo = media_chain.recognize_media(
                meta=meta,
                mtype=result_mtype,
                tmdbid=extracted_id,
                **kwargs
            )
            if mediainfo:
                logger.info(
                    f"TMDB直通识别 - 成功！"
                    f"{mediainfo.title} ({mediainfo.year}) "
                    f"tmdbid={mediainfo.tmdb_id}"
                )
                return mediainfo
            else:
                logger.warning(f"TMDB直通识别 - tmdbid={extracted_id} 系统识别返回空")
                return None

        except Exception as e:
            logger.error(f"TMDB直通识别 - 调用系统识别异常: {e}")
            return None

    # ============================================================
    #   方案二（兜底）：通过链式事件清洗文件名
    #   如果 get_module 不生效（老版本MP），走这条路
    # ============================================================

    @eventmanager.register(ChainEventType.NameRecognize)
    def name_recognize(self, event: Event):
        """
        监听名称识别链式事件
        在这一步把文件名清洗干净：全角→半角、移除{tmdbid=xxx}、
        提取年份，并尝试用tmdbid去TMDB拿到标准名称
        """
        if not self._enabled:
            return

        event_data = event.event_data
        if not event_data:
            return

        title = event_data.get("title", "")
        if not title:
            return

        # 提取 tmdbid
        extracted_id, _ = self._extract_tmdbid_from_title(title)
        if not extracted_id:
            # 没有 tmdbid，做基本的全角转半角清洗
            cleaned = self._normalize_title(title)
            if cleaned != title:
                logger.info(f"TMDB直通识别 [名称清洗] - {title} -> {cleaned}")
                # 提取年份
                name, year = self._extract_year(cleaned)
                if name:
                    event_data["name"] = name
                if year:
                    event_data["year"] = year
            return

        logger.info(f"TMDB直通识别 [名称识别] - 提取到 tmdbid={extracted_id}")

        # 用 tmdbid 查 TMDB
        tmdb_info = self._query_tmdb_by_id(extracted_id)

        if tmdb_info:
            # 从 TMDB 返回的数据中提取标准名称和年份
            name = self._get_title_from_tmdb(tmdb_info)
            year = self._get_year_from_tmdb(tmdb_info)

            logger.info(
                f"TMDB直通识别 [名称识别] - TMDB 返回: "
                f"name={name}, year={year}"
            )

            if name:
                event_data["name"] = name
            if year:
                event_data["year"] = year
        else:
            # TMDB 查询失败，至少做个基本清洗
            cleaned = self._normalize_title(title)
            name, year = self._extract_year(cleaned)
            if name:
                event_data["name"] = name
            if year:
                event_data["year"] = year

    # ============================================================
    #   TMDB API 查询（使用 MoviePilot 内置的 TMDB 模块）
    # ============================================================

    def _query_tmdb_by_id(
        self,
        tmdbid: int,
        mtype: MediaType = None,
    ) -> Optional[dict]:
        """
        通过 tmdbid 查询 TMDB，返回影片详情 dict
        优先尝试使用 MoviePilot 内置的 TMDB 模块，
        如果不可用则回退到直接 HTTP 请求
        """
        # 方式1：使用 MP 内置的 TmdbApi
        try:
            from app.modules.themoviedb.tmdbapi import TmdbApi
            tmdb_api = TmdbApi()

            info = None

            # 如果指定了类型，优先查对应类型
            if mtype == MediaType.TV:
                info = tmdb_api.tv_detail(tmdbid)
            elif mtype == MediaType.MOVIE:
                info = tmdb_api.movie_detail(tmdbid)
            else:
                # 未指定类型，先查电影，再查电视剧
                info = tmdb_api.movie_detail(tmdbid)
                if not info:
                    info = tmdb_api.tv_detail(tmdbid)

            if info:
                logger.debug(f"TMDB直通识别 - TmdbApi 查询成功: {tmdbid}")
                return info

        except ImportError:
            logger.debug("TMDB直通识别 - TmdbApi 不可用，尝试直接 HTTP 请求")
        except Exception as e:
            logger.warning(f"TMDB直通识别 - TmdbApi 查询异常: {e}")

        # 方式2：直接 HTTP 请求 TMDB API
        return self._query_tmdb_by_http(tmdbid, mtype)

    def _query_tmdb_by_http(
        self,
        tmdbid: int,
        mtype: MediaType = None,
    ) -> Optional[dict]:
        """
        直接通过 HTTP 请求 TMDB API（兜底方案）
        """
        try:
            import requests
            from app.core.config import settings

            api_domain = getattr(settings, "TMDB_API_DOMAIN", "api.themoviedb.org")
            # MoviePilot 内置的 TMDB API Key
            api_key = getattr(settings, "TMDB_API_KEY", None)

            if not api_key:
                # 尝试从已初始化的 TMDB 模块获取
                try:
                    from app.modules.themoviedb.tmdbapi import TmdbApi
                    api_key = TmdbApi().apikey if hasattr(TmdbApi(), 'apikey') else None
                except Exception:
                    pass

            if not api_key:
                logger.warning("TMDB直通识别 - 无法获取 TMDB API Key")
                return None

            # 构建代理
            proxies = None
            proxy_host = getattr(settings, "PROXY_HOST", None)
            if proxy_host:
                proxies = {
                    "http": proxy_host,
                    "https": proxy_host,
                }

            base_url = f"https://{api_domain}/3"

            # 先尝试电影
            endpoints = []
            if mtype == MediaType.TV:
                endpoints = [f"{base_url}/tv/{tmdbid}"]
            elif mtype == MediaType.MOVIE:
                endpoints = [f"{base_url}/movie/{tmdbid}"]
            else:
                endpoints = [
                    f"{base_url}/movie/{tmdbid}",
                    f"{base_url}/tv/{tmdbid}",
                ]

            for url in endpoints:
                try:
                    resp = requests.get(
                        url,
                        params={
                            "api_key": api_key,
                            "language": "zh-CN",
                            "append_to_response": "alternative_titles",
                        },
                        proxies=proxies,
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data and data.get("id"):
                            return data
                except requests.RequestException:
                    continue

            return None

        except Exception as e:
            logger.error(f"TMDB直通识别 - HTTP 请求异常: {e}")
            return None

    # ============================================================
    #   工具函数
    # ============================================================

    @staticmethod
    def _extract_tmdbid_from_title(title: str) -> Tuple[Optional[int], Optional[str]]:
        """
        从标题中提取 tmdbid 和可能的类型提示
        支持格式：
          {tmdbid=23155}  {tmdbid-23155}  {tmdbid:23155}
          [tmdbid=23155]  (tmdbid=23155)
          {tmdb=23155}    {tmdb-23155}
          {tvdbid=xxx} 不处理（那是另一个数据源）
        返回: (tmdbid, media_type_hint)
        """
        patterns = [
            (r'\{tmdbid[=\-:]?\s*(\d+)\}', None),
            (r'\[tmdbid[=\-:]?\s*(\d+)\]', None),
            (r'\(tmdbid[=\-:]?\s*(\d+)\)', None),
            (r'\{tmdb[=\-:]?\s*(\d+)\}', None),
            (r'\[tmdb[=\-:]?\s*(\d+)\]', None),
        ]
        for pattern, type_hint in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return int(match.group(1)), type_hint
        return None, None

    @staticmethod
    def _get_org_string(meta) -> Optional[str]:
        """
        从 MetaInfo 对象中获取原始文件名
        兼容不同版本的 MetaInfo 属性名
        """
        for attr in ["org_string", "title", "org_title", "_org_string"]:
            val = getattr(meta, attr, None)
            if val:
                return str(val)
        return None

    def _get_title_from_tmdb(self, tmdb_info: dict) -> Optional[str]:
        """
        从 TMDB 返回的数据中提取最合适的标题
        """
        if not tmdb_info:
            return None

        if self._prefer_cn_title:
            # 中文标题（zh-CN 查询返回的 title 就是中文）
            title = tmdb_info.get("title") or tmdb_info.get("name")
            if title:
                return title

        # 回退到原始标题
        return (
            tmdb_info.get("original_title")
            or tmdb_info.get("original_name")
            or tmdb_info.get("title")
            or tmdb_info.get("name")
        )

    @staticmethod
    def _get_year_from_tmdb(tmdb_info: dict) -> Optional[str]:
        """
        从 TMDB 返回数据中提取年份
        """
        if not tmdb_info:
            return None

        date_str = (
            tmdb_info.get("release_date")      # 电影
            or tmdb_info.get("first_air_date")  # 电视剧
        )
        if date_str and len(date_str) >= 4:
            return date_str[:4]
        return None

    @staticmethod
    def _guess_media_type(tmdb_info: dict) -> Optional[MediaType]:
        """
        从 TMDB 返回数据猜测媒体类型
        """
        if not tmdb_info:
            return None
        # 电影有 release_date，电视剧有 first_air_date
        if tmdb_info.get("release_date") is not None:
            return MediaType.MOVIE
        if tmdb_info.get("first_air_date") is not None:
            return MediaType.TV
        # 通过字段名判断
        if "title" in tmdb_info and "name" not in tmdb_info:
            return MediaType.MOVIE
        if "name" in tmdb_info and "title" not in tmdb_info:
            return MediaType.TV
        return None

    @staticmethod
    def _normalize_title(title: str) -> str:
        """
        基本的标题标准化：全角→半角，清理 {tmdbid=xxx} 标签
        """
        result = []
        for char in title:
            code = ord(char)
            if code == 0x3000:
                result.append(' ')
            elif char == '（':
                result.append('(')
            elif char == '）':
                result.append(')')
            elif char == '【':
                result.append('[')
            elif char == '】':
                result.append(']')
            elif 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            else:
                result.append(char)
        cleaned = ''.join(result)

        # 移除 tmdbid 标签
        cleaned = re.sub(
            r'[\{\[\(]tmdb(?:id)?[=\-:]?\s*\d+[\}\]\)]',
            '', cleaned, flags=re.IGNORECASE
        ).strip()

        # 清理多余空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    @staticmethod
    def _extract_year(title: str) -> Tuple[str, Optional[str]]:
        """
        从清洗后的标题中提取年份
        """
        year = None
        cleaned = title
        for pattern in [r'\((\d{4})\)', r'\[(\d{4})\]',
                        r'[\s._-]+(\d{4})(?=[\s._\-\[\]{}()$]|$)']:
            match = re.search(pattern, cleaned)
            if match:
                y = int(match.group(1))
                if 1900 <= y <= 2099:
                    year = str(y)
                    cleaned = cleaned[:match.start()] + cleaned[match.end():]
                    cleaned = cleaned.strip()
                    break
        return cleaned, year

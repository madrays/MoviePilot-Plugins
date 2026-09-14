"""
小米路由器监控插件
版本: 1.0.0
作者: madrays
功能：
- 自动登录小米路由器（适配新旧加密），抓取实时运行状态（在线设备、上下行、流量、CPU/内存、运行时长等）。
- 端口映射管理：列表、添加、删除。支持在设置页一次性执行或通过指令即时执行。
- 快捷操作预设：为常用场景预设一组端口规则，例如临时开启/关闭 SSH(22) 或远程管理端口，聊天中用“/xiaomi q”一键切换（存在则删，不存在则加）。
使用建议：
- 设置页填入路由器IP和登录密码（用户名固定 admin），启用后可定时获取状态并发送通知。
- 需要立刻执行一次（拉取状态或执行端口变更），勾选“立即运行一次”保存即可。
"""
import json
import time
import math
import hashlib
import random
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

import requests
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

try:
    from app.sdk.config import settings
except ImportError:
    from app.core.config import settings
from app.plugins import _PluginBase
try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from app.schemas import NotificationType
from app.schemas.types import EventType
try:
    from app.sdk.events import eventmanager
except ImportError:
    from app.core.event import eventmanager


class xiaomirouter(_PluginBase):
    # 插件元信息
    plugin_name = "小米路由器监控"
    plugin_desc = "登录小米路由器并获取运行状态，支持端口映射管理与快捷一键切换"
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/xiaomi.png"
    plugin_version = "3.0.0"
    plugin_author = "madrays"
    author_url = "https://github.com/madrays"
    plugin_config_prefix = "xiaomirouter_"
    plugin_order = 5
    auth_level = 2

    # 配置项
    _enabled: bool = False
    _notify: bool = False
    _onlyonce: bool = False
    _cron: Optional[str] = "0 */6 * * *"  # 默认每6小时
    _router_ip: Optional[str] = None
    _password: Optional[str] = None
    _debug: bool = False
    # 端口映射参数（填写即执行）
    _pf_name: str = ""
    _pf_proto: str = ""  # tcp/udp/both（前端展示文本，后台转换），留空不执行
    _pf_sport: int = 0
    _pf_ip: str = ""
    _pf_dport: int = 0
    _pf_del_port: int = 0
    _pf_del_proto: str = ""  # 删除无需选择类型，将自动从列表推断
    _pf_add_run: bool = False  # 添加执行开关
    _pf_del_run: bool = False  # 删除执行开关
    # 快捷操作预设
    _q_name: str = ""
    _q_proto: str = ""
    _q_sport: int = 0
    _q_ip: str = ""
    _q_dport: int = 0

    # 运行态
    _scheduler: Optional[BackgroundScheduler] = None
    _last_token: Optional[str] = None
    _last_mode_new_encrypt: Optional[bool] = None
    _last_login_key: Optional[str] = None
    _last_status: Optional[Dict[str, Any]] = None
    _init_info: Optional[Dict[str, Any]] = None
    _last_pf_list: Optional[List[Dict[str, Any]]] = None
    _last_pf_result: Optional[Dict[str, Any]] = None
    _do_pf_this_run: bool = False
    _evt_registered: bool = False

    def _d(self, msg: str):
        if self._debug:
            logger.info(f"[DEBUG][xiaomirouter] {msg}")

    def init_plugin(self, config: dict = None):
        self.stop_service()
        if config:
            if "enabled" in config: self._enabled = config.get("enabled")
            if "notify" in config: self._notify = config.get("notify")
            if "onlyonce" in config: self._onlyonce = config.get("onlyonce")
            if "cron" in config and config.get("cron"): self._cron = config.get("cron")
            if "router_ip" in config: self._router_ip = (config.get("router_ip") or "").strip()
            if "password" in config: self._password = config.get("password")
            if "debug" in config: self._debug = bool(config.get("debug", False))
            # 端口映射参数（填写即执行，保留基础配置）
            if "pf_name" in config: self._pf_name = (config.get("pf_name") or "").strip()
            if "pf_proto" in config: self._pf_proto = (str(config.get("pf_proto") or "").strip())
            if "pf_sport" in config:
                try: self._pf_sport = int(config.get("pf_sport", 0))
                except: pass
            if "pf_ip" in config: self._pf_ip = (config.get("pf_ip") or "").strip()
            if "pf_dport" in config:
                try: self._pf_dport = int(config.get("pf_dport", 0))
                except: pass
            if "pf_del_port" in config:
                try: self._pf_del_port = int(config.get("pf_del_port", 0))
                except: pass
            if "pf_del_proto" in config: self._pf_del_proto = (str(config.get("pf_del_proto") or "").strip())
            if "pf_add_run" in config: self._pf_add_run = bool(config.get("pf_add_run"))
            if "pf_del_run" in config: self._pf_del_run = bool(config.get("pf_del_run"))
            # 快捷操作配置（持久保存）
            if "q_name" in config: self._q_name = (config.get("q_name") or "").strip()
            if "q_proto" in config: self._q_proto = (str(config.get("q_proto") or "").strip())
            if "q_sport" in config:
                try: self._q_sport = int(config.get("q_sport", 0))
                except: pass
            if "q_ip" in config: self._q_ip = (config.get("q_ip") or "").strip()
            if "q_dport" in config:
                try: self._q_dport = int(config.get("q_dport", 0))
                except: pass
        # 标记本次是否执行端口增删：仅当用户勾选了“立即运行一次”时执行
        self._do_pf_this_run = bool(self._onlyonce)
        logger.info(f"小米路由器监控配置: enabled={self._enabled}, ip={self._router_ip}, cron={self._cron}")
        self._d(f"配置: notify={self._notify}, onlyonce={self._onlyonce}, debug={self._debug}")

        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(
                func=self.refresh_status,
                trigger='date',
                run_date=datetime.now(pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                name=self.plugin_name
            )
            # 与其它插件一致：手动触发后立即把onlyonce置回False，并完整回写当前配置，避免清空
            self._onlyonce = False
            try:
                self.update_config({
                    "enabled": self._enabled,
                    "notify": self._notify,
                    "onlyonce": False,
                    "debug": self._debug,
                    "router_ip": self._router_ip or "",
                    "password": self._password or "",
                    "cron": self._cron or "0 */6 * * *",
                    # onlyonce执行后，端口表单全部清空，仅保留基础信息
                    "pf_name": "",
                    "pf_proto": "",
                    "pf_sport": 0,
                    "pf_ip": "",
                    "pf_dport": 0,
                    "pf_del_port": 0,
                    "pf_del_proto": "",
                    "pf_add_run": False,
                    "pf_del_run": False,
                    # 保留快捷操作配置
                    "q_name": self._q_name,
                    "q_proto": self._q_proto,
                    "q_sport": self._q_sport,
                    "q_ip": self._q_ip,
                    "q_dport": self._q_dport,
                    
                })
            except Exception:
                pass
            if self._scheduler.get_jobs():
                self._scheduler.start()

        # 注册命令事件监听（只注册一次）
        try:
            if not self._evt_registered:
                eventmanager.add_event_listener(EventType.CommandExcute, self.on_command)
                self._evt_registered = True
                self._d("已注册事件监听：EventType.CommandExcute -> on_command")
        except Exception as e:
            logger.error(f"注册命令事件监听失败: {e}")

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            return [{
                "id": "xiaomirouter_monitor",
                "name": "小米路由器监控",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.refresh_status,
                "kwargs": {}
            }]
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        proto_items = [
            {'title': 'tcp', 'value': 'tcp'},
            {'title': 'udp', 'value': 'udp'},
            {'title': 'both', 'value': 'both'},
        ]
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'enabled', 'label': '启用插件'}
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'notify', 'label': '开启通知'}
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'debug', 'label': '调试日志'}
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 3},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'onlyonce', 'label': '立即运行一次'}
                                }]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VTextField',
                                    'props': {
                                        'model': 'router_ip',
                                        'label': '路由器IP (如 192.168.31.1)',
                                        'placeholder': '必填',
                                        'density': 'comfortable'
                                    }
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VTextField',
                                    'props': {
                                        'model': 'password',
                                        'label': '登录密码 (用户名固定 admin)',
                                        'type': 'password',
                                        'density': 'comfortable'
                                    }
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VCronField',
                                    'props': {
                                        'model': 'cron',
                                        'label': '定时（Cron）'
                                    }
                                }]
                            }
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'outlined', 'class': 'mt-2'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '📘 使用帮助'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VAlert', 'props': {
                                    'type': 'info',
                                    'variant': 'tonal',
                                    'text': '· 场景示例：需要随时临时开启/关闭 SSH(22) 或远程管理端口，可在下方“⚡ 快捷操作预设”填好规则，聊天发送 “/xiaomi q” 即可一键切换（存在则删，不存在则加）。\n· 立即运行一次：想要立刻拉取状态或执行添加/删除，请勾选顶部“立即运行一次”并保存。\n· 指令列表：\n  - /xiaomi list  查看端口映射列表\n  - /xiaomi add 名称 协议 外部端口 内网IP 内部端口  添加映射（如：/xiaomi add ssh tcp 22 192.168.31.10 22）\n  - /xiaomi del 端口  删除映射（协议自动推断，如：/xiaomi del 22）\n  - /xiaomi q  根据“快捷操作预设”一键切换（存在则删，不存在则加）\n  - /xiaomi help  查看帮助\n· 协议填写：tcp / udp / both（展示为文本，后台自动转换）。'}},
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'outlined', 'class': 'mt-2'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '⚡ 快捷操作预设'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'q_name', 'label': '名称', 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [{'component': 'VSelect', 'props': {'model': 'q_proto', 'items': proto_items, 'label': '协议', 'clearable': True, 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [{'component': 'VTextField', 'props': {'model': 'q_sport', 'label': '外部端口', 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'q_ip', 'label': '内网IP', 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [{'component': 'VTextField', 'props': {'model': 'q_dport', 'label': '内部端口', 'density': 'comfortable'}}]},
                                ]},
                                {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '⚡ 保存后，在聊天使用 “/xiaomi q” 一键切换（存在则删，不存在则加）。'}}
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'outlined', 'class': 'mt-2'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '➕ 添加端口映射'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VSwitch', 'props': {'model': 'pf_add_run', 'label': '执行添加'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'pf_name', 'label': '名称', 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [{'component': 'VSelect', 'props': {'model': 'pf_proto', 'items': proto_items, 'label': '协议', 'clearable': True, 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [{'component': 'VTextField', 'props': {'model': 'pf_sport', 'label': '外部端口', 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'pf_ip', 'label': '内网IP', 'density': 'comfortable'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [{'component': 'VTextField', 'props': {'model': 'pf_dport', 'label': '内部端口', 'density': 'comfortable'}}]},
                                ]},
                                {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '➕ 勾选“执行添加”，并配合“立即运行一次”保存后执行；留空不执行。'}}
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'outlined', 'class': 'mt-2'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '🗑️ 删除端口映射'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VSwitch', 'props': {'model': 'pf_del_run', 'label': '执行删除'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [{'component': 'VTextField', 'props': {'model': 'pf_del_port', 'label': '端口', 'density': 'comfortable'}}]},
                                    { 'component': 'VCol', 'props': {'cols': 12, 'md': 10} },
                                ]},
                                {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '🗑️ 勾选“执行删除”，并配合“立即运行一次”保存后执行；协议将自动推断。'}}
                            ]}
                        ]
                    },
                ]
            }
        ], {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "debug": False,
            "router_ip": "",
            "password": "",
            "pf_name": "",
            "pf_proto": "",
            "pf_sport": 0,
            "pf_ip": "",
            "pf_dport": 0,
            "pf_del_port": 0,
            "pf_del_proto": "",
            "pf_add_run": False,
            "pf_del_run": False,
            "cron": "0 */6 * * *",
            # 快捷操作默认
            "q_name": "",
            "q_proto": "",
            "q_sport": 0,
            "q_ip": "",
            "q_dport": 0,
            # 标签页默认索引
            "port_tab": 0,
        }

    # ===================== 端口映射 =====================
    _session: Optional[requests.Session] = None

    def _get_session(self) -> requests.Session:
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": f"http://{self._router_ip}/cgi-bin/luci/web"
            })
        return self._session

    def _ensure_token(self) -> Optional[str]:
        if self._last_token:
            return self._last_token
        # 触发一次刷新获取token
        self.refresh_status()
        return self._last_token

    def _stok_url(self, path: str) -> Optional[str]:
        token = self._ensure_token()
        if not token:
            return None
        return f"http://{self._router_ip}/cgi-bin/luci/;stok={token}{path}"

    def pf_list(self) -> Dict[str, Any]:
        url = self._stok_url("/api/xqnetwork/portforward?ftype=1")
        if not url:
            return {"code": 401, "msg": "no token"}
        try:
            s = self._get_session()
            r = s.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            return data
        except Exception as e:
            logger.error(f"获取端口映射列表失败: {e}")
            return {"code": 500, "msg": str(e)}

    def pf_add(self, name: str, proto: int, sport: int, ip: str, dport: int) -> Dict[str, Any]:
        url = self._stok_url("/api/xqnetwork/add_redirect")
        if not url:
            return {"code": 401, "msg": "no token"}
        payload = {
            "name": name,
            "proto": str(proto),  # 1 tcp, 2 udp, 3 both
            "sport": str(sport),
            "ip": ip,
            "dport": str(dport)
        }
        try:
            s = self._get_session()
            r = s.post(url, data=payload, timeout=10)
            text = r.text
            self._d(f"pf_add http={r.status_code}, len={len(text)}")
            r.raise_for_status()
            data = r.json()
            return data
        except Exception as e:
            logger.error(f"添加端口映射失败: {e}")
            return {"code": 500, "msg": str(e)}

    def pf_del(self, port: int, proto: int) -> Dict[str, Any]:
        url = self._stok_url("/api/xqnetwork/delete_redirect")
        if not url:
            return {"code": 401, "msg": "no token"}
        payload = {
            "port": str(port),
            "proto": str(proto)
        }
        try:
            s = self._get_session()
            r = s.post(url, data=payload, timeout=10)
            text = r.text
            self._d(f"pf_del http={r.status_code}, len={len(text)}")
            r.raise_for_status()
            data = r.json()
            return data
        except Exception as e:
            logger.error(f"删除端口映射失败: {e}")
            return {"code": 500, "msg": str(e)}

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/pf/list", "endpoint": self.pf_list, "methods": ["GET"], "summary": "端口映射列表"},
            {"path": "/pf/add", "endpoint": self._pf_add_api, "methods": ["POST"], "summary": "添加端口映射"},
            {"path": "/pf/del", "endpoint": self._pf_del_api, "methods": ["POST"], "summary": "删除端口映射"},
        ]

    def _pf_add_api(self, name: str, proto: int, sport: int, ip: str, dport: int):
        return self.pf_add(name=name, proto=proto, sport=sport, ip=ip, dport=dport)

    def _pf_del_api(self, port: int, proto: int):
        return self.pf_del(port=port, proto=proto)

    def get_page(self) -> List[dict]:
        # 状态 + 端口映射只读展示
        status = self._last_status or {}
        cards: List[dict] = []
        if not status:
            cards.append({
                'component': 'VAlert',
                'props': {'type': 'info', 'variant': 'tonal', 'text': '暂无数据，请先保存配置并运行一次'}
            })
        else:
            upload = status.get('upload_human', '-')
            download = status.get('download_human', '-')
            upspeed = status.get('upspeed_human', '-')
            downspeed = status.get('downspeed_human', '-')
            cpuload = status.get('cpu_load', '-')
            cputp = status.get('cpu_temp', '0')
            memusage = status.get('mem_usage', '-')
            uptime_h = status.get('uptime_human', '-')
            online = status.get('online_count', '-')
            routername = status.get('router_name', '-')
            hardware = status.get('hardware', '-')

            cards.append({
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': f'🏠 {routername} ({hardware})'},
                    {'component': 'VCardText', 'content': [
                        {'component': 'VRow', 'content': [
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [
                                {'component': 'div', 'props': {'class': 'text-center'}, 'content': [
                                    {'component': 'div', 'props': {'class': 'text-h5'}, 'text': online},
                                    {'component': 'div', 'props': {'class': 'text-caption'}, 'text': '在线设备数'}
                                ]}
                            ]},
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [
                                {'component': 'div', 'props': {'class': 'text-center'}, 'content': [
                                    {'component': 'div', 'props': {'class': 'text-h5'}, 'text': downspeed},
                                    {'component': 'div', 'props': {'class': 'text-caption'}, 'text': '实时下行'}
                                ]}
                            ]},
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [
                                {'component': 'div', 'props': {'class': 'text-center'}, 'content': [
                                    {'component': 'div', 'props': {'class': 'text-h5'}, 'text': upspeed},
                                    {'component': 'div', 'props': {'class': 'text-caption'}, 'text': '实时上行'}
                                ]}
                            ]},
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [
                                {'component': 'div', 'props': {'class': 'text-center'}, 'content': [
                                    {'component': 'div', 'props': {'class': 'text-h5'}, 'text': uptime_h},
                                    {'component': 'div', 'props': {'class': 'text-caption'}, 'text': '运行时长'}
                                ]}
                            ]}
                        ]}
                    ]}
                ]
            })

            rows_status = [
                {'component': 'tr', 'content': [
                    {'component': 'td', 'text': '本期下载'},
                    {'component': 'td', 'text': download},
                    {'component': 'td', 'text': '本期上传'},
                    {'component': 'td', 'text': upload},
                ]},
                {'component': 'tr', 'content': [
                    {'component': 'td', 'text': 'CPU负载'},
                    {'component': 'td', 'text': f"{cpuload}%"},
                    {'component': 'td', 'text': 'CPU温度'},
                    {'component': 'td', 'text': f"{cputp}"},
                ]},
                {'component': 'tr', 'content': [
                    {'component': 'td', 'text': '内存占用'},
                    {'component': 'td', 'text': f"{memusage}%"},
                    {'component': 'td', 'text': '上/下行速度'},
                    {'component': 'td', 'text': f"{upspeed} / {downspeed}"},
                ]},
            ]

            cards.append({
                'component': 'VCard',
                'props': {'variant': 'outlined'},
                'content': [
                    {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '📈 路由器状态'},
                    {'component': 'VCardText', 'content': [
                        {'component': 'VTable', 'props': {'density': 'compact'}, 'content': [
                            {'component': 'thead', 'content': [{'component': 'tr', 'content': [
                                {'component': 'th', 'text': '指标'},
                                {'component': 'th', 'text': '值'},
                                {'component': 'th', 'text': '指标'},
                                {'component': 'th', 'text': '值'}
                            ]}]},
                            {'component': 'tbody', 'content': rows_status}
                        ]}
                    ]}
                ]
            })

        # 端口映射只读表格
        pf = self._last_pf_list or []
        pf_rows = []
        for it in pf:
            pf_rows.append({'component': 'tr', 'content': [
                {'component': 'td', 'text': str(it.get('name', ''))},
                {'component': 'td', 'text': self._proto_to_text(it.get('proto', 3))},
                {'component': 'td', 'text': str(it.get('srcport', ''))},
                {'component': 'td', 'text': str(it.get('destip', ''))},
                {'component': 'td', 'text': str(it.get('destport', ''))},
            ]})

        cards.append({
            'component': 'VCard',
            'props': {'variant': 'outlined', 'class': 'mt-4'},
            'content': [
                {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '🌐 端口映射（只读）'},
                {'component': 'VCardText', 'content': [
                    {'component': 'VTable', 'props': {'density': 'compact'}, 'content': [
                        {'component': 'thead', 'content': [{'component': 'tr', 'content': [
                            {'component': 'th', 'text': '名称'},
                            {'component': 'th', 'text': '协议'},
                            {'component': 'th', 'text': '外部端口'},
                            {'component': 'th', 'text': '内网IP'},
                            {'component': 'th', 'text': '内部端口'},
                        ]}]},
                        {'component': 'tbody', 'content': pf_rows}
                    ]}
                ]}
            ]
        })

        return cards

    def refresh_status(self):
        if not self._router_ip or not self._password:
            logger.warning("未配置路由器IP或密码")
            return
        try:
            # 1) 获取init_info确定加密模式/路由器信息
            init = self._fetch_init_info(self._router_ip)
            if not init:
                logger.error("获取init_info失败")
                return
            self._init_info = init
            self._last_mode_new_encrypt = bool(init.get("newEncryptMode", 0))
            # 兼容key字段：key/salt/pwd；若均无，则尝试从web页解析
            login_key = str(init.get("key") or init.get("salt") or init.get("pwd") or "")
            if not login_key:
                login_key = self._fetch_login_key_from_web(self._router_ip) or ""
                self._d(f"web页提取key_len={len(login_key)}")
            self._last_login_key = login_key

            # 设备标识：优先routerId，其次id，再次deviceId/mac
            device_id = str(init.get("routerId") or init.get("id") or init.get("deviceId") or init.get("mac") or "")
            device_id = device_id.replace(':', '') if device_id else device_id
            self._d(f"init_info 字段: newEncryptMode={self._last_mode_new_encrypt}, key_len={len(self._last_login_key)}, device_id={device_id}, routername={init.get('routername')}, hardware={init.get('hardware')}")

            # 2) 登录获取token
            token = self._login_and_get_token(
                ip=self._router_ip,
                password=self._password,
                use_new_encrypt=self._last_mode_new_encrypt,
                key=self._last_login_key,
                device_id=device_id
            )
            if not token:
                logger.error("登录失败，未获取到token")
                return
            self._last_token = token
            self._d(f"登录成功，token_len={len(token)}")

            # 3) 执行端口映射（仅当本次为“立即运行一次”触发）
            executed = False
            if self._do_pf_this_run:
                # 删除优先（仅在开关开启且端口有效时执行）
                if self._pf_del_run and self._pf_del_port:
                    # 自动从列表推断协议
                    proto_auto = None
                    data_exist = self.pf_list()
                    if isinstance(data_exist, dict):
                        for it in data_exist.get('list', []) or []:
                            if int(it.get('srcport', -1)) == int(self._pf_del_port):
                                proto_auto = it.get('proto', 3)
                                break
                    res = self.pf_del(self._pf_del_port, int(proto_auto) if proto_auto is not None else 3)
                    self._last_pf_result = res
                    executed = executed or (isinstance(res, dict) and res.get('code') == 0)
                # 添加
                if self._pf_add_run and self._pf_name and self._pf_proto and self._pf_sport and self._pf_ip and self._pf_dport:
                    res = self.pf_add(self._pf_name, self._proto_to_int(self._pf_proto), self._pf_sport, self._pf_ip, self._pf_dport)
                    self._last_pf_result = res
                    executed = executed or (isinstance(res, dict) and res.get('code') == 0)
                # 不自动修改任何配置，保持开关与表单原样，由你手动控制

            # 获取列表（默认必须获取）
            data = self.pf_list()
            if isinstance(data, dict):
                self._last_pf_list = data.get('list', [])

            # 端口变更通知 & 汇总（周期与一次性均推送汇总；如有变更提示）
            if self._notify:
                # 增删报告细节（去掉code展示，提供友好摘要）
                if self._last_pf_result and isinstance(self._last_pf_result, dict) and 'code' in self._last_pf_result:
                    ok = (self._last_pf_result.get('code') == 0)
                    msg = self._last_pf_result.get('msg') or self._last_pf_result.get('message') or ''
                    # 组合本次操作意图
                    detail = []
                    if self._pf_del_run and self._pf_del_port:
                        detail.append(f"删除端口 {self._pf_del_port}")
                    if self._pf_add_run and self._pf_name:
                        detail.append(f"添加 {self._pf_name} {self._pf_proto or 'both'} {self._pf_sport}->{self._pf_ip}:{self._pf_dport}")
                    dline = "；".join(detail) if detail else "变更"
                    text = (f"✅ {dline} 成功" if ok else f"❌ {dline} 失败") + (f"\n原因：{msg}" if msg else "")
                    self.post_message(mtype=NotificationType.SiteMessage, title="【路由器端口映射】", text=text)
                self._notify_pf_summary(prefix=('🔄 已执行端口变更' if executed else '🔓 当前已开放端口'))

            # 4) 获取状态
            status = self._fetch_status(self._router_ip, token)
            if status:
                self._last_status = status
                if self._notify:
                    self._notify_status(status)
                logger.info("小米路由器状态刷新完成")
                self._d(f"状态摘要: online={status.get('online_count')}, up={status.get('upspeed_human')}, down={status.get('downspeed_human')}")
        except Exception as e:
            logger.error(f"刷新路由器状态失败: {e}")

    # ===================== HTTP & 业务 =====================
    def _fetch_init_info(self, ip: str) -> Optional[Dict[str, Any]]:
        url = f"http://{ip}/cgi-bin/luci/api/xqsystem/init_info"
        try:
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"http://{ip}/cgi-bin/luci/web"
            }
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            text = r.text
            self._d(f"init_info 原始长度={len(text)}")
            data = r.json()
            return data or {}
        except Exception as e:
            logger.error(f"获取init_info失败: {e}")
            return None

    def _fetch_login_key_from_web(self, ip: str) -> Optional[str]:
        try:
            url = f"http://{ip}/cgi-bin/luci/web"
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            html = r.text
            # 常见JS里会包含 key / Encrypt.key 等写法
            # 1) key: "xxxxx" 或 key: 'xxxxx'
            m = re.search(r"key\s*[:=]\s*\"([A-Za-z0-9]+)\"", html)
            if not m:
                m = re.search(r"key\s*[:=]\s*'([A-Za-z0-9]+)'", html)
            if m:
                return m.group(1)
            # 2) Encrypt\(['\"]([^'\"]+)['\"]\) 型调用包含key
            m = re.search(r"Encrypt\([^\)]*[\"\']([A-Za-z0-9]+)[\"\']", html)
            if m:
                return m.group(1)
            # 3) 如果有外链JS，再尝试拉取
            for js in re.findall(r'<script[^>]+src=\"([^\"]+)\"', html):
                try:
                    if js.startswith('//'):
                        js = 'http:' + js
                    elif js.startswith('/'):
                        js = f"http://{ip}{js}"
                    r2 = requests.get(js, timeout=10)
                    if r2.ok:
                        text = r2.text
                        m2 = re.search(r"key\s*[:=]\s*\"([A-Za-z0-9]+)\"", text)
                        if not m2:
                            m2 = re.search(r"key\s*[:=]\s*'([A-Za-z0-9]+)'", text)
                        if m2:
                            return m2.group(1)
                        m2 = re.search(r"Encrypt\([^\)]*[\"\']([A-Za-z0-9]+)[\"\']", text)
                        if m2:
                            return m2.group(1)
                except:
                    pass
        except Exception as e:
            self._d(f"提取web key失败: {e}")
        return None

    def _create_nonce(self, device_id: str = "") -> str:
        type_var = 0
        device = device_id or ""
        time_var = int(time.time())
        random_var = random.randint(0, 9999)
        nonce = f"{type_var}_{device}_{time_var}_{random_var}"
        self._d(f"生成nonce: {nonce}")
        return nonce

    def _sha1_hex(self, s: str) -> str:
        return hashlib.sha1(s.encode()).hexdigest()

    def _sha256_hex(self, s: str) -> str:
        return hashlib.sha256(s.encode()).hexdigest()

    def _hash_password_old(self, pwd: str, nonce: str, key: str) -> str:
        # 旧规则: sha1( nonce + sha1(pwd + key) )
        pwd_key_hash = self._sha1_hex(pwd + key)
        hashed = self._sha1_hex(nonce + pwd_key_hash)
        self._d(f"旧加密: key_len={len(key)}, hash_prefix={hashed[:8]}")
        return hashed

    def _hash_password_new(self, pwd: str, nonce: str, key: str) -> str:
        # 新规则: sha256( nonce + sha256(pwd + key) )
        pwd_key_hash = self._sha256_hex(pwd + key)
        hashed = self._sha256_hex(nonce + pwd_key_hash)
        self._d(f"新加密: key_len={len(key)}, hash_prefix={hashed[:8]}")
        return hashed

    def _login_and_get_token(self, ip: str, password: str, use_new_encrypt: bool, key: str, device_id: str) -> Optional[str]:
        url = f"http://{ip}/cgi-bin/luci/api/xqsystem/login"
        nonce = self._create_nonce(device_id=device_id)
        key = key or ""
        if use_new_encrypt:
            hashed = self._hash_password_new(password, nonce, key)
        else:
            hashed = self._hash_password_old(password, nonce, key)
        payload = {
            "username": "admin",
            "password": hashed,
            "logtype": "2",
            "nonce": nonce,
        }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": f"http://{ip}/cgi-bin/luci/web"
        }
        self._d(f"准备登录: encrypt={'sha256' if use_new_encrypt else 'sha1'}, device_id={device_id}, nonce_ts={nonce.split('_')[2] if '_' in nonce else ''}")
        try:
            s = requests.Session()
            r = s.post(url, data=payload, headers=headers, timeout=10)
            text = r.text
            self._d(f"login http={r.status_code}, len={len(text)}")
            r.raise_for_status()
            data = r.json()
            if data.get("code") == 0 and data.get("token"):
                return data.get("token")
            logger.error(f"登录返回失败: {data}")
            self._d(f"login raw: {text[:256]}")
            return None
        except Exception as e:
            logger.error(f"登录请求失败: {e}")
            return None

    def _format_speed(self, bps: float) -> str:
        try:
            v = float(bps)
        except:
            return "-"
        if v >= 1024*1024*1024:
            return f"{v/1024/1024/1024:.2f} GB/s"
        if v >= 1024*1024:
            return f"{v/1024/1024:.2f} MB/s"
        if v >= 1024:
            return f"{v/1024:.2f} KB/s"
        return f"{v:.2f} B/s"

    def _format_size(self, bytes_val: float) -> str:
        try:
            v = float(bytes_val)
        except:
            return "-"
        if v >= 1024**4:
            return f"{v/1024**4:.2f} TB"
        if v >= 1024**3:
            return f"{v/1024**3:.2f} GB"
        if v >= 1024**2:
            return f"{v/1024**2:.2f} MB"
        if v >= 1024:
            return f"{v/1024:.2f} KB"
        return f"{v:.2f} B"

    def _fetch_status(self, ip: str, token: str) -> Optional[Dict[str, Any]]:
        url = f"http://{ip}/cgi-bin/luci/;stok={token}/api/misystem/status"
        try:
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"http://{ip}/cgi-bin/luci/web"
            }
            r = requests.get(url, headers=headers, timeout=10)
            text = r.text
            self._d(f"status http={r.status_code}, len={len(text)}")
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return None

        try:
            # 解析关键信息
            wan = data.get("wan", {})
            cpu = data.get("cpu", {})
            mem = data.get("mem", {})
            temp = data.get("temperature")
            uptime = data.get("upTime")
            devs = data.get("dev", []) or data.get("client_list", [])
            count = data.get("count", {}) or {}
            display_name = data.get("displayName") or data.get("routername") or "Xiaomi Router"
            hw_obj = data.get("hardware")
            if isinstance(hw_obj, dict):
                hw_platform = hw_obj.get("platform") or hw_obj.get("mac") or "-"
                hw_version = hw_obj.get("version")
                hardware_str = f"{hw_platform}{(' ' + hw_version) if hw_version else ''}"
            else:
                hardware_str = str(hw_obj) if hw_obj else "-"

            status: Dict[str, Any] = {
                # 原始数值
                "upload": wan.get("upload"),
                "download": wan.get("download"),
                "downspeed": wan.get("downspeed"),
                "upspeed": wan.get("upspeed"),
                # 人类可读
                "upload_human": self._format_size(self._safe_float(wan.get("upload"))),
                "download_human": self._format_size(self._safe_float(wan.get("download"))),
                "downspeed_human": self._format_speed(self._safe_float(wan.get("downspeed"))),
                "upspeed_human": self._format_speed(self._safe_float(wan.get("upspeed"))),
                "cpu_load": round(float(cpu.get("load", 0)) * 10) / 10 if isinstance(cpu.get("load", 0), (int, float)) else cpu.get("load", 0),
                "cpu_temp": (int(temp) if isinstance(temp, (int, float)) and int(temp) != 0 else "-"),
                "mem_usage": round(float(mem.get("usage", 0)) * 100) / 100 if isinstance(mem.get("usage", 0), (int, float)) else mem.get("usage", 0),
                "uptime": uptime,
                "uptime_human": self._uptime_human(uptime),
                "online_count": int(count.get("online")) if str(count.get("online", "")).isdigit() else (len(devs) if isinstance(devs, list) else 0),
                "router_name": display_name,
                "hardware": hardware_str,
            }
            return status
        except Exception as e:
            logger.error(f"解析状态失败: {e}")
            self._d(f"status raw: {json.dumps(data)[:256] if isinstance(data, dict) else ''}")
            return None

    def _safe_float(self, v) -> float:
        try:
            if isinstance(v, str):
                return float(v)
            return float(v or 0)
        except:
            return 0.0

    def _uptime_human(self, uptime) -> str:
        try:
            sec = float(uptime)
        except:
            return "-"
        days = int(sec // 86400)
        hours = int((sec % 86400) // 3600)
        return f"{days}天 {hours}小时"

    def _notify_status(self, status: Dict[str, Any]):
        title = "【📶 小米路由器状态】"
        router_line = f"🏠 路由器：{status.get('router_name', '-')}/{status.get('hardware', '-')}"
        device_line = f"👥 在线设备：{status.get('online_count', '-')}"
        line_down_rt = f"⬇️ 实时下行：{status.get('downspeed_human', '-')}"
        line_up_rt = f"⬆️ 实时上行：{status.get('upspeed_human', '-')}"
        line_down_sum = f"📥 本期下载：{status.get('download_human', '-')}"
        line_up_sum = f"📤 本期上传：{status.get('upload_human', '-')}"
        cpu_line = f"🧠 CPU：{status.get('cpu_load', '-')}% / {status.get('cpu_temp', '0')}"
        mem_line = f"💾 内存：{status.get('mem_usage', '-')}%"
        up_line = f"⏱️ 运行：{status.get('uptime_human', '-')}"
        text = "\n".join([
            router_line,
            device_line,
            line_down_rt,
            line_up_rt,
            line_down_sum,
            line_up_sum,
            cpu_line,
            mem_line,
            up_line
        ])
        self.post_message(mtype=NotificationType.SiteMessage, title=title, text=text)

    # API/命令保留
    def get_command(self) -> List[Dict[str, Any]]:
        # 双通道：func 直调 + 事件驱动
        base = [
            {"cmd": "/xiaomi", "desc": "小米路由器-命令入口：/xia米 list|add|del", "category": "管理", "func": self.cmd_entry},
            {"cmd": "/xiaomi_list", "desc": "小米路由器-端口映射列表", "category": "管理", "func": self.cmd_list},
            {"cmd": "/xiaomi_add", "desc": "小米路由器-添加映射：名称 协议 外部端口 内网IP 内部端口", "category": "管理", "func": self.cmd_add},
            {"cmd": "/xiaomi_del", "desc": "小米路由器-删除映射：端口", "category": "管理", "func": self.cmd_del},
            {"cmd": "/xiaomi_q", "desc": "小米路由器-快捷切换映射（存在删/不存在加）", "category": "管理", "func": self.cmd_q},
            {"cmd": "/xiaomi_help", "desc": "小米路由器-帮助", "category": "管理", "func": self.cmd_help},
        ]
        events = [
            {"cmd": "/xiaomi", "event": EventType.CommandExcute, "desc": "小米路由器-命令入口：/xiaomi list|add|del", "category": "管理", "data": {}},
            {"cmd": "/xiaomi_list", "event": EventType.CommandExcute, "desc": "小米路由器-端口映射列表", "category": "管理", "data": {}},
            {"cmd": "/xiaomi_add", "event": EventType.CommandExcute, "desc": "小米路由器-添加映射：名称 协议 外部端口 内网IP 内部端口", "category": "管理", "data": {}},
            {"cmd": "/xiaomi_del", "event": EventType.CommandExcute, "desc": "小米路由器-删除映射：端口", "category": "管理", "data": {}},
            {"cmd": "/xiaomi_q", "event": EventType.CommandExcute, "desc": "小米路由器-快捷切换映射（存在删/不存在加）", "category": "管理", "data": {}},
            {"cmd": "/xiaomi_help", "event": EventType.CommandExcute, "desc": "小米路由器-帮助", "category": "管理", "data": {}},
        ]
        return base + events

    def _notify_pf_summary(self, prefix: str = '端口映射'):
        lst = self._last_pf_list or []
        if not lst:
            text = f"{prefix}\n暂无端口映射"
        else:
            lines = []
            for it in lst:
                lines.append(f"{self._proto_to_text(it.get('proto', 3))} {it.get('srcport')} -> {it.get('destip')}:{it.get('destport')}")
            text = f"{prefix}\n" + "\n".join(lines)
        self.post_message(mtype=NotificationType.SiteMessage, title="【路由器端口映射】", text=text)

    def cmd_list(self, *args, **kwargs):
        self._d("收到命令：列表")
        data = self.pf_list()
        if isinstance(data, dict):
            self._last_pf_list = data.get('list', [])
        self._notify_pf_summary(prefix='📋 当前端口')
        return {"status": "ok"}

    def cmd_add(self, *args, **kwargs):
        try:
            self._d("收到命令：添加端口映射")
            parts = kwargs.get('arg', '') or ''
            # 允许整句：/xiaomi add ...
            if isinstance(parts, str) and parts.startswith('/xiaomi'):
                parts = parts[len('/xiaomi'):].strip()
            if not parts:
                return {"status": "error", "msg": "参数：名称 协议 外部端口 内网IP 内部端口"}
            items = str(parts).split()
            if len(items) < 5:
                return {"status": "error", "msg": "参数不完整"}
            name, proto_t, sport, ip, dport = items[0], items[1], int(items[2]), items[3], int(items[4])
            res = self.pf_add(name=name, proto=self._proto_to_int(proto_t), sport=sport, ip=ip, dport=dport)
            data = self.pf_list()
            if isinstance(data, dict):
                self._last_pf_list = data.get('list', [])
            # 变更详情通知
            ok = isinstance(res, dict) and res.get('code') == 0
            msg = (res or {}).get('msg') or (res or {}).get('message') or ''
            detail = f"添加 {name} {proto_t} {sport}->{ip}:{dport}"
            text = (f"✅ {detail} 成功" if ok else f"❌ {detail} 失败") + (f"\n原因：{msg}" if msg else "")
            self.post_message(mtype=NotificationType.SiteMessage, title="【路由器端口映射】", text=text)
            self._notify_pf_summary(prefix="🔓 当前已开放端口")
            return res or {"status": "ok"}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

    def cmd_del(self, *args, **kwargs):
        try:
            self._d("收到命令：删除端口映射")
            parts = kwargs.get('arg', '') or ''
            if isinstance(parts, str) and parts.startswith('/xiaomi'):
                parts = parts[len('/xiaomi'):].strip()
            if not parts:
                return {"status": "error", "msg": "参数：端口"}
            items = str(parts).split()
            port = int(items[0])
            # 自动推断协议
            proto_auto = None
            data_exist = self.pf_list()
            if isinstance(data_exist, dict):
                for it in data_exist.get('list', []) or []:
                    if int(it.get('srcport', -1)) == int(port):
                        proto_auto = it.get('proto', 3)
                        break
            res = self.pf_del(port=port, proto=int(proto_auto) if proto_auto is not None else 3)
            data = self.pf_list()
            if isinstance(data, dict):
                self._last_pf_list = data.get('list', [])
            ok = isinstance(res, dict) and res.get('code') == 0
            msg = (res or {}).get('msg') or (res or {}).get('message') or ''
            detail = f"删除端口 {port}（{self._proto_to_text(proto_auto or 3)}）"
            text = (f"🗑️ {detail} 成功" if ok else f"❌ {detail} 失败") + (f"\n原因：{msg}" if msg else "")
            self.post_message(mtype=NotificationType.SiteMessage, title="【路由器端口映射】", text=text)
            self._notify_pf_summary(prefix="🔓 当前已开放端口")
            return res or {"status": "ok"}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

    def cmd_entry(self, *args, **kwargs):
        # args/kwargs由平台注入，这里从kwargs.get('arg')取原始文本命令行参数
        self._d(f"命令入口触发，args={args}, kwargs_keys={[k for k in kwargs.keys()]}")
        # 兼容多平台多字段：arg/args/text/message/content/positional
        argline = None
        for k in ('arg', 'args', 'text', 'message', 'content'):
            v = kwargs.get(k)
            if v:
                argline = str(v)
                break
        if argline is None and args:
            try:
                argline = " ".join([str(a) for a in args if a is not None])
            except:
                argline = ""
        argline = (argline or "").strip()
        # 允许整句：/xiaomi list|add|del ...
        if argline.startswith('/xiaomi'):
            argline = argline[len('/xiaomi'):].strip()
        parts = argline.split()
        if not parts:
            return {"status": "error", "msg": "用法：/xiaomi list | /xiaomi add 名称 协议 外部端口 内网IP 内部端口 | /xiaomi del 端口"}
        sub = parts[0].lower()
        if sub == 'list':
            return self.cmd_list()
        if sub == 'add':
            if len(parts) < 6:
                return {"status": "error", "msg": "用法：/xiaomi add 名称 协议 外部端口 内网IP 内部端口"}
            name, proto_t, sport, ip, dport = parts[1], parts[2], int(parts[3]), parts[4], int(parts[5])
            return self.cmd_add(arg=f"{name} {proto_t} {sport} {ip} {dport}")
        if sub == 'del':
            if len(parts) < 2:
                return {"status": "error", "msg": "用法：/xiaomi del 端口"}
            port = int(parts[1])
            return self.cmd_del(arg=f"{port}")
        if sub == 'q':
            return self.cmd_q()
        if sub == 'help':
            return self.cmd_help()
        return {"status": "error", "msg": "未知子命令"}

    # 事件驱动入口，兼容 CommandChain -> EventType
    def on_command(self, event):
        try:
            data = event.event_data or {}
            raw_cmd = (data.get('cmd') or '').strip()
            if not raw_cmd:
                return
            # 只处理本插件命令
            if not raw_cmd.startswith(('/xiaomi', )):
                return
            # 统一分发
            if raw_cmd.startswith('/xiaomi_list'):
                self.cmd_list(arg=raw_cmd)
                return
            if raw_cmd.startswith('/xiaomi_add'):
                # 截掉命令前缀，传递参数
                arg = raw_cmd[len('/xiaomi_add'):].strip()
                self.cmd_add(arg=arg)
                return
            if raw_cmd.startswith('/xiaomi_del'):
                arg = raw_cmd[len('/xiaomi_del'):].strip()
                self.cmd_del(arg=arg)
                return
            if raw_cmd.startswith('/xiaomi_q'):
                self.cmd_q()
                return
            if raw_cmd.startswith('/xiaomi_help'):
                self.cmd_help()
                return
            if raw_cmd.startswith('/xiaomi'):
                # 兼容 /xiaomi list|add|del
                arg = raw_cmd[len('/xiaomi'):].strip()
                self.cmd_entry(arg=arg)
                return
        except Exception as e:
            logger.error(f"[xiaomirouter] on_command error: {e}")

    def cmd_q(self, *args, **kwargs):
        # 校验配置
        if not (self._q_name and self._q_proto and self._q_sport and self._q_ip and self._q_dport):
            return {"status": "error", "msg": "请先在设置页填写完整快捷操作预设：名称/协议/外部端口/内网IP/内部端口"}
        # 列表中是否存在该端口
        data_exist = self.pf_list()
        exists = False
        proto_auto = None
        if isinstance(data_exist, dict):
            for it in data_exist.get('list', []) or []:
                if int(it.get('srcport', -1)) == int(self._q_sport):
                    exists = True
                    proto_auto = it.get('proto', 3)
                    break
        if exists:
            # 删除
            res = self.pf_del(port=self._q_sport, proto=int(proto_auto) if proto_auto is not None else 3)
            ok = isinstance(res, dict) and res.get('code') == 0
            msg = (res or {}).get('msg') or (res or {}).get('message') or ''
            detail = f"删除端口 {self._q_sport}（{self._proto_to_text(proto_auto or 3)}）"
            text = (f"🗑️ {detail} 成功" if ok else f"❌ {detail} 失败") + (f"\n原因：{msg}" if msg else "")
            self.post_message(mtype=NotificationType.SiteMessage, title="【路由器端口映射】", text=text)
        else:
            # 添加
            res = self.pf_add(name=self._q_name, proto=self._proto_to_int(self._q_proto), sport=self._q_sport, ip=self._q_ip, dport=self._q_dport)
            ok = isinstance(res, dict) and res.get('code') == 0
            msg = (res or {}).get('msg') or (res or {}).get('message') or ''
            detail = f"添加 {self._q_name} {self._q_proto} {self._q_sport}->{self._q_ip}:{self._q_dport}"
            text = (f"✅ {detail} 成功" if ok else f"❌ {detail} 失败") + (f"\n原因：{msg}" if msg else "")
            self.post_message(mtype=NotificationType.SiteMessage, title="【路由器端口映射】", text=text)
        # 刷新并汇总
        data = self.pf_list()
        if isinstance(data, dict):
            self._last_pf_list = data.get('list', [])
        self._notify_pf_summary(prefix='📋 当前端口')
        return {"status": "ok"}

    def cmd_help(self, *args, **kwargs):
        lines = [
            "命令使用说明：",
            "/xiaomi list  - 查看当前端口映射",
            "/xiaomi add 名称 协议 外部端口 内网IP 内部端口  - 添加映射",
            "/xiaomi del 端口  - 删除映射（协议自动推断）",
            "/xiaomi q  - 快捷切换（根据设置页预设，存在则删，不存在则加）",
            "/xiaomi help  - 查看帮助",
        ]
        self.post_message(mtype=NotificationType.SiteMessage, title="【小米路由器-帮助】", text="\n".join(lines))
        return {"status": "ok"}

    def _proto_to_int(self, v: str | int) -> int:
        if isinstance(v, int):
            return v if v in (1, 2, 3) else 3
        t = str(v).strip().lower()
        if t in ("1", "tcp"): return 1
        if t in ("2", "udp"): return 2
        return 3  # both

    def _proto_to_text(self, v: int | str) -> str:
        try:
            n = int(v)
        except:
            n = self._proto_to_int(v)
        return {1: "tcp", 2: "udp", 3: "both"}.get(n, "both")

    def stop_service(self):
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"停止服务失败: {str(e)}")

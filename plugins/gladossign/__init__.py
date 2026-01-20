import time
from datetime import datetime, timedelta
from typing import Any, List, Dict, Tuple, Optional

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from app.log import logger
from app.schemas import NotificationType
import requests


class gladossign(_PluginBase):
    plugin_name = "GlaDOS 签到"
    plugin_desc = "每日签到获取点数；积累点数可兑换 10~100 天套餐时长"
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/glados.png"
    plugin_version = "1.4.0"
    plugin_author = "madrays"
    author_url = "https://github.com/madrays"
    plugin_config_prefix = "gladossign_"
    plugin_order = 1
    auth_level = 2

    _enabled = False
    _notify = True
    _onlyonce = False
    _cron = "0 9 * * *"
    _base_url = "https://glados.space"
    _cookie = ""
    _proxy_enabled = False
    _timeout_seconds = 30
    _retry_interval_seconds = 300
    _max_attempts = 2
    _retry_no_proxy_fallback = True
    _history_days = 30
    _scheduler: Optional[BackgroundScheduler] = None

    def init_plugin(self, config: dict = None):
        self.stop_service()
        if config:
            self._enabled = config.get("enabled", False)
            self._notify = config.get("notify", True)
            self._onlyonce = config.get("onlyonce", False)
            self._cron = config.get("cron", "0 9 * * *")
            self._base_url = (config.get("base_url") or self._base_url).strip() or self._base_url
            self._cookie = (config.get("cookie") or "").strip()
            self._proxy_enabled = bool(config.get("proxy_enabled", False))
            try:
                self._timeout_seconds = int(config.get("timeout_seconds", 30))
            except Exception:
                self._timeout_seconds = 30
            try:
                self._max_attempts = int(config.get("max_attempts", 2))
            except Exception:
                self._max_attempts = 2
            self._retry_no_proxy_fallback = bool(config.get("retry_no_proxy_fallback", True))
            try:
                self._retry_interval_seconds = int(config.get("retry_interval_seconds", 2))
            except Exception:
                self._retry_interval_seconds = 2
            try:
                self._history_days = int(config.get("history_days", 30))
            except Exception:
                self._history_days = 30
        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(func=self.sign, trigger='date', run_date=datetime.now() + timedelta(seconds=3), name="GlaDOS签到")
            self._onlyonce = False
            self.update_config({
                "enabled": self._enabled,
                "notify": self._notify,
                "cookie": self._cookie,
                "cron": self._cron,
                "onlyonce": False,
                "base_url": self._base_url,
                "proxy_enabled": self._proxy_enabled,
                "timeout_seconds": self._timeout_seconds,
                "max_attempts": self._max_attempts,
                "retry_no_proxy_fallback": self._retry_no_proxy_fallback,
                "retry_interval_seconds": self._retry_interval_seconds,
                "history_days": self._history_days,
            })
            if self._scheduler.get_jobs():
                self._scheduler.start()
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")

    def sign(self):
        logger.info("开始 GlaDOS 签到")
        url = f"{self._base_url.rstrip('/')}/api/user/checkin"
        logger.info(f"请求地址: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': self._base_url,
            'Referer': self._base_url + '/',
            'Cookie': self._cookie,
        }
        proxies = self._get_proxies()
        logger.info(f"使用代理: {'是' if (proxies is not None) else '否'}")
        logger.info(f"Cookie: {'有' if bool(self._cookie) else '无'}")
        body = {"token": "glados.one"}
        attempts = [None]
        if proxies:
            attempts = [proxies] + ([None] if self._retry_no_proxy_fallback else [])
        last_error = None
        for idx, px in enumerate(attempts):
            for attempt in range(1, int(self._max_attempts) + 1):
                try:
                    start_ms = int(time.time()*1000)
                    resp = requests.post(url, json=body, headers=headers, timeout=self._timeout_seconds, proxies=px)
                    cost_ms = int(time.time()*1000) - start_ms
                    text_len = len(resp.text or "")
                    ctype = resp.headers.get('Content-Type') or resp.headers.get('content-type')
                    logger.info(f"响应状态: {resp.status_code}, 耗时: {cost_ms}ms, 类型: {ctype}, 长度: {text_len}")
                    data = {}
                    try:
                        data = resp.json() or {}
                    except Exception:
                        data = {}
                    logger.info(f"解析JSON: keys={list(data.keys())}")
                    code = int(data.get('code') or -1)
                    points_gain = int(data.get('points') or 0)
                    msg_en = str(data.get('message') or '')
                    lst = data.get('list') or []
                    item = lst[0] if lst else {}
                    uid = item.get('user_id')
                    balance = item.get('balance')
                    now_ms = int(time.time()*1000)
                    t_ms_server = int(item.get('time') or now_ms)
                    t_ms = now_ms if code == 1 else t_ms_server
                    dt = datetime.fromtimestamp(t_ms/1000.0)
                    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    status = '签到成功' if (points_gain > 0) else ('已签到' if (code == 1 or ('Repeats' in msg_en) or ('Try Tomorrow' in msg_en)) else '签到失败')
                    msg_cn = (f"签到成功！获得 {points_gain} 点数" if status == '签到成功' else ("重复签到！请明天再试" if status == '已签到' else (msg_en or '签到失败')))
                    logger.info(f"业务摘要: 状态={status}, 本次点数={points_gain}, 余额={balance}, 用户ID={uid}")
                    
                    # 尝试拉取最新的 Points 接口数据作为权威数据
                    self._fetch_user_summary(headers, px)
                    
                    # 重新读取数据用于通知
                    info_out = self.get_data('glados_user') or {}
                    last_point_info = self.get_data('glados_points_info') or {}
                    
                    # 优先使用 api/user/points 的数据
                    current_points = last_point_info.get('points') 
                    if current_points is None:
                         current_points = self._to_int(balance)
                    
                    # 修正：如果是“已签到”状态，尝试从历史记录中查找今天的签到记录，以展示“今日已获点数”
                    try:
                        tz = pytz.timezone(settings.TZ)
                        today_ymd = datetime.now(tz).strftime('%Y-%m-%d')
                        history_list = self.get_data('glados_history') or []
                        # 查找 message 或 date 匹配今天的记录 (API detail: checkin:2026-01-20-...)
                        todays_rec = next((h for h in history_list if today_ymd in str(h.get('message','')) and 'checkin' in str(h.get('message','')).lower()), None)
                        
                        if todays_rec:
                            # 找到了今天的权威记录
                            real_gain = int(todays_rec.get('points_gain', 0))
                            if status == '已签到':
                                points_gain = real_gain
                                msg_cn = f"重复签到！今日已获 {points_gain} 点数"
                    except Exception as e:
                        logger.warning(f"匹配今日记录失败: {e}")

                    # 更新通知逻辑
                    if self._notify:
                        title = '✅ GlaDOS 签到成功' if status == '签到成功' else ('✅ 今日已签到' if status == '已签到' else '🔴 GlaDOS 签到失败')
                        emoji = '📈' if points_gain > 0 else ('➖' if points_gain == 0 else '📉')
                        
                        text_parts = [
                            f"🆔 用户ID：{uid}" if uid else "",
                            f"{emoji} 本次点数：{points_gain}",
                            f"💰 当前点数：{current_points}" if current_points is not None else "",
                            f"⏰ 时间：{dt_str}",
                            (f"📅 已用天数：{info_out.get('days')}" if info_out.get('days') is not None else ""),
                            (f"🕒 剩余天数：{info_out.get('leftDays')}" if info_out.get('leftDays') is not None else ""),
                            (f"📧 邮箱：{info_out.get('email')}" if info_out.get('email') else ""),
                        ]
                        self.post_message(mtype=NotificationType.SiteMessage, title=title, text="\n".join([x for x in text_parts if x]))
                    return {} # 历史记录统一由 _fetch_user_summary 处理
                except Exception as e:
                    last_error = e
                    logger.warning(f"请求失败(第{idx+1}组{'使用代理' if px else '不使用代理'}第{attempt}/{self._max_attempts}次): {e}")
                    if attempt < int(self._max_attempts):
                        try:
                            time.sleep(max(0, int(self._retry_interval_seconds)))
                        except Exception:
                            pass
                    continue
        d = {"date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "status": "签到失败", "message": f"请求异常: {last_error}"}
        self._save_history(d)
        if self._notify:
            self.post_message(mtype=NotificationType.SiteMessage, title="🔴 GlaDOS 签到失败", text=f"⏰ {d['date']}\n❌ {d['message']}")
        return d

    def _normalize_proxies(self, p: Any) -> Optional[Dict[str, str]]:
        try:
            if not p:
                return None
            if isinstance(p, str):
                return {"http": p, "https": p}
            if isinstance(p, dict):
                http = p.get('http') or p.get('HTTP')
                https = p.get('https') or p.get('HTTPS') or http
                if http or https:
                    return {"http": http or https, "https": https or http}
        except Exception:
            pass
        return None

    def _get_proxies(self) -> Optional[Dict[str, str]]:
        try:
            if not self._proxy_enabled:
                return None
            p = getattr(settings, 'PROXY', None)
            return self._normalize_proxies(p)
        except Exception:
            return None

    def _to_int(self, v: Any) -> Optional[int]:
        try:
            if v is None:
                return None
            if isinstance(v, int):
                return v
            if isinstance(v, float):
                return int(v)
            s = str(v).strip()
            if s == "":
                return None
            if "." in s:
                return int(float(s))
            return int(s)
        except Exception:
            return None

    def _fetch_user_summary(self, headers: Dict[str, str], proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """
        拉取用户信息，包括 /api/user/points (积分/历史) 和 /api/user/info (账号详情)
        """
        try:
            # 1. 获取积分和历史记录 (Source of Truth)
            url_points = f"{self._base_url.rstrip('/')}/api/user/points"
            try:
                r = requests.get(url_points, headers=headers, timeout=12, proxies=proxies)
                if r.status_code == 200:
                    d = r.json() or {}
                    if d.get('code') == 0:
                        # 保存原始 Points 数据
                        self.save_data('glados_points_info', d)
                        
                        # 同步历史记录
                        history_list = d.get('history', [])
                        self._sync_history_from_api(history_list)
            except Exception as e:
                logger.warning(f"获取 Points 失败: {e}")

            # 2. 获取账号基本信息 (days, email etc)
            # /api/user/status 也可以，但 /api/user/info 似乎更常用于获取天数
            urls = [f"{self._base_url.rstrip('/')}/api/user/status"]
            for u in urls:
                r = requests.get(u, headers=headers, timeout=12, proxies=proxies)
                d = {}
                try: d = r.json() or {}
                except Exception: d = {}
                
                code = d.get('code')
                if code == 0 and isinstance(d.get('data'), dict):
                    data = d.get('data')
                    user_id = data.get('userId') or data.get('configureId')
                    email = data.get('email')
                    days = self._to_int(data.get('days'))
                    left_days = self._to_int(data.get('leftDays'))
                    out = {
                        'user_id': user_id or None,
                        'email': email or None,
                        'days': days,
                        'leftDays': left_days,
                    }
                    self.save_data('glados_user', out)
                    return out
        except Exception as e:
            logger.warning(f"拉取用户信息异常: {e}")
        return {}

    def _sync_history_from_api(self, api_history: List[Dict]):
        """
        将 API 返回的历史记录同步到本地存储
        API Item Example:
        {
            "id": 128424869,
            "user_id": 661475,
            "time": 1768695420698,
            "asset": "points",
            "business": "system:checkin:2026-01-18",
            "change": "3.00000000",
            "balance": "240.0000000000000000",
            "detail": "checkin:2026-01-18-661475"
        }
        """
        if not api_history:
            return
            
        formatted_history = []
        for item in api_history:
            try:
                ts = int(item.get('time') or 0)
                change = float(item.get('change') or 0)
                # 转换为整数展示，更简洁
                change_int = int(change) if change.is_integer() else change
                
                balance = float(item.get('balance') or 0)
                balance_int = int(balance) if balance.is_integer() else balance
                
                business = item.get('business', '')
                detail = item.get('detail', '')
                
                # 构造存入本地的格式
                dt = datetime.fromtimestamp(ts/1000.0)
                dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # 简单的状态推断
                status = "变动"
                if "checkin" in business or "checkin" in detail:
                    status = "签到"
                elif "exchange" in business or "exchange" in detail:
                    status = "兑换"
                
                # 构造消息
                msg = detail
                if not msg:
                    msg = business
                    
                formatted_history.append({
                    'date': dt_str,
                    'ts': ts,
                    'status': status,
                    'message': msg,
                    'points_gain': change_int, # 复用字段名，实际是 change
                    'balance': balance_int,
                    'user_id': item.get('user_id')
                })
            except Exception:
                continue
        
        # 保存，由于 API 返回的是完整的最近记录，直接覆盖即可
        # 但为了保留更久的数据，可以做合并。此处简单起见，且 User 想要 API 数据，直接保存 API 返回的最新数据的解析结果
        # 如果需要保留更久，可以与 self.get_data('glados_history') 合并去重
        # 考虑到 API 给的是 authoritative 的历史，直接覆盖显示最准确
        self.save_data('glados_history', formatted_history)

    def _save_history(self, record: Dict[str, Any]):
        try:
            history = self.get_data('glados_history') or []
            history.append(record)
            tz = pytz.timezone(settings.TZ)
            now = datetime.now(tz)
            keep = []
            for r in history:
                try:
                    dt_str = r.get('date', '')
                    ts_val = r.get('ts')
                    if dt_str:
                        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                        dt = tz.localize(dt) if dt.tzinfo is None else dt
                    else:
                        dt = now
                except Exception:
                    dt = now
                if (now - dt).days < int(self._history_days):
                    if ts_val is None:
                        try:
                            ts_val = int(dt.timestamp() * 1000)
                        except Exception:
                            ts_val = int(time.time()*1000)
                    r['ts'] = ts_val
                    keep.append(r)
            keep = sorted(keep, key=lambda x: int(x.get('ts') or 0), reverse=True)
            self.save_data('glados_history', keep)
        except Exception:
            pass

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            return [{
                "id": "gladossign",
                "name": "GlaDOS 签到",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.sign,
                "kwargs": {}
            }]
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 1, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '基础设置'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'enabled', 'label': '启用插件'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'notify', 'label': '开启通知'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'onlyonce', 'label': '立即运行一次'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VCronField', 'props': {'model': 'cron', 'label': '签到周期'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VTextField', 'props': {'model': 'history_days', 'label': '历史保留天数', 'type': 'number', 'placeholder': '30'}}]},
                                ]}
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 1, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '域名与认证'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'warning', 'variant': 'outlined', 'class': 'mb-2', 'text': '重要提示：请务必确认您的账号所属 Base URL。不同账号可能分配在不同域名 (如 https://glados.one 或 https://glados.cloud) ，填写错误将无法签到。请登录官网查看浏览器地址栏确认。'}}
                                    ]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VTextField', 'props': {'model': 'base_url', 'label': 'Base URL (基础域名)', 'placeholder': '例如 https://glados.one'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VTextarea', 'props': {'model': 'cookie', 'label': 'Cookie', 'rows': 3, 'placeholder': 'koa:sess=...; koa:sess.sig=...'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '从浏览器复制 Cookie (包含 koa:sess 和 koa:sess.sig)。插件仅负责签到和展示信息，请积攒点数后并在官网手动兑换 (100点=10天 / 200点=30天 / 500点=100天)。'}}
                                    ]},
                                ]},
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '🎁 注册与福利(AFF)'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 8}, 'content': [
                                        {'component': 'div', 'props': {'class': 'text-body-2'}, 'text': 'GlaDOS感觉挺佛系的，靠每日签到可长期使用，有需求可以点击注册体验。'},
                                        {'component': 'div', 'props': {'class': 'text-caption text-medium-emphasis mt-2'}, 'text': '提示：注册后每日签到获取点数，可兑换套餐时长 (100点=10天 / 200点=30天 / 500点=100天)。'},
                                        {'component': 'VBtn', 'props': {'href': 'https://glados.space/landing/1F8CJ-TKYWO-KHOV3-PN7X2', 'target': '_blank', 'rel': 'noopener', 'color': 'indigo', 'variant': 'elevated', 'class': 'mt-2'}, 'text': '✨ 立即注册'}
                                    ]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                        {'component': 'VImg', 'props': {'src': 'https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/glados.png', 'height': 120, 'class': 'rounded-lg'}}
                                    ]}
                                ]}
                            ]}
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {'variant': 'elevated', 'elevation': 1, 'rounded': 'lg', 'class': 'mb-3'},
                        'content': [
                            {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': '网络与重试'},
                            {'component': 'VCardText', 'content': [
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VSwitch', 'props': {'model': 'proxy_enabled', 'label': '使用 MP 全局代理'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'timeout_seconds', 'label': '超时(秒)', 'type': 'number', 'placeholder': '30'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'max_attempts', 'label': '重试次数/模式', 'type': 'number', 'placeholder': '2'}}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VTextField', 'props': {'model': 'retry_interval_seconds', 'label': '重试间隔(秒)', 'type': 'number', 'placeholder': '2'}}]},
                                ]},
                                {'component': 'VRow', 'content': [
                                    {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                        {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '说明：每种连接模式内按重试次数与间隔依次尝试；连接模式顺序为 代理→直连(可选)。建议在网络不稳时适当增大超时与间隔。'}}
                                    ]}
                                ]}
                            ]}
                        ]
                    },
                    
                ]
            }
        ], {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "base_url": "https://glados.space",
            "cookie": "",
            "proxy_enabled": True,
            "timeout_seconds": 30,
            "max_attempts": 2,
            "retry_no_proxy_fallback": True,
            "cron": "0 9 * * *",
            "history_days": 30,
        }

    def get_page(self) -> List[dict]:
        # 从 _fetch_user_summary 存储的数据中读取
        user_info = self.get_data('glados_user') or {}
        points_info = self.get_data('glados_points_info') or {}
        historys = self.get_data('glados_history') or []
        
        # 排序
        historys = sorted(historys, key=lambda x: int(x.get('ts') or 0), reverse=True)
        
        card = []
        if user_info or points_info:
            uid = user_info.get('user_id')
            email = user_info.get('email')
            days = user_info.get('days')
            left_days = user_info.get('leftDays')
            
            # 优先从 points_info 获取积分余额
            balance = points_info.get('points')
            if balance is None:
                 balance = "-"
            else:
                 # 格式化，去掉多余的 0
                 try:
                     balance = float(balance)
                     balance = int(balance) if balance.is_integer() else balance
                 except: pass

            latest = historys[0] if historys else {}
            latest_status = latest.get('status', '-')
            latest_gain = latest.get('points_gain', 0)
            latest_color = 'success' if int(latest_gain) > 0 else ('error' if int(latest_gain) < 0 else 'grey')
            latest_time = latest.get('date', '-')
            
            gain_emoji = '📈' if int(latest_gain or 0) > 0 else ('➖' if int(latest_gain or 0) == 0 else '📉')
            
            card = [
                {
                    'component': 'VCard',
                    'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-4'},
                    'content': [
                        {'component': 'VCardTitle', 'props': {'class': 'text-h5 font-weight-bold'}, 'text': '🚀 GlaDOS 用户摘要'},
                        {'component': 'VCardText', 'content': [
                            {'component': 'VRow', 'content': [
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'color': 'purple'}, 'text': f'🆔 用户ID {uid or "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'color': 'amber-darken-2'}, 'text': f'💰 点数 {balance or "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'color': latest_color}, 'text': f'{gain_emoji} 本次 {gain}'}
                                ]},
                            ]},
                            {'component': 'VDivider'},
                            {'component': 'VRow', 'props': {'class': 'mt-3'}, 'content': [
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated'}, 'text': f'📧 邮箱 {email or "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated'}, 'text': f'📅 已用天数 {days if days is not None else "-"}'}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated'}, 'text': f'🕒 剩余天数 {left_days if left_days is not None else "-"}'}
                                ]},
                            ]},
                            {'component': 'VRow', 'props': {'class': 'mt-3'}, 'content': [
                                {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'tonal'}, 'text': f'⏰ 更新时间 {last_time}'}
                                ]},
                            ]},
                            {'component': 'VRow', 'props': {'class': 'mt-3'}, 'content': [
                                {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                    {'component': 'VChip', 'props': {'size': 'default', 'variant': 'tonal', 'color': 'indigo'}, 'text': '💡 提示：点数可兑换套餐：100点=10天 / 200点=30天 / 500点=100天'}
                                ]}
                            ]},
                        ]}
                    ]
                }
            ]
        rows = []
        for h in historys:
            delta = int(h.get('points_gain') or 0)
            delta_color = 'success' if delta > 0 else ('grey' if delta == 0 else 'error')
            delta_emoji = '📈' if delta > 0 else ('➖' if delta == 0 else '📉')
            rows.append({
                'component': 'tr',
                'content': [
                    {'component': 'td', 'props': {'class': 'text-caption'}, 'text': h.get('date', '')},
                    {'component': 'td', 'content': [{'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': 'primary'}, 'text': h.get('status', '-')}]},
                    {'component': 'td', 'content': [{'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': delta_color}, 'text': f"{delta_emoji} {delta}"}]},
                    {'component': 'td', 'props': {'class': 'text-caption'}, 'text': h.get('message', '-')},
                ]
            })
        table = [
            {
                'component': 'VCard',
                'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-4'},
                'content': [
                    {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': f'📊 签到历史 (近{len(rows)}条)'},
                    {'component': 'VCardText', 'content': [
                        {'component': 'VTable', 'props': {'hover': True, 'density': 'comfortable'}, 'content': [
                            {'component': 'thead', 'content': [{'component': 'tr', 'content': [
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '时间'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '状态'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '点数变化'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '消息'},
                            ]}]},
                            {'component': 'tbody', 'content': rows}
                        ]}
                        ]
                    }
                ]
            }
        ]
        if not historys:
            return [{
                'component': 'VAlert',
                'props': {'type': 'info', 'variant': 'tonal', 'text': '暂无签到记录，请先配置域名与Cookie后运行一次签到', 'class': 'mb-2'}
            }]
        return card + table

    def stop_service(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        return True

    def get_command(self) -> List[Dict[str, Any]]: return []
    def get_api(self) -> List[Dict[str, Any]]: return []

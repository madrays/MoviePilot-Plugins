import random
import re
import string
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pytz
import requests
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


class gladossign(_PluginBase):
    plugin_name = "GlaDOS 签到"
    plugin_desc = "邮箱验证码登录，服务端自动签到；积累点数可兑换 10~100 天套餐时长"
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/glados.png"
    plugin_version = "4.0.1"
    plugin_author = "madrays"
    author_url = "https://github.com/madrays"
    plugin_config_prefix = "gladossign_"
    plugin_order = 1
    auth_level = 2

    _enabled = False
    _notify = True
    _onlyonce = False
    _cron = "0 9 * * *"
    _base_url = "https://glados.cloud"
    _email = ""
    _cookie = ""
    _device_id = ""
    _device_ua = ""
    _device_platform = "auto"
    _auto_exchange = ""
    _proxy_enabled = False
    _timeout_seconds = 30
    _retry_interval_seconds = 300
    _max_attempts = 2
    _retry_no_proxy_fallback = True
    _history_days = 30
    _scheduler: Optional[BackgroundScheduler] = None

    # 控制台登录/发码接口里的 site 是固定内部键，与控制台前端保持一致
    _SITE_KEY = "glados.network"

    # 设备身份按安装随机生成：登录与签到必须一致，但不同安装之间不应相同。
    # 平台默认跟随 MoviePilot 宿主机操作系统，也可在配置里手动指定。
    _UA_TEMPLATES = {
        "windows": (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'
        ),
        "macos": (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'
        ),
        "linux": (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'
        ),
    }
    _UA_VERSIONS = (138, 139, 140, 141, 142, 143)
    # 常见桌面分辨率（height, width），与指纹后缀 -{h}-{w} 对应
    _SCREENS = [(1080, 1920), (900, 1440), (1152, 2048), (1080, 2560), (864, 1536), (1200, 1920)]
    _DEFAULT_UA = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    )
    _DEVICE_SCREEN = (1080, 1920)  # 兼容旧引用

    # 兑换接口的 planType 是字符串枚举（见控制台前端：plan100 / plan200 / plan500）
    _EXCHANGE_PLANS = {
        "10": {"points": 100, "label": "10天套餐", "plan_type": "plan100"},
        "30": {"points": 200, "label": "30天套餐", "plan_type": "plan200"},
        "100": {"points": 500, "label": "100天套餐", "plan_type": "plan500"},
    }

    # ------------------------------------------------------------------ 生命周期

    def init_plugin(self, config: dict = None):
        self.stop_service()
        if config:
            self._enabled = bool(config.get("enabled", False))
            self._notify = bool(config.get("notify", True))
            self._onlyonce = bool(config.get("onlyonce", False))
            self._cron = config.get("cron") or "0 9 * * *"
            base_url = str(config.get("base_url") or "").strip()
            self._base_url = base_url or "https://glados.cloud"
            self._email = str(config.get("email") or "").strip()
            self._device_platform = str(config.get("device_platform") or "auto").strip().lower()
            if self._device_platform not in ("auto", "windows", "macos", "linux"):
                self._device_platform = "auto"
            self._auto_exchange = str(config.get("auto_exchange") or "").strip()
            if self._auto_exchange not in self._EXCHANGE_PLANS:
                self._auto_exchange = ""
            self._proxy_enabled = bool(config.get("proxy_enabled", False))
            self._timeout_seconds = self._as_int(config.get("timeout_seconds"), 30)
            self._max_attempts = max(1, self._as_int(config.get("max_attempts"), 2))
            self._retry_interval_seconds = self._as_int(config.get("retry_interval_seconds"), 300)
            self._retry_no_proxy_fallback = bool(config.get("retry_no_proxy_fallback", True))
            self._history_days = self._as_int(config.get("history_days"), 30)

        # 设备身份与会话都放在插件数据里，避免前端保存配置时被覆盖
        self._ensure_device()
        self._cookie = self._load_session_cookie()
        logger.info(
            f"加载配置: Base URL={self._base_url}, 邮箱={'已填' if self._email else '未填'}, "
            f"会话={'有效' if self._cookie else '无'}, 设备平台={self._ua_platform(self._device_ua).strip(chr(34))}"
        )

        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(
                func=self.sign,
                trigger="date",
                run_date=datetime.now() + timedelta(seconds=3),
                name="GlaDOS签到",
            )
            self._onlyonce = False
            self.update_config(self._initial_config(onlyonce=False))
            if self._scheduler.get_jobs():
                self._scheduler.start()
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")

    def stop_service(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        return True

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            return [{
                "id": "gladossign",
                "name": "GlaDOS 签到",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.sign,
                "kwargs": {},
            }]
        return []

    # ------------------------------------------------------------------ 配置与渲染

    @staticmethod
    def _as_int(value: Any, fallback: int) -> int:
        try:
            return int(value)
        except Exception:
            return fallback

    def _initial_config(self, onlyonce: bool = False) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": onlyonce,
            "cron": self._cron,
            "base_url": self._base_url,
            "email": self._email,
            "device_platform": self._device_platform,
            "auto_exchange": self._auto_exchange,
            "proxy_enabled": self._proxy_enabled,
            "timeout_seconds": self._timeout_seconds,
            "max_attempts": self._max_attempts,
            "retry_no_proxy_fallback": self._retry_no_proxy_fallback,
            "retry_interval_seconds": self._retry_interval_seconds,
            "history_days": self._history_days,
        }

    @staticmethod
    def get_render_mode() -> Tuple[str, Optional[str]]:
        """声明 Vue 联邦插件渲染模式，前端产物位于 dist/assets。"""
        return "vue", "dist/assets"

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """Vue 模式下不使用 JSON 表单，仅返回初始配置。"""
        return None, self._initial_config()

    def get_page(self) -> Optional[List[dict]]:
        return None

    def get_command(self) -> List[Dict[str, Any]]:
        return []

    # ------------------------------------------------------------------ 设备身份

    def _ensure_device(self) -> Dict[str, Any]:
        """
        生成并持久化一套固定的设备身份。

        服务端会把「登录设备」与「请求设备」做比对（UA 平台 + 设备指纹），
        因此登录与后续签到必须使用同一套设备信息。这套身份由插件自己生成，
        与用户浏览器无关，任何设备上部署的 MoviePilot 都能稳定签到。
        """
        device = self.get_data("glados_device") or {}
        if not isinstance(device, dict):
            device = {}
        changed = False
        desired_platform = self._resolve_platform()
        # 已存在身份：仅当用户在配置里换了平台时才重新生成 UA（需重新登录）
        if device.get("id") and desired_platform and device.get("platform") != desired_platform:
            ua = self._random_ua(desired_platform)
            device["ua"] = ua
            device["platform"] = self._ua_platform(ua).strip('"')
            device["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changed = True
            self._clear_session()
            logger.info(f"设备平台已切换为 {device.get('platform')}，已清除旧会话，需要重新登录")
        if not device.get("id"):
            platform = desired_platform or self._host_platform()
            ua = self._random_ua(platform)
            height, width = random.SystemRandom().choice(self._SCREENS)
            fingerprint = "".join(random.SystemRandom().choice(string.digits) for _ in range(32))
            device["id"] = f"{fingerprint}-{height}-{width}"
            device["screen"] = f"{width}x{height}"
            device["ua"] = ua
            device["platform"] = self._ua_platform(ua).strip('"')
            device["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changed = True
        if not device.get("ua"):
            platform = self._host_platform()
            ua = self._random_ua(platform)
            device["ua"] = ua
            device["platform"] = self._ua_platform(ua).strip('"')
            changed = True
        if changed:
            self.save_data("glados_device", device)
            logger.info(
                f"设备身份: 平台={device.get('platform')}, 屏幕={device.get('screen')}, "
                f"指纹={str(device.get('id'))[:8]}…"
            )
        self._device_id = str(device.get("id") or "")
        self._device_ua = str(device.get("ua") or self._DEFAULT_UA)
        return device

    def _resolve_platform(self) -> str:
        """配置指定优先；auto 时跟随宿主机平台。"""
        if self._device_platform in self._UA_TEMPLATES:
            return self._device_platform
        return self._host_platform()

    @staticmethod
    def _host_platform() -> str:
        try:
            import platform as _platform
            system = _platform.system().lower()
        except Exception:
            system = ""
        if "windows" in system:
            return "windows"
        if "darwin" in system:
            return "macos"
        return "linux"

    def _random_ua(self, platform: str) -> str:
        template = self._UA_TEMPLATES.get(platform) or self._UA_TEMPLATES["linux"]
        version = random.SystemRandom().choice(self._UA_VERSIONS)
        return template.format(version=version)

    @staticmethod
    def _ua_platform(ua: str) -> str:
        """从 UA 推断 sec-ch-ua-platform 取值，保持与登录设备声明一致。"""
        text = str(ua or "")
        if "Windows" in text:
            return '"Windows"'
        if "Android" in text:
            return '"Android"'
        if "iPhone" in text or "iPad" in text or "iOS" in text:
            return '"iOS"'
        if "Linux" in text:
            return '"Linux"'
        return '"macOS"'

    @staticmethod
    def _sec_ch_ua(ua: str) -> str:
        """按 UA 里的 Chrome 主版本生成 Sec-CH-UA，保持与声明一致。"""
        match = re.search(r"Chrome/(\d+)", ua or "")
        major = match.group(1) if match else "142"
        return f'"Chromium";v="{major}", "Google Chrome";v="{major}", "Not?A_Brand";v="99"'

    def _login_session(self) -> requests.Session:
        """创建会话并先访问登录页，尽量拿到 Cloudflare 等边缘节点下发的 Cookie。"""
        session = requests.Session()
        try:
            warm = session.get(
                f"{self._base_url.rstrip('/')}/login",
                headers=self._build_headers(with_cookie=False),
                timeout=max(6, min(self._timeout_seconds, 12)),
                proxies=self._get_proxies(),
                allow_redirects=False,
            )
            logger.info(
                f"登录预热: GET /login -> HTTP {warm.status_code}, Cookie 项={len(session.cookies)}"
            )
        except Exception as error:
            logger.warning(f"登录预热失败（继续尝试登录）: {error}")
        return session

    def _origin(self) -> str:
        base = self._base_url.rstrip("/")
        if base.startswith("http://"):
            return "http://" + base[len("http://"):].split("/")[0]
        rest = base[len("https://"):] if base.startswith("https://") else base
        return "https://" + rest.split("/")[0]

    def _build_headers(self, with_cookie: bool = True) -> Dict[str, str]:
        origin = self._origin()
        headers = {
            "User-Agent": self._device_ua or self._DEFAULT_UA,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": origin,
            "Referer": origin + "/console",
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": self._ua_platform(self._device_ua or self._DEFAULT_UA),
            "Sec-CH-UA": self._sec_ch_ua(self._device_ua or self._DEFAULT_UA),
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Authorization": self._device_id,
        }
        if with_cookie and self._cookie:
            headers["Cookie"] = self._cookie
        return headers

    def _get_proxies(self) -> Optional[Dict[str, str]]:
        if not self._proxy_enabled:
            return None
        try:
            proxy = getattr(settings, "PROXY", None)
            if not proxy:
                return None
            if isinstance(proxy, str):
                return {"http": proxy, "https": proxy}
            if isinstance(proxy, dict):
                http = proxy.get("http") or proxy.get("HTTP")
                https = proxy.get("https") or proxy.get("HTTPS") or http
                if http or https:
                    return {"http": http or https, "https": https or http}
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------ 会话存取

    def _load_session_cookie(self) -> str:
        session = self.get_data("glados_session") or {}
        cookie = str((session or {}).get("cookie") or "").strip()
        return cookie

    def _save_session(self, cookie: str, email: str) -> None:
        self._cookie = cookie
        self.save_data("glados_session", {
            "cookie": cookie,
            "email": email or self._email,
            "login_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ts": int(time.time() * 1000),
        })

    def _clear_session(self) -> None:
        self._cookie = ""
        self.save_data("glados_session", {})

    def _session_state(self) -> Dict[str, Any]:
        session = self.get_data("glados_session") or {}
        cookie = str((session or {}).get("cookie") or "")
        return {
            "logged_in": bool(cookie),
            "email": str((session or {}).get("email") or self._email or ""),
            "login_at": str((session or {}).get("login_at") or ""),
            "cookie_items": len([x for x in cookie.split(";") if x.strip()]) if cookie else 0,
        }

    # ------------------------------------------------------------------ 登录流程

    def send_login_code(self, email: str) -> Dict[str, Any]:
        """请求 GlaDOS 发送邮箱验证码。"""
        email = str(email or "").strip().lower()
        if not email or "@" not in email:
            return {"code": -1, "msg": "请填写正确的邮箱地址"}
        started = time.time()
        try:
            resp = requests.post(
                f"{self._base_url.rstrip('/')}/api/authorization",
                json={"address": email, "site": self._SITE_KEY},
                headers=self._build_headers(with_cookie=False),
                timeout=max(8, min(self._timeout_seconds, 20)),
                proxies=self._get_proxies(),
            )
            data = resp.json() or {}
        except requests.exceptions.Timeout:
            logger.warning(f"发送验证码超时（{time.time() - started:.1f}s）")
            return {"code": -1, "msg": "发送验证码超时：服务器到 GlaDOS 无响应，请稍后重试或检查出网"}
        except Exception as error:
            logger.warning(f"发送验证码失败: {error}")
            return {"code": -1, "msg": f"发送验证码失败: {error}"}

        logger.info(f"发码响应: code={data.get('code')}, method={data.get('method')}, 耗时={time.time() - started:.1f}s")

        if data.get("code") == 0:
            self._email = email
            self.update_config(self._initial_config())
            logger.info(f"验证码已发送: {email}（method={data.get('method')}）")
            return {"code": 0, "msg": "验证码已发送，请查收邮箱（注意垃圾箱）"}
        message = str(data.get("message") or data.get("reason") or "发送失败")
        logger.warning(f"发送验证码被拒绝: {message}")
        return {"code": -1, "msg": message}

    def login_with_code(self, email: str, code: str) -> Dict[str, Any]:
        """
        使用邮箱 + 验证码在服务器端登录，并持久化会话 Cookie。

        登录发生在 MoviePilot 所在服务器，设备指纹与 UA 由插件自己决定并
        保持不变，因此不存在跨设备 device-mismatch。
        """
        email = str(email or "").strip().lower()
        code = str(code or "").strip()
        if not email or "@" not in email:
            return {"code": -1, "msg": "请填写正确的邮箱地址"}
        if not code:
            return {"code": -1, "msg": "请填写邮箱收到的验证码"}

        self._ensure_device()
        session = self._login_session()
        # 反代通常 30s 就回 504，登录请求必须在此前给出结果
        request_timeout = max(8, min(self._timeout_seconds, 20))
        started = time.time()
        try:
            resp = session.post(
                f"{self._base_url.rstrip('/')}/api/login",
                json={"method": "email", "site": self._SITE_KEY, "email": email, "mailcode": code},
                headers=self._build_headers(with_cookie=False),
                timeout=request_timeout,
                proxies=self._get_proxies(),
                # 不跟随跳转：登录成功可能 302 到 /console，跟随会去拉页面而阻塞
                allow_redirects=False,
            )
            data = {}
            try:
                data = resp.json() or {}
            except Exception:
                data = {}
            # 302/303 且已下发 Cookie 时视为登录成功
            if resp.status_code in (301, 302, 303, 307, 308) and len(session.cookies) > 0:
                data = {"code": 0, "message": "redirect login ok"}
        except requests.exceptions.Timeout:
            elapsed = time.time() - started
            logger.warning(f"登录请求超时（{elapsed:.1f}s）: 服务器到 GlaDOS 的 /api/login 无响应")
            return {
                "code": -1,
                "msg": f"登录请求超时（{elapsed:.0f}s 无响应）：服务器到 GlaDOS 的 /api/login 被阻塞，"
                       f"请检查 MoviePilot 服务器出网或稍后重试",
            }
        except Exception as error:
            elapsed = time.time() - started
            logger.warning(f"登录请求失败（{elapsed:.1f}s）: {error}")
            return {"code": -1, "msg": f"登录请求失败: {error}"}

        logger.info(f"登录响应: code={data.get('code')}, message={data.get('message')}, 耗时={time.time() - started:.1f}s")

        if data.get("code") != 0:
            message = str(data.get("message") or data.get("reason") or "登录失败")
            logger.warning(f"登录被拒绝: {message}")
            return {"code": -1, "msg": message}

        # 收集完整 Cookie jar（含不同域/路径下发的会话项）
        cookies = {cookie.name: cookie.value for cookie in session.cookies}
        cookie_str = "; ".join(f"{name}={value}" for name, value in cookies.items())
        if not cookie_str:
            logger.warning("登录返回成功但未拿到 Cookie")
            return {"code": -1, "msg": "登录成功但未获取到会话 Cookie，请重试"}

        self._email = email
        self._save_session(cookie_str, email)
        self.update_config(self._initial_config())
        logger.info(f"登录成功: {email}, Cookie 项={len(cookies)}, 耗时={time.time() - started:.1f}s")

        # 资料刷新放后台，避免把登录响应拖过反代超时
        try:
            threading.Thread(target=self._refresh_profile, daemon=True).start()
        except Exception:
            pass

        cached_user = self.get_data("glados_user") or {}
        return {
            "code": 0,
            "msg": "登录成功",
            "email": email,
            "cookie_items": len(cookies),
            "leftDays": cached_user.get("leftDays"),
            "points": self._current_points(),
            "platform": self._ua_platform(self._device_ua).strip('"'),
        }

    def _refresh_profile(self) -> None:
        """后台刷新账号资料，失败不影响登录结果。"""
        try:
            self._fetch_user_summary(self._build_headers(), self._get_proxies())
        except Exception as error:
            logger.warning(f"后台刷新账号资料失败: {error}")

    def logout(self) -> Dict[str, Any]:
        self._clear_session()
        logger.info("已清除 GlaDOS 会话")
        return {"code": 0, "msg": "已退出登录"}

    # ------------------------------------------------------------------ 状态

    def _current_points(self) -> Optional[int]:
        points_info = self.get_data("glados_points_info") or {}
        return self._to_int(points_info.get("points"))

    @staticmethod
    def _to_int(value: Any) -> Optional[int]:
        try:
            if value is None:
                return None
            if isinstance(value, bool):
                return int(value)
            if isinstance(value, (int, float)):
                return int(value)
            text = str(value).strip()
            if not text:
                return None
            return int(float(text)) if "." in text else int(text)
        except Exception:
            return None

    def get_state_api(self) -> Dict[str, Any]:
        """前端页面初始化数据。"""
        user = self.get_data("glados_user") or {}
        device = self.get_data("glados_device") or {}
        history = self.get_data("glados_history") or []
        return {
            "config": self._initial_config(),
            "session": self._session_state(),
            "device": {
                "platform": device.get("platform") or self._ua_platform(self._device_ua).strip('"'),
                "screen": device.get("screen") or "",
                "ua": device.get("ua") or "",
                "fingerprint": (str(device.get("id") or "")[:10] + "…") if device.get("id") else "",
            },
            "summary": {
                "email": user.get("email") or self._email,
                "user_id": user.get("user_id"),
                "days": user.get("days"),
                "leftDays": user.get("leftDays"),
                "points": self._current_points(),
            },
            "last_checkin": history[0] if history else None,
        }

    def get_history(self) -> List[Dict[str, Any]]:
        history = self.get_data("glados_history") or []
        return sorted(history, key=lambda x: int(x.get("ts") or 0), reverse=True)[: self._history_days * 2]

    # ------------------------------------------------------------------ 签到

    def checkin_now(self, payload: Optional[dict] = None) -> Dict[str, Any]:
        """供前端「立即签到」按钮调用。"""
        result = self.sign()
        return result if isinstance(result, dict) else {"code": -1, "msg": "签到失败"}

    def sign(self) -> Dict[str, Any]:
        logger.info("开始 GlaDOS 签到")
        self._ensure_device()
        self._cookie = self._load_session_cookie()
        if not self._cookie:
            message = "尚未登录，请先在插件页面用邮箱验证码登录"
            logger.warning(message)
            self._save_history({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "未登录",
                "message": message,
                "points_gain": 0,
            })
            if self._notify:
                self.post_message(mtype=NotificationType.SiteMessage, title="🔴 GlaDOS 签到失败", text=message)
            return {"code": -1, "status": "未登录", "msg": message}

        url = f"{self._base_url.rstrip('/')}/api/user/checkin"
        domain = self._origin().replace("https://", "").replace("http://", "").split("/")[0]
        body = {"token": domain}
        headers = self._build_headers()
        proxies = self._get_proxies()
        attempts = [proxies, None] if proxies and self._retry_no_proxy_fallback else [proxies]
        attempts = [item for item in attempts if item is not None] or [None]
        last_error: Optional[Exception] = None

        for index, proxy in enumerate(attempts):
            for attempt in range(1, self._max_attempts + 1):
                try:
                    start_ms = int(time.time() * 1000)
                    resp = requests.post(
                        url, json=body, headers=headers, timeout=self._timeout_seconds, proxies=proxy
                    )
                    cost_ms = int(time.time() * 1000) - start_ms
                    data = {}
                    try:
                        data = resp.json() or {}
                    except Exception:
                        data = {}
                    logger.info(
                        f"响应状态: {resp.status_code}, 耗时: {cost_ms}ms, "
                        f"code={data.get('code')}, reason={data.get('reason')}, message={data.get('message')}"
                    )
                    result = self._handle_checkin_response(data)
                    if result is not None:
                        return result
                except Exception as error:
                    last_error = error
                    logger.warning(
                        f"请求失败(第{index + 1}组第{attempt}/{self._max_attempts}次): {error}"
                    )
                    if attempt < self._max_attempts:
                        time.sleep(max(0, self._retry_interval_seconds))

        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "签到失败",
            "message": f"请求异常: {last_error}",
            "points_gain": 0,
        }
        self._save_history(record)
        if self._notify:
            self.post_message(
                mtype=NotificationType.SiteMessage,
                title="🔴 GlaDOS 签到失败",
                text=f"⏰ {record['date']}\n❌ {record['message']}",
            )
        return {"code": -1, "status": "签到失败", "msg": record["message"]}

    def _handle_checkin_response(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析签到响应；返回 None 表示应继续重试。"""
        raw_code = data.get("code")
        try:
            code = int(raw_code) if raw_code is not None else -1
        except Exception:
            code = -1

        if code == -2:
            self._clear_session()
            message = "登录已失效（没有权限），请在插件页面重新用邮箱验证码登录"
            logger.warning(message)
            self._save_history({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "登录失效",
                "message": message,
                "points_gain": 0,
            })
            if self._notify:
                self.post_message(mtype=NotificationType.SiteMessage, title="🔴 GlaDOS 登录失效", text=message)
            return {"code": -2, "status": "登录失效", "msg": message}

        if code == 4 and data.get("reason") == "device-mismatch":
            message = (
                "服务端判定设备不一致（登录设备={login}，当前设备={current}）。"
                "插件已固定设备身份，出现该提示通常意味着账号在别处重新登录过，请在本插件重新登录。"
            ).format(
                login=data.get("loginDevice") or "未知",
                current=data.get("currentDevice") or "未知",
            )
            logger.warning(message)
            self._save_history({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "设备不一致",
                "message": message,
                "points_gain": 0,
            })
            if self._notify:
                self.post_message(mtype=NotificationType.SiteMessage, title="🔴 GlaDOS 设备校验失败", text=message)
            return {"code": 4, "status": "设备不一致", "msg": message}

        points_gain = self._to_int(data.get("points")) or 0
        message_en = str(data.get("message") or "")
        items = data.get("list") or []
        item = items[0] if items else {}
        if not points_gain and item.get("points"):
            points_gain = self._to_int(item.get("points")) or 0

        if points_gain > 0:
            status = "签到成功"
        elif code == 1 or "Repeats" in message_en or "Try Tomorrow" in message_en:
            status = "已签到"
        else:
            status = "签到失败"

        self._fetch_user_summary(self._build_headers(), self._get_proxies())
        points = self._current_points()

        exchange_result = ""
        if status in ("签到成功", "已签到"):
            exchange_result = self._try_auto_exchange(self._build_headers(), self._get_proxies())
            if exchange_result.startswith("自动兑换成功"):
                self._fetch_user_summary(self._build_headers(), self._get_proxies())
                points = self._current_points()

        user = self.get_data("glados_user") or {}
        history = self.get_data("glados_history") or []
        if status == "已签到" and history:
            today = datetime.now(pytz.timezone(settings.TZ)).strftime("%Y-%m-%d")
            record = next(
                (
                    row for row in history
                    if today in str(row.get("date", ""))
                    and (
                        "checkin" in str(row.get("message", "")).lower()
                        or "签到" in str(row.get("message", ""))
                    )
                ),
                None,
            )
            if record:
                points_gain = int(record.get("points_gain") or 0)

        if status == "签到失败":
            self._save_history({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "签到失败",
                "message": message_en or "签到失败",
                "points_gain": 0,
            })

        if status == "签到成功":
            summary = f"签到成功！获得 {points_gain} 点数"
        elif status == "已签到":
            summary = f"今日已签到，本次获得 {points_gain} 点数" if points_gain else "今日已签到，请明天再试"
        else:
            summary = message_en or "签到失败"

        if self._notify:
            title = {
                "签到成功": "✅ GlaDOS 签到成功",
                "已签到": "✅ 今日已签到",
            }.get(status, "🔴 GlaDOS 签到失败")
            lines = [
                f"📝 {summary}",
                f"💰 当前点数：{points}" if points is not None else "",
                f"🕒 剩余天数：{user.get('leftDays')}" if user.get("leftDays") is not None else "",
                f"📧 邮箱：{user.get('email') or self._email}" if (user.get("email") or self._email) else "",
                f"🎁 {exchange_result}" if exchange_result else "",
            ]
            self.post_message(
                mtype=NotificationType.SiteMessage,
                title=title,
                text="\n".join(item for item in lines if item),
            )

        result = {
            "code": 0 if status in ("签到成功", "已签到") else -1,
            "status": status,
            "msg": summary,
            "points_gain": points_gain,
            "points": points,
            "leftDays": user.get("leftDays"),
            "email": user.get("email") or self._email,
            "exchange": exchange_result,
        }
        logger.info(f"签到完成: {status}, 本次 {points_gain} 点, 余额 {points}")
        return result

    # ------------------------------------------------------------------ 用户信息

    def _fetch_user_summary(self, headers: Dict[str, str], proxies: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """拉取点数、历史与账号信息。"""
        timeout = max(10, min(self._timeout_seconds, 30))
        try:
            resp = requests.get(
                f"{self._base_url.rstrip('/')}/api/user/points",
                headers=headers,
                timeout=timeout,
                proxies=proxies,
            )
            if resp.status_code == 200:
                data = resp.json() or {}
                if data.get("code") == 0:
                    self.save_data("glados_points_info", data)
                    self._sync_history_from_api(data.get("history") or [])
        except Exception as error:
            logger.warning(f"获取 Points 失败: {error}")

        try:
            resp = requests.get(
                f"{self._base_url.rstrip('/')}/api/user/status",
                headers=headers,
                timeout=timeout,
                proxies=proxies,
            )
            data = resp.json() or {}
            if data.get("code") == 0 and isinstance(data.get("data"), dict):
                payload = data["data"]
                result = {
                    "user_id": payload.get("userId") or payload.get("configureId"),
                    "email": payload.get("email"),
                    "days": self._to_int(payload.get("days")),
                    "leftDays": self._to_int(payload.get("leftDays")),
                }
                self.save_data("glados_user", result)
                return result
        except Exception as error:
            logger.warning(f"获取账号信息失败: {error}")
        return {}

    def _sync_history_from_api(self, api_history: List[Dict[str, Any]]) -> None:
        if not api_history:
            return
        formatted: List[Dict[str, Any]] = []
        for item in api_history:
            try:
                ts = int(item.get("time") or 0)
                change = float(item.get("change") or 0)
                change_value: Any = int(change) if change.is_integer() else change
                balance = float(item.get("balance") or 0)
                balance_value: Any = int(balance) if balance.is_integer() else balance
                business = str(item.get("business") or "")
                detail = str(item.get("detail") or "")
                if "checkin" in business or "checkin" in detail:
                    status, message = "签到", "每日签到奖励"
                elif "exchange" in business or "exchange" in detail:
                    status, message = "兑换", "积分兑换套餐"
                else:
                    status, message = "变动", (detail or business)
                formatted.append({
                    "date": datetime.fromtimestamp(ts / 1000.0).strftime("%Y-%m-%d %H:%M:%S"),
                    "ts": ts,
                    "status": status,
                    "message": message,
                    "points_gain": change_value,
                    "balance": balance_value,
                    "user_id": item.get("user_id"),
                })
            except Exception:
                continue
        self.save_data("glados_history", formatted)

    def _save_history(self, record: Dict[str, Any]) -> None:
        try:
            history = self.get_data("glados_history") or []
            history.append(record)
            tz = pytz.timezone(settings.TZ)
            now = datetime.now(tz)
            kept: List[Dict[str, Any]] = []
            for row in history:
                try:
                    stamp = datetime.strptime(str(row.get("date", "")), "%Y-%m-%d %H:%M:%S")
                    stamp = tz.localize(stamp) if stamp.tzinfo is None else stamp
                except Exception:
                    stamp = now
                if (now - stamp).days < self._history_days:
                    if row.get("ts") is None:
                        row["ts"] = int(stamp.timestamp() * 1000)
                    kept.append(row)
            kept.sort(key=lambda x: int(x.get("ts") or 0), reverse=True)
            self.save_data("glados_history", kept)
        except Exception:
            pass

    # ------------------------------------------------------------------ 自动兑换

    def _try_auto_exchange(self, headers: Dict[str, str], proxies: Optional[Dict[str, str]]) -> str:
        plan = self._EXCHANGE_PLANS.get(self._auto_exchange)
        if not plan:
            return ""

        def record(status: str, message: str, points_change: int = 0) -> None:
            self._save_history({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
                "message": message,
                "points_gain": points_change,
            })

        today = datetime.now(pytz.timezone(settings.TZ)).strftime("%Y-%m-%d")
        if any(
            today in str(item.get("date", "")) and item.get("status") in ("兑换", "兑换成功")
            for item in (self.get_data("glados_history") or [])
        ):
            logger.info("今日已兑换套餐，跳过自动兑换")
            return ""

        current = self._current_points()
        required = plan["points"]
        if current is None:
            return "积分数据未就绪，跳过自动兑换"
        if current < required:
            return f"积分不足（{current}/{required}），未兑换{plan['label']}"

        try:
            resp = requests.post(
                f"{self._base_url.rstrip('/')}/api/user/exchange",
                json={"planType": plan["plan_type"]},
                headers=headers,
                timeout=self._timeout_seconds,
                proxies=proxies,
            )
            data = resp.json() or {}
        except Exception as error:
            logger.warning(f"自动兑换请求失败: {error}")
            record("兑换异常", f"自动兑换请求失败：{error}")
            return f"自动兑换请求失败：{error}"

        if data.get("code") == 0:
            result = f"自动兑换成功：{plan['label']}（-{required}点）"
            logger.info(result)
            return result

        reason = data.get("message") or data.get("reason") or f"HTTP {resp.status_code}"
        logger.warning(f"自动兑换失败: {reason}（planType={plan['plan_type']}）")
        record("兑换失败", f"自动兑换失败：{reason}")
        return f"自动兑换失败：{reason}"

    # ------------------------------------------------------------------ API

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/state",
                "endpoint": self.get_state_api,
                "methods": ["GET"],
                "summary": "插件状态",
                "description": "获取登录状态、设备身份与用户摘要",
                "auth": "bear",
            },
            {
                "path": "/send_code",
                "endpoint": self.send_login_code_api,
                "methods": ["POST"],
                "summary": "发送验证码",
                "description": "向指定邮箱发送 GlaDOS 登录验证码",
                "auth": "bear",
            },
            {
                "path": "/login",
                "endpoint": self.login_api,
                "methods": ["POST"],
                "summary": "邮箱验证码登录",
                "description": "在服务器端完成登录并保存会话",
                "auth": "bear",
            },
            {
                "path": "/logout",
                "endpoint": self.logout_api,
                "methods": ["POST"],
                "summary": "退出登录",
                "description": "清除已保存的会话",
                "auth": "bear",
            },
            {
                "path": "/checkin",
                "endpoint": self.checkin_now,
                "methods": ["POST"],
                "summary": "立即签到",
                "description": "立即执行一次签到",
                "auth": "bear",
            },
            {
                "path": "/history",
                "endpoint": self.get_history,
                "methods": ["GET"],
                "summary": "签到历史",
                "description": "获取本地签到记录",
                "auth": "bear",
            },
        ]

    def send_login_code_api(self, payload: dict) -> Dict[str, Any]:
        return self.send_login_code((payload or {}).get("email", ""))

    def login_api(self, payload: dict) -> Dict[str, Any]:
        payload = payload or {}
        return self.login_with_code(payload.get("email", ""), payload.get("code", ""))

    def logout_api(self, payload: dict = None) -> Dict[str, Any]:
        return self.logout()

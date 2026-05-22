__all__ = ["HDHivePlaywrightClient", "HDHiveLoginError"]

import re
from contextlib import contextmanager
from socket import (
    AF_INET,
    SO_REUSEADDR,
    SOCK_STREAM,
    SOL_SOCKET,
    socket,
)
from platform import machine as _machine
from sys import platform
from time import sleep
from typing import Any, Dict, Iterator, Optional, Tuple
from urllib.parse import unquote, urlparse

from httpx import Client
import orjson

try:
    from cloakbrowser import launch_context as cloak_launch_context
except Exception:
    cloak_launch_context = None

try:
    from playwright.sync_api import (
        TimeoutError as PlaywrightTimeoutError,
        sync_playwright,
    )
except Exception:
    PlaywrightTimeoutError = TimeoutError
    sync_playwright = None

from app.core.config import settings


class HDHiveLoginError(Exception):
    """
    HDHive 网页登录失败或超时
    """


class HDHivePlaywrightClient:
    """
    HDHive 站点 Playwright 客户端
    """

    _CHROME_UA_SUFFIX = (
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, base_url: str = "https://hdhive.com", headless: bool = True) -> None:
        """
        :param base_url: 网站根域名
        :param headless: Playwright 是否无头模式
        """
        self.base_url = base_url.rstrip("/")
        self.login_page = "/login"
        self._headless = headless
        self._cookie_str: Optional[str] = None

    @staticmethod
    def _build_ua() -> str:
        m = _machine().lower()
        arm_like = "arm" in m or "aarch" in m
        if platform == "linux":
            arch = "aarch64" if arm_like else "x86_64"
            product = f"X11; Linux {arch}"
        elif platform == "win32":
            product = (
                "Windows NT 10.0; ARM64" if arm_like else "Windows NT 10.0; Win64; x64"
            )
        else:
            product = "Macintosh; Intel Mac OS X 10_15_7"
        return f"Mozilla/5.0 ({product}) {HDHivePlaywrightClient._CHROME_UA_SUFFIX}"

    @staticmethod
    def _chromium_launch_args() -> list[str]:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
        ]
        if platform == "linux":
            args.extend(
                [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                ]
            )
        return args

    @staticmethod
    def _proxy_url_from_settings() -> Optional[str]:
        p = getattr(settings, 'PROXY', None)
        if not p:
            return None
        if isinstance(p, str):
            return p
        if isinstance(p, dict):
            u = p.get("https") or p.get("http")
            return str(u) if u else None
        return None

    @staticmethod
    def _playwright_proxy_settings() -> Optional[Dict[str, str]]:
        raw = HDHivePlaywrightClient._proxy_url_from_settings()
        if not raw:
            return None
        u = urlparse(raw)
        if not u.scheme or not u.hostname:
            return None
        if u.scheme in ("socks5", "socks") and (u.username or u.password):
            return None
        port = u.port
        if port is None:
            port = 443 if u.scheme == "https" else 80
        server = f"{u.scheme}://{u.hostname}:{port}"
        pw: Dict[str, str] = {"server": server}
        if u.username:
            pw["username"] = unquote(u.username)
        if u.password:
            pw["password"] = unquote(u.password)
        return pw

    @staticmethod
    @contextmanager
    def _socks5_slippers_if_needed() -> Iterator[Optional[Dict[str, str]]]:
        raw = HDHivePlaywrightClient._proxy_url_from_settings()
        if not raw:
            yield None
            return
        u = urlparse(raw)
        if u.scheme not in ("socks5", "socks") or not (u.username or u.password):
            yield None
            return
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", 0))
            local_port = sock.getsockname()[1]
        finally:
            sock.close()
            
        try:
            from slippers import Proxy
        except ImportError as e:
            import logging
            logging.error(f"HDHive: 无法使用 SOCKS5 代理验证转接，缺少依赖或包错误 {e}")
            yield None
            return
            
        sp = Proxy(raw, host="127.0.0.1", port=local_port)
        with sp:
            local_url = sp.url()
            yield {"server": local_url}

    @staticmethod
    def _chromium_launch_kwargs(
        headless: bool, proxy: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "headless": headless,
            "args": HDHivePlaywrightClient._chromium_launch_args(),
        }
        if proxy:
            kwargs["proxy"] = proxy
        return kwargs

    @staticmethod
    def _cloakbrowser_launch_kwargs(
        headless: bool, proxy: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "headless": headless,
            "user_agent": HDHivePlaywrightClient._build_ua(),
            "humanize": getattr(settings, "CLOAKBROWSER_HUMANIZE", True),
            "human_preset": getattr(settings, "CLOAKBROWSER_HUMAN_PRESET", "default"),
            "viewport": {"width": 1280, "height": 720},
        }
        if proxy:
            kwargs["proxy"] = proxy
        return kwargs

    @staticmethod
    def _use_cloakbrowser() -> bool:
        return cloak_launch_context is not None

    def _make_context(
        self,
        pw: Any,
        proxy: Optional[Dict[str, str]] = None,
    ) -> tuple[Any, Any]:
        if HDHivePlaywrightClient._use_cloakbrowser():
            context = cloak_launch_context(
                **HDHivePlaywrightClient._cloakbrowser_launch_kwargs(
                    self._headless, proxy
                )
            )
            return context, context

        if sync_playwright is None:
            raise HDHiveLoginError("当前环境缺少 CloakBrowser 或 Playwright 依赖")

        browser = pw.chromium.launch(
            **HDHivePlaywrightClient._chromium_launch_kwargs(self._headless, proxy),
        )
        context = browser.new_context(
            user_agent=HDHivePlaywrightClient._build_ua(),
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            viewport={"width": 1280, "height": 720},
        )
        return browser, context

    @staticmethod
    def _parse_cookie_str(cookie_str: str) -> dict[str, str]:
        cookies: dict[str, str] = {}
        for item in cookie_str.split(";"):
            if "=" in item:
                name, value = item.strip().split("=", 1)
                cookies[name.strip()] = value.strip()
        return cookies

    def _fetch_action_hash_via_playwright(self) -> Optional[str]:
        if not self._cookie_str:
            return None
        found_hash: list[str] = []

        def on_response(response: Any) -> None:
            if found_hash:
                return
            url = response.url
            if "_next/static/chunks" not in url or not url.endswith(".js"):
                return
            try:
                body = response.body().decode("utf-8", errors="ignore")
            except Exception:
                return
            m = re.search(
                r'createServerReference\)[(\s]*"([0-9a-f]{40,})"[^"]*"checkIn"',
                body,
            )
            if m:
                found_hash.append(m.group(1))

        try:
            cookies = HDHivePlaywrightClient._parse_cookie_str(self._cookie_str)
            domain = self.base_url.replace("https://", "").replace("http://", "")

            with HDHivePlaywrightClient._browser_runtime() as p:
                with HDHivePlaywrightClient._socks5_slippers_if_needed() as slip:
                    proxy = (
                        slip
                        if slip is not None
                        else HDHivePlaywrightClient._playwright_proxy_settings()
                    )
                    browser, context = self._make_context(p, proxy)
                    try:
                        for name, value in cookies.items():
                            context.add_cookies(
                                [
                                    {
                                        "name": name,
                                        "value": value,
                                        "domain": domain,
                                        "path": "/",
                                    }
                                ]
                            )
                        page = context.new_page()
                        page.on("response", on_response)
                        page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                    finally:
                        browser.close()
        except Exception:
            pass

        return found_hash[0] if found_hash else None

    @staticmethod
    def _checkin_parse_rsc_result(text: str) -> Optional[Dict[str, Any]]:
        redirected_to_login = False
        for line in text.splitlines():
            m = re.match(r"^\d+:(\{.*\})\s*$", line)
            if not m:
                continue
            try:
                obj = orjson.loads(m.group(1))
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            obj_keys = set(obj.keys())
            if obj_keys <= {"a", "f", "b", "q", "i", "S"}:
                if "login" in str(obj):
                    redirected_to_login = True
                continue
            if "f" in obj and not any(
                key in obj for key in ("error", "response", "success", "message", "description")
            ):
                if "login" in str(obj):
                    redirected_to_login = True
                continue
            if "error" in obj and isinstance(obj["error"], dict):
                return obj["error"]
            return obj
        if redirected_to_login:
            return {
                "success": False,
                "message": "认证失效或 Cookie 无效，签到请求被站点重定向到登录页",
            }
        return None

    @staticmethod
    def _checkin_payload_dict(result: Dict[str, Any]) -> Dict[str, Any]:
        inner = result.get("response")
        if isinstance(inner, dict):
            return inner
        return result

    def _fill_and_submit(
        self,
        page: Any,
        username: str,
        password: str,
    ) -> bool:
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page.goto(
            f"{self.base_url}{self.login_page}",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_selector("input", timeout=15000)

        user_selectors = [
            "input[name='username']",
            "input[name='email']",
            "input[type='email']",
            "input[placeholder*='邮箱']",
            "input[placeholder*='email']",
            "input[placeholder*='用户名']",
        ]
        for sel in user_selectors:
            try:
                if page.query_selector(sel):
                    page.locator(sel).type(username, delay=60)
                    break
            except Exception:
                continue

        pwd_selectors = [
            "input[name='password']",
            "input[type='password']",
            "input[placeholder*='密码']",
        ]
        for sel in pwd_selectors:
            try:
                if page.query_selector(sel):
                    page.locator(sel).type(password, delay=60)
                    break
            except Exception:
                continue

        sleep(0.3)
        try:
            btn = (
                page.query_selector("button[type='submit']")
                or page.query_selector("button:has-text('登录')")
                or page.query_selector("button:has-text('Login')")
            )
            if btn:
                btn.click()
            else:
                page.keyboard.press("Enter")
        except Exception:
            page.keyboard.press("Enter")

        try:
            page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
            return True
        except PlaywrightTimeoutError:
            raise HDHiveLoginError(
                f"登录超时，当前 URL: {page.url}，页面标题: {page.title()}"
            )

    def checkin(
        self,
        cookie_str: str,
        gamble: bool = False,
    ) -> Tuple[bool, str]:
        self._cookie_str = cookie_str
        if not self._cookie_str:
            return False, "请先 login 或传入 Cookie"

        cookies = HDHivePlaywrightClient._parse_cookie_str(self._cookie_str)
        token = cookies.get("token")
        if not token:
            return False, "Cookie missing 'token'"

        resolved_hash = self._fetch_action_hash_via_playwright()
        if not resolved_hash:
            return False, "无法获取 action hash，签到中止，站点可能有反爬更新或网络问题。"

        ua = HDHivePlaywrightClient._build_ua()
        headers = {
            "User-Agent": ua,
            "Accept": "text/x-component",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
            "next-action": resolved_hash,
            "Authorization": f"Bearer {token}",
        }

        body = orjson.dumps([gamble])
        label = "赌狗签到" if gamble else "每日签到"

        proxy_h = HDHivePlaywrightClient._proxy_url_from_settings()
        try:
            with Client(verify=False, timeout=30.0, proxy=proxy_h) as client:
                resp = client.post(
                    self.base_url,
                    headers=headers,
                    cookies=cookies,
                    content=body,
                )
            text = resp.content.decode("utf-8", errors="replace")
            result = HDHivePlaywrightClient._checkin_parse_rsc_result(text)
            if result is None:
                if resp.status_code == 200:
                    return True, f"{label}请求可能成功"
                return False, f"HTTP {resp.status_code}"

            payload = HDHivePlaywrightClient._checkin_payload_dict(result)
            message = str(payload.get("message") or "")
            description = str(payload.get("description") or "")
            display = description or message or str(payload)
            already_signed = any(
                k in part
                for k in ("已经签到", "签到过", "明天再来")
                for part in (message, description)
            )
            success = bool(payload.get("success")) or already_signed
            return success, display
        except Exception as e:
            return False, str(e)

    def login(
        self,
        username: str,
        password: str,
    ) -> Optional[Tuple[str, str]]:
        if not username or not password:
            raise HDHiveLoginError("必须传入用户名和密码")

        try:
            with HDHivePlaywrightClient._browser_runtime() as p:
                with HDHivePlaywrightClient._socks5_slippers_if_needed() as slip:
                    proxy = (
                        slip
                        if slip is not None
                        else HDHivePlaywrightClient._playwright_proxy_settings()
                    )
                    browser, context = self._make_context(p, proxy)
                    try:
                        page = context.new_page()
                        ok = self._fill_and_submit(page, username, password)
                        raw_cookies = context.cookies()
                    finally:
                        browser.close()

            if not ok:
                return None
            token = next(
                (c["value"] for c in raw_cookies if c["name"] == "token"), None
            )
            csrf = next(
                (c["value"] for c in raw_cookies if c["name"] == "csrf_access_token"),
                None,
            )
            if token:
                parts = [f"token={token}"]
                if csrf:
                    parts.append(f"csrf_access_token={csrf}")
                self._cookie_str = "; ".join(parts)
                return self._cookie_str, token
        except HDHiveLoginError:
            raise
        except Exception as e:
            raise HDHiveLoginError(f"登录失败: {e}") from e
        return None

    @staticmethod
    @contextmanager
    def _browser_runtime() -> Iterator[Optional[Any]]:
        if HDHivePlaywrightClient._use_cloakbrowser():
            yield None
            return
        if sync_playwright is None:
            raise HDHiveLoginError("当前环境缺少 CloakBrowser 或 Playwright 依赖")
        with sync_playwright() as p:
            yield p

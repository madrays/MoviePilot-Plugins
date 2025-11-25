import re
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


class ugreendiscuz(_PluginBase):
    plugin_name = "绿联论坛签到"
    plugin_desc = "自动登录刷新Cookie或手动Cookie，登录即签到；抓取头像、积分等信息并展示与通知"
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/lvlian.jpg"
    plugin_version = "1.0.0"
    plugin_author = "madrays"
    author_url = "https://github.com/madrays"
    plugin_config_prefix = "ugreendiscuz_"
    plugin_order = 1
    auth_level = 2

    _enabled = False
    _notify = True
    _onlyonce = False
    _cron = "0 8 * * *"
    _cookie = ""
    _username = ""
    _password = ""
    _history_days = 30
    _scheduler: Optional[BackgroundScheduler] = None

    def init_plugin(self, config: dict = None):
        self.stop_service()
        if config:
            self._enabled = config.get("enabled", False)
            self._notify = config.get("notify", True)
            self._onlyonce = config.get("onlyonce", False)
            self._cron = config.get("cron", "0 8 * * *")
            self._cookie = (config.get("cookie") or "").strip()
            self._username = (config.get("username") or "").strip()
            self._password = (config.get("password") or "").strip()
            try:
                self._history_days = int(config.get("history_days", 30))
            except Exception:
                self._history_days = 30
        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(func=self.sign, trigger='date', run_date=datetime.now() + timedelta(seconds=3), name="Ugreen论坛签到")
            self._onlyonce = False
            self.update_config({
                "enabled": self._enabled,
                "notify": self._notify,
                "cookie": self._cookie,
                "cron": self._cron,
                "onlyonce": False,
                "username": self._username,
                "password": self._password,
                "history_days": self._history_days,
                            })
            if self._scheduler.get_jobs():
                self._scheduler.start()
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")

    def sign(self):
        logger.info("开始绿联论坛签到")
        if not self._cookie:
            logger.info("Cookie为空，尝试自动登录")
            ok = self._auto_login()
            if not ok:
                d = {"date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "status": "签到失败", "message": "自动登录失败或未配置用户名密码"}
                self._save_history(d)
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="🔴 绿联论坛签到失败",
                        text=f"⏰ {d['date']}\n❌ {d['message']}"
                    )
                return d
        info = self._fetch_user_profile()
        if not info:
            d = {"date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "status": "签到失败", "message": "无法获取用户资料"}
            self._save_history(d)
            if self._notify:
                self.post_message(
                    mtype=NotificationType.SiteMessage,
                    title="🔴 绿联论坛签到失败",
                    text=f"⏰ {d['date']}\n❌ {d['message']}"
                )
            return d
        last_raw = self.get_data('last_points')
        first_run = last_raw is None
        last_points = 0
        try:
            if isinstance(last_raw, (int, float)):
                last_points = int(last_raw)
        except Exception:
            pass
        current_points = int(info.get('points') or 0)
        delta = current_points - last_points if not first_run else 0
        delta_str = f"+{delta}" if delta > 0 else f"{delta}"
        status = "首次运行（建立基线）" if first_run else ("签到成功" if delta > 0 else "已签到")
        d = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": status,
            "message": ("已记录当前积分作为基线" if first_run else f"积分变化: {delta_str}"),
            "points": current_points,
            "delta": delta
        }
        self.save_data('last_points', current_points)
        self.save_data('last_user_info', info)
        self._save_history(d)
        logger.info(f"签到完成: {status}, 当前积分: {current_points}, 变化: {delta_str}")
        if self._notify:
            name = info.get('username','-')
            uid = info.get('uid', '')
            delta_emoji = '📈' if delta > 0 else ('➖' if delta == 0 else '📉')
            pts_line = f"💰 积分：{current_points}" + (f" ({delta_emoji} {delta_str})" if not first_run else " (首次基线)")
            time_str = d.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 构建美化的通知
            if first_run:
                title = "🎉 绿联论坛首次签到"
                text_parts = [
                    f"👤 用户：{name}",
                    f"🆔 UID：{uid}" if uid else "",
                    pts_line,
                    f"⏰ 时间：{time_str}",
                    "━━━━━━━━━━",
                    "📌 已建立积分基线",
                    "💡 后续签到将显示积分变化"
                ]
            elif delta > 0:
                title = "✅ 绿联论坛签到成功"
                text_parts = [
                    f"👤 用户：{name}",
                    f"🆔 UID：{uid}" if uid else "",
                    pts_line,
                    f"⏰ 时间：{time_str}",
                    "━━━━━━━━━━",
                    f"🎊 本次获得 {delta} 积分！"
                ]
            else:
                title = "✅ 绿联论坛签到"
                text_parts = [
                    f"👤 用户：{name}",
                    f"🆔 UID：{uid}" if uid else "",
                    pts_line,
                    f"⏰ 时间：{time_str}",
                    "━━━━━━━━━━",
                    "📅 今日已完成签到"
                ]
            
            text = "\n".join([p for p in text_parts if p])
            self.post_message(mtype=NotificationType.SiteMessage, title=title, text=text)
        return d

    def _auto_login(self) -> bool:
        try:
            if not (self._username and self._password):
                return False
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context()
                page = ctx.new_page()
                page.goto("https://club.ugnas.com/", wait_until="domcontentloaded")
                try:
                    btn = page.locator("button:has-text('同意')")
                    if btn.count() > 0:
                        btn.first.click()
                        page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                try:
                    ctx.add_cookies([{ "name": "6LQh_2132_BBRules_ok", "value": "1", "domain": "club.ugnas.com", "path": "/", "secure": True, "httpOnly": False, "expires": int(time.time()) + 31536000 }])
                except Exception:
                    pass
                page.goto("https://club.ugnas.com/member.php?mod=logging&action=login", wait_until="domcontentloaded")
                current_url = page.url
                callback_url = {"url": None}
                def _on_resp(resp):
                    try:
                        u = resp.url
                        if "api-zh.ugnas.com/api/oauth/authorize" in u:
                            h = resp.headers
                            loc = h.get('location') or h.get('Location')
                            if loc and "club.ugnas.com/api/ugreen/callback.php" in loc:
                                callback_url["url"] = loc
                    except Exception:
                        pass
                try:
                    page.on("response", _on_resp)
                except Exception:
                    pass
                if "web.ugnas.com" in current_url:
                    try:
                        u_sels = ["input[name='username']", "input[id='username']", "input[type='text']"]
                        p_sels = ["input[name='password']", "input[id='password']", "input[type='password']"]
                        for s in u_sels:
                            if page.query_selector(s):
                                page.fill(s, self._username)
                                break
                        for s in p_sels:
                            if page.query_selector(s):
                                page.fill(s, self._password)
                                break
                        if not any(page.query_selector(s) for s in u_sels):
                            ti = page.query_selector_all("input[type='text'], input[type='email'], input[autocomplete='username'], input[placeholder*='账号'], input[placeholder*='邮箱'], input[placeholder*='手机号']")
                            if ti:
                                ti[0].fill(self._username)
                        if not any(page.query_selector(s) for s in p_sels):
                            pi = page.query_selector_all("input[type='password'], input[autocomplete='current-password']")
                            if pi:
                                pi[0].fill(self._password)
                        btn_oauth = page.query_selector("button[type='submit']") or page.query_selector("input[type='submit']") or page.query_selector("button:has-text('登录')")
                        if not btn_oauth:
                            for sel in ["button:has-text('Login')", "button:has-text('Sign in')", "button:has-text('登入')"]:
                                b = page.query_selector(sel)
                                if b:
                                    btn_oauth = b
                                    break
                        if btn_oauth:
                            btn_oauth.click()
                        else:
                            page.keyboard.press("Enter")
                        page.wait_for_load_state("networkidle", timeout=20000)
                        try:
                            if callback_url["url"]:
                                page.goto(callback_url["url"], wait_until="domcontentloaded")
                            page.wait_for_url(lambda u: "club.ugnas.com" in u, timeout=20000)
                        except Exception:
                            pass
                    except Exception:
                        pass
                u_sels = ["input[name='username']", "input[id='username']", "input[type='text']"]
                p_sels = ["input[name='password']", "input[id='password']", "input[type='password']"]
                for s in u_sels:
                    if page.query_selector(s):
                        page.fill(s, self._username)
                        break
                for s in p_sels:
                    if page.query_selector(s):
                        page.fill(s, self._password)
                        break
                btn = page.query_selector("button[type='submit']") or page.query_selector("input[type='submit']")
                if btn:
                    btn.click()
                else:
                    page.keyboard.press("Enter")
                try:
                    page.wait_for_load_state("networkidle", timeout=12000)
                except Exception:
                    pass
                try:
                    page.goto("https://club.ugnas.com/", wait_until="domcontentloaded")
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                cookies = ctx.cookies()
                try:
                    names = sorted([c.get('name') for c in cookies if c.get('name')])
                except Exception:
                    pass
                try:
                    has_auth = any(c.get('name') == '6LQh_2132_auth' for c in cookies)
                except Exception:
                    pass
                parts = []
                for c in cookies:
                    n, v = c.get('name'), c.get('value')
                    if n and v:
                        parts.append(f"{n}={v}")
                ctx.close()
                browser.close()
                if parts:
                    self._cookie = "; ".join(parts)
                    if '6LQh_2132_BBRules_ok=' not in self._cookie:
                        self._cookie += "; 6LQh_2132_BBRules_ok=1"
                    if not has_auth:
                        logger.warning("自动登录: 未检测到有效登录Cookie")
                    self.update_config({
                        "enabled": self._enabled,
                        "notify": self._notify,
                        "cookie": self._cookie,
                        "cron": self._cron,
                        "onlyonce": self._onlyonce,
                        "username": self._username,
                        "password": self._password,
                        "history_days": self._history_days,
                    })
                    return True
        except Exception as e:
            logger.warning(f"自动登录失败: {e}")
        try:
            if self._oauth_api_login():
                return True
        except Exception as e:
            logger.warning(f"OAuth API 登录失败: {e}")
        return False

    def _fetch_user_profile(self) -> Dict[str, Any]:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cookie': self._cookie
            }
            if '6LQh_2132_auth=' not in (self._cookie or ''):
                try:
                    if self._oauth_api_login():
                        headers['Cookie'] = self._cookie
                except Exception:
                    pass
            uid = self._discover_uid(headers)
            html = ""
            if uid:
                url = f'https://club.ugnas.com/home.php?mod=space&uid={uid}'
                logger.info(f"访问用户主页: {url}")
                resp = requests.get(url, headers=headers, timeout=15)
                html = resp.text or ""
                logger.info(f"获取到HTML长度: {len(html)} 字符")
                # 检查HTML是否包含关键区域
                if '基本资料' in html:
                    logger.info("✓ HTML包含'基本资料'区域")
                else:
                    logger.warning("✗ HTML不包含'基本资料'区域")
                if '统计信息' in html:
                    logger.info("✓ HTML包含'统计信息'区域")
                else:
                    logger.warning("✗ HTML不包含'统计信息'区域")
            else:
                url = 'https://club.ugnas.com/forum.php?mod=forumdisplay&fid=0'
                logger.warning(f"未发现UID，访问论坛首页: {url}")
                resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                html = resp.text or ""
                logger.info(f"获取到HTML长度: {len(html)} 字符")
            
            # 初始化所有字段
            username = "-"
            points = None
            avatar = None
            usergroup = None
            threads = 0
            posts = 0
            friends = 0
            
            # 提取用户名
            try:
                t = re.search(r"<li><em>用户名</em>([^<]+)</li>", html)
                if t:
                    username = t.group(1).strip()
                else:
                    t2 = re.search(r"<h2 class=\"mbn\">基本资料</h2>[\s\S]*?<li><em>用户名</em>([^<]+)</li>", html)
                    if t2:
                        username = t2.group(1).strip()
                if username == "-":
                    t3 = re.search(r"class=\"kmname\">([^<]+)</span>", html)
                    if t3:
                        username = t3.group(1).strip()
            except Exception:
                pass
            
            # 提取积分
            try:
                # 优先从统计信息区域提取
                p = re.search(r"class=\"kmjifen kmico09\"><span>(\d+)</span>积分", html)
                if p:
                    points = int(p.group(1))
                else:
                    p2 = re.search(r"积分[：:]\s*(\d+)", html)
                    if p2:
                        points = int(p2.group(1))
                if points is None:
                    p3 = re.search(r"class=\"xg1\"[^>]*>积分: (\d+)</a>", html)
                    if p3:
                        points = int(p3.group(1))
            except Exception:
                pass
            
            # 提取用户组
            try:
                ug = re.search(r"<li><em>用户组</em>.*?<a[^>]*>([^<]+)</a>", html)
                if ug:
                    usergroup = ug.group(1).strip()
                    logger.info(f"提取到用户组: {usergroup}")
                else:
                    logger.warning("未找到用户组信息")
            except Exception as e:
                logger.error(f"提取用户组失败: {e}")
                pass
            
            # 提取主题数
            try:
                th = re.search(r"<span>(\d+)</span>主题数", html)
                if th:
                    threads = int(th.group(1))
                    logger.info(f"提取到主题数: {threads}")
                else:
                    logger.warning("未找到主题数信息")
            except Exception as e:
                logger.error(f"提取主题数失败: {e}")
                pass
            
            # 提取回帖数
            try:
                po = re.search(r"<span>(\d+)</span>回帖数", html)
                if po:
                    posts = int(po.group(1))
                    logger.info(f"提取到回帖数: {posts}")
                else:
                    logger.warning("未找到回帖数信息")
            except Exception as e:
                logger.error(f"提取回帖数失败: {e}")
                pass
            
            # 提取好友数
            try:
                fr = re.search(r"<span>(\d+)</span>好友数", html)
                if fr:
                    friends = int(fr.group(1))
                    logger.info(f"提取到好友数: {friends}")
                else:
                    logger.warning("未找到好友数信息")
            except Exception as e:
                logger.error(f"提取好友数失败: {e}")
                pass
            
            # 提取头像 - 验证URL有效性
            try:
                # 查找包含user_avatar类的img标签（属性顺序无关）
                avatar_match = re.search(r'<img[^>]*class="user_avatar"[^>]*>', html)
                if avatar_match:
                    img_tag = avatar_match.group(0)
                    # 从img标签中提取src属性
                    src_match = re.search(r'src="([^"]+)"', img_tag)
                    if src_match:
                        avatar_url = src_match.group(1)
                        logger.info(f"提取到头像URL: {avatar_url}")
                        
                        # 验证头像URL是否有效（避免404导致MP显示空白）
                        if '/avatar/' in avatar_url and avatar_url.startswith('http'):
                            try:
                                # 发送HEAD请求检查文件是否存在
                                head_resp = requests.head(avatar_url, timeout=3, allow_redirects=True)
                                if head_resp.status_code == 200:
                                    avatar = avatar_url
                                    logger.info(f"✅ 头像URL有效: {avatar}")
                                else:
                                    avatar = "https://bbs-cn-oss.ugnas.com/bbs/avatar/noavatar.png"
                                    logger.info(f"⚠️ 头像不存在({head_resp.status_code})，使用默认头像")
                            except Exception as e:
                                # 网络错误时仍使用原URL，让浏览器的onerror处理
                                avatar = avatar_url
                                logger.warning(f"⚠️ 头像URL验证失败: {e}，仍使用原URL")
                        else:
                            avatar = avatar_url
                            logger.info(f"✅ 找到头像URL: {avatar}")
                    else:
                        avatar = "https://bbs-cn-oss.ugnas.com/bbs/avatar/noavatar.png"
                        logger.warning("⚠️ img标签中未找到src属性，使用默认头像")
                else:
                    # 如果没找到，使用默认头像
                    avatar = "https://bbs-cn-oss.ugnas.com/bbs/avatar/noavatar.png"
                    logger.warning("⚠️ 未找到user_avatar标签，使用默认头像")
            except Exception as e:
                logger.error(f"❌ 头像提取失败: {e}")
                avatar = "https://bbs-cn-oss.ugnas.com/bbs/avatar/noavatar.png"
            
            logger.info(f"解析结果: 用户名={username}, UID={uid or '未知'}, 积分={points if points is not None else '未知'}, 用户组={usergroup or '未知'}, 主题={threads}, 回帖={posts}, 好友={friends}")
            info = {
                "uid": (uid if uid and uid != '0' else None),
                "username": username,
                "points": points or 0,
                "avatar": avatar,
                "usergroup": usergroup,
                "threads": threads,
                "posts": posts,
                "friends": friends
            }
            self.save_data('last_user_info', info)
            return info
        except Exception as e:
            logger.error(f"获取用户资料失败: {e}")
            return {}

    def _oauth_api_login(self) -> bool:
        try:
            import uuid, base64
            from urllib.parse import quote
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            
            sess = requests.Session()
            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
            headers_json = {
                'User-Agent': ua,
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://web.ugnas.com',
                'Referer': 'https://web.ugnas.com/',
                'Accept-Language': 'zh-CN',
            }
            
            # 1. 获取加密密钥
            r1 = sess.get('https://api-zh.ugnas.com/api/user/v3/sa/encrypt/key', headers=headers_json, timeout=12)
            if r1.status_code != 200:
                logger.warning(f"OAuth API 加密密钥获取失败: {r1.status_code}")
                return False
            
            data = {}
            try:
                data = r1.json()
            except Exception:
                pass
                
            # 新版 API 返回 encryptKey 和 uuid
            # {"code":200,"data":{"encryptKey":"...","uuid":"..."},"msg":"SUCCESS"}
            api_data = data.get('data', {})
            encrypt_key = api_data.get('encryptKey')
            api_uuid = api_data.get('uuid')
            
            if not encrypt_key or not api_uuid:
                logger.warning("OAuth API 未返回有效密钥")
                return False

            # 2. AES 加密 (AES-128-CBC, Key=encryptKey, IV=uuid[:16], Padding=PKCS7)
            def aes_encrypt(text, key_str, iv_str):
                key = key_str.encode('utf-8')
                iv = iv_str[:16].encode('utf-8')
                cipher = AES.new(key, AES.MODE_CBC, iv)
                padded_data = pad(text.encode('utf-8'), AES.block_size)
                encrypted = cipher.encrypt(padded_data)
                return base64.b64encode(encrypted).decode('utf-8')

            try:
                enc_user = aes_encrypt(self._username, encrypt_key, api_uuid)
                enc_pwd = aes_encrypt(self._password, encrypt_key, api_uuid)
            except Exception as e:
                logger.warning(f"OAuth API 加密失败: {e}")
                return False

            # 3. 登录获取 Token
            form_headers = {
                'User-Agent': ua,
                'Accept': 'application/json;charset=UTF-8',
                'Origin': 'https://web.ugnas.com',
                'Referer': 'https://web.ugnas.com/',
                'Accept-Language': 'zh-CN',
            }
            
            # 生成随机 bid/uuid 用于请求参数 (似乎不强制要求与 api_uuid 一致，但为了保险起见，uuid 字段使用 api_uuid)
            req_bid = uuid.uuid4().hex
            
            files = {
                'platform': (None, 'PC'),
                'clientType': (None, 'browser'),
                'osVer': (None, '142.0.0.0'),
                'model': (None, 'Edge/142.0.0.0'),
                'bid': (None, req_bid),
                'alias': (None, 'Edge/142.0.0.0'),
                'grant_type': (None, 'password'),
                'username': (None, enc_user),
                'password': (None, enc_pwd),
                'uuid': (None, api_uuid), # 使用 API 返回的 UUID
            }
            
            r2 = sess.post('https://api-zh.ugnas.com/api/oauth/token', headers=form_headers, files=files, timeout=12)
            if r2.status_code != 200:
                logger.warning(f"OAuth API 获取令牌失败: {r2.status_code}")
                return False
                
            tok = {}
            try:
                tok = r2.json()
            except Exception:
                pass
                
            access_token = tok.get('access_token') or tok.get('data', {}).get('access_token')
            if not access_token:
                logger.warning("OAuth API 未返回有效令牌")
                return False

            # 4. 授权回调
            state = uuid.uuid4().hex[:12]
            authorize_url = (
                'https://api-zh.ugnas.com/api/oauth/authorize?response_type=code&client_id=discuz-client&scope=user_info'
                f'&state={state}&redirect_uri={quote("https://club.ugnas.com/api/ugreen/callback.php")}&access_token={access_token}'
            )
            
            r3 = sess.get(authorize_url, headers=headers_json, allow_redirects=False, timeout=12)
            loc = r3.headers.get('location') or r3.headers.get('Location')
            
            if not loc:
                logger.warning("OAuth API 未获取回调地址")
                return False
                
            # 5. 访问回调地址设置 Cookie
            r4 = sess.get(loc, headers={ 'User-Agent': ua, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'zh-CN' }, timeout=12)
            
            # 刷新站点首页以确保 Cookie 生效
            sess.get('https://club.ugnas.com/', headers={ 'User-Agent': ua, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'zh-CN' }, timeout=12)
            
            # 汇总 Cookie
            cookie_items = []
            try:
                for c in sess.cookies:
                    cookie_items.append(f"{c.name}={c.value}")
            except Exception:
                pass
                
            if cookie_items:
                ck = '; '.join(cookie_items)
                if '6LQh_2132_BBRules_ok=' not in ck:
                    ck += '; 6LQh_2132_BBRules_ok=1'
                self._cookie = ck
                self.update_config({
                    "enabled": self._enabled,
                    "notify": self._notify,
                    "cookie": self._cookie,
                    "cron": self._cron,
                    "onlyonce": self._onlyonce,
                    "username": self._username,
                    "password": self._password,
                    "history_days": self._history_days,
                                    })
                has_auth = ('6LQh_2132_auth=' in ck)
                return has_auth
            return False
        except Exception as e:
            logger.warning(f"OAuth API 登录异常: {e}")
            return False

    def _discover_uid(self, headers: Dict[str, str]) -> Optional[str]:
        try:
            urls = [
                'https://club.ugnas.com/forum.php?mod=forumdisplay&fid=0',
                'https://club.ugnas.com/home.php',
            ]
            for u in urls:
                resp = requests.get(u, headers=headers, timeout=12, allow_redirects=True)
                html = resp.text or ""
                try:
                    self.save_data('ugreen_uid_discover_last', {'url': u, 'status': resp.status_code, 'length': len(html or '')})
                except Exception:
                    pass
                # 顶栏“我的”头像区域链接
                m_nav = re.search(r"id=\"comiis_user\"[\s\S]*?href=\"home\\.php\?mod=space(?:&|&amp;)uid=(\d+)\"", html)
                if m_nav and m_nav.group(1) and m_nav.group(1) != '0':
                    return m_nav.group(1)
                # 用户菜单块中的“访问我的空间”链接
                m_menu = re.search(r"id=\"comiis_user_menu\"[\s\S]*?href=\"home\\.php\?mod=space(?:&|&amp;)uid=(\d+)\"", html)
                if m_menu and m_menu.group(1) and m_menu.group(1) != '0':
                    return m_menu.group(1)
                # 页面脚本中的 discuz_uid 变量
                m1 = re.search(r"discuz_uid\s*=\s*'?(\d+)'?", html)
                if m1 and m1.group(1) and m1.group(1) != '0':
                    return m1.group(1)
                # 通用 space 链接
                m2_all = re.findall(r"home\\.php\?mod=space(?:&|&amp;)uid=(\d+)", html)
                if m2_all:
                    uid_candidates = [x for x in m2_all if x and x != '0']
                    if uid_candidates:
                        return uid_candidates[0]
            return None
        except Exception:
            return None

    def _save_history(self, record: Dict[str, Any]):
        try:
            history = self.get_data('sign_history') or []
            history.append(record)
            tz = pytz.timezone(settings.TZ)
            now = datetime.now(tz)
            keep = []
            for r in history:
                try:
                    dt_str = r.get('date', '')
                    if dt_str:
                        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                        dt = tz.localize(dt) if dt.tzinfo is None else dt
                    else:
                        dt = now
                except Exception as e:
                    logger.debug(f"解析历史记录时间失败: {e}")
                    dt = now
                if (now - dt).days < int(self._history_days):
                    keep.append(r)
            self.save_data('sign_history', keep)
            logger.info(f"历史记录已保存，当前保留 {len(keep)} 条记录")
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
            pass

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            return [{
                "id": "ugreendiscuz",
                "name": "绿联论坛签到",
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
                    {'component': 'VRow', 'content': [
                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'enabled', 'label': '启用插件'}}]},
                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'notify', 'label': '开启通知'}}]},
                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VSwitch', 'props': {'model': 'onlyonce', 'label': '立即运行一次'}}]},
                    ]},
                    {'component': 'VRow', 'content': [
                        {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                            {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'text': '💡 推荐：首次使用请手动获取Cookie并填入下方，避免触发新设备验证。Cookie获取方法：登录论坛后按F12打开开发者工具，在Application > Cookies中找到club.ugnas.com的6LQh_2132_auth字段。'}}
                        ]},
                    ]},
                    {'component': 'VRow', 'content': [
                        {'component': 'VCol', 'props': {'cols': 12}, 'content': [{'component': 'VTextarea', 'props': {'model': 'cookie', 'label': '论坛Cookie', 'placeholder': '6LQh_2132_auth=...; 其它...', 'rows': 3}}]},
                    ]},
                    {'component': 'VRow', 'content': [
                        {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                            {'component': 'VAlert', 'props': {'type': 'warning', 'variant': 'tonal', 'text': '⚠️ 自动登录功能：可能触发新设备手机验证。建议仅在Cookie过期时使用，或直接手动更新Cookie。'}}
                        ]},
                    ]},
                    {'component': 'VRow', 'content': [
                        {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VTextField', 'props': {'model': 'username', 'label': '用户名/手机号', 'placeholder': '用于自动登录（可选）'}}]},
                        {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VTextField', 'props': {'model': 'password', 'label': '密码', 'type': 'password', 'placeholder': '用于自动登录（可选）'}}]},
                    ]},
                    {'component': 'VRow', 'content': [
                        {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VCronField', 'props': {'model': 'cron', 'label': '签到周期'}}]},
                        {'component': 'VCol', 'props': {'cols': 12, 'md': 6}, 'content': [{'component': 'VTextField', 'props': {'model': 'history_days', 'label': '历史保留天数', 'type': 'number', 'placeholder': '30'}}]},
                    ]},
                ]
            }
        ], {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "cookie": "",
            "cron": "0 8 * * *",
            "username": "",
            "password": "",
            "history_days": 30,
        }

    def get_page(self) -> List[dict]:
        """构建插件详情页面"""
        info = self.get_data('last_user_info') or {}
        historys = self.get_data('sign_history') or []
        
        # 空状态处理
        if not historys:
            return [
                {
                    'component': 'VAlert',
                    'props': {
                        'type': 'info',
                        'variant': 'tonal',
                        'text': '暂无签到记录，请先配置Cookie并启用插件后运行一次签到',
                        'class': 'mb-2'
                    }
                }
            ]
        
        historys = sorted(historys, key=lambda x: x.get("date", ""), reverse=True)
        card = []
        if info:
            name = info.get('username', '-')
            avatar = info.get('avatar')
            points = info.get('points', 0)
            usergroup = info.get('usergroup', '')
            threads = info.get('threads', 0)
            posts = info.get('posts', 0)
            friends = info.get('friends', 0)
            uid_val = info.get('uid', '')
            latest = historys[0] if historys else {}
            latest_status = latest.get('status', '-')
            latest_delta = latest.get('delta', 0)
            latest_date = latest.get('date', '-')
            latest_color = 'success' if any(kw in str(latest_status) for kw in ['成功', '已签到']) else ('warning' if '基线' in str(latest_status) else 'error')
            latest_delta_color = 'success' if (latest_delta or 0) > 0 else ('grey' if (latest_delta or 0) == 0 else 'error')
            latest_delta_emoji = '📈' if (latest_delta or 0) > 0 else ('➖' if (latest_delta or 0) == 0 else '📉')
            
            card = [
                {
                    'component': 'VCard',
                    'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-4'},
                    'content': [
                        {'component': 'VCardTitle', 'props': {'class': 'text-h5 font-weight-bold'}, 'text': '👤 绿联论坛用户信息'},
                        {'component': 'VCardText', 'content': [
                            {'component': 'VRow', 'props': {'align': 'center'}, 'content': [
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 2}, 'content': [
                                    ({'component': 'VAvatar', 'props': {'size': 96, 'class': 'mx-auto'}, 'content': [{'component': 'VImg', 'props': {'src': avatar}}]} if avatar else {'component': 'VAvatar', 'props': {'size': 96, 'color': 'grey-lighten-2', 'class': 'mx-auto'}, 'text': name[:1] if name else '?'})
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12, 'md': 10}, 'content': [
                                    {'component': 'VRow', 'props': {'class': 'mb-3'}, 'content': [
                                        {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                            {'component': 'div', 'props': {'class': 'text-h5 font-weight-bold'}, 'text': name},
                                            {'component': 'div', 'props': {'class': 'text-subtitle-2 text-medium-emphasis mt-1'}, 'text': f"🆔 UID: {uid_val}" + (f" | 👥 {usergroup}" if usergroup else "")}
                                        ]}
                                    ]},
                                    {'component': 'VRow', 'content': [
                                        {'component': 'VCol', 'props': {'cols': 6, 'sm': 3}, 'content': [
                                            {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'class': 'ma-1', 'color': 'amber-darken-2'}, 'text': f'💰 积分 {points}'}
                                        ]},
                                        {'component': 'VCol', 'props': {'cols': 6, 'sm': 3}, 'content': [
                                            {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'class': 'ma-1', 'color': 'blue'}, 'text': f'📝 主题 {threads}'}
                                        ]},
                                        {'component': 'VCol', 'props': {'cols': 6, 'sm': 3}, 'content': [
                                            {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'class': 'ma-1', 'color': 'green'}, 'text': f'💬 回帖 {posts}'}
                                        ]},
                                        {'component': 'VCol', 'props': {'cols': 6, 'sm': 3}, 'content': [
                                            {'component': 'VChip', 'props': {'size': 'large', 'variant': 'tonal', 'class': 'ma-1', 'color': 'purple'}, 'text': f'👥 好友 {friends}'}
                                        ]}
                                    ]}
                                ]},
                                {'component': 'VCol', 'props': {'cols': 12}, 'content': [
                                    {'component': 'VDivider'},
                                    {'component': 'VRow', 'props': {'class': 'mt-3'}, 'content': [
                                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                            {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated', 'color': latest_color}, 'text': f'状态 {latest_status}'}
                                        ]},
                                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                            {'component': 'VChip', 'props': {'size': 'default', 'variant': 'elevated', 'color': latest_delta_color}, 'text': f'{latest_delta_emoji} {("+" + str(latest_delta)) if (latest_delta or 0) > 0 else str(latest_delta)}'}
                                        ]},
                                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [
                                            {'component': 'VChip', 'props': {'size': 'default', 'variant': 'tonal'}, 'text': f'更新时间 {latest_date}'}
                                        ]}
                                    ]}
                                ]}
                            ]}
                        ]}
                    ]
                }
            ]
        rows = []
        for h in historys:
            status_text = h.get('status', '未知')
            # 判断状态颜色
            is_success = any(kw in status_text for kw in ['成功', '已签到', '基线'])
            status_color = 'success' if is_success else 'error'
            
            # 积分变化
            delta = h.get('delta', 0)
            delta_color = 'success' if delta > 0 else ('grey' if delta == 0 else 'error')
            delta_text = f"+{delta}" if delta > 0 else str(delta)
            delta_emoji = '📈' if delta > 0 else ('➖' if delta == 0 else '📉')
            
            rows.append({
                'component': 'tr',
                'content': [
                    {'component': 'td', 'props': {'class': 'text-caption'}, 'text': h.get('date', '')},
                    {'component': 'td', 'content': [{'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': status_color}, 'text': status_text}]},
                    {'component': 'td', 'content': [{'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': delta_color}, 'text': f"{delta_emoji} {delta_text}"}]},
                    {'component': 'td', 'props': {'class': 'text-caption'}, 'text': h.get('message', '-')},
                ]
            })
        
        table = [
            {
                'component': 'VCard',
                'props': {'variant': 'elevated', 'elevation': 2, 'rounded': 'lg', 'class': 'mb-4'},
                'content': [
                    {'component': 'VCardTitle', 'props': {'class': 'text-h6 font-weight-bold'}, 'text': f'📊 绿联论坛签到历史 (近{len(rows)}条)'},
                    {'component': 'VCardText', 'content': [
                        {'component': 'VTable', 'props': {'hover': True, 'density': 'comfortable'}, 'content': [
                            {'component': 'thead', 'content': [{'component': 'tr', 'content': [
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '时间'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '状态'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '积分变化'},
                                {'component': 'th', 'props': {'class': 'text-body-2'}, 'text': '消息'},
                            ]}]},
                            {'component': 'tbody', 'content': rows}
                        ]}
                    ]}
                ]
            }
        ]
        return card + table

    def stop_service(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        return True

    def get_command(self) -> List[Dict[str, Any]]: return []
    def get_api(self) -> List[Dict[str, Any]]: return []
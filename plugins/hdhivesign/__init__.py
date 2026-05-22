"""
影巢签到插件
版本: 1.5.0
作者: madrays
功能:
- 自动完成影巢(HDHive)每日签到
- 支持使用用户名密码依托 CloakBrowser/Playwright 以规避最新的指纹校验
- 支持签到失败自动进行环境重制与鉴权
- 提供详细签到信息和赌狗签到模式

修改记录:
- v1.5.0: 适配 MoviePilot v2.12.0 CloakBrowser 内核，优先复用新浏览器缓存目录并兼容旧版 Playwright
- v1.4.0: 全面重构底层签到与接口通讯，采用内置无头浏览器规避 Next.js 站点保护；修复配置项遗失；修正无头像时的缺省展示方案
- v1.3.0: 优化用户信息抓取机制，修复多项问题
- v1.1.0: 域名改为可配置，统一API拼接(Referer/Origin/接口)，精简日志
- v1.0.0: 初始版本，基于影巢网站结构实现自动签到
"""
import time
import requests
import re
import json
from datetime import datetime, timedelta

import jwt
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger
from app.schemas import NotificationType
from app.utils.http import RequestUtils

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from .playwright_helper import HDHivePlaywrightClient
    PLAYWRIGHT_READY = True
    IMPORT_ERROR = ""
except Exception as e:
    HDHivePlaywrightClient = None
    PLAYWRIGHT_READY = False
    IMPORT_ERROR = str(e)

class HdhiveSign(_PluginBase):
    # 插件名称
    plugin_name = "影巢签到"
    # 插件描述
    plugin_desc = "自动完成影巢(HDHive)每日签到/赌狗签到，支持失败重试和历史记录"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/hdhive.ico"
    # 插件版本
    plugin_version = "1.5.0"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "hdhivesign_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _cookie = None
    _notify = False
    _onlyonce = False
    _gamble = False
    _cron = None
    _max_retries = 3  # 最大重试次数
    _retry_interval = 30  # 重试间隔(秒)
    _history_days = 30  # 历史保留天数
    _manual_trigger = False
    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None
    _current_trigger_type = None  # 保存当前执行的触发类型

    # 影巢站点配置（域名可配置）
    _base_url = "https://hdhive.com"
    _site_url = f"{_base_url}/"
    _signin_api = f"{_base_url}/api/customer/user/checkin"
    _user_info_api = f"{_base_url}/api/customer/user/info"
    _login_api_candidates = [
        "/api/customer/user/login",
        "/api/customer/auth/login",
    ]
    _login_page = "/login"

    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()

        logger.info("============= hdhivesign 初始化 =============")
        try:
            if config:
                self._enabled = config.get("enabled")
                self._cookie = config.get("cookie")
                self._notify = config.get("notify")
                self._cron = config.get("cron")
                self._onlyonce = config.get("onlyonce")
                self._gamble = config.get("gamble", False)
                # 新增：站点地址配置
                self._base_url = (config.get("base_url") or self._base_url or "").rstrip("/") or "https://hdhive.com"
                # 基于 base_url 统一构建接口地址
                self._site_url = f"{self._base_url}/"
                self._signin_api = f"{self._base_url}/api/customer/user/checkin"
                self._user_info_api = f"{self._base_url}/api/customer/user/info"
                self._max_retries = int(config.get("max_retries", 3))
                self._retry_interval = int(config.get("retry_interval", 30))
                self._history_days = int(config.get("history_days", 30))
                self._username = (config.get("username") or "").strip()
                self._password = (config.get("password") or "").strip()
                logger.info(f"影巢签到插件已加载，配置：enabled={self._enabled}, notify={self._notify}, cron={self._cron}")
            
            # 清理所有可能的延长重试任务
            self._clear_extended_retry_tasks()
            
            if self._onlyonce:
                logger.info("执行一次性签到")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._manual_trigger = True
                self._scheduler.add_job(func=self.sign, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="影巢签到")
                self._onlyonce = False
                self.update_config({
                    "onlyonce": False,
                    "gamble": self._gamble,
                    "enabled": self._enabled,
                    "cookie": self._cookie,
                    "notify": self._notify,
                    "cron": self._cron,
                    "base_url": self._base_url,
                    "max_retries": self._max_retries,
                    "retry_interval": self._retry_interval,
                    "history_days": self._history_days,
                    "username": getattr(self, "_username", ""),
                    "password": getattr(self, "_password", "")
                })

                # 启动任务
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()

        except Exception as e:
            logger.error(f"hdhivesign初始化错误: {str(e)}", exc_info=True)

    def sign(self, retry_count=0, extended_retry=0):
        """
        执行签到，支持失败重试。
        参数：
            retry_count: 常规重试计数
            extended_retry: 延长重试计数（0=首次尝试, 1=第一次延长重试, 2=第二次延长重试）
        """
        # 设置执行超时保护
        start_time = datetime.now()
        sign_timeout = 300  # 限制签到执行最长时间为5分钟
        
        # 保存当前执行的触发类型
        self._current_trigger_type = "手动触发" if self._is_manual_trigger() else "定时触发"
        
        # 如果是定时任务且不是重试，检查是否有正在运行的延长重试任务
        if retry_count == 0 and extended_retry == 0 and not self._is_manual_trigger():
            if self._has_running_extended_retry():
                logger.warning("检测到有正在运行的延长重试任务，跳过本次执行")
                return {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "跳过: 有正在进行的重试任务"
                }
        
        logger.info("开始影巢签到")
        logger.debug(f"参数: retry={retry_count}, ext_retry={extended_retry}, trigger={self._current_trigger_type}")

        notification_sent = False  # 标记是否已发送通知
        sign_dict = None
        sign_status = None  # 记录签到状态

        # 根据重试情况记录日志
        if retry_count > 0:
            logger.debug(f"常规重试: 第{retry_count}次")
        if extended_retry > 0:
            logger.debug(f"延长重试: 第{extended_retry}次")
        
        try:
            if not self._is_manual_trigger() and self._is_already_signed_today():
                logger.info("根据历史记录，今日已成功签到，跳过本次执行")
                
                # 创建跳过记录
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "跳过: 今日已签到",
                }
                
                # 获取最后一次成功签到的记录信息
                history = self.get_data('sign_history') or []
                today = datetime.now().strftime('%Y-%m-%d')
                today_success = [
                    record for record in history 
                    if record.get("date", "").startswith(today) 
                    and record.get("status") in ["签到成功", "已签到"]
                ]
                
                # 添加最后成功签到记录的详细信息
                if today_success:
                    last_success = max(today_success, key=lambda x: x.get("date", ""))
                    # 复制积分信息到跳过记录
                    sign_dict.update({
                        "message": last_success.get("message"),
                        "points": last_success.get("points"),
                        "days": last_success.get("days")
                    })
                
                # 发送通知 - 通知用户已经签到过了
                if self._notify:
                    last_sign_time = self._get_last_sign_time()
                    
                    title = "【ℹ️ 影巢重复签到】"
                    text = (
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"📍 方式：{self._current_trigger_type}\n"
                        f"ℹ️ 状态：今日已完成签到 ({last_sign_time})\n"
                    )
                    
                    # 如果有积分信息，添加到通知中
                    if "message" in sign_dict and sign_dict["message"]:
                        text += (
                            f"━━━━━━━━━━\n"
                            f"📊 签到信息\n"
                            f"💬 消息：{sign_dict.get('message', '—')}\n"
                            f"🎁 奖励：{sign_dict.get('points', '—')}\n"
                            f"📆 天数：{sign_dict.get('days', '—')}\n"
                        )
                    
                    text += f"━━━━━━━━━━"
                    
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title=title,
                        text=text
                    )
                try:
                    cookies = {}
                    if self._cookie:
                        for cookie_item in self._cookie.split(';'):
                            if '=' in cookie_item:
                                name, value = cookie_item.strip().split('=', 1)
                                cookies[name] = value
                    token = cookies.get('token')
                    if token:
                        self._fetch_user_info(cookies, token)
                except Exception:
                    pass
                
                return sign_dict
            
            if not self._cookie:
                # 尝试自动登录获取 Cookie
                new_cookie = self._auto_login()
                if new_cookie:
                    self._cookie = new_cookie
                    self.update_config({
                        "enabled": self._enabled,
                        "notify": self._notify,
                        "gamble": getattr(self, "_gamble", False),
                        "cron": self._cron,
                        "cookie": self._cookie,
                        "base_url": self._base_url,
                        "max_retries": self._max_retries,
                        "retry_interval": self._retry_interval,
                        "history_days": self._history_days,
                        "username": getattr(self, "_username", ""),
                        "password": getattr(self, "_password", ""),
                    })
                    logger.info("已通过自动登录获取新Cookie")
                else:
                    logger.error("未配置Cookie且自动登录失败")
                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": "签到失败: 未配置Cookie",
                    }
                    self._save_sign_history(sign_dict)
                    
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【影巢签到失败】",
                            text="❌ 未配置Cookie，且自动登录失败，请在设置中添加Cookie或用户名密码"
                        )
                        notification_sent = True
                    return sign_dict
            
            logger.info("执行签到...")

            try:
                ensured = self._ensure_valid_cookie()
                if ensured:
                    self._cookie = ensured
                    self.update_config({
                        "enabled": self._enabled,
                        "notify": self._notify,
                        "gamble": getattr(self, "_gamble", False),
                        "cron": self._cron,
                        "cookie": self._cookie,
                        "base_url": self._base_url,
                        "max_retries": self._max_retries,
                        "retry_interval": self._retry_interval,
                        "history_days": self._history_days,
                        "username": getattr(self, "_username", ""),
                        "password": getattr(self, "_password", ""),
                    })
            except Exception:
                pass

            try:
                cookies = {}
                if self._cookie:
                    for cookie_item in self._cookie.split(';'):
                        if '=' in cookie_item:
                            name, value = cookie_item.strip().split('=', 1)
                            cookies[name] = value
                token = cookies.get('token')
                if token:
                    logger.info("尝试预拉取用户信息用于页面展示")
                    self._fetch_user_info(cookies, token)
            except Exception:
                pass
            
            state, message = self._signin_base()
            
            if state:
                logger.debug(f"签到API消息: {message}")
                
                if "已经签到" in message or "签到过" in message:
                    sign_status = "已签到"
                else:
                    sign_status = "签到成功"
                
                logger.debug(f"签到状态: {sign_status}")

                # --- 核心修复：插件自身逻辑计算连续签到天数 ---
                today_str = datetime.now().strftime('%Y-%m-%d')
                last_date_str = self.get_data('last_success_date')
                consecutive_days = self.get_data('consecutive_days', 0)

                if last_date_str == today_str:
                    # 当天重复运行，天数不变
                    pass
                elif last_date_str == (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'):
                    # 连续签到，天数+1
                    consecutive_days += 1
                else:
                    # 签到中断或首次签到，重置为1
                    consecutive_days = 1
                
                # 更新连续签到数据
                self.save_data('consecutive_days', consecutive_days)
                self.save_data('last_success_date', today_str)

                # 创建签到记录
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": sign_status,
                    "message": message,
                    "days": consecutive_days  # 使用计算出的天数
                }
                
                # 解析奖励积分
                points_match = re.search(r'获得 (\d+) 积分', message)
                sign_dict['points'] = int(points_match.group(1)) if points_match else "—"

                self._save_sign_history(sign_dict)
                self._send_sign_notification(sign_dict)
                return sign_dict
            else:
                # 签到失败, a real failure that needs retry
                logger.error(f"影巢签到失败: {message}")

                # 检测鉴权失败，尝试自动登录刷新 Cookie 后重试一次
                if any(k in (message or "") for k in ["未配置Cookie", "缺少'token'", "未授权", "Unauthorized", "token", "csrf", "登录已过期", "过期", "expired", "认证失效", "Cookie 无效", "登录页", "重定向到登录页"]):
                    logger.info("检测到Cookie或鉴权问题，尝试自动登录刷新Cookie后重试一次")
                    new_cookie = self._auto_login()
                    if new_cookie:
                        self._cookie = new_cookie
                        self.update_config({
                            "enabled": self._enabled,
                            "notify": self._notify,
                            "gamble": getattr(self, "_gamble", False),
                            "cron": self._cron,
                            "cookie": self._cookie,
                            "base_url": self._base_url,
                            "max_retries": self._max_retries,
                            "retry_interval": self._retry_interval,
                            "history_days": self._history_days,
                            "username": getattr(self, "_username", ""),
                            "password": getattr(self, "_password", ""),
                        })
                        logger.info("自动登录成功，使用新Cookie重试签到")
                        state2, message2 = self._signin_base()
                        if state2:
                            sign_status = "签到成功" if "签到" in (message2 or "") and "已" not in message2 else "已签到"
                            sign_dict = {
                                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                                "status": sign_status,
                                "message": message2,
                            }
                            # 解析奖励积分
                            points_match = re.search(r'获得 (\d+) 积分', message2 or "")
                            sign_dict['points'] = int(points_match.group(1)) if points_match else "—"
                            self._save_sign_history(sign_dict)
                            self._send_sign_notification(sign_dict)
                            return sign_dict
                
                # 暂不保存失败记录，视重试策略决定是否写入
                
                # 常规重试逻辑
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【影巢签到重试】",
                            text=f"❗ 签到失败: {message}，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)
                
                # 所有重试都失败
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": f"签到失败: {message}",
                    "message": message
                }
                self._save_sign_history(sign_dict)
                
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 影巢签到失败】",
                        text=f"❌ 签到失败: {message}，所有重试均已失败"
                    )
                    notification_sent = True
                return sign_dict
        
        except requests.RequestException as req_exc:
            # 网络请求异常处理
            logger.error(f"网络请求异常: {str(req_exc)}")
            # 添加执行超时检查
            if (datetime.now() - start_time).total_seconds() > sign_timeout:
                logger.error("签到执行时间超过5分钟，执行超时")
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 执行超时",
                }
                self._save_sign_history(sign_dict)
                
                if self._notify and not notification_sent:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 影巢签到失败】",
                        text="❌ 签到执行超时，已强制终止，请检查网络或站点状态"
                    )
                    notification_sent = True
                
                return sign_dict
        except Exception as e:
            logger.error(f"影巢 签到异常: {str(e)}", exc_info=True)
            sign_dict = {
                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": f"签到失败: {str(e)}",
            }
            self._save_sign_history(sign_dict)
            
            if self._notify and not notification_sent:
                self.post_message(
                    mtype=NotificationType.SiteMessage,
                    title="【❌ 影巢签到失败】",
                    text=f"❌ 签到异常: {str(e)}"
                )
                notification_sent = True
            
            return sign_dict

    def _signin_base(self) -> Tuple[bool, str]:
        """
        基于 Playwright 的 Server Action 签到实现
        """
        try:
            if not self._cookie:
                return False, "未配置Cookie"
            
            if HDHivePlaywrightClient is None:
                return False, f"底层浏览器依赖加载失败，请确保 MoviePilot 环境正常并在后台安装了插件依赖。错误信息: {IMPORT_ERROR}"
                
            client = HDHivePlaywrightClient(base_url=self._base_url, headless=True)
            success, message = client.checkin(cookie_str=self._cookie, gamble=getattr(self, "_gamble", False))
            
            # 无论成功失败，尝试顺便获取用户信息更新展示
            try:
                cookies = {}
                for cookie_item in self._cookie.split(';'):
                    if '=' in cookie_item:
                        name, value = cookie_item.strip().split('=', 1)
                        cookies[name] = value
                token = cookies.get('token')
                if token:
                    self._fetch_user_info(cookies, token)
            except Exception:
                pass
                
            return success, message

        except Exception as e:
            logger.error(f"签到流程发生未知异常", exc_info=True)
            return False, f'签到异常: {str(e)}'

    def _save_sign_history(self, sign_data):
        """
        保存签到历史记录
        """
        try:
            # 读取现有历史
            history = self.get_data('sign_history') or []

            # 确保日期格式正确
            if "date" not in sign_data:
                sign_data["date"] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

            history.append(sign_data)

            # 清理旧记录
            retention_days = int(self._history_days)
            now = datetime.now()
            valid_history = []

            for record in history:
                try:
                    # 尝试将记录日期转换为datetime对象
                    record_date = datetime.strptime(record["date"], '%Y-%m-%d %H:%M:%S')
                    # 检查是否在保留期内
                    if (now - record_date).days < retention_days:
                        valid_history.append(record)
                except (ValueError, KeyError):
                    # 如果记录日期格式不正确，尝试修复
                    logger.warning(f"历史记录日期格式无效: {record.get('date', '无日期')}")
                    # 添加新的日期并保留记录
                    record["date"] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    valid_history.append(record)

            # 保存历史
            self.save_data(key="sign_history", value=valid_history)
            logger.info(f"保存签到历史记录，当前共有 {len(valid_history)} 条记录")

        except Exception as e:
            logger.error(f"保存签到历史记录失败: {str(e)}", exc_info=True)

    def _fetch_user_info(self, cookies: Dict[str, str], token: str) -> Optional[dict]:
        try:
            referer = self._site_url
            try:
                decoded_token = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
                user_id = decoded_token.get('sub')
                if user_id:
                    referer = f"{self._base_url}/user/{user_id}"
            except Exception:
                pass
            info = {
                'id': None,
                'nickname': None,
                'avatar_url': None,
                'created_at': None,
                'points': None,
                'signin_days_total': None,
                'warnings_nums': None,
            }
            if True:
                try:
                    rsc_headers = {
                        'User-Agent': settings.USER_AGENT,
                        'Accept': 'text/x-component',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Origin': self._base_url,
                        'Referer': referer,
                        'rsc': '1',
                    }
                    rsc_url = referer
                    rsc_resp = requests.get(rsc_url, headers=rsc_headers, cookies=cookies, proxies=settings.PROXY, timeout=30, verify=False)
                    logger.info(f"RSC 用户页状态码: {getattr(rsc_resp,'status_code','unknown')} CT: {getattr(rsc_resp.headers,'get',lambda k:'' )('Content-Type')}")
                    rsc_text = rsc_resp.text or ''
                    logger.info(f"RSC 网页文本长度: {len(rsc_text)}")
                    import re as _re
                    m_nick = _re.search(r'"nickname":"([^"]+)"', rsc_text)
                    m_points = _re.search(r'"points":(\d+)', rsc_text)
                    m_days = _re.search(r'"signin_days_total":(\d+)', rsc_text)
                    m_avatar = _re.search(r'"(?:avatar_url|gravatar_url)":"([^"]+)"', rsc_text)
                    m_created = _re.search(r'"created_at":"([^"]+)"', rsc_text)
                    if m_nick:
                        info['nickname'] = m_nick.group(1)
                    if m_points:
                        info['points'] = int(m_points.group(1))
                    if m_days:
                        info['signin_days_total'] = int(m_days.group(1))
                    if m_avatar:
                        raw_url = m_avatar.group(1)
                        if raw_url.strip() and raw_url != "null":
                            info['avatar_url'] = raw_url.replace('\\/', '/').replace('\\u0026', '&')
                    if m_created:
                        info['created_at'] = m_created.group(1)
                    if (not info.get('nickname') or info.get('points') is None or info.get('signin_days_total') is None) and '"user":' in rsc_text:
                        user_json = self._extract_rsc_object(rsc_text, 'user')
                        if user_json:
                            try:
                                obj = json.loads(user_json)
                                info['id'] = obj.get('id') or info.get('id')
                                info['nickname'] = obj.get('nickname') or info.get('nickname')
                                info['avatar_url'] = obj.get('avatar_url') or info.get('avatar_url')
                                info['created_at'] = obj.get('created_at') or info.get('created_at')
                                meta = obj.get('user_meta') or {}
                                if isinstance(meta, dict):
                                    if meta.get('points') is not None:
                                        info['points'] = meta.get('points')
                                    if meta.get('signin_days_total') is not None:
                                        info['signin_days_total'] = meta.get('signin_days_total')
                            except Exception:
                                pass
                except Exception:
                    pass
            logger.info(f"RSC解析完毕，获得的数据结果: {info}")
            self.save_data('hdhive_user_info', info)
            return info
        except Exception as e:
            logger.warning(f"获取用户信息失败: {e}")
            return None

    def _extract_rsc_object(self, text: str, key: str) -> Optional[str]:
        try:
            marker = f'"{key}":'
            idx = text.find(marker)
            if idx == -1:
                return None
            brace_idx = text.find('{', idx + len(marker))
            if brace_idx == -1:
                return None
            depth = 0
            i = brace_idx
            in_str = False
            prev = ''
            while i < len(text):
                ch = text[i]
                if ch == '"' and prev != '\\':
                    in_str = not in_str
                if not in_str:
                    if ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            segment = text[brace_idx:i+1]
                            return segment
                prev = ch
                i += 1
            return None
        except Exception:
            return None

    def _send_sign_notification(self, sign_dict):
        """
        发送签到通知
        """
        if not self._notify:
            return

        status = sign_dict.get("status", "未知")
        message = sign_dict.get("message", "—")
        points = sign_dict.get("points", "—")
        days = sign_dict.get("days", "—")
        sign_time = sign_dict.get("date", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        user = self.get_data('hdhive_user_info') or {}
        nickname = user.get('nickname') or '—'
        user_points = user.get('points') if user.get('points') is not None else '—'
        signin_days_total = user.get('signin_days_total') if user.get('signin_days_total') is not None else '—'
        created_at = user.get('created_at') or '—'

        # 检查奖励信息是否为空
        info_missing = message == "—" and points == "—" and days == "—"

        # 获取触发方式
        trigger_type = self._current_trigger_type

        # 构建通知文本
        if "签到成功" in status:
            title = "【✅ 影巢签到成功】"

            if info_missing:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"⚠️ 详细信息获取失败，请手动查看\n"
                    f"━━━━━━━━━━\n"
                    f"👤 用户信息\n"
                    f"昵称：{nickname}\n"
                    f"积分：{user_points}\n"
                    f"累计签到天数（站点）：{signin_days_total}\n"
                    f"加入时间：{created_at}\n"
                    f"━━━━━━━━━━"
                )
            else:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"━━━━━━━━━━\n"
                    f"📊 签到信息\n"
                    f"💬 消息：{message}\n"
                    f"🎁 奖励：{points}\n"
                    f"📆 天数：{days}\n"
                    f"━━━━━━━━━━\n"
                    f"👤 用户信息\n"
                    f"昵称：{nickname}\n"
                    f"积分：{user_points}\n"
                    f"累计签到天数（站点）：{signin_days_total}\n"
                    f"加入时间：{created_at}\n"
                    f"━━━━━━━━━━"
                )
        elif "已签到" in status:
            title = "【ℹ️ 影巢重复签到】"

            if info_missing:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"ℹ️ 说明：今日已完成签到\n"
                    f"⚠️ 详细信息获取失败，请手动查看\n"
                    f"━━━━━━━━━━\n"
                    f"👤 用户信息\n"
                    f"昵称：{nickname}\n"
                    f"积分：{user_points}\n"
                    f"累计签到天数（站点）：{signin_days_total}\n"
                    f"加入时间：{created_at}\n"
                    f"━━━━━━━━━━"
                )
            else:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"ℹ️ 说明：今日已完成签到\n"
                    f"━━━━━━━━━━\n"
                    f"📊 签到信息\n"
                    f"💬 消息：{message}\n"
                    f"🎁 奖励：{points}\n"
                    f"📆 天数：{days}\n"
                    f"━━━━━━━━━━\n"
                    f"👤 用户信息\n"
                    f"昵称：{nickname}\n"
                    f"积分：{user_points}\n"
                    f"累计签到天数（站点）：{signin_days_total}\n"
                    f"加入时间：{created_at}\n"
                    f"━━━━━━━━━━"
                )
        else:
            title = "【❌ 影巢签到失败】"
            text = (
                f"📢 执行结果\n"
                f"━━━━━━━━━━\n"
                f"🕐 时间：{sign_time}\n"
                f"📍 方式：{trigger_type}\n"
                f"❌ 状态：{status}\n"
                f"━━━━━━━━━━\n"
                f"💡 可能的解决方法\n"
                f"• 检查Cookie是否有效\n"
                f"• 确认代理连接正常\n"
                f"• 查看站点是否正常访问\n"
                f"━━━━━━━━━━"
            )

        # 发送通知
        self.post_message(
            mtype=NotificationType.SiteMessage,
            title=title,
            text=text
        )

    def get_state(self) -> bool:
        logger.info(f"hdhivesign状态: {self._enabled}")
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")
            return [{
                "id": "hdhivesign",
                "name": "影巢签到",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.sign,
                "kwargs": {}
            }]
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        返回插件配置的表单
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify',
                                            'label': '开启通知',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'gamble',
                                            'label': '赌狗签到',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'onlyonce',
                                            'label': '立即运行一次',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cookie',
                                            'label': '站点Cookie',
                                            'placeholder': '请输入影巢站点Cookie值'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'username',
                                            'label': '用户名/邮箱（用于自动登录）',
                                            'placeholder': '例如：email@example.com'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'password',
                                            'label': '密码（用于自动登录）',
                                            'placeholder': '请输入密码',
                                            'type': 'password'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'base_url',
                                            'label': '站点地址',
                                            'placeholder': '例如：https://hdhive.online 或新域名',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '签到周期'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'max_retries',
                                            'label': '最大重试次数',
                                            'type': 'number',
                                            'placeholder': '3'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'retry_interval',
                                            'label': '重试间隔(秒)',
                                            'type': 'number',
                                            'placeholder': '30'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'history_days',
                                            'label': '历史保留天数',
                                            'type': 'number',
                                            'placeholder': '30'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '【使用说明】\n1. 推荐：只需在此处填写您的影巢“用户名”与“密码”，插件将通过内置无头浏览器自动获取权限进行签到。\n2. 亦可手动登录影巢站点，提取完整的 Cookie 字符串进行设置。\n\n⚠️ 如果您开启了"赌狗签到"，签到时将自动参与概率奖池。基于 Playwright 的底层自动化重构将为您自动规避验证失效。'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "notify": True,
            "gamble": False,
            "onlyonce": False,
            "cookie": "",
            "base_url": "https://hdhive.com",
            "cron": "0 8 * * *",
            "max_retries": 3,
            "retry_interval": 30,
            "history_days": 30,
            "username": "",
            "password": ""
        }

    def get_page(self) -> List[dict]:
        """
        构建插件详情页面，展示签到历史 (完全参照 qmjsign)
        """
        historys = self.get_data('sign_history') or []
        user = self.get_data('hdhive_user_info') or {}
        consecutive_days = self.get_data('consecutive_days') or 0

        info_card = []
        if user:
            avatar = user.get('avatar_url') or f'{self._base_url}/images/default-avatar.webp'
            nickname = user.get('nickname') or '—'
            points = user.get('points') if user.get('points') is not None else '—'
            signin_days_total = user.get('signin_days_total') if user.get('signin_days_total') is not None else '—'
            created_at = user.get('created_at') or '—'
            info_card = [{
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'd-flex align-center justify-space-between'},
                        'content': [
                            {
                                'component': 'div',
                                'content': [
                                    {'component': 'span', 'props': {'class': 'text-h6'}, 'text': '👤 影巢用户信息'},
                                    {'component': 'div', 'props': {'class': 'text-caption'}, 'text': f'加入时间：{created_at}'}
                                ]
                            },
                            {'component': 'VAvatar', 'props': {'size': 64}, 'content': [{'component': 'img', 'props': {'src': avatar, 'alt': nickname}}]}
                        ]
                    },
                    {'component': 'VDivider'},
                    {
                        'component': 'VCardText',
                        'content': [
                            {
                                'component': 'VRow',
                                'content': [
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VChip', 'props': {'variant': 'elevated', 'color': 'primary', 'class': 'mb-2'}, 'text': f'用户：{nickname}'}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VChip', 'props': {'variant': 'elevated', 'color': 'amber-darken-2', 'class': 'mb-2'}, 'text': f'积分：{points}'}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VChip', 'props': {'variant': 'elevated', 'color': 'success', 'class': 'mb-2'}, 'text': f'累计签到天数（站点）：{signin_days_total}'}]},
                                    {'component': 'VCol', 'props': {'cols': 12, 'md': 3}, 'content': [{'component': 'VChip', 'props': {'variant': 'elevated', 'color': 'cyan-darken-2', 'class': 'mb-2'}, 'text': f'连续签到天数（插件）：{consecutive_days}'}]},
                                ]
                            },
                            {'component': 'VAlert', 'props': {'type': 'info', 'variant': 'tonal', 'class': 'mt-2', 'text': '注：累计签到天数来自站点数据；插件统计的是连续天数，两者可能不同'}},
                        ]
                    }
                ]
            }]

        if not historys:
            return info_card + [{
                'component': 'VAlert',
                'props': {
                    'type': 'info', 'variant': 'tonal',
                    'text': '暂无签到记录，请等待下一次自动签到或手动触发一次。',
                    'class': 'mb-2'
                }
            }]

        historys = sorted(historys, key=lambda x: x.get("date", ""), reverse=True)

        history_rows = []
        for history in historys:
            status = str(history.get("status", "未知"))
            message = str(history.get('message', '—'))
            if "成功" in status or "已签到" in status:
                status_color = "success"
            elif "失败" in status:
                status_color = "error"
            else:
                status_color = "info"

            history_rows.append({
                'component': 'tr',
                'content': [
                    {'component': 'td', 'props': {'class': 'text-caption'}, 'text': history.get("date", "")},
                    {
                        'component': 'td',
                        'props': {
                            'title': status,
                            'style': 'width: 220px; max-width: 220px; overflow: hidden;'
                        },
                        'content': [{
                            'component': 'VChip',
                            'props': {
                                'color': status_color,
                                'size': 'small',
                                'variant': 'outlined',
                                'class': 'text-truncate',
                                'style': 'max-width: 100%;'
                            },
                            'content': [{
                                'component': 'span',
                                'props': {
                                    'class': 'text-truncate d-inline-block',
                                    'style': 'max-width: 190px;',
                                    'title': status
                                },
                                'text': status
                            }]
                        }]
                    },
                    {
                        'component': 'td',
                        'props': {
                            'title': message,
                            'style': 'max-width: 360px; overflow: hidden;'
                        },
                        'content': [{
                            'component': 'span',
                            'props': {
                                'class': 'text-truncate d-inline-block',
                                'style': 'max-width: 340px; vertical-align: middle;',
                                'title': message
                            },
                            'text': message
                        }]
                    },
                    {'component': 'td', 'text': str(history.get('points', '—'))},
                    {'component': 'td', 'text': str(history.get('days', '—'))},
                ]
            })

        return info_card + [{
            'component': 'VCard',
            'props': {'variant': 'outlined', 'class': 'mb-4'},
            'content': [
                {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '📊 影巢签到历史'},
                {
                    'component': 'VCardText',
                    'content': [{
                        'component': 'VTable',
                        'props': {'hover': True, 'density': 'compact'},
                        'content': [
                            {
                                'component': 'thead',
                                'content': [{
                                    'component': 'tr',
                                    'content': [
                                        {'component': 'th', 'text': '时间'},
                                        {'component': 'th', 'props': {'style': 'width: 220px; max-width: 220px;'}, 'text': '状态'},
                                        {'component': 'th', 'props': {'style': 'max-width: 360px;'}, 'text': '详情'},
                                        {'component': 'th', 'text': '奖励积分'},
                                        {'component': 'th', 'text': '连续天数'}
                                    ]
                                }]
                            },
                            {'component': 'tbody', 'content': history_rows}
                        ]
                    }]
                }
            ]
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    def stop_service(self):
        """
        停止服务
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"停止影巢签到服务失败: {str(e)}")

    def _is_manual_trigger(self) -> bool:
        """
        判断是否为手动触发
        """
        return getattr(self, '_manual_trigger', False)

    def _clear_extended_retry_tasks(self):
        """
        清理所有延长重试任务
        """
        try:
            if self._scheduler:
                jobs = self._scheduler.get_jobs()
                for job in jobs:
                    if "延长重试" in job.name:
                        self._scheduler.remove_job(job.id)
                        logger.info(f"清理延长重试任务: {job.name}")
        except Exception as e:
            logger.warning(f"清理延长重试任务失败: {str(e)}")

    def _has_running_extended_retry(self) -> bool:
        """
        检查是否有正在运行的延长重试任务
        """
        try:
            if self._scheduler:
                jobs = self._scheduler.get_jobs()
                for job in jobs:
                    if "延长重试" in job.name:
                        return True
            return False
        except Exception:
            return False

    def _is_already_signed_today(self) -> bool:
        """
        检查今天是否已经签到成功
        """
        history = self.get_data('sign_history') or []
        if not history:
            return False
        today = datetime.now().strftime('%Y-%m-%d')
        # 查找今日是否有成功签到记录
        return any(
            record.get("date", "").startswith(today)
            and record.get("status") in ["签到成功", "已签到"]
            for record in history
        )

    def _ensure_valid_cookie(self) -> Optional[str]:
        try:
            if not self._cookie:
                return None
            token = None
            for part in self._cookie.split(';'):
                p = part.strip()
                if p.startswith('token='):
                    token = p.split('=', 1)[1]
                    break
            if not token:
                return None
            try:
                decoded = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
                exp_ts = decoded.get('exp')
            except Exception:
                exp_ts = None
            if exp_ts and isinstance(exp_ts, (int, float)):
                import time as _t
                now_ts = int(_t.time())
                if exp_ts <= now_ts:
                    return self._auto_login()
            return None
        except Exception:
            return None

    def _auto_login(self) -> Optional[str]:
        try:
            if not getattr(self, "_username", None) or not getattr(self, "_password", None):
                logger.warning("未配置用户名或密码，无法自动登录")
                return None
            
            if HDHivePlaywrightClient is None:
                logger.error(f"无法执行自动登录，缺少 CloakBrowser/Playwright 依赖或加载失败。内部错误: {IMPORT_ERROR}")
                return None
                
            logger.info("采用 CloakBrowser/Playwright 执行真实无头浏览器登录...")
            try:
                client = HDHivePlaywrightClient(base_url=self._base_url, headless=True)
                result = client.login(username=getattr(self, "_username", ""), password=getattr(self, "_password", ""))
                if result:
                    cookie_str, _ = result
                    logger.info("CloakBrowser/Playwright 登录成功，已重新生成 Cookie")
                    return cookie_str
            except Exception as e:
                logger.error(f"CloakBrowser/Playwright 登录异常: {e}")
                
            logger.error("自动登录失败，未获取到有效Cookie")
            return None
        except Exception as e:
            logger.error(f"自动登录异常: {str(e)}")
            return None

    def _get_last_sign_time(self) -> str:
        """
        获取最后一次签到成功的时间
        """
        history = self.get_data('sign_history') or []
        if history:
            try:
                last_success = max([
                    record for record in history if record.get("status") in ["签到成功", "已签到"]
                ], key=lambda x: x.get("date", ""))
                return last_success.get("date")
            except ValueError:
                return "从未"
        return "从未"

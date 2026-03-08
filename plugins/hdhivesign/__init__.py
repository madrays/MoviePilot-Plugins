"""
影巢签到插件
版本: 1.6.3
作者: madrays,sakezerto
功能:
- 支持选择每日签到或者赌狗签到
- 自动完成影巢(HDHive)签到
- 支持签到失败重试
- 保存签到历史记录
- 提供详细的签到通知
- 默认使用代理访问

修改记录:
- v1.6.3: 移除get_state中的info日志，修复框架轮询导致日志刷屏的问题
- v1.6.2: 修复插件更新后签到模式、用户名、密码丢失的问题（update_config全量覆盖时字段缺失）
- v1.6.1: 更新了通知模板，修复冗余前缀并统一显示签到模式
- v1.6.0: 修复了一些bug
- v1.5.0: 支持自选影巢(HDHive)每日签到或者赌狗签到
- v1.4.0: 修复1.3.0无法自动获取cookie
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


class HdhiveSign(_PluginBase):
    # 插件名称
    plugin_name = "影巢签到"
    # 插件描述
    plugin_desc = "自动完成影巢(HDHive)签到，支持失败重试、历史记录和签到模式选择"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/hdhive.ico"
    # 插件版本
    plugin_version = "1.6.3"
    # 插件作者
    plugin_author = "madrays,sakezerto"
    # 作者主页
    author_url = "https://github.com/sakezerto/MoviePilot-Plugins"
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
    _cron = None
    _max_retries = 3  # 最大重试次数
    _retry_interval = 30  # 重试间隔(秒)
    _history_days = 30  # 历史保留天数
    _manual_trigger = False
    _sign_mode = "daily"  # daily=每日签到, gambling=赌狗签到
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
        "/api/customer/user/signin",
        "/api/customer/auth/signin",
        "/api/customer/user/token",
        "/api/auth/login",
        "/api/user/login",
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
                self._sign_mode = config.get("sign_mode") or "daily"
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
                    "enabled": self._enabled,
                    "cookie": self._cookie,
                    "notify": self._notify,
                    "cron": self._cron,
                    "base_url": self._base_url,
                    "max_retries": self._max_retries,
                    "retry_interval": self._retry_interval,
                    "history_days": self._history_days,
                    "sign_mode": self._sign_mode,
                    "username": getattr(self, "_username", ""),
                    "password": getattr(self, "_password", ""),
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
                            f"📝 签到模式：{'赌狗签到' if self._sign_mode == 'gambling' else '每日签到'}\n"
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
                        "cron": self._cron,
                        "cookie": self._cookie,
                        "base_url": self._base_url,
                        "max_retries": self._max_retries,
                        "retry_interval": self._retry_interval,
                        "history_days": self._history_days,
                        "username": getattr(self, "_username", ""),
                        "password": getattr(self, "_password", ""),
                        "sign_mode": getattr(self, "_sign_mode", "daily"),
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
                        "cron": self._cron,
                        "cookie": self._cookie,
                        "base_url": self._base_url,
                        "max_retries": self._max_retries,
                        "retry_interval": self._retry_interval,
                        "history_days": self._history_days,
                        "username": getattr(self, "_username", ""),
                        "password": getattr(self, "_password", ""),
                        "sign_mode": getattr(self, "_sign_mode", "daily"),
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
                if any(k in (message or "") for k in ["未配置Cookie", "缺少'token'", "未授权", "Unauthorized", "token", "csrf", "登录已过期", "过期", "expired"]):
                    logger.info("检测到Cookie或鉴权问题，尝试自动登录刷新Cookie后重试一次")
                    new_cookie = self._auto_login()
                    if new_cookie:
                        self._cookie = new_cookie
                        self.update_config({
                            "enabled": self._enabled,
                            "notify": self._notify,
                            "cron": self._cron,
                            "cookie": self._cookie,
                            "base_url": self._base_url,
                            "max_retries": self._max_retries,
                            "retry_interval": self._retry_interval,
                            "history_days": self._history_days,
                            "username": getattr(self, "_username", ""),
                            "password": getattr(self, "_password", ""),
                            "sign_mode": getattr(self, "_sign_mode", "daily"),
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
        基于影巢API的签到实现
        """
        try:
            cookies = {}
            if self._cookie:
                for cookie_item in self._cookie.split(';'):
                    if '=' in cookie_item:
                        name, value = cookie_item.strip().split('=', 1)
                        cookies[name] = value
            else:
                return False, "未配置Cookie"

            token = cookies.get('token')
            csrf_token = cookies.get('csrf_access_token')

            if not token:
                return False, "Cookie中缺少'token'"

            user_id = None
            referer = self._site_url
            try:
                decoded_token = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
                user_id = decoded_token.get('sub')
                if user_id:
                    referer = f"{self._base_url}/user/{user_id}"
            except Exception as e:
                logger.warning(f"从Token中解析用户ID失败，将使用默认Referer: {e}")

            proxies = settings.PROXY
            ua = settings.USER_AGENT

            headers = {
                'User-Agent': ua,
                'Accept': 'application/json, text/plain, */*',
                'Origin': self._base_url,
                'Referer': referer,
                'Authorization': f'Bearer {token}',
            }
            if csrf_token:
                headers['x-csrf-token'] = csrf_token

            # 根据签到模式选择接口
            # checkIn Server Action：[false]=每日签到, [true]=赌狗签到
            checkin_action_id = "409fcfaf6015ab7d6e7fbcaf2f551cbbc4875c691b"
            is_gambling = getattr(self, "_sign_mode", "daily") == "gambling"
            sa_headers = {
                "User-Agent": ua,
                "Accept": "text/x-component",
                "Content-Type": "text/plain;charset=UTF-8",
                "Next-Action": checkin_action_id,
                "Next-Router-State-Tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22(app)%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D",
                "Origin": self._base_url,
                "Referer": referer,
                "Authorization": f"Bearer {token}",
            }
            if csrf_token:
                sa_headers["x-csrf-token"] = csrf_token
            try:
                sa_res = requests.post(
                    url=f"{self._base_url}/",
                    headers=sa_headers,
                    cookies=cookies,
                    data=json.dumps([is_gambling]),
                    proxies=proxies,
                    timeout=30,
                    verify=False
                )
                mode_name = "赌狗签到" if is_gambling else "每日签到"
                logger.info(f"{mode_name} Server Action 响应: {sa_res.status_code}")
                if sa_res.status_code in (200, 500):
                    # RSC 响应格式: 0:{...} 1:{...}，找第二行解析实际结果
                    rsc_text = sa_res.text
                    # 尝试 UTF-8，失败则 latin-1 再手动解码
                    try:
                        rsc_text = sa_res.content.decode("utf-8")
                    except Exception:
                        try:
                            rsc_text = sa_res.content.decode("latin-1")
                        except Exception:
                            pass
                    result_json = None
                    for line in rsc_text.splitlines():
                        if line.startswith("1:"):
                            try:
                                result_json = json.loads(line[2:])
                                break
                            except Exception:
                                pass
                    if result_json:
                        error = result_json.get("error") or {}
                        data = result_json.get("data") or result_json
                        if error:
                            desc = error.get("description") or error.get("message") or str(error)
                            logger.info(f"{mode_name} 结果: {desc}")
                            # 已签到也算成功（不是真正的失败）
                            if "已经签到" in desc or "已签到" in desc or "明天" in desc:
                                return True, desc
                            return False, desc
                        msg = data.get("message") or data.get("description") or mode_name
                        logger.info(f"{mode_name} 成功: {msg}")
                        return True, msg
                    return True, mode_name
                return False, f"{mode_name}失败: HTTP {sa_res.status_code}"
            except Exception as e:
                return False, f"签到异常: {e}"

            signin_res = requests.post(
                url=self._signin_api,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                timeout=30,
                verify=False
            )

            if signin_res is None:
                return False, '签到请求失败，响应为空，请检查代理或网络环境'

            try:
                signin_result = signin_res.json()
            except json.JSONDecodeError:
                logger.error(f"API响应JSON解析失败 (状态码 {signin_res.status_code}): {signin_res.text[:500]}")
                return False, f'签到API响应格式错误，状态码: {signin_res.status_code}'

            message = signin_result.get('message', '无明确消息')
            
            if signin_result.get('success'):
                try:
                    self._fetch_user_info(cookies, token)
                except Exception:
                    pass
                return True, message

            if "已经签到" in message or "签到过" in message:
                try:
                    self._fetch_user_info(cookies, token)
                except Exception:
                    pass
                return True, message 

            logger.error(f"签到失败, HTTP状态码: {signin_res.status_code}, 消息: {message}")
            return False, message

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
            headers = {
                'User-Agent': settings.USER_AGENT,
                'Accept': 'application/json, text/plain, */*',
                'Origin': self._base_url,
                'Referer': referer,
                'Authorization': f'Bearer {token}',
            }
            resp = requests.get(self._user_info_api, headers=headers, cookies=cookies, proxies=settings.PROXY, timeout=30, verify=False)
            logger.info(f"拉取用户信息 API 状态码: {getattr(resp,'status_code','unknown')} CT: {getattr(resp.headers,'get',lambda k:'' )('Content-Type')}")
            data = {}
            try:
                data = resp.json()
            except Exception:
                data = {}
            # 统一解析 response.data / detail / data 结构
            detail = (data.get('response') or {}).get('data') or data.get('detail') or data.get('data') or {}
            if not isinstance(detail, dict):
                detail = {}
            info = {
                'id': detail.get('id') or detail.get('member_id'),
                'nickname': detail.get('nickname') or detail.get('member_name'),
                'avatar_url': detail.get('avatar_url') or detail.get('gravatar_url'),
                'created_at': detail.get('created_at'),
                'points': ((detail.get('user_meta') or {}).get('points')),
                'signin_days_total': ((detail.get('user_meta') or {}).get('signin_days_total')),
                'warnings_nums': detail.get('warnings_nums'),
            }
            # 若 API 未返回完整信息，尝试 RSC 页面解析
            if not info.get('nickname') or info.get('points') is None or info.get('signin_days_total') is None:
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
                    import re as _re
                    m_nick = _re.search(r'"nickname":"([^"]+)"', rsc_text)
                    m_points = _re.search(r'"points":(\d+)', rsc_text)
                    m_days = _re.search(r'"signin_days_total":(\d+)', rsc_text)
                    m_avatar = _re.search(r'"avatar_url":"([^"]+)"', rsc_text)
                    m_created = _re.search(r'"created_at":"([^"]+)"', rsc_text)
                    if m_nick:
                        info['nickname'] = m_nick.group(1)
                    if m_points:
                        info['points'] = int(m_points.group(1))
                    if m_days:
                        info['signin_days_total'] = int(m_days.group(1))
                    if m_avatar:
                        info['avatar_url'] = m_avatar.group(1)
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

        # 获取 Cookie 到期信息
        cookie_expire_info = ""
        try:
            token = None
            for part in (self._cookie or "").split(';'):
                p = part.strip()
                if p.startswith('token='):
                    token = p.split('=', 1)[1]
                    break
            if token:
                decoded = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
                exp_ts = decoded.get('exp')
                if exp_ts:
                    import time as _t
                    remaining_days = (exp_ts - int(_t.time())) / 86400
                    expire_str = datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%d')
                    if remaining_days <= 0:
                        cookie_expire_info = f"🔴 Cookie 已过期！请立即更新"
                    elif remaining_days <= 2:
                        hours = int(remaining_days * 24)
                        cookie_expire_info = f"⚠️ Cookie 剩余约 {hours} 小时（{expire_str} 到期）"
                    else:
                        days_left = int(remaining_days)
                        cookie_expire_info = f"🟢 Cookie 剩余 {days_left} 天（{expire_str} 到期）"
        except Exception:
            pass

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
                    f"📝 签到模式：{'赌狗签到' if self._sign_mode == 'gambling' else '每日签到'}\n"
                    f"💬 消息：{message}\n"
                    f"🎁 奖励：{points}\n"
                    f"📆 天数：{days}\n"
                    f"━━━━━━━━━━\n"
                    f"👤 用户信息\n"
                    f"昵称：{nickname}\n"
                    f"积分：{user_points}\n"
                    f"累计签到天数（站点）：{signin_days_total}\n"
                    f"加入时间：{created_at}\n"
                    f"━━━━━━━━━━\n"
                    f"🔑 {cookie_expire_info}\n"
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
                    f"📝 签到模式：{'赌狗签到' if self._sign_mode == 'gambling' else '每日签到'}\n"
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
                                    'md': 4
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
                                    'md': 4
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
                                    'md': 4
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
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'sign_mode',
                                            'label': '签到模式',
                                            'items': [
                                                {'title': '每日签到（固定积分）', 'value': 'daily'},
                                                {'title': '赌狗签到（随机积分，最多3倍）', 'value': 'gambling'},
                                            ]
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
                                            'text': '【使用教程】\n1. 登录影巢站点（具体域名请在上方“站点地址”中填写），按F12打开开发者工具。\n2. 切换到"应用(Application)" -> "Cookie"，或"网络(Network)"选项卡，找到发往API的请求。\n3. 复制完整的Cookie字符串。\n4. 确保Cookie中包含 `token` 和 `csrf_access_token` 字段。\n5. 粘贴到上方输入框，启用插件并保存。\n\n⚠️ 影巢可能变更域名，若签到异常请先更新“站点地址”。插件会自动使用系统配置的代理。'
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
            "onlyonce": False,
            "cookie": "",
            "base_url": "https://hdhive.com",
            "cron": "0 8 * * *",
            "max_retries": 3,
            "retry_interval": 30,
            "history_days": 30,
            "username": "",
            "password": "",
            "sign_mode": "daily"
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
            avatar = user.get('avatar_url') or ''
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
            status = history.get("status", "未知")
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
                        'content': [{
                            'component': 'VChip',
                            'props': {'color': status_color, 'size': 'small', 'variant': 'outlined'},
                            'text': status
                        }]
                    },
                    {'component': 'td', 'text': history.get('message', '—')},
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
                                        {'component': 'th', 'text': '状态'},
                                        {'component': 'th', 'text': '详情'},
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
                remaining_seconds = exp_ts - now_ts
                remaining_days = remaining_seconds / 86400

                # Cookie 已过期，尝试自动登录
                if remaining_seconds <= 0:
                    logger.warning("Cookie 已过期，尝试自动登录刷新")
                    new_cookie = self._auto_login()
                    if not new_cookie and self._notify:
                        expire_time = datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%d %H:%M')
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【⚠️ 影巢 Cookie 已过期】",
                            text=(
                                f"⚠️ Cookie 已于 {expire_time} 过期，自动登录失败\n"
                                f"━━━━━━━━━━\n"
                                f"请前往插件设置手动更新 Cookie：\n"
                                f"1. 登录 {self._base_url}\n"
                                f"2. F12 → Application → Cookies\n"
                                f"3. 复制 token 值填入插件配置"
                            )
                        )
                    return new_cookie

                # Cookie 即将在 2 天内过期，提前预警
                elif remaining_days <= 2:
                    expire_time = datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%d %H:%M')
                    hours_left = int(remaining_seconds / 3600)
                    logger.warning(f"Cookie 即将过期，剩余约 {hours_left} 小时（{expire_time}）")
                    if self._notify:
                        # 避免重复通知：记录上次预警日期
                        last_warned = self.get_data('cookie_expire_warned_date')
                        today_str = datetime.now().strftime('%Y-%m-%d')
                        if last_warned != today_str:
                            self.save_data('cookie_expire_warned_date', today_str)
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【⏰ 影巢 Cookie 即将过期】",
                                text=(
                                    f"⏰ Cookie 将于 {expire_time} 过期\n"
                                    f"剩余约 {hours_left} 小时，请尽快更新！\n"
                                    f"━━━━━━━━━━\n"
                                    f"更新步骤：\n"
                                    f"1. 登录 {self._base_url}\n"
                                    f"2. F12 → Application → Cookies\n"
                                    f"3. 复制 token 值填入插件配置"
                                )
                            )
                else:
                    expire_time = datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%d %H:%M')
                    days_left = int(remaining_days)
                    logger.info(f"Cookie 有效，剩余约 {days_left} 天（过期时间：{expire_time}）")
            return None
        except Exception:
            return None

    def _auto_login(self) -> Optional[str]:
        """
        自动登录获取 Cookie，按优先级依次尝试：
        1. NextAuth.js 凭证登录（/api/auth/...）
        2. Next.js Server Action（从 HTML + JS bundle 提取 next-action token）
        3. Playwright 浏览器自动化兜底
        """
        import re as _re

        username = getattr(self, "_username", "")
        password = getattr(self, "_password", "")
        if not username or not password:
            logger.warning("未配置用户名或密码，无法自动登录")
            return None

        # 优先使用 curl_cffi（模拟真实浏览器 TLS 指纹，能绕过新版 Cloudflare）
        # 其次 cloudscraper，最后 requests
        scraper = None
        scraper_type = None
        try:
            from curl_cffi import requests as cffi_requests
            scraper = cffi_requests.Session(impersonate="chrome120")
            scraper_type = "curl_cffi"
            logger.info("自动登录: 使用 curl_cffi (chrome120)")
        except ImportError:
            pass
        if scraper is None:
            try:
                import cloudscraper
                scraper = cloudscraper.create_scraper()
                scraper_type = "cloudscraper"
                logger.info("自动登录: 使用 cloudscraper")
            except ImportError:
                pass
        if scraper is None:
            scraper = requests
            scraper_type = "requests"
            logger.info("自动登录: 回退到 requests")

        login_url = f"{self._base_url}{self._login_page}"
        proxies = settings.PROXY
        ua = settings.USER_AGENT
        domain = self._base_url.replace('https://', '').replace('http://', '').split('/')[0]

        def _extract_cookies(resp):
            """从响应中提取 token 和 csrf_access_token，兼容 curl_cffi / requests / cloudscraper"""
            cd = {}
            try:
                c = getattr(resp, 'cookies', None)
                if c is not None:
                    try:
                        cd = c.get_dict()
                    except Exception:
                        try:
                            cd = dict(c)
                        except Exception:
                            try:
                                cd = {i.name: i.value for i in c}
                            except Exception:
                                pass
            except Exception:
                pass
            # 从 Set-Cookie header 兜底提取（curl_cffi 有时只在 header 里）
            if not cd.get('token'):
                sc = ''
                try:
                    sc = resp.headers.get('set-cookie', '') or ''
                except Exception:
                    pass
                if not sc:
                    try:
                        sc = ' '.join(resp.headers.get_list('set-cookie') or [])
                    except Exception:
                        pass
                if sc:
                    m = _re.search(r'(?<!\w)token=([^;,\s]+)', sc)
                    if m:
                        cd['token'] = m.group(1)
                    m2 = _re.search(r'csrf_access_token=([^;,\s]+)', sc)
                    if m2:
                        cd['csrf_access_token'] = m2.group(1)
            return cd

        def _build_cookie_str(cd):
            parts = [f"token={cd['token']}"]
            if cd.get('csrf_access_token'):
                parts.append(f"csrf_access_token={cd['csrf_access_token']}")
            return "; ".join(parts)

        # ── 预热：拿到页面 HTML 和初始 Session Cookie ──────────────────
        warm_text = ""
        resp_warm = None
        try:
            logger.info(f"自动登录: 预热 {login_url}")
            resp_warm = scraper.get(login_url, timeout=30, proxies=proxies)
            warm_text = getattr(resp_warm, 'text', '') or ''
            logger.info(f"自动登录: 预热状态码 {getattr(resp_warm, 'status_code', '?')}")
        except Exception as e:
            logger.warning(f"自动登录: 预热失败 {e}")

        # ── 策略 1：NextAuth.js ─────────────────────────────────────────
        # NextAuth 流程：GET /api/auth/csrf → POST /api/auth/signin/credentials
        try:
            csrf_url = f"{self._base_url}/api/auth/csrf"
            logger.info(f"自动登录: 尝试 NextAuth GET {csrf_url}")
            r_csrf = scraper.get(csrf_url, timeout=15, proxies=proxies,
                                 headers={'User-Agent': ua, 'Referer': login_url})
            logger.info(f"自动登录: NextAuth csrf 状态码 {r_csrf.status_code}")
            if r_csrf.status_code == 200:
                csrf_token = (r_csrf.json() or {}).get('csrfToken', '')
                logger.info(f"自动登录: NextAuth csrfToken={'已获取' if csrf_token else '未获取'}")
                if csrf_token:
                    signin_url = f"{self._base_url}/api/auth/signin/credentials"
                    payload = {
                        'username': username,
                        'password': password,
                        'csrfToken': csrf_token,
                        'callbackUrl': self._base_url,
                        'json': 'true'
                    }
                    r_sign = scraper.post(signin_url, data=payload, timeout=30, proxies=proxies,
                                          headers={
                                              'User-Agent': ua,
                                              'Content-Type': 'application/x-www-form-urlencoded',
                                              'Referer': login_url,
                                              'Origin': self._base_url,
                                          })
                    logger.info(f"自动登录: NextAuth 登录状态码 {r_sign.status_code} 响应={r_sign.text[:300]}")
                    cd = _extract_cookies(r_sign)
                    logger.info(f"自动登录: NextAuth 响应Cookie keys={list(cd.keys())}")
                    if cd.get('token'):
                        logger.info("自动登录: NextAuth 登录成功")
                        return _build_cookie_str(cd)
        except Exception as e:
            logger.warning(f"自动登录: NextAuth 失败 {type(e).__name__}: {e}")

        # ── 策略 2：Next.js Server Action ──────────────────────────────
        # next-action token 藏在 HTML 或 JS bundle 里，需要主动抓取
        next_action_token = None

        # 2a. 先在 HTML 里找
        patterns = [
            r'"next-action"\s*:\s*"([a-fA-F0-9]{40,})"',
            r'name="next-action"\s+value="([a-fA-F0-9]{40,})"',
            r'data-action="([a-fA-F0-9]{40,})"',
            r'"([a-fA-F0-9]{40,})"\s*,\s*\[\s*"username"',
            r'action["\s:=]+["\']([a-fA-F0-9]{40,})["\']',
        ]
        for pat in patterns:
            m = _re.search(pat, warm_text)
            if m:
                next_action_token = m.group(1)
                logger.info(f"自动登录: 在HTML中找到 next-action={next_action_token[:12]}...")
                break

        # 2b. HTML 里没有，去 JS bundle 里找
        if not next_action_token:
            try:
                js_srcs = _re.findall(r'src="(/_next/static/chunks/[^"]+\.js)"', warm_text)
                # 优先搜索可能含登录逻辑的文件名
                priority = [s for s in js_srcs if any(k in s for k in ['login', 'auth', 'page', 'app'])]
                others = [s for s in js_srcs if s not in priority]
                for src in (priority + others)[:10]:  # 最多抓10个JS文件
                    js_url = f"{self._base_url}{src}"
                    try:
                        r_js = scraper.get(js_url, timeout=15, proxies=proxies, headers={'User-Agent': ua})
                        js_text = r_js.text or ''
                        for pat in patterns:
                            m = _re.search(pat, js_text)
                            if m:
                                next_action_token = m.group(1)
                                logger.info(f"自动登录: 在JS({src[-30:]})中找到 next-action={next_action_token[:12]}...")
                                break
                    except Exception:
                        continue
                    if next_action_token:
                        break
            except Exception as e:
                logger.debug(f"自动登录: JS bundle 搜索失败 {e}")

        # 用从 JS bundle 提取到的 Server Action ID 直接尝试登录
        hardcoded_sa_ids = [
            "60a3fc399468c700be8a3ecc69cd86c911899c9c85",
            "40b483478930efba01f4734184d67a8c34a915dd29",
        ]
        for sa_id in hardcoded_sa_ids:
            if not next_action_token:
                sa_hdrs = {
                    "User-Agent": ua,
                    "Accept": "text/x-component",
                    "Content-Type": "text/plain;charset=UTF-8",
                    "Next-Action": sa_id,
                    "Next-Router-State-Tree": '%5B%22%22%2C%7B%22children%22%3A%5B%22(auth)%22%2C%7B%22children%22%3A%5B%22login%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2Flogin%22%2C%22refresh%22%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
                    "Origin": self._base_url,
                    "Referer": login_url,
                }
                for body in [
                    json.dumps([{"username": username, "password": password}]),
                    json.dumps([username, password]),
                    json.dumps({"username": username, "password": password}),
                ]:
                    try:
                        r_sa = scraper.post(login_url, headers=sa_hdrs, data=body, timeout=30, proxies=proxies)
                        logger.info(f"自动登录: SA({sa_id[:12]}) 状态={r_sa.status_code}")
                        cd = _extract_cookies(r_sa)
                        logger.info(f"自动登录: SA Cookie keys={list(cd.keys())}")
                        if cd.get("token"):
                            logger.info("自动登录: Server Action 硬编码ID 登录成功")
                            return _build_cookie_str(cd)
                    except Exception as e:
                        logger.debug(f"自动登录: SA({sa_id[:12]}) 失败 {e}")

        if next_action_token:
            sa_headers = {
                'User-Agent': ua,
                'Accept': 'text/x-component',
                'Content-Type': 'text/plain;charset=UTF-8',
                'Next-Action': next_action_token,
                'Next-Router-State-Tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22(auth)%22%2C%7B%22children%22%3A%5B%22login%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2Flogin%22%2C%22refresh%22%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
                'Origin': self._base_url,
                'Referer': login_url,
            }
            # 尝试多种 payload 格式
            payloads = [
                json.dumps([{'username': username, 'password': password}]),
                json.dumps([username, password]),
                json.dumps({'username': username, 'password': password}),
            ]
            for body in payloads:
                try:
                    logger.info(f"自动登录: 尝试 Server Action 登录")
                    r_sa = scraper.post(login_url, headers=sa_headers, data=body, timeout=30, proxies=proxies)
                    logger.info(f"自动登录: SA 状态码 {r_sa.status_code}")
                    cd = _extract_cookies(r_sa)
                    if cd.get('token'):
                        logger.info("自动登录: Server Action 登录成功")
                        return _build_cookie_str(cd)
                except Exception as e:
                    logger.debug(f"自动登录: SA payload 失败 {e}")
        else:
            logger.warning("自动登录: 未找到 next-action token，跳过 Server Action")

        # ── 策略 3：从 JS bundle 挖掘真实登录 API 并直接调用 ──────────
        try:
            logger.info("自动登录: 尝试从 JS bundle 提取登录 API")
            js_srcs = _re.findall(r'src="(/_next/static/chunks/[^"]+\.js)"', warm_text)
            found_apis = []
            api_patterns = [
                r"fetch\([\"'](/api/[^\"']+)[\"']",
                r"post\([\"'](/api/[^\"']+)[\"']",
                r"\"(/api/[^\"]+(?:login|auth|signin)[^\"]*)\"",
            ]
            for src in js_srcs:
                try:
                    r_js = scraper.get(f"{self._base_url}{src}", timeout=15, proxies=proxies,
                                       headers={'User-Agent': ua})
                    js_text = r_js.text or ''
                    for pat in api_patterns:
                        for m in _re.finditer(pat, js_text):
                            api = m.group(1)
                            if api not in found_apis and any(k in api for k in ['login','auth','signin']):
                                found_apis.append(api)
                except Exception:
                    continue
            # 扫描 JS bundle，打印所有 /api/ 路径（不过滤关键词）
            all_apis = []
            broad_pat = r'["\'](\/api\/[^\"\'\s]{3,60})["\']'  
            for src in all_scripts[:15]:
                try:
                    r_js = scraper.get(f"{self._base_url}{src}", timeout=15, proxies=proxies,
                                       headers={"User-Agent": ua})
                    for m in _re.finditer(broad_pat, r_js.text or ""):
                        p = m.group(1)
                        if p not in all_apis:
                            all_apis.append(p)
                except Exception:
                    continue
            logger.info(f"自动登录: JS bundle 发现的 API 路径={found_apis}")
            login_payloads = [
                {'username': username, 'password': password},
                {'email': username, 'password': password},
            ]
            for api_path in found_apis:
                url = f"{self._base_url}{api_path}"
                for payload in login_payloads:
                    try:
                        r = scraper.post(url, json=payload, timeout=20, proxies=proxies,
                                         headers={
                                             'User-Agent': ua,
                                             'Content-Type': 'application/json',
                                             'Referer': login_url,
                                             'Origin': self._base_url,
                                         })
                        logger.info(f"自动登录: POST {api_path} 状态={r.status_code} 响应={r.text[:200]}")
                        cd = _extract_cookies(r)
                        if cd.get('token'):
                            logger.info(f"自动登录: JS bundle API 登录成功 ({api_path})")
                            return _build_cookie_str(cd)
                        try:
                            rj = r.json()
                            t = (rj.get('token') or rj.get('access_token') or
                                 (rj.get('data') or {}).get('token') or
                                 (rj.get('meta') or {}).get('access_token'))
                            if t:
                                logger.info(f"自动登录: 从响应体提取 token ({api_path})")
                                return f"token={t}"
                        except Exception:
                            pass
                    except Exception as e:
                        logger.debug(f"自动登录: {api_path} 失败 {e}")
        except Exception as e:
            logger.warning(f"自动登录: JS bundle 策略异常 {e}")

        # ── 策略 4：Playwright 浏览器自动化兜底 ───────────────────────
        try:
            from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
            logger.info("自动登录: 尝试 Playwright 浏览器自动化")
            proxy_cfg = None
            try:
                pxy = settings.PROXY or {}
                server = pxy.get('https') or pxy.get('http')
                if server:
                    proxy_cfg = {"server": server}
            except Exception:
                pass

            with sync_playwright() as pw:
                stealth_args = [
                    "--no-sandbox", "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
                launch_args = {"headless": True, "args": stealth_args}
                if proxy_cfg:
                    launch_args["proxy"] = proxy_cfg
                browser = pw.chromium.launch(**launch_args)
                context = browser.new_context(
                    user_agent=ua,
                    viewport={"width": 1920, "height": 1080},
                    locale="zh-CN",
                    timezone_id="Asia/Shanghai",
                )
                # 优先使用 playwright-stealth 隐藏自动化特征
                try:
                    from playwright_stealth import stealth_sync
                    page_temp = context.new_page()
                    stealth_sync(page_temp)
                    page_temp.close()
                    logger.info("自动登录: playwright-stealth 已启用")
                except ImportError:
                    logger.warning("自动登录: playwright-stealth 未安装，建议 pip install playwright-stealth")
                    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN','zh','en']});window.chrome = {runtime: {}};")

                # 注入 curl_cffi/scraper 已通过 Cloudflare 验证的 Cookie
                try:
                    cf_cookies = {}
                    c = getattr(scraper, 'cookies', None)
                    if c is not None:
                        # curl_cffi Session: cookies 是 Cookies 对象，迭代取 (name, value)
                        try:
                            for cookie in c:
                                cf_cookies[cookie.name] = cookie.value
                        except Exception:
                            pass
                        if not cf_cookies:
                            try:
                                cf_cookies = dict(c)
                            except Exception:
                                pass
                        if not cf_cookies:
                            try:
                                cf_cookies = c.get_dict()
                            except Exception:
                                pass
                    # 也从 resp_warm 的响应 Cookie 里补充
                    if resp_warm is not None:
                        try:
                            for cookie in getattr(resp_warm, 'cookies', []):
                                try:
                                    cf_cookies[cookie.name] = cookie.value
                                except Exception:
                                    pass
                        except Exception:
                            pass
                    logger.info(f"自动登录: scraper Cookie keys={list(cf_cookies.keys())}")
                    if cf_cookies:
                        pw_cookies = [
                            {"name": k, "value": v, "domain": domain, "path": "/"}
                            for k, v in cf_cookies.items()
                        ]
                        context.add_cookies(pw_cookies)
                        logger.info(f"自动登录: 已注入 Cookie 到 Playwright，共 {len(pw_cookies)} 个")
                    else:
                        logger.warning("自动登录: scraper 无 Cookie 可注入，Playwright 可能被 Cloudflare 拦截")
                except Exception as e:
                    logger.warning(f"自动登录: Cookie 注入失败 {e}")

                page = context.new_page()
                # 对实际页面也应用 stealth
                try:
                    from playwright_stealth import stealth_sync
                    stealth_sync(page)
                except ImportError:
                    pass

                # 拦截网络响应，主动捕获 Set-Cookie
                captured_token = {}
                def on_response(response):
                    try:
                        hdrs = response.headers
                        sc = hdrs.get('set-cookie', '')
                        if 'token=' in sc:
                            m = _re.search(r'token=([^;,\s]+)', sc)
                            if m:
                                captured_token['token'] = m.group(1)
                            m2 = _re.search(r'csrf_access_token=([^;,\s]+)', sc)
                            if m2:
                                captured_token['csrf_access_token'] = m2.group(1)
                    except Exception:
                        pass
                page.on("response", on_response)

                page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
                logger.info(f"自动登录: Playwright 页面加载完成，当前URL={page.url}")
                # 等待 React 渲染完成——直到页面出现任意 input 或超时
                try:
                    page.wait_for_selector("input", timeout=15000)
                    logger.info("自动登录: 检测到 input，React 已渲染")
                except Exception:
                    logger.warning("自动登录: 等待 input 超时，继续尝试")

                # 列出页面所有 input，帮助诊断选择器
                try:
                    all_inputs = page.eval_on_selector_all(
                        'input',
                        'els => els.map(e => ({type: e.type, name: e.name, placeholder: e.placeholder, id: e.id}))'
                    )
                    logger.info(f"自动登录: 页面 input 列表={all_inputs}")
                except Exception as e:
                    logger.debug(f"自动登录: 无法列出 input {e}")

                # 填写用户名
                user_filled = False
                for sel in ["input[name='username']", "input[name='email']",
                            "input[type='email']", "input[placeholder*='邮箱']",
                            "input[placeholder*='用户名']", "input[placeholder*='email']"]:
                    try:
                        el = page.query_selector(sel)
                        if el and el.is_visible():
                            el.fill(username)
                            user_filled = True
                            logger.info(f"自动登录: 用户名已填入，选择器={sel}")
                            break
                    except Exception:
                        continue
                if not user_filled:
                    logger.warning("自动登录: 未找到用户名输入框，尝试填入第一个 input")
                    try:
                        page.eval_on_selector('input:first-of-type', f'el => el.value = "{username}"')
                    except Exception:
                        pass

                # 填写密码
                pwd_filled = False
                for sel in ["input[name='password']", "input[type='password']",
                            "input[placeholder*='密码']"]:
                    try:
                        el = page.query_selector(sel)
                        if el and el.is_visible():
                            el.fill(password)
                            pwd_filled = True
                            logger.info(f"自动登录: 密码已填入，选择器={sel}")
                            break
                    except Exception:
                        continue
                if not pwd_filled:
                    logger.warning("自动登录: 未找到密码输入框")

                # 点击登录
                btn_clicked = False
                try:
                    btn = (page.query_selector("button[type='submit']")
                           or page.query_selector("button:has-text('登录')")
                           or page.query_selector("button:has-text('Login')")
                           or page.query_selector("button:has-text('Sign in')")
                           or page.query_selector("button:has-text('登 录')"))
                    if btn:
                        btn_text = btn.inner_text() if btn else ''
                        logger.info(f"自动登录: 点击登录按钮，文本='{btn_text}'")
                        btn.click()
                        btn_clicked = True
                    else:
                        # 列出所有 button 帮助诊断
                        try:
                            all_btns = page.eval_on_selector_all('button', 'els => els.map(e => e.innerText)')
                            logger.warning(f"自动登录: 未找到登录按钮，页面所有按钮={all_btns}")
                        except Exception:
                            pass
                        page.keyboard.press("Enter")
                        btn_clicked = True
                        logger.info("自动登录: 通过 Enter 键提交")
                except Exception as e:
                    logger.warning(f"自动登录: 点击按钮异常 {e}，改用 Enter")
                    page.keyboard.press("Enter")

                # 等待跳转或网络静止
                try:
                    page.wait_for_url(lambda url: '/login' not in url, timeout=10000)
                    logger.info(f"自动登录: 登录后跳转到 {page.url}")
                except PWTimeout:
                    logger.warning(f"自动登录: 等待跳转超时，当前仍在 {page.url}，可能登录失败或账号密码错误")
                except Exception:
                    try:
                        page.wait_for_load_state("networkidle", timeout=8000)
                        logger.info(f"自动登录: 网络静止，当前URL={page.url}")
                    except Exception:
                        pass

                # 打印所有 Cookie 帮助诊断
                all_cookies = context.cookies()
                logger.info(f"自动登录: 当前所有Cookie名={[c.get('name') for c in all_cookies]}")

                # 优先用响应拦截到的 token
                if not captured_token.get('token'):
                    for c in all_cookies:
                        if c.get('name') == 'token':
                            captured_token['token'] = c.get('value')
                        elif c.get('name') == 'csrf_access_token':
                            captured_token['csrf_access_token'] = c.get('value')

                context.close()
                browser.close()

                if captured_token.get('token'):
                    logger.info("自动登录: Playwright 登录成功")
                    return _build_cookie_str(captured_token)
                else:
                    logger.error("自动登录: Playwright 未获取到 token Cookie")

        except ImportError:
            logger.warning("自动登录: Playwright 未安装，可执行 'pip install playwright && playwright install chromium'")
        except Exception as e:
            logger.error(f"自动登录: Playwright 异常 {e}")

        logger.error("自动登录失败，所有策略均未获取到有效Cookie")
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

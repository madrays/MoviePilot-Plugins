"""
飞牛论坛签到插件
版本: 2.5.7
作者: madrays
功能:
- 自动完成飞牛论坛每日签到
- 支持签到失败重试
- 保存签到历史记录
- 提供详细的签到通知
- 增强的错误处理和日志

修改记录:
- v1.0: 初始版本，基本签到功能
"""
import time
import requests
import re
from html import unescape
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger
from app.schemas import NotificationType
from concurrent.futures import ThreadPoolExecutor

try:
    # MoviePilot v2.12+ 内置。此处只用于执行 ESA 的普通 JS Challenge，
    # 不会尝试处理需要人工操作的滑块验证。
    from cloakbrowser import launch_context as cloak_launch_context
except Exception:
    cloak_launch_context = None


class fnossign(_PluginBase):
    # 插件名称
    plugin_name = "飞牛论坛签到"
    # 插件描述
    plugin_desc = "自动完成飞牛论坛每日签到，支持失败重试和历史记录"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/fnos.ico"
    # 插件版本
    plugin_version = "2.5.7"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "fnossign_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _cookie = None
    _notify = False
    _onlyonce = False
    _log_profile_once = False
    _cron = None
    _max_retries = 3  # 最大重试次数
    _retry_interval = 30  # 重试间隔(秒)
    _history_days = 30  # 历史保留天数
    _manual_trigger = False
    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None
    _current_trigger_type = None  # 保存当前执行的触发类型

    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()

        logger.info("============= fnossign 初始化 =============")
        try:
            if config:
                self._enabled = config.get("enabled")
                self._cookie = config.get("cookie")
                self._notify = config.get("notify")
                self._cron = config.get("cron")
                self._onlyonce = config.get("onlyonce")
                self._log_profile_once = config.get("log_profile_once", False)
                self._max_retries = int(config.get("max_retries", 3))
                self._retry_interval = int(config.get("retry_interval", 30))
                self._history_days = int(config.get("history_days", 30))
                logger.info(f"配置: enabled={self._enabled}, notify={self._notify}, cron={self._cron}, max_retries={self._max_retries}, retry_interval={self._retry_interval}, history_days={self._history_days}")
            
            # 清理所有可能的延长重试任务
            self._clear_extended_retry_tasks()
            
            if self._onlyonce or self._log_profile_once:
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)

            if self._onlyonce:
                logger.info("执行一次性签到")
                self._manual_trigger = True
                self._scheduler.add_job(func=self.sign, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="飞牛论坛签到")
                self._onlyonce = False

            if self._log_profile_once:
                logger.info("执行一次性用户信息输出")
                self._scheduler.add_job(
                    func=self._log_user_info,
                    trigger='date',
                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                    name="飞牛论坛用户信息输出"
                )
                self._log_profile_once = False

            if self._scheduler and self._scheduler.get_jobs():
                self.update_config({
                    "enabled": self._enabled,
                    "onlyonce": self._onlyonce,
                    "log_profile_once": self._log_profile_once,
                    "cookie": self._cookie,
                    "notify": self._notify,
                    "cron": self._cron,
                    "max_retries": self._max_retries,
                    "retry_interval": self._retry_interval,
                    "history_days": self._history_days
                })

                # 启动任务
                self._scheduler.print_jobs()
                self._scheduler.start()

        except Exception as e:
            logger.error(f"fnossign初始化错误: {str(e)}", exc_info=True)

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
        
        logger.info("============= 开始签到 =============")
        notification_sent = False  # 标记是否已发送通知
        sign_dict = None
        sign_status = None  # 记录签到状态
        
        # 根据重试情况记录日志
        if retry_count > 0:
            logger.info(f"当前为第{retry_count}次常规重试")
        if extended_retry > 0:
            logger.info(f"当前为第{extended_retry}次延长重试")
        
        try:
            # 检查是否今日已成功签到（通过记录）
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
                        "fnb": last_success.get("fnb"),
                        "nz": last_success.get("nz"),
                        "credit": last_success.get("credit"),
                        "login_days": last_success.get("login_days")
                    })
                
                # 发送通知 - 通知用户已经签到过了
                if self._notify:
                    last_sign_time = self._get_last_sign_time()
                    
                    title = "【ℹ️ 飞牛论坛重复签到】"
                    text = (
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"📍 方式：{self._current_trigger_type}\n"
                        f"ℹ️ 状态：今日已完成签到 ({last_sign_time})\n"
                    )
                    
                    # 如果有积分信息，添加到通知中
                    if "fnb" in sign_dict and sign_dict["fnb"] is not None:
                        text += (
                            f"━━━━━━━━━━\n"
                            f"📊 积分统计\n"
                            f"💎 飞牛币：{sign_dict.get('fnb', '—')}\n"
                            f"🔥 牛  值：{sign_dict.get('nz', '—')}\n"
                            f"✨ 积  分：{sign_dict.get('credit', '—')}\n"
                            f"📆 签到天数：{sign_dict.get('login_days', '—')}\n"
                        )
                    
                    text += f"━━━━━━━━━━"
                    
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title=title,
                        text=text
                    )
                
                return sign_dict
            
            # 解析Cookie
            cookies = {}
            if self._cookie:
                try:
                    for cookie_item in self._cookie.split(';'):
                        if '=' in cookie_item:
                            name, value = cookie_item.strip().split('=', 1)
                            cookies[name] = value
                    
                    # 检查必要的Cookie值
                    required_cookies = ["pvRK_2132_saltkey", "pvRK_2132_auth"]
                    missing_cookies = [c for c in required_cookies if c not in cookies]
                    
                    if missing_cookies:
                        logger.error(f"Cookie中缺少必要的值: {', '.join(missing_cookies)}")
                        sign_dict = {
                            "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                            "status": "签到失败: Cookie无效，缺少必要值",
                        }
                        self._save_sign_history(sign_dict)
                        
                        if self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【飞牛论坛签到失败】",
                                text=f"❌ Cookie无效，缺少必要值: {', '.join(missing_cookies)}"
                            )
                            notification_sent = True
                        return sign_dict
                    
                    logger.info(f"成功提取必要的Cookie值: {', '.join(required_cookies)}")
                    logger.info(f"使用Cookie长度: {len(self._cookie)} 字符")
                except Exception as e:
                    logger.error(f"解析Cookie时出错: {str(e)}")
                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": "签到失败: Cookie解析错误",
                    }
                    self._save_sign_history(sign_dict)
                    
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到失败】",
                            text=f"❌ Cookie解析错误: {str(e)}"
                        )
                        notification_sent = True
                    return sign_dict
            else:
                logger.error("未配置Cookie")
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 未配置Cookie",
                }
                self._save_sign_history(sign_dict)
                
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【飞牛论坛签到失败】",
                        text="❌ 未配置Cookie，请在设置中添加Cookie"
                    )
                    notification_sent = True
                return sign_dict
            
            # 检查今日是否已签到
            logger.info("今日尚未成功签到")
            
            # 设置请求头和会话
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Referer": "https://club.fnnas.com/",
                "DNT": "1"
            }
            
            # 创建session并添加重试机制
            session = requests.Session()
            session.headers.update(headers)
            session.cookies.update(cookies)
            
            # 添加重试机制
            retry = requests.adapters.Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = requests.adapters.HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            # 验证 Cookie 是否有效；ESA 挑战不能再被误判为 Cookie 失效。
            cookie_check = "invalid"
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    # 使用Future和超时机制
                    future = executor.submit(self._check_cookie_valid, session)
                    try:
                        cookie_check = future.result(timeout=15)  # 15秒超时
                    except TimeoutError:
                        logger.error("检查Cookie有效性超时")
                        cookie_check = "invalid"
            except Exception as e:
                logger.error(f"检查Cookie时出现异常: {str(e)}")
                cookie_check = "invalid"
            
            if cookie_check == "js_challenge":
                browser_result = self._pass_esa_js_challenge(session)
                if browser_result == "passed":
                    cookie_check = self._check_cookie_valid(session)
                else:
                    cookie_check = browser_result

            if cookie_check != "valid":
                if cookie_check in ("slider_challenge", "js_challenge", "browser_unavailable", "browser_failed"):
                    return self._stop_for_forum_verification(cookie_check)

                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: Cookie无效或已过期",
                }
                self._save_sign_history(sign_dict)
                
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【飞牛论坛签到失败】",
                        text="❌ Cookie无效或已过期，请更新Cookie"
                    )
                    notification_sent = True
                return sign_dict
            
            # 步骤1: 访问签到页面获取sign参数
            logger.info("正在访问论坛首页...")
            try:
                # 设置较短的超时时间，避免卡住
                session.get("https://club.fnnas.com/", timeout=(3, 10))
            except requests.Timeout:
                logger.warning("访问论坛首页超时，尝试重试...")
                # 首页访问超时时尝试重试
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到重试】",
                            text=f"❗ 访问论坛首页超时，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)
                # 延长重试逻辑
                elif extended_retry < 2:
                    delay = 300  # 5分钟延迟
                    next_retry = extended_retry + 1
                    logger.info(f"已达最大常规重试次数，将在{delay}秒后进行第{next_retry}次延长重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到延长重试】",
                            text=f"⚠️ 常规重试{self._max_retries}次后首页仍访问超时，将在5分钟后进行第{next_retry}次延长重试"
                        )
                    
                    # 确保清理之前可能存在的延长重试任务
                    self._clear_extended_retry_tasks()
                    
                    # 安排延迟任务
                    scheduler = BackgroundScheduler(timezone=settings.TZ)
                    retry_job_id = f"fnossign_extended_retry_{next_retry}"
                    scheduler.add_job(
                        func=self.sign,
                        trigger='date',
                        id=retry_job_id,
                        run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=delay),
                        args=[0, next_retry],
                        name=f"飞牛论坛签到延长重试{next_retry}"
                    )
                    scheduler.start()
                    
                    # 记录当前重试任务ID
                    self.save_data('current_retry_task', retry_job_id)
                    
                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": f"首页访问超时: 已安排{next_retry}次延长重试",
                    }
                    self._save_sign_history(sign_dict)
                    return sign_dict
                
                # 所有重试都失败
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 首页多次访问超时",
                }
                self._save_sign_history(sign_dict)
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 飞牛论坛签到失败】",
                        text="❌ 访问论坛首页多次超时，所有重试均失败，请检查网络连接或站点状态"
                    )
                    notification_sent = True
                return sign_dict
            except Exception as e:
                logger.warning(f"访问论坛首页出错: {str(e)}，尝试重试...")
                # 首页访问出错时尝试重试
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到重试】",
                            text=f"❗ 访问论坛首页出错: {str(e)}，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)
                elif extended_retry < 2:
                    # 延长重试逻辑...省略与上面相同的代码
                    delay = 300  # 5分钟延迟
                    next_retry = extended_retry + 1
                    logger.info(f"已达最大常规重试次数，将在{delay}秒后进行第{next_retry}次延长重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到延长重试】",
                            text=f"⚠️ 常规重试{self._max_retries}次后首页访问仍出错，将在5分钟后进行第{next_retry}次延长重试"
                        )
                    
                    # 确保清理之前可能存在的延长重试任务
                    self._clear_extended_retry_tasks()
                    
                    # 安排延迟任务
                    scheduler = BackgroundScheduler(timezone=settings.TZ)
                    retry_job_id = f"fnossign_extended_retry_{next_retry}"
                    scheduler.add_job(
                        func=self.sign,
                        trigger='date',
                        id=retry_job_id,
                        run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=delay),
                        args=[0, next_retry],
                        name=f"飞牛论坛签到延长重试{next_retry}"
                    )
                    scheduler.start()
                    
                    # 记录当前重试任务ID
                    self.save_data('current_retry_task', retry_job_id)
                    
                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": f"首页访问错误: 已安排{next_retry}次延长重试",
                    }
                    self._save_sign_history(sign_dict)
                    return sign_dict
                
                # 所有重试都失败
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": f"签到失败: 首页多次访问出错 - {str(e)}",
                }
                self._save_sign_history(sign_dict)
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 飞牛论坛签到失败】",
                        text=f"❌ 访问论坛首页多次出错: {str(e)}，所有重试均失败"
                    )
                    notification_sent = True
                return sign_dict
            
            logger.info("正在访问签到页面...")
            sign_page_url = "https://club.fnnas.com/plugin.php?id=zqlj_sign"
            try:
                response = session.get(sign_page_url, timeout=(3, 10))
                html_content = response.text
            except requests.Timeout:
                logger.error("访问签到页面超时")
                # 常规重试逻辑
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到重试】",
                            text=f"❗ 访问签到页面超时，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)
                # 延长重试逻辑
                elif extended_retry < 2:
                    delay = 300  # 5分钟延迟
                    next_retry = extended_retry + 1
                    logger.info(f"已达最大常规重试次数，将在{delay}秒后进行第{next_retry}次延长重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到延长重试】",
                            text=f"⚠️ 常规重试{self._max_retries}次后仍失败，将在5分钟后进行第{next_retry}次延长重试"
                        )
                    
                    # 确保清理之前可能存在的延长重试任务
                    self._clear_extended_retry_tasks()
                    
                    # 安排延迟任务
                    scheduler = BackgroundScheduler(timezone=settings.TZ)
                    retry_job_id = f"fnossign_extended_retry_{next_retry}"
                    scheduler.add_job(
                        func=self.sign,
                        trigger='date',
                        id=retry_job_id,
                        run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=delay),
                        args=[0, next_retry],
                        name=f"飞牛论坛签到延长重试{next_retry}"
                    )
                    scheduler.start()
                    
                    # 记录当前重试任务ID
                    self.save_data('current_retry_task', retry_job_id)
                    
                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": f"签到超时: 已安排{next_retry}次延长重试",
                    }
                    self._save_sign_history(sign_dict)
                    return sign_dict
                
                # 所有重试都失败
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 所有重试均超时",
                }
                self._save_sign_history(sign_dict)
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 飞牛论坛签到失败】",
                        text="❌ 访问签到页面多次超时，所有重试均已失败，请检查网络连接或站点状态"
                    )
                    notification_sent = True
                return sign_dict

            challenge = self._classify_esa_challenge(html_content)
            if challenge == "js_challenge":
                browser_result = self._pass_esa_js_challenge(session)
                if browser_result == "passed":
                    response = session.get(sign_page_url, timeout=(3, 10))
                    html_content = response.text
                    challenge = self._classify_esa_challenge(html_content)
                else:
                    challenge = browser_result
            if challenge:
                return self._stop_for_forum_verification(challenge)
            
            # 检查是否已经签到
            if "您今天已经打过卡了" in html_content:
                logger.info("今日已签到")
                sign_status = "已签到"
                
                # 先保存一个基本记录，即使后续获取积分信息失败也有记录
                basic_sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": sign_status
                }
                self._save_last_sign_date()
                
                # 尝试获取积分信息
                try:
                    sign_dict = self._get_credit_info_and_create_record(session, sign_status)
                    
                    # 发送通知
                    if self._notify:
                        self._send_sign_notification(sign_dict)
                        notification_sent = True
                except Exception as e:
                    logger.error(f"处理已签到状态时发生错误: {str(e)}", exc_info=True)
                    
                    # 如果获取积分信息失败，尝试单独再次获取
                    logger.info("尝试单独获取积分信息...")
                    try:
                        credit_info = self._get_credit_info(session)
                        if credit_info:
                            # 更新之前保存的基本记录
                            basic_sign_dict.update({
                                "fnb": credit_info.get("fnb", 0),
                                "nz": credit_info.get("nz", 0),
                                "credit": credit_info.get("jf", 0),
                                "login_days": credit_info.get("ts", 0)
                            })
                            self._save_sign_history(basic_sign_dict)
                            sign_dict = basic_sign_dict
                            
                            # 发送包含积分信息的通知
                            if self._notify and not notification_sent:
                                self._send_sign_notification(sign_dict)
                                notification_sent = True
                        else:
                            # 如果还是获取不到积分信息，发送基本通知
                            self._save_sign_history(basic_sign_dict)
                            if not notification_sent and self._notify:
                                self.post_message(
                                    mtype=NotificationType.SiteMessage,
                                    title="【✅ 飞牛论坛已签到】",
                                    text=f"今日已签到，但获取详细信息失败\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                notification_sent = True
                            sign_dict = basic_sign_dict
                    except Exception as e2:
                        logger.error(f"二次获取积分信息失败: {str(e2)}", exc_info=True)
                        self._save_sign_history(basic_sign_dict)
                        if not notification_sent and self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【✅ 飞牛论坛已签到】",
                                text=f"今日已签到，但获取详细信息失败\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            notification_sent = True
                        sign_dict = basic_sign_dict
                
                return sign_dict
            
            # 从页面中提取sign参数
            sign_match = re.search(r'sign&sign=(.+)" class="btna', html_content)
            if not sign_match:
                logger.error("未找到签到参数")
                
                # 常规重试逻辑
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到重试】",
                            text=f"❗ 未找到签到参数，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)
                # 延长重试逻辑
                elif extended_retry < 2:
                    delay = 300  # 5分钟延迟
                    next_retry = extended_retry + 1
                    logger.info(f"已达最大常规重试次数，将在{delay}秒后进行第{next_retry}次延长重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【飞牛论坛签到延长重试】",
                            text=f"⚠️ 常规重试{self._max_retries}次后仍未找到签到参数，将在5分钟后进行第{next_retry}次延长重试"
                        )
                    
                    # 确保清理之前可能存在的延长重试任务
                    self._clear_extended_retry_tasks()
                    
                    # 安排延迟任务
                    scheduler = BackgroundScheduler(timezone=settings.TZ)
                    retry_job_id = f"fnossign_extended_retry_{next_retry}"
                    scheduler.add_job(
                        func=self.sign,
                        trigger='date',
                        id=retry_job_id,
                        run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=delay),
                        args=[0, next_retry],
                        name=f"飞牛论坛签到延长重试{next_retry}"
                    )
                    scheduler.start()
                    
                    # 记录当前重试任务ID
                    self.save_data('current_retry_task', retry_job_id)
                    
                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": f"签到失败: 已安排{next_retry}次延长重试",
                    }
                    self._save_sign_history(sign_dict)
                    return sign_dict
                
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 所有重试后仍未找到签到参数",
                }
                self._save_sign_history(sign_dict)
                
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 飞牛论坛签到失败】",
                        text="❌ 签到失败: 所有重试后仍未找到签到参数，请检查站点是否变更"
                    )
                    notification_sent = True
                return sign_dict
            
            sign_param = sign_match.group(1)
            logger.info(f"找到签到按钮 (匹配规则: '签到')")
            
            # 步骤2: 使用提取的sign参数执行签到
            logger.info("正在执行签到...")
            sign_url = f"https://club.fnnas.com/plugin.php?id=zqlj_sign&sign={sign_param}"
            
            # 更新Referer头
            session.headers.update({"Referer": sign_page_url})
            
            response = session.get(sign_url, timeout=(5, 15))
            html_content = response.text

            challenge = self._classify_esa_challenge(html_content)
            if challenge == "js_challenge":
                browser_result = self._pass_esa_js_challenge(session)
                if browser_result == "passed":
                    response = session.get(sign_url, timeout=(5, 15))
                    html_content = response.text
                    challenge = self._classify_esa_challenge(html_content)
                else:
                    challenge = browser_result
            if challenge:
                return self._stop_for_forum_verification(challenge)
            
            # 储存响应以便调试
            debug_resp = html_content[:500]
            logger.info(f"签到响应内容预览: {debug_resp}")
            
            # 检查签到结果
            success_flag = False
            if "恭喜您，打卡成功" in html_content or "打卡成功" in html_content:
                logger.info("签到成功")
                sign_status = "签到成功"
                success_flag = True
                
                # 先保存一个基本记录，即使后续获取积分信息失败也有记录
                basic_sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": sign_status
                }
                self._save_last_sign_date()
                
                # 尝试获取积分信息
                try:
                    sign_dict = self._get_credit_info_and_create_record(session, sign_status)
                    
                    # 发送通知
                    if self._notify:
                        self._send_sign_notification(sign_dict)
                        notification_sent = True
                except Exception as e:
                    logger.error(f"处理签到成功状态时发生错误: {str(e)}", exc_info=True)
                    
                    # 如果获取积分信息失败，尝试单独再次获取
                    logger.info("尝试单独获取积分信息...")
                    try:
                        credit_info = self._get_credit_info(session)
                        if credit_info:
                            # 更新之前保存的基本记录
                            basic_sign_dict.update({
                                "fnb": credit_info.get("fnb", 0),
                                "nz": credit_info.get("nz", 0),
                                "credit": credit_info.get("jf", 0),
                                "login_days": credit_info.get("ts", 0)
                            })
                            self._save_sign_history(basic_sign_dict)
                            sign_dict = basic_sign_dict
                            
                            # 发送包含积分信息的通知
                            if self._notify and not notification_sent:
                                self._send_sign_notification(sign_dict)
                                notification_sent = True
                        else:
                            # 如果还是获取不到积分信息，发送基本通知
                            self._save_sign_history(basic_sign_dict)
                            if not notification_sent and self._notify:
                                self.post_message(
                                    mtype=NotificationType.SiteMessage,
                                    title="【✅ 飞牛论坛签到成功】",
                                    text=f"签到成功，但获取详细信息失败\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                notification_sent = True
                            sign_dict = basic_sign_dict
                    except Exception as e2:
                        logger.error(f"二次获取积分信息失败: {str(e2)}", exc_info=True)
                        self._save_sign_history(basic_sign_dict)
                        if not notification_sent and self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【✅ 飞牛论坛签到成功】",
                                text=f"签到成功，但获取详细信息失败\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            notification_sent = True
                        sign_dict = basic_sign_dict
                
                return sign_dict
                
            elif "您今天已经打过卡了" in html_content:
                logger.info("今日已签到")
                sign_status = "已签到"
                
                # 先保存一个基本记录，即使后续获取积分信息失败也有记录
                basic_sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": sign_status
                }
                self._save_last_sign_date()
                
                # 尝试获取积分信息
                try:
                    sign_dict = self._get_credit_info_and_create_record(session, sign_status)
                    
                    # 发送通知
                    if self._notify:
                        self._send_sign_notification(sign_dict)
                        notification_sent = True
                except Exception as e:
                    logger.error(f"处理已签到状态时发生错误: {str(e)}", exc_info=True)
                    
                    # 如果获取积分信息失败，尝试单独再次获取
                    logger.info("尝试单独获取积分信息...")
                    try:
                        credit_info = self._get_credit_info(session)
                        if credit_info:
                            # 更新之前保存的基本记录
                            basic_sign_dict.update({
                                "fnb": credit_info.get("fnb", 0),
                                "nz": credit_info.get("nz", 0),
                                "credit": credit_info.get("jf", 0),
                                "login_days": credit_info.get("ts", 0)
                            })
                            self._save_sign_history(basic_sign_dict)
                            sign_dict = basic_sign_dict
                            
                            # 发送包含积分信息的通知
                            if self._notify and not notification_sent:
                                self._send_sign_notification(sign_dict)
                                notification_sent = True
                        else:
                            # 如果还是获取不到积分信息，发送基本通知
                            self._save_sign_history(basic_sign_dict)
                            if not notification_sent and self._notify:
                                self.post_message(
                                    mtype=NotificationType.SiteMessage,
                                    title="【飞牛论坛已签到】",
                                    text=f"今日已签到，但获取详细信息失败\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                notification_sent = True
                            sign_dict = basic_sign_dict
                    except Exception as e2:
                        logger.error(f"二次获取积分信息失败: {str(e2)}", exc_info=True)
                        self._save_sign_history(basic_sign_dict)
                        if not notification_sent and self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【飞牛论坛已签到】",
                                text=f"今日已签到，但获取详细信息失败\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            notification_sent = True
                        sign_dict = basic_sign_dict
                
                return sign_dict
            else:
                # 签到可能失败
                logger.error(f"签到请求发送成功，但结果异常: {debug_resp}")
                
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
                            title="【❌ 飞牛论坛签到失败】",
                            text="❌ 签到执行超时，已强制终止，请检查网络或站点状态"
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
                        title="【❌ 飞牛论坛签到失败】",
                        text="❌ 签到执行超时，已强制终止，请检查网络或站点状态"
                    )
                    notification_sent = True
                
                return sign_dict
        finally:
            # 确保在退出前关闭会话
            try:
                if 'session' in locals() and session:
                    session.close()
            except:
                pass

    def _get_credit_info_and_create_record(self, session, status):
        """获取积分信息并创建签到记录"""
        try:
            # 步骤3: 获取积分信息
            credit_info = self._get_credit_info(session)
            
            # 创建签到记录
            sign_dict = {
                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": status,
                "fnb": credit_info.get("fnb", 0),
                "nz": credit_info.get("nz", 0),
                "credit": credit_info.get("jf", 0),
                "login_days": credit_info.get("ts", 0)
            }
            
            # 保存签到记录
            self._save_sign_history(sign_dict)
            
            # 记录最后一次成功签到的日期
            if "签到成功" in status or "已签到" in status:
                self._save_last_sign_date()
            
            return sign_dict
        except Exception as e:
            logger.error(f"获取积分信息并创建记录失败: {str(e)}", exc_info=True)
            # 创建一个基本记录
            sign_dict = {
                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": status
            }
            # 尝试保存基本记录
            try:
                self._save_sign_history(sign_dict)
                if "签到成功" in status or "已签到" in status:
                    self._save_last_sign_date()
            except Exception as save_error:
                logger.error(f"保存基本签到记录失败: {str(save_error)}")
                
            return sign_dict

    def _get_credit_info(self, session):
        """
        获取积分信息并解析
        """
        try:
            # 访问正确的积分页面
            credit_url = "https://club.fnnas.com/home.php?mod=spacecp&ac=credit&showcredit=1"
            response = session.get(credit_url, timeout=(5, 15))  # 添加超时参数
            response.raise_for_status()
            
            # 检查是否重定向到登录页
            if "您需要先登录才能继续本操作" in response.text or "请先登录后才能继续浏览" in response.text:
                logger.error("获取积分信息失败：需要登录")
                return {}  # 返回空字典，表示获取失败
            
            html_content = response.text
            
            # 创建积分信息字典
            credit_info = {}
            
            # 基于实际HTML结构创建精确的匹配模式
            # 首先尝试提取整个积分区块
            credit_block_pattern = r'<ul class="creditl mtm bbda cl">.*?</ul>'
            credit_block_match = re.search(credit_block_pattern, html_content, re.DOTALL)
            
            if credit_block_match:
                credit_block = credit_block_match.group(0)
                logger.info("成功找到积分信息区块")
                
                # 从区块中提取各项积分
                # 飞牛币
                fnb_pattern = r'<em>\s*飞牛币:\s*</em>(\d+)'
                fnb_match = re.search(fnb_pattern, credit_block)
                if fnb_match:
                    credit_info["fnb"] = int(fnb_match.group(1))
                    logger.info(f"成功提取飞牛币: {credit_info['fnb']}")
                
                # 牛值
                nz_pattern = r'<em>\s*牛值:\s*</em>(\d+)'
                nz_match = re.search(nz_pattern, credit_block)
                if nz_match:
                    credit_info["nz"] = int(nz_match.group(1))
                    logger.info(f"成功提取牛值: {credit_info['nz']}")
                
                # 登陆天数
                ts_pattern = r'<em>\s*登陆天数:\s*</em>(\d+)'
                ts_match = re.search(ts_pattern, credit_block)
                if ts_match:
                    credit_info["ts"] = int(ts_match.group(1))
                    logger.info(f"成功提取登陆天数: {credit_info['ts']}")
                
                # 积分
                jf_pattern = r'<em>\s*积分:\s*</em>(\d+)'
                jf_match = re.search(jf_pattern, credit_block)
                if jf_match:
                    credit_info["jf"] = int(jf_match.group(1))
                    logger.info(f"成功提取积分: {credit_info['jf']}")
            else:
                logger.warning("未找到积分信息区块，尝试使用备用方法")
                
                # 备用方法：直接在整个页面中搜索
                # 飞牛币
                fnb_patterns = [
                    r'<em>\s*飞牛币:\s*</em>(\d+)',
                    r'飞牛币:\s*(\d+)',
                    r'飞牛币</em>\s*(\d+)'
                ]
                
                for pattern in fnb_patterns:
                    fnb_match = re.search(pattern, html_content, re.DOTALL)
                    if fnb_match:
                        credit_info["fnb"] = int(fnb_match.group(1))
                        logger.info(f"通过备用方法找到飞牛币: {credit_info['fnb']}")
                        break
                
                # 牛值
                nz_patterns = [
                    r'<em>\s*牛值:\s*</em>(\d+)',
                    r'牛值:\s*(\d+)',
                    r'牛值</em>\s*(\d+)'
                ]
                
                for pattern in nz_patterns:
                    nz_match = re.search(pattern, html_content, re.DOTALL)
                    if nz_match:
                        credit_info["nz"] = int(nz_match.group(1))
                        logger.info(f"通过备用方法找到牛值: {credit_info['nz']}")
                        break
                
                # 登陆天数
                ts_patterns = [
                    r'<em>\s*登陆天数:\s*</em>(\d+)',
                    r'登陆天数:\s*(\d+)',
                    r'登陆天数</em>\s*(\d+)'
                ]
                
                for pattern in ts_patterns:
                    ts_match = re.search(pattern, html_content, re.DOTALL)
                    if ts_match:
                        credit_info["ts"] = int(ts_match.group(1))
                        logger.info(f"通过备用方法找到登陆天数: {credit_info['ts']}")
                        break
                
                # 积分
                jf_patterns = [
                    r'<em>\s*积分:\s*</em>(\d+)',
                    r'积分:\s*(\d+)',
                    r'积分</em>\s*(\d+)'
                ]
                
                for pattern in jf_patterns:
                    jf_match = re.search(pattern, html_content, re.DOTALL)
                    if jf_match:
                        credit_info["jf"] = int(jf_match.group(1))
                        logger.info(f"通过备用方法找到积分: {credit_info['jf']}")
                        break
            
            # 检查是否成功提取了所有积分信息
            required_fields = ["fnb", "nz", "ts", "jf"]
            missing_fields = [field for field in required_fields if field not in credit_info]
            
            if missing_fields:
                logger.error(f"积分信息提取不完整，缺少以下字段: {', '.join(missing_fields)}")
                
                # 不返回默认值，而是返回已成功提取的值，缺失的值保持为空
                return credit_info
            
            logger.info(f"成功获取所有积分信息: 飞牛币={credit_info.get('fnb')}, 牛值={credit_info.get('nz')}, "
                      f"积分={credit_info.get('jf')}, 登录天数={credit_info.get('ts')}")
            
            return credit_info
            
        except requests.RequestException as request_exception:
            logger.error(f"获取积分信息网络错误: {str(request_exception)}")
            return {}  # 返回空字典，表示获取失败
            
        except Exception as e:
            logger.error(f"获取积分信息失败: {str(e)}", exc_info=True)
            return {}  # 返回空字典，表示获取失败

    def _log_user_info(self):
        """读取账号资料，并将允许的账号找回信息输出到日志。"""
        logger.info("============= 开始获取飞牛论坛用户信息 =============")
        if not self._cookie:
            logger.error("获取用户信息失败：未配置Cookie")
            return

        session = requests.Session()
        try:
            session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://club.fnnas.com/"
            })
            session.cookies.update(self._extract_required_cookies(self._cookie))

            profile_response = session.get(
                "https://club.fnnas.com/home.php?mod=spacecp&ac=profile",
                timeout=(5, 15)
            )
            password_response = session.get(
                "https://club.fnnas.com/home.php?mod=spacecp&ac=profile&op=password",
                timeout=(5, 15)
            )
            profile_response.raise_for_status()
            password_response.raise_for_status()

            combined_html = profile_response.text + password_response.text
            if (
                "您需要先登录才能继续本操作" in combined_html
                or "请先登录后才能继续浏览" in combined_html
            ):
                logger.error("获取用户信息失败：Cookie无效或已过期")
                return

            username = (
                self._extract_input_value(profile_response.text, "username")
                or self._extract_labeled_value(profile_response.text, "用户名")
            )
            uid_match = re.search(
                r'home\.php\?mod=space(?:&amp;|&)uid=(\d+)',
                profile_response.text,
                re.IGNORECASE
            )
            if not uid_match:
                uid_match = re.search(
                    r"\bdiscuz_uid\s*=\s*['\"](\d+)['\"]",
                    profile_response.text,
                    re.IGNORECASE
            )
            uid = uid_match.group(1) if uid_match else ""

            email = self._extract_input_value(password_response.text, "emailnew")
            phone_prefix = self._extract_input_value(
                password_response.text,
                "secmobiccnew"
            )
            phone = self._extract_input_value(
                password_response.text,
                "secmobilenew"
            )

            display_phone = phone
            if phone and phone_prefix:
                display_phone = f"+{phone_prefix} {phone}"

            logger.info("============= 飞牛论坛用户信息 =============")
            logger.info(f"用户名: {username or '未获取到'}")
            logger.info(f"用户UID: {uid or '未获取到'}")
            logger.info(f"邮箱: {email or '未获取到'}")
            logger.info(f"手机号: {display_phone or '未获取到'}")
            logger.info("============= 用户信息输出完成 =============")
        except requests.RequestException as e:
            logger.error(f"获取用户信息网络错误: {str(e)}")
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}", exc_info=True)
        finally:
            session.close()

    @staticmethod
    def _extract_input_value(html_content, field_name):
        """按明确的字段名读取输入框，避免接触密码等无关字段。"""
        input_match = re.search(
            rf'<input\b(?=[^>]*\bname=["\']{re.escape(field_name)}["\'])[^>]*>',
            html_content,
            re.IGNORECASE | re.DOTALL
        )
        if not input_match:
            return ""
        value_match = re.search(
            r'\bvalue=(["\'])(.*?)\1',
            input_match.group(0),
            re.IGNORECASE | re.DOTALL
        )
        return unescape(value_match.group(2)).strip() if value_match else ""

    @staticmethod
    def _extract_labeled_value(html_content, label):
        """从“表头标签 + 单元格值”的Discuz资料行中读取文本。"""
        value_match = re.search(
            rf"<th\b[^>]*>(?:(?!</th>).)*?{re.escape(label)}"
            rf"(?:(?!</th>).)*?</th>\s*<td\b[^>]*>(.*?)</td>",
            html_content,
            re.IGNORECASE | re.DOTALL
        )
        if not value_match:
            return ""

        value_html = re.sub(
            r"<(?:script|style)\b[^>]*>.*?</(?:script|style)>",
            "",
            value_match.group(1),
            flags=re.IGNORECASE | re.DOTALL
        )
        value = unescape(re.sub(r"<[^>]+>", "", value_html))
        return re.sub(r"\s+", " ", value).strip()

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

    def _send_sign_notification(self, sign_dict):
        """
        发送签到通知
        """
        if not self._notify:
            return
            
        status = sign_dict.get("status", "未知")
        fnb = sign_dict.get("fnb", "—")
        nz = sign_dict.get("nz", "—")
        credit = sign_dict.get("credit", "—")
        login_days = sign_dict.get("login_days", "—")
        sign_time = sign_dict.get("date", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 检查积分信息是否为空
        credits_missing = fnb == "—" and nz == "—" and credit == "—" and login_days == "—"
        
        # 获取触发方式
        trigger_type = self._current_trigger_type
        
        # 构建通知文本
        if "签到成功" in status:
            title = "【✅ 飞牛论坛签到成功】"
            
            if credits_missing:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"⚠️ 积分信息获取失败，请手动查看\n"
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
                    f"📊 积分统计\n"
                    f"💎 飞牛币：{fnb}\n"
                    f"🔥 牛  值：{nz}\n"
                    f"✨ 积  分：{credit}\n"
                    f"📆 签到天数：{login_days}\n"
                    f"━━━━━━━━━━"
                )
        elif "已签到" in status:
            title = "【ℹ️ 飞牛论坛重复签到】"
            
            if credits_missing:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"ℹ️ 说明：今日已完成签到\n"
                    f"⚠️ 积分信息获取失败，请手动查看\n"
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
                    f"📊 积分统计\n"
                    f"💎 飞牛币：{fnb}\n"
                    f"🔥 牛  值：{nz}\n"
                    f"✨ 积  分：{credit}\n"
                    f"📆 签到天数：{login_days}\n"
                    f"━━━━━━━━━━"
                )
        else:
            title = "【❌ 飞牛论坛签到失败】"
            text = (
                f"📢 执行结果\n"
                f"━━━━━━━━━━\n"
                f"🕐 时间：{sign_time}\n"
                f"📍 方式：{trigger_type}\n"
                f"❌ 状态：{status}\n"
                f"━━━━━━━━━━\n"
                f"💡 可能的解决方法\n"
                f"• 检查Cookie是否过期\n"
                f"• 确认站点是否可访问\n"
                f"• 检查是否需要验证码\n"
                f"• 尝试手动登录网站\n"
                f"━━━━━━━━━━\n"
                f"⚡ 插件将在下次执行时重试"
            )
            
        # 发送通知
        self.post_message(
            mtype=NotificationType.SiteMessage,
            title=title,
            text=text
        )

    def get_state(self) -> bool:
        logger.info(f"fnossign状态: {self._enabled}")
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")
            return [{
                "id": "fnossign",
                "name": "飞牛论坛签到",
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
                                            'model': 'onlyonce',
                                            'label': '立即运行一次',
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
                                            'model': 'log_profile_once',
                                            'label': '输出用户信息一次',
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
                                            'placeholder': '请输入站点Cookie值'
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
                                            'text': '【使用教程】\n1. 登录飞牛论坛网站，按F12打开开发者工具\n2. 在"网络"或"应用"选项卡中复制Cookie\n3. 粘贴Cookie到上方输入框\n4. 设置签到时间，建议早上8点(0 8 * * *)\n5. 启用插件并保存\n\n开启通知可在签到后收到结果通知，也可随时查看签到历史页面。遇普通 ESA JS 验证会自动调用 MoviePilot 无头浏览器；遇人工滑块时插件不闯关、不过盾，会停止并通知。\n“输出用户信息一次”会把用户名、UID、邮箱和手机号以明文写入日志，保存后自动关闭。'
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
            "log_profile_once": False,
            "cookie": "",
            "cron": "0 8 * * *",
            "max_retries": 3,
            "retry_interval": 30,
            "history_days": 30
        }

    def get_page(self) -> List[dict]:
        """
        构建插件详情页面，展示签到历史
        """
        # 获取签到历史
        historys = self.get_data('sign_history') or []
        
        # 如果没有历史记录
        if not historys:
            return [
                {
                    'component': 'VAlert',
                                                                    'props': {
                        'type': 'info',
                        'variant': 'tonal',
                        'text': '暂无签到记录，请先配置Cookie并启用插件',
                        'class': 'mb-2'
                    }
                }
            ]
        
        # 按时间倒序排列历史
        historys = sorted(historys, key=lambda x: x.get("date", ""), reverse=True)
        
        # 构建历史记录表格行
        history_rows = []
        for history in historys:
            status_text = history.get("status", "未知")
            status_color = "success" if status_text in ["签到成功", "已签到"] else "error"
            
            history_rows.append({
                'component': 'tr',
                'content': [
                    # 日期列
                    {
                        'component': 'td',
                                                            'props': {
                            'class': 'text-caption'
                                                            },
                        'text': history.get("date", "")
                    },
                    # 状态列
                    {
                        'component': 'td',
                                                            'content': [
                                                                {
                                'component': 'VChip',
                                                                    'props': {
                                    'color': status_color,
                                    'size': 'small',
                                    'variant': 'outlined'
                                },
                                'text': status_text
                            }
                        ]
                    },
                    # 飞牛币列
                    {
                        'component': 'td',
                        'text': f"{history.get('fnb', '—')} 💎" if "fnb" in history else "—"
                    },
                    # 牛值列
                    {
                        'component': 'td',
                        'text': f"{history.get('nz', '—')} 🔥" if "nz" in history else "—"
                    },
                    # 积分列
                    {
                        'component': 'td',
                        'text': f"{history.get('credit', '—')} ✨" if "credit" in history else "—"
                    },
                    # 登录天数列
                    {
                        'component': 'td',
                        'text': f"{history.get('login_days', '—')} 📆" if "login_days" in history else "—"
                    }
                ]
            })
        
        # 最终页面组装
        return [
            # 标题
                {
                    'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'text-h6'},
                        'text': '📊 飞牛论坛签到历史'
                    },
                    {
                        'component': 'VCardText',
                    'content': [
                        {
                                'component': 'VTable',
                            'props': {
                                    'hover': True,
                                    'density': 'compact'
                                },
                                'content': [
                                    # 表头
                                    {
                                        'component': 'thead',
                                        'content': [
                                            {
                                                'component': 'tr',
                                                'content': [
                                                    {'component': 'th', 'text': '时间'},
                                                    {'component': 'th', 'text': '状态'},
                                                    {'component': 'th', 'text': '飞牛币'},
                                                    {'component': 'th', 'text': '牛值'},
                                                    {'component': 'th', 'text': '积分'},
                                                    {'component': 'th', 'text': '登录天数'}
                                                ]
                                            }
                                        ]
                                    },
                                    # 表内容
                                    {
                                        'component': 'tbody',
                                        'content': history_rows
                                    }
                                ]
                            }
                        ]
                    }
                ]
                }
            ]

    def stop_service(self):
        """停止服务，清理所有任务"""
        try:
            # 清理当前插件的主定时任务
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
            
            # 清理所有延长重试任务
            self._clear_extended_retry_tasks()
            
            # 清除当前重试任务记录
            self.save_data('current_retry_task', None)
            
        except Exception as e:
            logger.error(f"退出插件失败: {str(e)}")
            
    def _clear_extended_retry_tasks(self):
        """清理所有延长重试任务"""
        try:
            # 查找所有fnossign_extended_retry开头的任务，并停止它们
            from apscheduler.schedulers.background import BackgroundScheduler
            import apscheduler.schedulers
            
            # 获取当前记录的延长重试任务ID
            current_retry_task = self.get_data('current_retry_task')
            if current_retry_task:
                logger.info(f"清理延长重试任务: {current_retry_task}")
                
                # 查找该任务并停止
                for scheduler in apscheduler.schedulers.schedulers:
                    if isinstance(scheduler, BackgroundScheduler) and scheduler.running:
                        for job in scheduler.get_jobs():
                            if job.id == current_retry_task:
                                logger.info(f"找到并移除延长重试任务: {job.id}")
                                job.remove()
                
                # 清除记录
                self.save_data('current_retry_task', None)
        except Exception as e:
            logger.error(f"清理延长重试任务失败: {str(e)}")
            
    def _has_running_extended_retry(self):
        """检查是否有正在运行的延长重试任务"""
        current_retry_task = self.get_data('current_retry_task')
        if not current_retry_task:
            return False
            
        try:
            # 检查该任务是否存在且未执行
            import apscheduler.schedulers
            for scheduler in apscheduler.schedulers.schedulers:
                if hasattr(scheduler, 'get_jobs'):
                    for job in scheduler.get_jobs():
                        if job.id == current_retry_task:
                            # 任务存在且未执行
                            next_run_time = job.next_run_time
                            if next_run_time and next_run_time > datetime.now(tz=pytz.timezone(settings.TZ)):
                                logger.info(f"发现正在运行的延长重试任务: {job.id}, 下次执行时间: {next_run_time}")
                                return True
            
            # 如果找不到任务或任务已执行，清除记录
            self.save_data('current_retry_task', None)
            return False
        except Exception as e:
            logger.error(f"检查延长重试任务状态失败: {str(e)}")
            # 出错时为安全起见，返回False
            return False

    def get_command(self) -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    @staticmethod
    def _classify_esa_challenge(html_content: str) -> Optional[str]:
        """识别 ESA 挑战页面，不把它当作 Cookie 过期。"""
        html = (html_content or "").lower()
        slider_markers = (
            "aliyuncaptcha-sliding",
            "aliyuncaptcha-window-embed",
            "waf_nc_block",
            "请按住滑块",
            "拖动到最右边",
            "acw_sc__v3",
        )
        if any(marker in html for marker in slider_markers):
            return "slider_challenge"

        js_markers = (
            "acw_sc__v2",
            "javascript challenge",
            "js challenge",
        )
        if any(marker in html for marker in js_markers):
            return "js_challenge"
        return None

    def _pass_esa_js_challenge(self, session) -> str:
        """使用 MoviePilot 的 CloakBrowser 完成 ESA 普通 JS Challenge 并同步 Cookie。"""
        if cloak_launch_context is None:
            logger.warning("检测到 ESA JS 验证，但当前 MoviePilot 未提供 CloakBrowser")
            return "browser_unavailable"

        context = None
        try:
            logger.info("检测到 ESA JS 验证，使用 MoviePilot 无头浏览器尝试正常访问论坛...")
            context = cloak_launch_context(
                headless=True,
                user_agent=session.headers.get("User-Agent"),
                humanize=getattr(settings, "CLOAKBROWSER_HUMANIZE", True),
                human_preset=getattr(settings, "CLOAKBROWSER_HUMAN_PRESET", "default"),
                viewport={"width": 1280, "height": 720},
            )
            context.add_cookies([
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "url": "https://club.fnnas.com/",
                }
                for cookie in session.cookies
            ])
            page = context.new_page()

            # 普通 JS Challenge 会自行跳转并下发 acw_sc__v2，最多等三次。
            for _ in range(3):
                page.goto("https://club.fnnas.com/", wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
                html_content = page.content()
                challenge = self._classify_esa_challenge(html_content)
                if challenge == "slider_challenge":
                    logger.warning("无头浏览器确认论坛要求人工滑块验证")
                    return challenge
                if challenge != "js_challenge" and "退出" in html_content:
                    for cookie in context.cookies("https://club.fnnas.com/"):
                        session.cookies.set(
                            cookie["name"],
                            cookie["value"],
                            domain=cookie.get("domain") or "club.fnnas.com",
                            path=cookie.get("path") or "/",
                        )
                    logger.info("ESA 普通 JS 验证已通过，继续本次签到")
                    return "passed"

            logger.warning("无头浏览器未能完成 ESA JS 验证")
            return "browser_failed"
        except Exception as e:
            logger.warning(f"调用 MoviePilot 无头浏览器处理 ESA 验证失败: {str(e)}")
            return "browser_failed"
        finally:
            if context:
                try:
                    context.close()
                except Exception:
                    pass

    def _stop_for_forum_verification(self, challenge: str) -> Dict[str, str]:
        """遇到人工验证时停止，不重试，也不将其归因为 Cookie 失效。"""
        if challenge == "slider_challenge":
            reason = "论坛要求人工滑块验证"
            text = "🛡️ 论坛门口来了位滑块小门卫。插件不闯关、不过盾，也不反复敲门；请先在浏览器完成验证后再试。"
        elif challenge == "browser_unavailable":
            reason = "论坛 JS 验证需要 MoviePilot 无头浏览器"
            text = "🛡️ 论坛派出了验证小门卫，但当前 MoviePilot 无头浏览器不可用。插件不闯关、不过盾；请检查 CloakBrowser 后再试。"
        else:
            reason = "论坛验证未放行"
            text = "🛡️ 论坛正在验明正身。插件已经请 MoviePilot 浏览器正常访问，但验证没有放行；插件不闯关、不过盾，也不重试。"

        logger.warning(f"签到暂停: {reason}。插件不会尝试绕过验证。")
        sign_dict = {
            "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            "status": f"签到暂停: {reason}",
        }
        self._save_sign_history(sign_dict)
        if self._notify:
            self.post_message(
                mtype=NotificationType.SiteMessage,
                title="【飞牛论坛签到暂停】",
                text=text,
            )
        return sign_dict

    def _check_cookie_valid(self, session) -> str:
        """检查 Cookie 是否有效，返回有效性或 ESA 验证状态。"""
        try:
            response = session.get("https://club.fnnas.com/", timeout=(3, 10))
            challenge = self._classify_esa_challenge(response.text)
            if challenge:
                logger.info(f"Cookie 检查命中 ESA 验证页面: {challenge}")
                return challenge
            if "退出" in response.text:
                try:
                    uid_match = re.search(r'uid=(\d+)', response.text)
                    if uid_match:
                        self._uid = uid_match.group(1)
                    else:
                        logger.warning("Cookie有效，但未找到UID")
                except Exception as e:
                    logger.warning(f"提取UID时出错: {str(e)}")
                return "valid"
            return "invalid"
        except Exception as e:
            logger.warning(f"检查Cookie有效性时出错: {str(e)}")
            return "invalid"

    def _extract_required_cookies(self, cookie_str):
        """从Cookie字符串中提取所需的值"""
        # 此方法保留，用于向下兼容，实际不再调用
        if not cookie_str:
            return {}
            
        cookies = {}
        try:
            for cookie_item in cookie_str.split(';'):
                if '=' in cookie_item:
                    name, value = cookie_item.strip().split('=', 1)
                    cookies[name] = value
        except Exception as e:
            logger.error(f"解析Cookie时出错: {str(e)}")
        
        return cookies

    def _is_manual_trigger(self):
        """
        检查是否为手动触发的签到
        手动触发的签到不应该被历史记录阻止
        """
        # 在调用堆栈中检查sign_in_api是否存在，若存在则为手动触发
        import inspect
        for frame in inspect.stack():
            if frame.function == 'sign_in_api':
                logger.info("检测到手动触发签到")
                return True
        
        if hasattr(self, '_manual_trigger') and self._manual_trigger:
            logger.info("检测到通过_onlyonce手动触发签到")
            self._manual_trigger = False
            return True
            
        return False

    def _is_already_signed_today(self):
        """
        检查今天是否已经成功签到过
        只有当今天已经成功签到时才返回True
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取历史记录
        history = self.get_data('sign_history') or []
        
        # 检查今天的签到记录
        today_records = [
            record for record in history 
            if record.get("date", "").startswith(today) 
            and record.get("status") in ["签到成功", "已签到"]
        ]
        
        if today_records:
            last_success = max(today_records, key=lambda x: x.get("date", ""))
            logger.info(f"今日已成功签到，时间: {last_success.get('date', '').split()[1]}")
            return True
            
        # 获取最后一次签到的日期和时间
        last_sign_date = self.get_data('last_sign_date')
        if last_sign_date:
            try:
                last_sign_datetime = datetime.strptime(last_sign_date, '%Y-%m-%d %H:%M:%S')
                last_sign_day = last_sign_datetime.strftime('%Y-%m-%d')
                
                # 如果最后一次签到是今天且是成功的
                if last_sign_day == today:
                    # 检查最后一条历史记录的状态
                    if history and history[-1].get("status") in ["签到成功", "已签到"]:
                        logger.info(f"今日已成功签到，时间: {last_sign_datetime.strftime('%H:%M:%S')}")
                        return True
                    else:
                        logger.info("今日虽有签到记录但未成功，将重试签到")
                        return False
            except Exception as e:
                logger.error(f"解析最后签到日期时出错: {str(e)}")
        
        logger.info("今日尚未成功签到")
        return False
        
    def _save_last_sign_date(self):
        """
        保存最后一次成功签到的日期和时间
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_data('last_sign_date', now)
        logger.info(f"记录签到成功时间: {now}") 

    def _get_last_sign_time(self):
        """获取上次签到的时间"""
        try:
            # 获取最后一次签到的日期和时间
            last_sign_date = self.get_data('last_sign_date')
            if last_sign_date:
                try:
                    last_sign_datetime = datetime.strptime(last_sign_date, '%Y-%m-%d %H:%M:%S')
                    return last_sign_datetime.strftime('%H:%M:%S')
                except Exception as e:
                    logger.error(f"解析最后签到日期时出错: {str(e)}")
            
            # 如果没有记录或解析出错，查找今日的成功签到记录
            history = self.get_data('sign_history') or []
            today = datetime.now().strftime('%Y-%m-%d')
            today_success = [
                record for record in history 
                if record.get("date", "").startswith(today) 
                and record.get("status") in ["签到成功", "已签到"]
            ]
            
            if today_success:
                last_success = max(today_success, key=lambda x: x.get("date", ""))
                try:
                    last_time = datetime.strptime(last_success.get("date", ""), '%Y-%m-%d %H:%M:%S')
                    return last_time.strftime('%H:%M:%S')
                except:
                    pass
            
            # 如果都没有找到，返回一个默认值
            return "今天早些时候"
        except Exception as e:
            logger.error(f"获取上次签到时间出错: {str(e)}")
            return "今天早些时候"

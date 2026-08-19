"""
阡陌居签到插件
版本: 1.0.0
作者: madrays
功能:
- 自动完成阡陌居每日签到
- 支持签到失败重试
- 保存签到历史记录
- 提供详细的签到通知
- 增强的错误处理和日志

修改记录:
- v1.1.2: 修复签到失败（“未定义操作”）：改用 https、补齐 qdmode/todaysay/fastreply 参数、优化响应解析
- v1.0.0: 初始版本，基于QD签到模板实现
"""
import time
import requests
import re
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


def _extract_sign_message(html_content: str) -> Optional[str]:
    """
    从 Discuz AJAX 响应（<root><![CDATA[...]]></root>）中提取提示消息文本。
    兼容 <div class="c"> 与 <div class="c altw">，并优先提取 alert_error/alert_right/alert_info。
    """
    def _clean(segment: str) -> str:
        # 去掉 script 标签及其内容，再去掉其余 HTML 标签
        segment = re.sub(r'<script.*?</script>', '', segment, flags=re.S)
        segment = re.sub(r'<[^>]+>', '', segment)
        return segment.strip()

    # 1) 优先提取 alert_xxx 中的消息
    alert_match = re.search(r'<div class="alert_(?:error|right|info)">(.*?)</div>', html_content, re.S)
    if alert_match:
        msg = _clean(alert_match.group(1))
        if msg:
            return msg

    # 2) 回退：提取 <div class="c"> 或 <div class="c altw"> 内容
    div_match = re.search(r'<div class="c(?: altw)?">(.*?)</div>', html_content, re.S)
    if div_match:
        msg = _clean(div_match.group(1))
        if msg:
            return msg

    return None


class QmjSign(_PluginBase):
    # 插件名称
    plugin_name = "阡陌居签到"
    # 插件描述
    plugin_desc = "自动完成阡陌居每日签到，支持失败重试和历史记录"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/qmj.ico"
    # 插件版本
    plugin_version = "1.1.2"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "qmjsign_"
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
    _draw_prestige_enabled = False  # 是否领取每日威望红包
    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None
    _current_trigger_type = None  # 保存当前执行的触发类型

    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()

        logger.info("============= qmjsign 初始化 =============")
        try:
            if config:
                self._enabled = config.get("enabled")
                self._cookie = config.get("cookie")
                self._notify = config.get("notify")
                self._cron = config.get("cron")
                self._onlyonce = config.get("onlyonce")
                self._max_retries = int(config.get("max_retries", 3))
                self._retry_interval = int(config.get("retry_interval", 30))
                self._history_days = int(config.get("history_days", 30))
                self._draw_prestige_enabled = bool(config.get("draw_prestige", False))
                logger.info(f"配置: enabled={self._enabled}, notify={self._notify}, cron={self._cron}, max_retries={self._max_retries}, retry_interval={self._retry_interval}, history_days={self._history_days}, draw_prestige={self._draw_prestige_enabled}")
            
            # 清理所有可能的延长重试任务
            self._clear_extended_retry_tasks()
            
            if self._onlyonce:
                logger.info("执行一次性签到")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._manual_trigger = True
                self._scheduler.add_job(func=self.sign, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="阡陌居签到")
                self._onlyonce = False
                self.update_config({
                    "onlyonce": False,
                    "enabled": self._enabled,
                    "cookie": self._cookie,
                    "notify": self._notify,
                    "cron": self._cron,
                    "max_retries": self._max_retries,
                    "retry_interval": self._retry_interval,
                    "history_days": self._history_days,
                    "draw_prestige": self._draw_prestige_enabled
                })

                # 启动任务
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()

        except Exception as e:
            logger.error(f"qmjsign初始化错误: {str(e)}", exc_info=True)

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
                
                # 即使已签到，也尝试领取每日威望红包
                try:
                    if getattr(self, "_draw_prestige_enabled", False):
                        logger.info("（已签到分支）开始领取每日威望红包任务...")
                        prestige_info = self._claim_daily_prestige_reward(None)
                        if prestige_info:
                            sign_dict.update(prestige_info)
                    else:
                        logger.info("领取每日威望红包已关闭，跳过此步骤")
                except Exception as e:
                    logger.warning(f"（已签到分支）领取每日威望红包出错（忽略）: {str(e)}")

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
                        "days": last_success.get("days"),
                        "coins_gain": last_success.get("coins_gain")
                    })
                
                # 发送通知 - 通知用户已经签到过了（附带威望信息）
                if self._notify:
                    last_sign_time = self._get_last_sign_time()
                    
                    title = "【ℹ️ 阡陌居重复签到】"
                    text = (
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"📍 方式：{self._current_trigger_type}\n"
                        f"ℹ️ 状态：今日已完成签到 ({last_sign_time})\n"
                        f"━━━━━━━━━━\n"
                        f"📊 签到信息\n"
                        f"💬 消息：{sign_dict.get('message', '—')}\n"
                        f"🪙 当日奖励：铜币 +{sign_dict.get('coins_gain', '—')} | 威望 +{sign_dict.get('prestige_gain', '—')}\n"
                    )
                    # 六项汇总
                    text += (
                        f"━━━━━━━━━━\n"
                        f"🧧 威望红包（汇总）\n"
                        f"🪙 铜币：{sign_dict.get('coins_total', '—')}\n"
                        f"🥇 威望：{sign_dict.get('prestige_total', '—')}\n"
                        f"🤝 贡献：{sign_dict.get('contribution_total', '—')}\n"
                        f"📚 发书数：{sign_dict.get('books_total', '—')}\n"
                        f"📈 积分：{sign_dict.get('credits_total', '—')}\n"
                        f"🏆 总积分：{sign_dict.get('credits_sum', '—')}\n"
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
                    
                    logger.info(f"成功解析Cookie，共 {len(cookies)} 个值")
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
                            title="【阡陌居签到失败】",
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
                        title="【阡陌居签到失败】",
                        text="❌ 未配置Cookie，请在设置中添加Cookie"
                    )
                    notification_sent = True
                return sign_dict
            
            # 检查今日是否已签到
            logger.info("今日尚未成功签到")
            
            # 设置请求头和会话
            headers = {
                "Host": "www.1000qm.vip",
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
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
            
            # 验证Cookie是否有效 - 增加超时保护
            cookie_valid = False
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    # 使用Future和超时机制
                    future = executor.submit(self._check_cookie_valid, session)
                    try:
                        cookie_valid = future.result(timeout=15)  # 15秒超时
                    except TimeoutError:
                        logger.error("检查Cookie有效性超时")
                        cookie_valid = False
            except Exception as e:
                logger.error(f"检查Cookie时出现异常: {str(e)}")
                cookie_valid = False
            
            if not cookie_valid:
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: Cookie无效或已过期",
                }
                self._save_sign_history(sign_dict)
                
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【阡陌居签到失败】",
                        text="❌ Cookie无效或已过期，请更新Cookie"
                    )
                    notification_sent = True
                return sign_dict

            # 领取每日威望红包（可选开关）
            prestige_info = None
            try:
                if getattr(self, "_draw_prestige_enabled", False):
                    logger.info("开始领取每日威望红包任务...")
                    prestige_info = self._claim_daily_prestige_reward(session)
                else:
                    logger.info("领取每日威望红包已关闭，跳过此步骤")
            except Exception as e:
                logger.warning(f"领取每日威望红包过程中出错（忽略继续签到）: {str(e)}")

            # 步骤1: 访问首页获取formhash参数
            logger.info("正在访问阡陌居首页...")
            try:
                # 设置较短的超时时间，避免卡住
                response = session.get("https://www.1000qm.vip/", timeout=(3, 10))
                html_content = response.text

                # 提取formhash参数
                formhash_match = re.search(r'name="formhash" value="(.+)"', html_content)
                if not formhash_match:
                    logger.error("未找到formhash参数")

                    # 常规重试逻辑
                    if retry_count < self._max_retries:
                        logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                        if self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【阡陌居签到重试】",
                                text=f"❗ 未找到formhash参数，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                            )
                        time.sleep(self._retry_interval)
                        return self.sign(retry_count + 1, extended_retry)

                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": "签到失败: 未找到formhash参数",
                    }
                    self._save_sign_history(sign_dict)

                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【❌ 阡陌居签到失败】",
                            text="❌ 签到失败: 未找到formhash参数，请检查站点是否变更"
                        )
                        notification_sent = True
                    return sign_dict

                formhash = formhash_match.group(1)
                logger.info(f"成功获取formhash: {formhash[:10]}...")

            except requests.Timeout:
                logger.error("访问阡陌居首页超时")
                # 常规重试逻辑
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【阡陌居签到重试】",
                            text=f"❗ 访问首页超时，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)

                # 所有重试都失败
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 首页多次访问超时",
                }
                self._save_sign_history(sign_dict)
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 阡陌居签到失败】",
                        text="❌ 访问首页多次超时，所有重试均失败，请检查网络连接或站点状态"
                    )
                    notification_sent = True
                return sign_dict
            except Exception as e:
                logger.warning(f"访问阡陌居首页出错: {str(e)}，尝试重试...")
                # 首页访问出错时尝试重试
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【阡陌居签到重试】",
                            text=f"❗ 访问首页出错: {str(e)}，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)

                # 所有重试都失败
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": f"签到失败: 首页多次访问出错 - {str(e)}",
                }
                self._save_sign_history(sign_dict)
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 阡陌居签到失败】",
                        text=f"❌ 访问首页多次出错: {str(e)}，所有重试均失败"
                    )
                    notification_sent = True
                return sign_dict

            # 步骤2: 执行签到
            logger.info("正在执行签到...")
            sign_url = "https://www.1000qm.vip/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1"

            # 准备POST数据
            post_data = {
                "formhash": formhash,
                # 以下参数与手动签到成功请求保持一致：
                # qdmode=1 为快速签到模式（缺失会导致“未定义操作”）
                "qdxq": "wl",
                "qdmode": "1",
                "todaysay": "今天开心 ing",
                "fastreply": "0"
            }

            # 更新请求头
            session.headers.update({
                "Origin": "https://www.1000qm.vip",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.1000qm.vip/plugin.php?id=dsu_paulsign:sign"
            })

            try:
                response = session.post(sign_url, data=post_data, timeout=(5, 15))
                html_content = response.text

                # 储存响应以便调试
                debug_resp = html_content[:500]
                logger.info(f"签到响应内容预览: {debug_resp}")

                # 检查签到结果并提取日志信息
                log_message = _extract_sign_message(html_content)
                if log_message:
                    logger.info(f"签到响应消息: {log_message}")

                    # 判断签到结果（注意顺序：先判失败/已签到，再判成功）
                    if any(k in log_message for k in ["未定义操作", "失败", "错误", "无效", "无法", "不能"]):
                        # 签到失败
                        logger.error(f"签到失败: {log_message}")
                        sign_dict = {
                            "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                            "status": f"签到失败: {log_message}",
                            "message": log_message
                        }
                        self._save_sign_history(sign_dict)

                        if self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【❌ 阡陌居签到失败】",
                                text=f"❌ 签到失败: {log_message}"
                            )
                            notification_sent = True
                        return sign_dict

                    elif "已经签到" in log_message or "已签到" in log_message:
                        logger.info("今日已签到")
                        sign_status = "已签到"

                        # 创建签到记录
                        sign_dict = {
                            "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                            "status": sign_status,
                            "message": log_message
                        }

                        # 合并威望红包信息
                        if prestige_info:
                            sign_dict.update(prestige_info)

                        # 保存签到记录
                        self._save_sign_history(sign_dict)
                        self._save_last_sign_date()

                        # 发送通知
                        if self._notify:
                            self._send_sign_notification(sign_dict)
                            notification_sent = True

                        return sign_dict

                    elif "成功" in log_message or "签到" in log_message:
                        logger.info("签到成功")
                        sign_status = "签到成功"

                        # 创建签到记录
                        sign_dict = {
                            "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                            "status": sign_status,
                            "message": log_message
                        }

                        # 合并威望红包信息
                        if prestige_info:
                            sign_dict.update(prestige_info)

                        # 尝试提取铜币和天数信息
                        try:
                            # 从消息中提取铜币信息（优先匹配“铜币 +X/铜币 X”）
                            coins_match = re.search(r'铜币[^0-9+]*\+?(\d+)', log_message)
                            if coins_match:
                                sign_dict["coins_gain"] = coins_match.group(1)

                            # 可以根据实际响应格式调整提取逻辑
                            # 这里先设置默认值
                            sign_dict["days"] = "—"

                        except Exception as e:
                            logger.warning(f"提取积分信息失败: {str(e)}")

                        # 保存签到记录
                        self._save_sign_history(sign_dict)
                        self._save_last_sign_date()

                        # 发送通知
                        if self._notify:
                            self._send_sign_notification(sign_dict)
                            notification_sent = True

                        return sign_dict

                    else:
                        # 未知消息，按失败处理
                        logger.error(f"签到返回未知消息: {log_message}")
                        sign_dict = {
                            "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                            "status": f"签到失败: {log_message}",
                            "message": log_message
                        }
                        self._save_sign_history(sign_dict)

                        if self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【❌ 阡陌居签到失败】",
                                text=f"❌ 签到失败: {log_message}"
                            )
                            notification_sent = True
                        return sign_dict
                else:
                    # 未找到响应消息
                    logger.error(f"签到请求发送成功，但未找到响应消息: {debug_resp}")

                    # 常规重试逻辑
                    if retry_count < self._max_retries:
                        logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                        if self._notify:
                            self.post_message(
                                mtype=NotificationType.SiteMessage,
                                title="【阡陌居签到重试】",
                                text=f"❗ 未找到响应消息，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                            )
                        time.sleep(self._retry_interval)
                        return self.sign(retry_count + 1, extended_retry)

                    sign_dict = {
                        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                        "status": "签到失败: 未找到响应消息",
                    }
                    self._save_sign_history(sign_dict)

                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【❌ 阡陌居签到失败】",
                            text="❌ 签到失败: 未找到响应消息，请检查站点是否变更"
                        )
                        notification_sent = True
                    return sign_dict
            except requests.Timeout:
                logger.error("签到请求超时")
                # 常规重试逻辑
                if retry_count < self._max_retries:
                    logger.info(f"将在{self._retry_interval}秒后进行第{retry_count+1}次常规重试...")
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【阡陌居签到重试】",
                            text=f"❗ 签到请求超时，{self._retry_interval}秒后将进行第{retry_count+1}次常规重试"
                        )
                    time.sleep(self._retry_interval)
                    return self.sign(retry_count + 1, extended_retry)

                # 所有重试都失败
                sign_dict = {
                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 所有重试均超时",
                }
                self._save_sign_history(sign_dict)
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【❌ 阡陌居签到失败】",
                        text="❌ 签到请求多次超时，所有重试均已失败，请检查网络连接或站点状态"
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
                        title="【❌ 阡陌居签到失败】",
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

    def _claim_daily_prestige_reward(self, session: Optional[requests.Session]):
        """
        领取每日威望红包任务：
        1) GET https://www.1000qm.vip/home.php?mod=task&do=apply&id=1
        2) GET https://www.1000qm.vip/home.php?mod=task&do=draw&id=1
        3) 跳转页 GET https://www.1000qm.vip/home.php?mod=task&item=done
        无论成功或重复，都将响应摘要写入日志，便于后续优化。
        """
        try:
            apply_url = "https://www.1000qm.vip/home.php?mod=task&do=apply&id=1"
            draw_url = "https://www.1000qm.vip/home.php?mod=task&do=draw&id=1"
            done_url = "https://www.1000qm.vip/home.php?mod=task&item=done"

            # 补充必要头部
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Referer": "https://www.1000qm.vip/home.php?mod=task",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            }

            # 如未传入会话，则创建并注入Cookie
            if session is None:
                session = requests.Session()
                # 从配置Cookie注入
                try:
                    cookies = {}
                    if self._cookie:
                        for cookie_item in self._cookie.split(';'):
                            if '=' in cookie_item:
                                name, value = cookie_item.strip().split('=', 1)
                                cookies[name] = value
                    session.cookies.update(cookies)
                except Exception as e:
                    logger.warning(f"威望红包：解析Cookie失败（忽略继续）: {str(e)}")

            # 第一步：申请任务
            logger.info(f"请求申请威望红包任务: {apply_url}")
            resp_apply = session.get(apply_url, headers=headers, timeout=(5, 15))
            text_apply = resp_apply.text or ""
            logger.info(f"领取响应-apply: status={resp_apply.status_code}, len={len(text_apply)}")

            # 第二步：领取任务
            logger.info(f"请求领取威望红包: {draw_url}")
            resp1 = session.get(draw_url, headers=headers, timeout=(5, 15))
            text1 = resp1.text or ""
            logger.info(f"领取响应1: status={resp1.status_code}, len={len(text1)}")

            # 成功关键字判定（更稳健）：
            # 1) 直接包含成功文案
            # 2) 包含跳转到 item=done 的链接或脚本
            # 3) 其它可能变体
            success = False
            try:
                patterns = [
                    r"恭喜您，?任务已成功完成",
                    r"任务已成功完成",
                    r"home\.php\?mod=task&item=done",
                    r"window\.location\.href\s*=\s*['\"]home\.php\?mod=task&item=done",
                ]
                for pat in patterns:
                    if re.search(pat, text1):
                        success = True
                        break
            except Exception:
                # 回退到最简单包含判断
                success = ("任务已成功完成" in text1) or ("item=done" in text1)

            # 第三步：查看完成页
            logger.info(f"请求查看完成页: {done_url}")
            resp2 = session.get(done_url, headers=headers, timeout=(5, 15))
            text2 = resp2.text or ""
            logger.info(f"领取响应2: status={resp2.status_code}, len={len(text2)}")

            if success:
                logger.info("每日威望红包：领取成功")
            else:
                # 可能是已领取或其他情况，记录为信息级别，后续可细化解析
                logger.info("每日威望红包：非成功提示（可能为重复领取或其它情况），已记录响应用于后续优化")

            # 从完成页解析威望获取数量与完成时间/积分
            prestige_gain = None
            credits_total = None
            completed_at = None
            try:
                # 解析奖励行：例如 “积分 威望 1 ”
                m_gain = re.search(r"积分\s*威望\s*(\d+)", text2)
                if m_gain:
                    prestige_gain = m_gain.group(1)

                # 解析页面顶部“积分: 104”
                m_total = re.search(r"积分:\s*(\d+)", text2)
                if m_total:
                    credits_total = m_total.group(1)

                # 解析完成时间：例如 “完成于 2025-9-8 19:20”
                m_done = re.search(r"完成于\s*([0-9\-: ]+)", text2)
                if m_done:
                    completed_at = m_done.group(1).strip()
            except Exception as e:
                logger.warning(f"解析威望红包信息失败: {str(e)}")

            info = {}
            if prestige_gain is not None:
                info["prestige_gain"] = prestige_gain
            if credits_total is not None:
                info["credits_total"] = credits_total
            if completed_at is not None:
                info["days"] = completed_at

            # 追加拉取“积分总览”页，解析六项财富信息
            try:
                credit_url = "https://www.1000qm.vip/home.php?mod=spacecp&ac=credit&showcredit=1"
                logger.info(f"请求财富总览: {credit_url}")
                resp3 = session.get(credit_url, headers=headers, timeout=(5, 15))
                text3 = resp3.text or ""
                logger.info(f"财富总览响应: status={resp3.status_code}, len={len(text3)}")

                # 解析六项：铜币/威望/贡献/发书数/积分/总积分
                def _search_num(label: str):
                    try:
                        # 兼容空格与标签，捕获整数
                        pattern = rf"<em>\s*{label}\s*:\s*</em>\s*(\d+)"
                        m = re.search(pattern, text3)
                        return m.group(1) if m else None
                    except Exception:
                        return None

                coins_total = _search_num("铜币")
                prestige_total = _search_num("威望")
                contribution_total = _search_num("贡献")
                books_total = _search_num("发书数")

                # 积分与总积分
                points_total = _search_num("积分")
                credits_sum = None
                try:
                    m_sum = re.search(r"<li class=\"cl\"><em>积分:\s*</em>\s*(\d+)", text3)
                    if m_sum:
                        credits_sum = m_sum.group(1)
                except Exception:
                    pass

                # 写入info并持久化最近一次概览
                overview = {}
                if coins_total is not None:
                    info["coins_total"] = coins_total; overview["coins_total"] = coins_total
                if prestige_total is not None:
                    info["prestige_total"] = prestige_total; overview["prestige_total"] = prestige_total
                if contribution_total is not None:
                    info["contribution_total"] = contribution_total; overview["contribution_total"] = contribution_total
                if books_total is not None:
                    info["books_total"] = books_total; overview["books_total"] = books_total
                if points_total is not None:
                    info["credits_total"] = points_total; overview["credits_total"] = points_total
                if credits_sum is not None:
                    info["credits_sum"] = credits_sum; overview["credits_sum"] = credits_sum

                if overview:
                    self.save_data('last_credits_overview', overview)
                    logger.info(f"财富汇总解析结果: {overview}")
            except requests.Timeout:
                logger.warning("财富总览请求超时，跳过")
            except Exception as e:
                logger.warning(f"财富总览处理异常（忽略）: {str(e)}")

            if info:
                logger.info(f"威望红包解析结果: {info}")
            return info

        except requests.Timeout:
            logger.warning("每日威望红包：请求超时，已忽略")
        except Exception as e:
            logger.warning(f"每日威望红包：处理异常（忽略继续）: {str(e)}")

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
        message = sign_dict.get("message", "—")
        points = sign_dict.get("points", "—")
        days = sign_dict.get("days", "—")
        sign_time = sign_dict.get("date", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # 检查积分信息是否为空
        info_missing = message == "—" and points == "—" and days == "—"

        # 获取触发方式
        trigger_type = self._current_trigger_type

        # 构建通知文本
        if "签到成功" in status:
            title = "【✅ 阡陌居签到成功】"

            if info_missing:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"⚠️ 详细信息获取失败，请手动查看\n"
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
                    f"🪙 铜币：{sign_dict.get('coins_gain', '—')}\n"
                    + (
                        "\n🧧 威望红包\n"
                        f"🪙 铜币：{sign_dict.get('coins_total', '—')}\n"
                        f"🥇 威望：{sign_dict.get('prestige_total', '—')} (本次+{sign_dict.get('prestige_gain', '—')})\n"
                        f"🤝 贡献：{sign_dict.get('contribution_total', '—')}\n"
                        f"📚 发书数：{sign_dict.get('books_total', '—')}\n"
                        f"📈 积分：{sign_dict.get('credits_total', '—')}\n"
                        f"🏆 总积分：{sign_dict.get('credits_sum', '—')}\n"
                        if any(sign_dict.get(k) for k in ['coins_total','prestige_total','prestige_gain','contribution_total','books_total','credits_total','credits_sum']) else ""
                    )
                    + f"━━━━━━━━━━"
                )
        elif "已签到" in status:
            title = "【ℹ️ 阡陌居重复签到】"

            if info_missing:
                text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{sign_time}\n"
                    f"📍 方式：{trigger_type}\n"
                    f"✨ 状态：{status}\n"
                    f"ℹ️ 说明：今日已完成签到\n"
                    f"⚠️ 详细信息获取失败，请手动查看\n"
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
                    f"🪙 铜币：{sign_dict.get('coins_gain', '—')}\n"
                    + (
                        "\n🧧 威望红包\n"
                        f"🪙 铜币：{sign_dict.get('coins_total', '—')}\n"
                        f"🥇 威望：{sign_dict.get('prestige_total', '—')} (本次+{sign_dict.get('prestige_gain', '—')})\n"
                        f"🤝 贡献：{sign_dict.get('contribution_total', '—')}\n"
                        f"📚 发书数：{sign_dict.get('books_total', '—')}\n"
                        f"📈 积分：{sign_dict.get('credits_total', '—')}\n"
                        f"🏆 总积分：{sign_dict.get('credits_sum', '—')}\n"
                        if any(sign_dict.get(k) for k in ['coins_total','prestige_total','prestige_gain','contribution_total','books_total','credits_total','credits_sum']) else ""
                    )
                    + f"━━━━━━━━━━"
                )
        else:
            title = "【❌ 阡陌居签到失败】"
            text = (
                f"📢 执行结果\n"
                f"━━━━━━━━━━\n"
                f"🕐 时间：{sign_time}\n"
                f"📍 方式：{trigger_type}\n"
                f"❌ 状态：{status}\n"
                f"━━━━━━━━━━\n"
                f"💡 可能的解决方法\n"
                f"• 检查Cookie是否有效\n"
                f"• 确认网络连接正常\n"
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
        logger.info(f"qmjsign状态: {self._enabled}")
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")
            return [{
                "id": "qmjsign",
                "name": "阡陌居签到",
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
                                            'model': 'draw_prestige',
                                            'label': '领取每日威望红包',
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
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cookie',
                                            'label': '站点Cookie',
                                            'placeholder': '请输入阡陌居站点Cookie值'
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
                                            'text': '【使用教程】\n1. 登录阡陌居网站(www.1000qm.vip)，按F12打开开发者工具\n2. 在"网络"或"应用"选项卡中复制Cookie\n3. 粘贴Cookie到上方输入框\n4. 设置签到时间，建议早上8点(0 8 * * *)\n5. 启用插件并保存\n\n开启通知可在签到后收到结果通知，也可随时查看签到历史页面'
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
            "cron": "0 8 * * *",
            "max_retries": 3,
            "retry_interval": 30,
            "history_days": 30,
            "draw_prestige": False
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

        # 读取最近一次财富汇总
        credits_overview = self.get_data('last_credits_overview') or {}

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
                    # 消息列
                    {
                        'component': 'td',
                        'text': history.get('message', '—')
                    },
                    # 奖励列
                    {
                        'component': 'td',
                        'text': (
                            f"铜币 +{history.get('coins_gain', '—')} | "
                            f"威望 +{history.get('prestige_gain', '—')}"
                        )
                    }
                ]
            })

        # 财富汇总信息卡
        overview_card = []
        if credits_overview:
            def chip(label, key, color='primary'):
                return {
                    'component': 'VChip',
                    'props': {'size': 'small','variant': 'outlined','color': color,'class': 'mr-2 mb-2'},
                    'text': f"{label} {credits_overview.get(key, '—')}"
                }
            overview_card = [{
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '💰 账户财富汇总'},
                    {'component': 'VCardText','content': [{'component': 'div','content': [
                        chip('铜币','coins_total','amber-darken-2'),
                        chip('威望','prestige_total','success'),
                        chip('贡献','contribution_total'),
                        chip('发书数','books_total'),
                        chip('积分','credits_total','info'),
                        chip('总积分','credits_sum','deep-purple')
                    ]}]}
                ]
            }]

        # 最终页面组装
        return overview_card + [
            # 标题
            {
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'text-h6'},
                        'text': '📊 阡陌居签到历史'
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
                                                    {'component': 'th', 'text': '消息'},
                                                    {'component': 'th', 'text': '奖励'}
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
            # 查找所有qmjsign_extended_retry开头的任务，并停止它们
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

    def _check_cookie_valid(self, session):
        """检查Cookie是否有效"""
        try:
            # 使用更短的超时时间，防止卡住
            response = session.get("https://www.1000qm.vip/", timeout=(3, 10))
            # 检查是否包含登录后的特征
            if "退出" in response.text or "个人资料" in response.text or "用户名" in response.text:
                logger.info("Cookie验证成功")
                return True
            return False
        except Exception as e:
            logger.warning(f"检查Cookie有效性时出错: {str(e)}")
            # 发生异常时，假设Cookie无效
            return False

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

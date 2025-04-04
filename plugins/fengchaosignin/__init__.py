import json
import re
import time
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger
from app.schemas import NotificationType
from app.utils.http import RequestUtils


class FengchaoSignin(_PluginBase):
    # 插件名称
    plugin_name = "蜂巢签到"
    # 插件描述
    plugin_desc = "蜂巢论坛签到。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/fengchao.png"
    # 插件版本
    plugin_version = "1.0.3"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "fengchaosignin_"
    # 加载顺序
    plugin_order = 24
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    # 任务执行间隔
    _cron = None
    _cookie = None
    _onlyonce = False
    _notify = False
    _history_days = None
    # 重试相关
    _retry_count = 0  # 最大重试次数
    _current_retry = 0  # 当前重试次数
    _retry_interval = 2  # 重试间隔(小时)
    # MoviePilot数据推送相关
    _mp_push_enabled = False  # 是否启用数据推送
    _mp_push_interval = 1  # 推送间隔(天)
    _last_push_time = None  # 上次推送时间
    # 代理相关
    _use_proxy = True  # 是否使用代理，默认启用

    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None

    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()

        if config:
            self._enabled = config.get("enabled")
            self._cron = config.get("cron")
            self._cookie = config.get("cookie")
            self._notify = config.get("notify")
            self._onlyonce = config.get("onlyonce")
            self._history_days = config.get("history_days") or 30
            # 加载重试设置
            self._retry_count = int(config.get("retry_count") or 0)
            self._retry_interval = int(config.get("retry_interval") or 2)
            # 加载MoviePilot数据推送设置
            self._mp_push_enabled = config.get("mp_push_enabled")
            self._mp_push_interval = int(config.get("mp_push_interval") or 1)
            # 加载代理设置
            self._use_proxy = config.get("use_proxy", True)
            
            # 加载上次推送时间
            self._last_push_time = self.get_data('last_push_time')

        # 重置当前重试次数
        self._current_retry = 0

        if self._enabled and (
            self._cron or (self._onlyonce and not self._scheduler)
        ):
            # 定时服务
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)

            # 如果是立即运行一次
            if self._onlyonce:
                logger.info(f"蜂巢签到服务启动，立即运行一次")
                self._scheduler.add_job(func=self.__signin, trigger='date',
                                        run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                        name="蜂巢签到")
                # 关闭一次性开关
                self._onlyonce = False
                self.update_config({
                    "onlyonce": False,
                    "cron": self._cron,
                    "enabled": self._enabled,
                    "cookie": self._cookie,
                    "notify": self._notify,
                    "history_days": self._history_days,
                    "retry_count": self._retry_count,
                    "retry_interval": self._retry_interval,
                    "mp_push_enabled": self._mp_push_enabled,
                    "mp_push_interval": self._mp_push_interval,
                    "use_proxy": self._use_proxy
                })
            # 周期运行
            elif self._cron:
                logger.info(f"蜂巢签到服务启动，周期：{self._cron}")
                self._scheduler.add_job(func=self.__signin,
                                       trigger=CronTrigger.from_crontab(self._cron),
                                       name="蜂巢签到")
                
                # 如果启用了MoviePilot数据推送，添加定时任务检查是否需要推送
                if self._mp_push_enabled:
                    logger.info(f"MoviePilot数据推送检查服务启动，每6小时检查一次")
                    self._scheduler.add_job(func=self.__check_and_push_mp_stats,
                                           trigger='interval',
                                           hours=6,
                                           name="MoviePilot数据推送检查")

            # 启动任务
            if self._scheduler.get_jobs():
                self._scheduler.print_jobs()
                self._scheduler.start()

    def _send_notification(self, title, text):
        """
        发送通知
        """
        if self._notify:
            self.post_message(
                mtype=NotificationType.SiteMessage,
                title=title,
                text=text
            )

    def _schedule_retry(self):
        """
        安排重试任务
        """
        if not self._scheduler:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            
        # 计算下次重试时间
        next_run_time = datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(hours=self._retry_interval)
        
        # 安排重试任务
        self._scheduler.add_job(
            func=self.__signin, 
            trigger='date',
            run_date=next_run_time,
            name=f"蜂巢签到重试 ({self._current_retry}/{self._retry_count})"
        )
        
        logger.info(f"蜂巢签到失败，将在{self._retry_interval}小时后重试，当前重试次数: {self._current_retry}/{self._retry_count}")
        
        # 启动定时器（如果未启动）
        if not self._scheduler.running:
            self._scheduler.start()

    def _get_proxies(self):
        """
        获取代理设置
        """
        if not self._use_proxy:
            logger.info("未启用代理")
            return None
            
        try:
            # 获取系统代理设置
            if hasattr(settings, 'PROXY') and settings.PROXY:
                logger.info(f"使用系统代理: {settings.PROXY}")
                return settings.PROXY
            else:
                logger.warning("系统代理未配置")
                return None
        except Exception as e:
            logger.error(f"获取代理设置出错: {str(e)}")
            return None

    def __signin(self):
        """
        蜂巢签到
        """
        # 获取代理设置
        proxies = self._get_proxies()
        
        # 连接失败处理
        res = RequestUtils(cookies=self._cookie, proxies=proxies).get_res(url="https://pting.club")
        if not res or res.status_code != 200:
            logger.error("请求蜂巢错误")
            
            # 发送通知
            if self._notify:
                self._send_notification(
                    title="【❌ 蜂巢签到失败】",
                    text=(
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"❌ 状态：签到失败，无法连接到站点\n"
                        f"━━━━━━━━━━\n"
                        f"💡 可能的解决方法\n"
                        f"• 检查Cookie是否过期\n"
                        f"• 确认站点是否可访问\n"
                        f"• 检查代理设置是否正确\n"
                        f"• 尝试手动登录网站\n"
                        f"━━━━━━━━━━"
                    )
                )
            
            # 记录历史
            history = {
                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": "签到失败：无法连接到站点",
                "money": None,
                "totalContinuousCheckIn": None,
                "retry": {
                    "enabled": self._retry_count > 0,
                    "current": self._current_retry,
                    "max": self._retry_count,
                    "interval": self._retry_interval
                }
            }
            self._save_history(history)
            
            # 判断是否需要重试
            if self._retry_count > 0 and self._current_retry < self._retry_count:
                self._current_retry += 1
                # 安排下次重试
                self._schedule_retry()
            else:
                # 重置重试计数
                self._current_retry = 0
            
            return

        # 获取csrfToken
        pattern = r'"csrfToken":"(.*?)"'
        csrfToken = re.findall(pattern, res.text)
        if not csrfToken:
            logger.error("请求csrfToken失败")
            
            # 发送通知
            if self._notify:
                self._send_notification(
                    title="【❌ 蜂巢签到失败】",
                    text=(
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"❌ 状态：签到失败，无法获取CSRF令牌\n"
                        f"━━━━━━━━━━\n"
                        f"💡 可能的解决方法\n"
                        f"• 检查Cookie是否过期\n"
                        f"• 尝试手动登录网站\n"
                        f"━━━━━━━━━━"
                    )
                )
            
            # 记录历史
            history = {
                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": "签到失败：无法获取CSRF令牌",
                "money": None,
                "totalContinuousCheckIn": None,
                "retry": {
                    "enabled": self._retry_count > 0,
                    "current": self._current_retry,
                    "max": self._retry_count,
                    "interval": self._retry_interval
                }
            }
            self._save_history(history)
            
            # 判断是否需要重试
            if self._retry_count > 0 and self._current_retry < self._retry_count:
                self._current_retry += 1
                # 安排下次重试
                self._schedule_retry()
            else:
                # 重置重试计数
                self._current_retry = 0
            
            return

        csrfToken = csrfToken[0]
        logger.info(f"获取csrfToken成功 {csrfToken}")

        # 获取userid
        pattern = r'"userId":(\d+)'
        match = re.search(pattern, res.text)

        if match:
            userId = match.group(1)
            logger.info(f"获取userid成功 {userId}")
            
            # 调试：无论是否需要推送，都获取并打印站点数据
            logger.info("调试：开始获取站点数据")
            debug_stats_data = self._get_site_statistics()
            if debug_stats_data:
                sites = debug_stats_data.get("sites", [])
                sample_sites = [site.get("name") for site in sites[:3] if site.get("name")]
                logger.info(f"调试：获取到 {len(sites)} 个站点数据，示例站点: {', '.join(sample_sites) if sample_sites else '无'}")
                
                # 格式化并打印汇总数据
                debug_formatted = self._format_stats_data(debug_stats_data)
                if debug_formatted:
                    summary = debug_formatted.get("summary", {})
                    logger.info(f"调试：站点数据汇总 - 总上传: {round(summary.get('total_upload', 0)/1024/1024/1024, 2)} GB, "
                             f"总下载: {round(summary.get('total_download', 0)/1024/1024/1024, 2)} GB, "
                             f"总做种数: {summary.get('total_seed', 0)}, "
                             f"总做种体积: {round(summary.get('total_seed_size', 0)/1024/1024/1024, 2)} GB")
            else:
                logger.info("调试：未获取到站点数据")
            
            # 如果开启了MoviePilot统计推送，尝试推送数据
            if self._mp_push_enabled:
                self.__push_mp_stats(user_id=userId, csrf_token=csrfToken)
        else:
            logger.error("未找到userId")
            
            # 发送通知
            if self._notify:
                self._send_notification(
                    title="【❌ 蜂巢签到失败】",
                    text=(
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"❌ 状态：签到失败，无法获取用户ID\n"
                        f"━━━━━━━━━━\n"
                        f"💡 可能的解决方法\n"
                        f"• 检查Cookie是否有效\n"
                        f"• 尝试手动登录网站\n"
                        f"━━━━━━━━━━"
                    )
                )
            
            # 记录历史
            history = {
                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": "签到失败：无法获取用户ID",
                "money": None,
                "totalContinuousCheckIn": None,
                "retry": {
                    "enabled": self._retry_count > 0,
                    "current": self._current_retry,
                    "max": self._retry_count,
                    "interval": self._retry_interval
                }
            }
            self._save_history(history)
            
            # 判断是否需要重试
            if self._retry_count > 0 and self._current_retry < self._retry_count:
                self._current_retry += 1
                # 安排下次重试
                self._schedule_retry()
            else:
                # 重置重试计数
                self._current_retry = 0
            
            return

        headers = {
            "X-Csrf-Token": csrfToken,
            "X-Http-Method-Override": "PATCH",
            "Cookie": self._cookie
        }

        data = {
            "data": {
                "type": "users",
                "attributes": {
                    "canCheckin": False,
                    "totalContinuousCheckIn": 2
                },
                "id": userId
            }
        }

        # 开始签到
        res = RequestUtils(headers=headers, proxies=proxies).post_res(url=f"https://pting.club/api/users/{userId}", json=data)

        if not res or res.status_code != 200:
            logger.error("蜂巢签到失败")

            # 发送通知
            if self._notify:
                self._send_notification(
                    title="【❌ 蜂巢签到失败】",
                    text=(
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"❌ 状态：签到失败，API请求错误\n"
                        f"━━━━━━━━━━\n"
                        f"💡 可能的解决方法\n"
                        f"• 检查Cookie是否有效\n"
                        f"• 确认站点是否可访问\n"
                        f"• 尝试手动登录网站\n"
                        f"━━━━━━━━━━"
                    )
                )
            
            # 记录历史
            history = {
                "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": "签到失败：API请求错误",
                "money": None,
                "totalContinuousCheckIn": None,
                "retry": {
                    "enabled": self._retry_count > 0,
                    "current": self._current_retry,
                    "max": self._retry_count,
                    "interval": self._retry_interval
                }
            }
            self._save_history(history)
            
            # 判断是否需要重试
            if self._retry_count > 0 and self._current_retry < self._retry_count:
                self._current_retry += 1
                # 安排下次重试
                self._schedule_retry()
            else:
                # 重置重试计数
                self._current_retry = 0
            
            return

        sign_dict = json.loads(res.text)
        
        # 保存用户信息数据（用于个人信息卡）
        self.save_data("user_info", sign_dict)
        
        money = sign_dict['data']['attributes']['money']
        totalContinuousCheckIn = sign_dict['data']['attributes']['totalContinuousCheckIn']

        # 检查是否已签到
        if "canCheckin" in sign_dict['data']['attributes'] and not sign_dict['data']['attributes']['canCheckin']:
            status_text = "已签到"
            reward_text = "今日已领取奖励"
            logger.info(f"蜂巢已签到，当前花粉: {money}，累计签到: {totalContinuousCheckIn}")
        else:
            status_text = "签到成功"
            reward_text = "获得10花粉奖励"
            logger.info(f"蜂巢签到成功，当前花粉: {money}，累计签到: {totalContinuousCheckIn}")

        # 发送通知
        if self._notify:
            self._send_notification(
                title=f"【✅ 蜂巢{status_text}】",
                text=(
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"✨ 状态：{status_text}\n"
                    f"🎁 奖励：{reward_text}\n"
                    f"━━━━━━━━━━\n"
                    f"📊 积分统计\n"
                    f"🌸 花粉：{money}\n"
                    f"📆 签到天数：{totalContinuousCheckIn}\n"
                    f"━━━━━━━━━━"
                )
            )

        # 读取历史记录
        history = {
            "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            "status": status_text,
            "money": money,
            "totalContinuousCheckIn": totalContinuousCheckIn,
            "retry": {
                "enabled": self._retry_count > 0,
                "current": self._current_retry,
                "max": self._retry_count,
                "interval": self._retry_interval
            }
        }
        
        # 保存签到历史
        self._save_history(history)
        
        # 如果是重试后成功，重置重试计数
        if self._current_retry > 0:
            logger.info(f"蜂巢签到重试成功，重置重试计数")
            self._current_retry = 0

    def _save_history(self, record):
        """
        保存签到历史记录
        """
        # 读取历史记录
        history = self.get_data('history') or []
        
        # 如果是失败状态，添加重试信息
        if "失败" in record.get("status", ""):
            record["retry"] = {
                "enabled": self._retry_count > 0,
                "current": self._current_retry,
                "max": self._retry_count,
                "interval": self._retry_interval
            }
        
        # 添加新记录
        history.append(record)
        
        # 保留指定天数的记录
        if self._history_days:
            try:
                thirty_days_ago = time.time() - int(self._history_days) * 24 * 60 * 60
                history = [record for record in history if
                          datetime.strptime(record["date"],
                                         '%Y-%m-%d %H:%M:%S').timestamp() >= thirty_days_ago]
            except Exception as e:
                logger.error(f"清理历史记录异常: {str(e)}")
        
        # 保存历史记录
        self.save_data(key="history", value=history)

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        [{
            "id": "服务ID",
            "name": "服务名称",
            "trigger": "触发器：cron/interval/date/CronTrigger.from_crontab()",
            "func": self.xxx,
            "kwargs": {} # 定时器参数
        }]
        """
        services = []
        
        if self._enabled and self._cron:
            services.append({
                "id": "FengchaoSignin",
                "name": "蜂巢签到服务",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.__signin,
                "kwargs": {}
            })
        
        if self._enabled and self._mp_push_enabled:
            services.append({
                "id": "MoviePilotStatsPush",
                "name": "MoviePilot统计推送检查服务",
                "trigger": "interval",
                "func": self.__check_and_push_mp_stats,
                "kwargs": {"hours": 6} # 每6小时检查一次是否需要推送
            })
            
        return services

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VTabs',
                        'props': {
                            'grow': True,
                            'v-model': 'activeTab'
                        },
                        'content': [
                            {
                                'component': 'VTab',
                                'props': {'value': 'basic'},
                                'text': '基本设置'
                            },
                            {
                                'component': 'VTab',
                                'props': {'value': 'mp_stats'},
                                'text': 'MoviePilot统计'
                            }
                        ]
                    },
                    {
                        'component': 'VWindow',
                        'props': {'v-model': 'activeTab'},
                        'content': [
                            {
                                'component': 'VWindowItem',
                                'props': {'value': 'basic'},
                                'content': [
                                    {
                                        'component': 'VCard',
                                        'props': {
                                            'variant': 'outlined',
                                            'class': 'mt-3'
                                        },
                                        'content': [
                                            {
                                                'component': 'VCardTitle',
                                                'props': {
                                                    'class': 'd-flex align-center'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VIcon',
                                                        'props': {
                                                            'style': 'color: #1976D2;',
                                                            'class': 'mr-2'
                                                        },
                                                        'text': 'mdi-calendar-check'
                                                    },
                                                    {
                                                        'component': 'span',
                                                        'text': '基本设置'
                                                    }
                                                ]
                                            },
                                            {
                                                'component': 'VDivider'
                                            },
                                            {
                                                'component': 'VCardText',
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
                                                                'props': {
                                                                    'cols': 12,
                                                                    'md': 6
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'VTextField',
                                                                        'props': {
                                                                            'model': 'cron',
                                                                            'label': '签到周期',
                                                                            'placeholder': '30 8 * * *',
                                                                            'hint': '五位cron表达式，每天早上8:30执行'
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
                                                                            'model': 'history_days',
                                                                            'label': '历史保留天数',
                                                                            'placeholder': '30',
                                                                            'hint': '历史记录保留天数'
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
                                                                            'model': 'retry_count',
                                                                            'label': '失败重试次数',
                                                                            'type': 'number',
                                                                            'placeholder': '0',
                                                                            'hint': '0表示不重试，大于0则在签到失败后重试'
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
                                                                            'model': 'retry_interval',
                                                                            'label': '重试间隔(小时)',
                                                                            'type': 'number',
                                                                            'placeholder': '2',
                                                                            'hint': '签到失败后多少小时后重试'
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
                                                                        'component': 'VSwitch',
                                                                        'props': {
                                                                            'model': 'use_proxy',
                                                                            'label': '使用代理',
                                                                            'hint': '与蜂巢论坛通信时使用系统代理'
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
                                                                    'cols': 12
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'VTextarea',
                                                                        'props': {
                                                                            'model': 'cookie',
                                                                            'label': 'Cookie',
                                                                            'rows': 2,
                                                                            'placeholder': 'session=xxx; uid=xxx',
                                                                            'hint': '登录蜂巢获取Cookie'
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                'component': 'VWindowItem',
                                'props': {'value': 'mp_stats'},
                                'content': [
                                    {
                                        'component': 'VCard',
                                        'props': {
                                            'variant': 'outlined',
                                            'class': 'mt-3'
                                        },
                                        'content': [
                                            {
                                                'component': 'VCardTitle',
                                                'props': {
                                                    'class': 'd-flex align-center'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VIcon',
                                                        'props': {
                                                            'style': 'color: #1976D2;',
                                                            'class': 'mr-2'
                                                        },
                                                        'text': 'mdi-chart-box'
                                                    },
                                                    {
                                                        'component': 'span',
                                                        'text': 'MoviePilot统计设置'
                                                    }
                                                ]
                                            },
                                            {
                                                'component': 'VDivider'
                                            },
                                            {
                                                'component': 'VCardText',
                                                'content': [
                                                    {
                                                        'component': 'VRow',
                                                        'content': [
                                                            {
                                                                'component': 'VCol',
                                                                'props': {'cols': 12},
                                                                'content': [{
                                                                    'component': 'VAlert',
                                                                    'props': {
                                                                        'type': 'info',
                                                                        'text': True,
                                                                        'variant': 'tonal'
                                                                    },
                                                                    'text': '该功能将MoviePilot站点数据推送到蜂巢论坛个人资料页展示'
                                                                }]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'VRow',
                                                        'content': [
                                                            {
                                                                'component': 'VCol',
                                                                'props': {'cols': 12},
                                                                'content': [{
                                                                    'component': 'VSwitch',
                                                                    'props': {
                                                                        'model': 'mp_push_enabled',
                                                                        'label': '启用MoviePilot统计推送'
                                                                    }
                                                                }]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'VRow',
                                                        'content': [
                                                            {
                                                                'component': 'VCol',
                                                                'props': {'cols': 12},
                                                                'content': [{
                                                                    'component': 'VTextField',
                                                                    'props': {
                                                                        'model': 'mp_push_interval',
                                                                        'label': '推送间隔(天)',
                                                                        'type': 'number',
                                                                        'placeholder': '1',
                                                                        'hint': '多少天推送一次数据，默认1天'
                                                                    }
                                                                }]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
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
            "cron": "30 8 * * *",
            "onlyonce": False,
            "cookie": "",
            "history_days": 30,
            "retry_count": 0,
            "retry_interval": 2,
            "mp_push_enabled": False,
            "mp_push_interval": 1,
            "use_proxy": True,
            "activeTab": "basic"
        }

    def get_page(self) -> List[dict]:
        """
        构建插件详情页面，展示签到历史
        """
        # 获取签到历史
        history = self.get_data('history') or []
        # 获取用户信息
        user_info = self.get_data('user_info')
        
        # 如果有用户信息，构建用户信息卡
        user_info_card = None
        if user_info and 'data' in user_info and 'attributes' in user_info['data']:
            user_attrs = user_info['data']['attributes']
            
            # 获取用户基本信息
            username = user_attrs.get('displayName', '未知用户')
            avatar_url = user_attrs.get('avatarUrl', '')
            money = user_attrs.get('money', 0)
            discussion_count = user_attrs.get('discussionCount', 0)
            comment_count = user_attrs.get('commentCount', 0)
            follower_count = user_attrs.get('followerCount', 0)
            following_count = user_attrs.get('followingCount', 0)
            last_checkin_time = user_attrs.get('lastCheckinTime', '未知')
            total_continuous_checkin = user_attrs.get('totalContinuousCheckIn', 0)
            join_time = user_attrs.get('joinTime', '')
            last_seen_at = user_attrs.get('lastSeenAt', '')
            
            # 处理时间格式
            if join_time:
                try:
                    join_time = datetime.fromisoformat(join_time.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                except:
                    join_time = '未知'
            
            if last_seen_at:
                try:
                    last_seen_at = datetime.fromisoformat(last_seen_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                except:
                    last_seen_at = '未知'
            
            # 获取用户组
            groups = []
            if 'included' in user_info:
                for item in user_info.get('included', []):
                    if item.get('type') == 'groups':
                        groups.append({
                            'name': item.get('attributes', {}).get('nameSingular', ''),
                            'color': item.get('attributes', {}).get('color', '#888'),
                            'icon': item.get('attributes', {}).get('icon', '')
                        })
            
            # 获取用户徽章
            badges = []
            badge_map = {}
            badge_category_map = {}
            
            # 预处理徽章数据
            if 'included' in user_info:
                for item in user_info.get('included', []):
                    if item.get('type') == 'badges':
                        badge_map[item.get('id')] = {
                            'name': item.get('attributes', {}).get('name', ''),
                            'icon': item.get('attributes', {}).get('icon', ''),
                            'description': item.get('attributes', {}).get('description', ''),
                            'background_color': item.get('attributes', {}).get('backgroundColor', '#444'),
                            'icon_color': item.get('attributes', {}).get('iconColor', '#fff'),
                            'label_color': item.get('attributes', {}).get('labelColor', '#fff'),
                            'category_id': item.get('relationships', {}).get('category', {}).get('data', {}).get('id')
                        }
                    elif item.get('type') == 'badgeCategories':
                        badge_category_map[item.get('id')] = {
                            'name': item.get('attributes', {}).get('name', ''),
                            'order': item.get('attributes', {}).get('order', 0)
                        }
            
            # 处理用户的徽章
            if 'included' in user_info:
                # 先获取所有徽章信息
                badges_data = {}
                for item in user_info.get('included', []):
                    if item.get('type') == 'badges':
                        badges_data[item.get('id')] = {
                            'name': item.get('attributes', {}).get('name', '未知徽章'),
                            'icon': item.get('attributes', {}).get('icon', 'fas fa-award'),
                            'description': item.get('attributes', {}).get('description', ''),
                            'background_color': item.get('attributes', {}).get('backgroundColor') or '#444',
                            'icon_color': item.get('attributes', {}).get('iconColor') or '#FFFFFF',
                            'label_color': item.get('attributes', {}).get('labelColor') or '#FFFFFF',
                            'category_id': item.get('relationships', {}).get('category', {}).get('data', {}).get('id')
                        }
                
                # 获取徽章分类信息
                categories = {}
                for item in user_info.get('included', []):
                    if item.get('type') == 'badgeCategories':
                        categories[item.get('id')] = {
                            'name': item.get('attributes', {}).get('name', '其他'),
                            'order': item.get('attributes', {}).get('order', 0)
                        }
                
                # 处理用户徽章
                for item in user_info.get('included', []):
                    if item.get('type') == 'userBadges':
                        badge_id = item.get('relationships', {}).get('badge', {}).get('data', {}).get('id')
                        if badge_id in badges_data:
                            badge_info = badges_data[badge_id]
                            category_id = badge_info.get('category_id')
                            category_name = categories.get(category_id, {}).get('name', '其他')
                            
                            badges.append({
                                'name': badge_info.get('name', ''),
                                'icon': badge_info.get('icon', 'fas fa-award'),
                                'description': badge_info.get('description', ''),
                                'background_color': badge_info.get('background_color', '#444'),
                                'icon_color': badge_info.get('icon_color', '#FFFFFF'),
                                'label_color': badge_info.get('label_color', '#FFFFFF'),
                                'category': category_name
                            })
            
            # 用户信息卡
            user_info_card = {
                'component': 'VCard',
                'props': {
                    'variant': 'outlined', 
                    'class': 'mb-4',
                    'style': f"background-image: url('{user_attrs.get('decorationProfileBackground', '')}'); background-size: cover; background-position: center;" if user_attrs.get('decorationProfileBackground') else ''
                },
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'd-flex align-center'},
                        'content': [
                            {
                                'component': 'VSpacer'
                            }
                        ]
                    },
                    {
                        'component': 'VDivider'
                    },
                    {
                        'component': 'VCardText',
                        'content': [
                            # 用户基本信息部分
                                    {
                                        'component': 'VRow',
                                'props': {'class': 'ma-1'},
                                        'content': [
                                    # 左侧头像和用户名
                                            {
                                                'component': 'VCol',
                                                'props': {
                                            'cols': 12,
                                            'md': 5
                                                },
                                                'content': [
                                                    {
                                                'component': 'div',
                                                'props': {'class': 'd-flex align-center'},
                                                'content': [
                                                    # 头像和头像框
                                                    {
                                                        'component': 'div',
                                                        'props': {
                                                            'class': 'mr-3',
                                                            'style': 'position: relative; width: 90px; height: 90px;'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'VAvatar',
                                                                'props': {
                                                                    'size': 60,
                                                                    'rounded': 'circle',
                                                                    'style': 'position: absolute; top: 15px; left: 15px; z-index: 1;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'VImg',
                                                                        'props': {
                                                                            'src': avatar_url,
                                                                            'alt': username
                                                                        }
                                                                    }
                                                                ]
                                                            },
                                                            # 头像框
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'style': f"position: absolute; top: 0; left: 0; width: 90px; height: 90px; background-image: url('{user_attrs.get('decorationAvatarFrame', '')}'); background-size: contain; background-repeat: no-repeat; background-position: center; z-index: 2;"
                                                                }
                                                            } if user_attrs.get('decorationAvatarFrame') else {}
                                                        ]
                                                    },
                                                    # 用户名和身份组
                                                    {
                                                        'component': 'div',
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-h6 mb-1 pa-1 d-inline-block elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                                                },
                                                                'text': username
                                                            },
                                                            # 用户组标签
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex flex-wrap mt-1'},
                                                                'content': [
                                                                    {
                                                                        'component': 'VChip',
                                                                        'props': {
                                                                            'style': f"background-color: #6B7CA8; color: white; padding: 0 8px; min-width: 60px; border-radius: 2px; height: 32px;",
                                                                            'size': 'small',
                                                                            'class': 'mr-1 mb-1',
                                                                            'variant': 'elevated'
                                                                        },
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'start': True,
                                                                                    'size': 'small',
                                                                                    'style': 'margin-right: 3px;'
                                                                                },
                                                                                'text': group.get('icon') or 'mdi-account'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'text': group.get('name')
                                                                            }
                                                                        ]
                                                                    } for group in groups
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            },
                                            # 注册和最后访问时间
                                    {
                                        'component': 'VRow',
                                                'props': {'class': 'mt-2'},
                                        'content': [
                                            {
                                                'component': 'VCol',
                                                        'props': {'cols': 12},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                'props': {
                                                                    'class': 'pa-1 elevation-1 mb-1 ml-0',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px; width: fit-content;'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex align-center text-caption'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                        'props': {
                                                                                    'style': 'color: #4CAF50;',
                                                                                    'size': 'x-small',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-calendar'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'text': f'注册于 {join_time}'
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'pa-1 elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px; width: fit-content;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex align-center text-caption'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'style': 'color: #2196F3;',
                                                                                    'size': 'x-small',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-clock-outline'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'text': f'最后访问 {last_seen_at}'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
                                                ]
                                            }
                                        ]
                                    },
                                    # 右侧统计数据
                                    {
                                        'component': 'VCol',
                                        'props': {
                                            'cols': 12,
                                            'md': 7
                                        },
                                        'content': [
                                            {
                                                'component': 'VRow',
                                                'content': [
                                                    # 花粉数量
                                                    {
                                                        'component': 'VCol',
                                                        'props': {
                                                            'cols': 6,
                                                            'md': 4
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-center pa-1 elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex justify-center align-center'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'style': 'color: #FFC107;',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-flower'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'props': {'class': 'text-h6'},
                                                                                'text': str(money)
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'text-caption mt-1'},
                                                                        'text': '花粉'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    # 发帖数
                                                    {
                                                        'component': 'VCol',
                                                        'props': {
                                                            'cols': 6,
                                                            'md': 4
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-center pa-1 elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex justify-center align-center'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'style': 'color: #3F51B5;',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-forum'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'props': {'class': 'text-h6'},
                                                                                'text': str(discussion_count)
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'text-caption mt-1'},
                                                                        'text': '主题'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    # 评论数
                                                    {
                                                        'component': 'VCol',
                                                        'props': {
                                                            'cols': 6,
                                                            'md': 4
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-center pa-1 elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex justify-center align-center'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'style': 'color: #00BCD4;',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-comment-text-multiple'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'props': {'class': 'text-h6'},
                                                                                'text': str(comment_count)
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'text-caption mt-1'},
                                                                        'text': '评论'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    # 粉丝数
                                                    {
                                                        'component': 'VCol',
                                                        'props': {
                                                            'cols': 6,
                                                            'md': 4
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-center pa-1 elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex justify-center align-center'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'style': 'color: #673AB7;',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-account-group'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'props': {'class': 'text-h6'},
                                                                                'text': str(follower_count)
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'text-caption mt-1'},
                                                                        'text': '粉丝'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    # 关注数
                                                    {
                                                        'component': 'VCol',
                                                        'props': {
                                                            'cols': 6,
                                                            'md': 4
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-center pa-1 elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex justify-center align-center'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'style': 'color: #03A9F4;',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-account-multiple-plus'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'props': {'class': 'text-h6'},
                                                                                'text': str(following_count)
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'text-caption mt-1'},
                                                                        'text': '关注'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    # 连续签到
                                                    {
                                                        'component': 'VCol',
                                                        'props': {
                                                            'cols': 6,
                                                            'md': 4
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-center pa-1 elevation-1',
                                                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'd-flex justify-center align-center'},
                                                                        'content': [
                                                                            {
                                                                                'component': 'VIcon',
                                                                                'props': {
                                                                                    'style': 'color: #009688;',
                                                                                    'class': 'mr-1'
                                                                                },
                                                                                'text': 'mdi-calendar-check'
                                                                            },
                                                                            {
                                                                                'component': 'span',
                                                                                'props': {'class': 'text-h6'},
                                                                                'text': str(total_continuous_checkin)
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {'class': 'text-caption mt-1'},
                                                                        'text': '连续签到'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            # 徽章部分
                            {
                                'component': 'div',
                                'props': {'class': 'mb-1 mt-1 pl-0'},
                                'content': [
                                    {
                                        'component': 'div',
                                        'props': {
                                            'class': 'd-flex align-center mb-1 elevation-1 d-inline-block ml-0',
                                            'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 3px; width: fit-content; padding: 2px 8px 2px 5px;'
                                        },
                                        'content': [
                                            {
                                                'component': 'VIcon',
                                                'props': {
                                                    'style': 'color: #FFA000;',
                                                    'class': 'mr-1',
                                                    'size': 'small'
                                                },
                                                'text': 'mdi-medal'
                                            },
                                            {
                                                'component': 'span',
                                                'props': {'class': 'text-body-2 font-weight-medium'},
                                                'text': f'徽章({len(badges)})'
                                            }
                                        ]
                                    },
                                    {
                                        'component': 'div',
                                        'props': {'class': 'd-flex flex-wrap'},
                                        'content': [
                                            {
                                                'component': 'VChip',
                                                'props': {
                                                    'class': 'ma-1',
                                                    'style': f"background-color: {['#1976D2', '#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0', '#E91E63', '#FF5722', '#009688', '#3F51B5'][hash(badge.get('name', '')) % 10]}; color: white; display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; margin: 2px; border-radius: 6px; font-size: 0.9rem; min-width: 110px; height: 32px;",
                                                    'variant': 'flat',
                                                    'size': 'large',
                                                    'title': badge.get('description', '') or '无描述'
                                                },
                                                'text': badge.get('name', '未知徽章')
                                            } for badge in badges
                                        ]
                                    }
                                ]
                            },
                            # 最后签到时间
                            {
                                'component': 'div',
                                'props': {
                                    'class': 'mt-1 text-caption text-right grey--text pa-1 elevation-1 d-inline-block float-right',
                                    'style': 'background-color: rgba(255, 255, 255, 0.6); border-radius: 4px;'
                                },
                                'text': f'最后签到: {last_checkin_time}'
                            }
                        ]
                    }
                ]
            }
        
        # 如果没有历史记录
        if not history:
            components = []
            if user_info_card:
                components.append(user_info_card)
                
            components.extend([
                {
                    'component': 'VAlert',
                    'props': {
                        'type': 'info',
                        'variant': 'tonal',
                        'text': '暂无签到记录，请先配置Cookie并启用插件',
                        'class': 'mb-2',
                        'prepend-icon': 'mdi-information'
                    }
                },
                {
                    'component': 'VCard',
                    'props': {'variant': 'outlined', 'class': 'mb-4'},
                    'content': [
                        {
                            'component': 'VCardTitle',
                            'props': {'class': 'd-flex align-center'},
                            'content': [
                                {
                                    'component': 'VIcon',
                                    'props': {
                                        'color': 'amber-darken-2',
                                        'class': 'mr-2'
                                    },
                                    'text': 'mdi-flower'
                                },
                                {
                                    'component': 'span',
                                    'props': {'class': 'text-h6'},
                                    'text': '签到奖励说明'
                                }
                            ]
                        },
                        {
                            'component': 'VDivider'
                        },
                        {
                            'component': 'VCardText',
                            'props': {'class': 'pa-3'},
                            'content': [
                                {
                                    'component': 'div',
                                    'props': {'class': 'd-flex align-center mb-2'},
                                    'content': [
                                        {
                                            'component': 'VIcon',
                                            'props': {
                                                'style': 'color: #FF8F00;',
                                                'size': 'small',
                                                'class': 'mr-2'
                                            },
                                            'text': 'mdi-check-circle'
                                        },
                                        {
                                            'component': 'span',
                                            'text': '每日签到可获得10花粉奖励'
                                        }
                                    ]
                                },
                                {
                                    'component': 'div',
                                    'props': {'class': 'd-flex align-center'},
                                    'content': [
                                        {
                                            'component': 'VIcon',
                                            'props': {
                                                'style': 'color: #1976D2;',
                                                'size': 'small',
                                                'class': 'mr-2'
                                            },
                                            'text': 'mdi-calendar-check'
                                        },
                                        {
                                            'component': 'span',
                                            'text': '连续签到可累积天数，提升论坛等级'
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ])
            return components
        
        # 按时间倒序排列历史
        history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)
        
        # 构建历史记录表格行
        history_rows = []
        for record in history:
            status_text = record.get("status", "未知")
            
            # 根据状态设置颜色和图标
            if "签到成功" in status_text or "已签到" in status_text:
                status_color = "success"
                status_icon = "mdi-check-circle"
            else:
                status_color = "error"
                status_icon = "mdi-close-circle"
            
            history_rows.append({
                'component': 'tr',
                'content': [
                    # 日期列
                    {
                        'component': 'td',
                        'props': {
                            'class': 'text-caption'
                        },
                        'text': record.get("date", "")
                    },
                    # 状态列
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'VChip',
                                'props': {
                                    'style': 'background-color: #4CAF50; color: white;' if status_color == 'success' else 'background-color: #F44336; color: white;',
                                    'size': 'small',
                                    'variant': 'elevated'
                                },
                                'content': [
                                    {
                                        'component': 'VIcon',
                                        'props': {
                                            'start': True,
                                            'style': 'color: white;',
                                            'size': 'small'
                                        },
                                        'text': status_icon
                                    },
                                    {
                                        'component': 'span',
                                'text': status_text
                                    }
                                ]
                            },
                            # 显示重试信息
                            {
                                'component': 'div',
                                'props': {'class': 'mt-1 text-caption grey--text'},
                                'text': f"将在{record.get('retry', {}).get('interval', self._retry_interval)}小时后重试 ({record.get('retry', {}).get('current', 0)}/{record.get('retry', {}).get('max', self._retry_count)})" if status_color == 'error' and record.get('retry', {}).get('enabled', False) and record.get('retry', {}).get('current', 0) > 0 else ""
                            }
                        ]
                    },
                    # 花粉列
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'props': {
                                    'class': 'd-flex align-center'
                                },
                                'content': [
                                    {
                                        'component': 'VIcon',
                                        'props': {
                                            'style': 'color: #FFC107;',
                                            'class': 'mr-1'
                                        },
                                        'text': 'mdi-flower'
                                    },
                                    {
                                        'component': 'span',
                                        'text': record.get('money', '—')
                                    }
                                ]
                            }
                        ]
                    },
                    # 签到天数列
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'props': {
                                    'class': 'd-flex align-center'
                                },
                                'content': [
                                    {
                                        'component': 'VIcon',
                                        'props': {
                                            'style': 'color: #1976D2;',
                                            'class': 'mr-1'
                                        },
                                        'text': 'mdi-calendar-check'
                                    },
                                    {
                                        'component': 'span',
                                        'text': record.get('totalContinuousCheckIn', '—')
                                    }
                                ]
                            }
                        ]
                    },
                    # 奖励列
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'props': {
                                    'class': 'd-flex align-center'
                                },
                                'content': [
                                    {
                                        'component': 'VIcon',
                                        'props': {
                                            'style': 'color: #FF8F00;',
                                            'class': 'mr-1'
                                        },
                                        'text': 'mdi-gift'
                                    },
                                    {
                                        'component': 'span',
                                        'text': '10花粉' if ("签到成功" in status_text or "已签到" in status_text) else '—'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            })
        
        # 最终页面组装
        components = []
        
        # 添加用户信息卡（如果有）
        if user_info_card:
            components.append(user_info_card)
            
        # 添加历史记录表
        components.append({
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'd-flex align-center'},
                        'content': [
                            {
                                'component': 'VIcon',
                                'props': {
                                'style': 'color: #9C27B0;',
                                    'class': 'mr-2'
                                },
                                'text': 'mdi-calendar-check'
                            },
                            {
                                'component': 'span',
                            'props': {'class': 'text-h6 font-weight-bold'},
                                'text': '蜂巢签到历史'
                            },
                            {
                                'component': 'VSpacer'
                            },
                            {
                                'component': 'VChip',
                                'props': {
                                'style': 'background-color: #FF9800; color: white;',
                                    'size': 'small',
                                'variant': 'elevated'
                            },
                            'content': [
                                {
                                    'component': 'VIcon',
                                    'props': {
                                        'start': True,
                                        'style': 'color: white;',
                                        'size': 'small'
                                    },
                                    'text': 'mdi-flower'
                                },
                                {
                                    'component': 'span',
                                'text': '每日可得10花粉'
                                }
                            ]
                            }
                        ]
                    },
                    {
                        'component': 'VDivider'
                    },
                    {
                        'component': 'VCardText',
                        'props': {'class': 'pa-2'},
                        'content': [
                            {
                                'component': 'VTable',
                                'props': {
                                    'hover': True,
                                    'density': 'comfortable'
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
                                                    {'component': 'th', 'text': '花粉'},
                                                    {'component': 'th', 'text': '签到天数'},
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
        })
        
        # 添加基本样式
        components.append({
                'component': 'style',
                'text': """
                .v-table {
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                }
                .v-table th {
                    background-color: rgba(var(--v-theme-primary), 0.05);
                    color: rgb(var(--v-theme-primary));
                    font-weight: 600;
                }
                """
        })
        
        return components

    def stop_service(self):
        """
        退出插件
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error("退出插件失败：%s" % str(e)) 

    def __check_and_push_mp_stats(self):
        """检查是否需要推送MoviePilot统计数据"""
        if not self._mp_push_enabled or not self._cookie:
            return
            
        # 检查上次推送时间，是否需要推送
        now = datetime.now()
        if self._last_push_time:
            last_push = datetime.strptime(self._last_push_time, '%Y-%m-%d %H:%M:%S')
            days_since_push = (now - last_push).days
            if days_since_push < self._mp_push_interval:
                logger.info(f"距离上次推送不足{self._mp_push_interval}天，跳过本次推送")
                return
                
        # 获取代理设置
        proxies = self._get_proxies()
        
        # 需要推送，首先获取用户信息
        res = RequestUtils(cookies=self._cookie, proxies=proxies).get_res(url="https://pting.club")
        if not res or res.status_code != 200:
            logger.error("请求蜂巢失败，无法获取用户信息进行推送")
            return
            
        # 获取CSRF令牌
        pattern = r'"csrfToken":"(.*?)"'
        csrf_matches = re.findall(pattern, res.text)
        if not csrf_matches:
            logger.error("获取CSRF令牌失败，无法进行推送")
            return
        csrf_token = csrf_matches[0]
        
        # 获取用户ID
        pattern = r'"userId":(\d+)'
        user_matches = re.search(pattern, res.text)
        if not user_matches:
            logger.error("获取用户ID失败，无法进行推送")
            return
        user_id = user_matches.group(1)
        
        # 执行推送
        self.__push_mp_stats(user_id=user_id, csrf_token=csrf_token)

    def __push_mp_stats(self, user_id=None, csrf_token=None):
        """推送MoviePilot统计数据到蜂巢论坛"""
        # 检查是否启用推送
        if not self._mp_push_enabled:
            return

        # 检查上次推送时间，是否需要推送
        now = datetime.now()
        if self._last_push_time:
            last_push = datetime.strptime(self._last_push_time, '%Y-%m-%d %H:%M:%S')
            days_since_push = (now - last_push).days
            if days_since_push < self._mp_push_interval:
                logger.info(f"距离上次推送不足{self._mp_push_interval}天，跳过本次推送")
                return
        
        # 如果没有传入user_id和csrf_token，直接返回
        if not user_id or not csrf_token:
            logger.error("用户ID或CSRF令牌为空，无法进行推送")
            return
        
        logger.info(f"开始获取站点统计数据以推送到蜂巢论坛 (用户ID: {user_id})")
            
        # 获取站点统计数据
        stats_data = self._get_site_statistics()
        if not stats_data:
            logger.error("获取站点统计数据失败，无法进行推送")
            return
            
        # 格式化数据
        formatted_stats = self._format_stats_data(stats_data)
        if not formatted_stats:
            logger.error("格式化站点统计数据失败，无法进行推送")
            return
        
        # 记录第一个站点的数据以便确认所有字段是否都被正确传递
        if formatted_stats.get("sites") and len(formatted_stats.get("sites")) > 0:
            first_site = formatted_stats.get("sites")[0]
            logger.info(f"推送数据示例：站点={first_site.get('name')}, 用户名={first_site.get('username')}, 等级={first_site.get('user_level')}, "
                        f"上传={first_site.get('upload')}, 下载={first_site.get('download')}, 分享率={first_site.get('ratio')}, "
                        f"魔力值={first_site.get('bonus')}, 做种数={first_site.get('seeding')}, 做种体积={first_site.get('seeding_size')}")
            
        # 准备请求头和请求体
        headers = {
            "X-Csrf-Token": csrf_token,
            "X-Http-Method-Override": "PATCH",  # 关键：使用PATCH方法覆盖
            "Content-Type": "application/json",
            "Cookie": self._cookie
        }
        
        # 创建请求数据
        data = {
            "data": {
                "type": "users",  # 注意：类型是users不是moviepilot-stats
                "attributes": {
                    "mpStatsSummary": json.dumps(formatted_stats.get("summary", {})),
                    "mpStatsSites": json.dumps(formatted_stats.get("sites", []))
                },
                "id": user_id
            }
        }
        
        # 输出JSON数据片段以便确认
        json_data = json.dumps(formatted_stats.get("sites", []))
        if len(json_data) > 500:
            logger.info(f"推送的JSON数据片段: {json_data[:500]}...")
        else:
            logger.info(f"推送的JSON数据: {json_data}")
        
        # 获取代理设置
        proxies = self._get_proxies()
        
        # 发送请求
        url = f"https://pting.club/api/users/{user_id}"
        logger.info(f"准备推送站点统计数据到蜂巢论坛: {len(formatted_stats.get('sites', []))} 个站点")
        res = RequestUtils(headers=headers, proxies=proxies).post_res(url=url, json=data)
        
        if res and res.status_code == 200:
            logger.info(f"成功推送MoviePilot统计数据到蜂巢论坛: 总上传 {round(formatted_stats['summary']['total_upload']/1024/1024/1024, 2)} GB, 总下载 {round(formatted_stats['summary']['total_download']/1024/1024/1024, 2)} GB")
            # 更新最后推送时间
            self._last_push_time = now.strftime('%Y-%m-%d %H:%M:%S')
            self.save_data('last_push_time', self._last_push_time)
            
            if self._notify:
                self._send_notification(
                    title="【✅ MoviePilot统计推送成功】",
                    text=(
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"✨ 状态：成功推送MoviePilot统计数据\n"
                        f"📊 站点数：{len(formatted_stats.get('sites', []))} 个\n"
                        f"🔄 下次推送：{(now + timedelta(days=self._mp_push_interval)).strftime('%Y-%m-%d')}\n"
                        f"━━━━━━━━━━"
                    )
                )
        else:
            logger.error(f"推送MoviePilot统计数据失败：{res.status_code if res else '请求失败'}, 响应: {res.text[:100] if res else ''}")
            if self._notify:
                self._send_notification(
                    title="【❌ MoviePilot统计推送失败】",
                    text=(
                        f"📢 执行结果\n"
                        f"━━━━━━━━━━\n"
                        f"🕐 时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"❌ 状态：推送MoviePilot统计数据失败\n"
                        f"━━━━━━━━━━\n"
                        f"💡 可能的解决方法\n"
                        f"• 检查Cookie是否有效\n"
                        f"• 确认站点是否可访问\n"
                        f"• 尝试手动登录网站\n"
                        f"━━━━━━━━━━"
                    )
                )

    def _get_site_statistics(self):
        """获取站点统计数据（参考站点统计插件实现）"""
        try:
            # 导入SiteOper类
            from app.db.site_oper import SiteOper
            from app.db.models.siteuserdata import SiteUserData
            
            # 初始化SiteOper
            site_oper = SiteOper()
            
            # 获取站点数据 - 使用get_userdata()方法
            raw_data_list = site_oper.get_userdata()
            
            if not raw_data_list:
                logger.error("未获取到站点数据")
                return None
            
            logger.info(f"成功获取到 {len(raw_data_list)} 条原始站点数据记录")
            
            # 打印第一条数据的所有字段，用于调试
            if raw_data_list and len(raw_data_list) > 0:
                first_data = raw_data_list[0]
                data_dict = first_data.to_dict() if hasattr(first_data, "to_dict") else first_data.__dict__
                if "_sa_instance_state" in data_dict:
                    data_dict.pop("_sa_instance_state")
                logger.info(f"站点数据示例字段: {list(data_dict.keys())}")
                logger.info(f"站点数据示例值: {data_dict}")
            
            # 每个站点只保留最新的一条数据（参考站点统计插件的__get_data方法）
            # 使用站点名称和日期组合作为键，确保每个站点每天只有一条记录
            data_dict = {f"{data.updated_day}_{data.name}": data for data in raw_data_list}
            data_list = list(data_dict.values())
            
            # 按日期倒序排序
            data_list.sort(key=lambda x: x.updated_day, reverse=True)
            
            # 获取每个站点的最新数据
            site_names = set()
            latest_site_data = []
            
            for data in data_list:
                if data.name not in site_names:
                    site_names.add(data.name)
                    latest_site_data.append(data)
            
            logger.info(f"处理后得到 {len(latest_site_data)} 个站点的最新数据")
                
            # 转换为字典格式
            sites = []
            for site_data in latest_site_data:
                # 转换为字典
                site_dict = site_data.to_dict() if hasattr(site_data, "to_dict") else site_data.__dict__
                # 移除不需要的属性
                if "_sa_instance_state" in site_dict:
                    site_dict.pop("_sa_instance_state")
                sites.append(site_dict)
                
            # 记录几个站点的名称作为示例
            sample_sites = [site.get("name") for site in sites[:3] if site.get("name")]
            logger.info(f"站点数据示例: {', '.join(sample_sites) if sample_sites else '无'}")
                
            return {"sites": sites}
                
        except ImportError as e:
            logger.error(f"导入站点操作模块失败: {str(e)}")
            # 降级到API方式获取
            return self._get_site_statistics_via_api()
        except Exception as e:
            logger.error(f"获取站点统计数据出错: {str(e)}")
            # 降级到API方式获取
            return self._get_site_statistics_via_api()
            
    def _get_site_statistics_via_api(self):
        """通过API获取站点统计数据（备用方法）"""
        try:
            # 使用正确的API URL
            api_url = f"{settings.HOST}/api/v1/site/statistics"
            
            # 使用全局API KEY
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.API_TOKEN}"
            }
            
            logger.info(f"尝试通过API获取站点数据: {api_url}")
            res = RequestUtils(headers=headers).get_res(url=api_url)
            if res and res.status_code == 200:
                data = res.json()
                sites = data.get("sites", [])
                logger.info(f"通过API成功获取 {len(sites)} 个站点数据")
                return data
            else:
                logger.error(f"获取站点统计数据失败: {res.status_code if res else '连接失败'}")
                return None
        except Exception as e:
            logger.error(f"获取站点统计数据出错: {str(e)}")
            return None
            
    def _format_stats_data(self, stats_data):
        """格式化站点统计数据"""
        try:
            if not stats_data or not stats_data.get("sites"):
                return None
                
            sites = stats_data.get("sites", [])
            logger.info(f"开始格式化 {len(sites)} 个站点的数据")
            
            # 汇总数据
            total_upload = 0
            total_download = 0
            total_seed = 0
            total_seed_size = 0
            site_details = []
            valid_sites_count = 0
            
            # 处理每个站点数据
            for site in sites:
                if not site.get("name") or site.get("error"):
                    continue
                
                valid_sites_count += 1
                
                # 计算分享率
                upload = float(site.get("upload", 0))
                download = float(site.get("download", 0))
                ratio = round(upload / download, 2) if download > 0 else float('inf')
                
                # 汇总
                total_upload += upload
                total_download += download
                total_seed += int(site.get("seeding", 0))
                total_seed_size += float(site.get("seeding_size", 0))
                
                # 确保数值类型字段有默认值
                username = site.get("username", "")
                user_level = site.get("user_level", "")
                bonus = site.get("bonus", 0)
                seeding = site.get("seeding", 0)
                seeding_size = site.get("seeding_size", 0)
                
                # 将所有需要的字段保存到站点详情中
                site_details.append({
                    "name": site.get("name"),
                    "username": username,
                    "user_level": user_level,
                    "upload": upload,
                    "download": download,
                    "ratio": ratio,
                    "bonus": bonus,
                    "seeding": seeding,
                    "seeding_size": seeding_size
                })
                
                # 记录日志确认某个特定站点的数据是否包含所有字段
                if site.get("name") == sites[0].get("name"):
                    logger.info(f"站点 {site.get('name')} 数据: 用户名={username}, 等级={user_level}, 魔力值={bonus}, 做种大小={seeding_size}")
            
            # 构建结果
            result = {
                "summary": {
                    "total_upload": total_upload,
                    "total_download": total_download,
                    "total_seed": total_seed,
                    "total_seed_size": total_seed_size,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "sites": site_details
            }
            
            logger.info(f"数据格式化完成: 有效站点 {valid_sites_count} 个，总上传 {round(total_upload/1024/1024/1024, 2)} GB，总下载 {round(total_download/1024/1024/1024, 2)} GB，总做种数 {total_seed}")
            
            return result
        except Exception as e:
            logger.error(f"格式化站点统计数据出错: {str(e)}")
            return None 
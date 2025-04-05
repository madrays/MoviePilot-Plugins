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

        # 重置当前重试次数
        self._current_retry = 0

        if self._onlyonce:
            # 定时服务
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
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
            })

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

    def __signin(self):
        """
        蜂巢签到
        """

        # 获取系统代理配置
        proxies = settings.PROXY if hasattr(settings, 'PROXY') else None
        
        # 连接失败处理
        if proxies:
            res = RequestUtils(cookies=self._cookie, proxies=proxies).get_res(url="https://pting.club")
        else:
            res = RequestUtils(cookies=self._cookie).get_res(url="https://pting.club")
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

        # 获取系统代理配置
        proxies = settings.PROXY if hasattr(settings, 'PROXY') else None

        # 开始签到
        if proxies:
            res = RequestUtils(headers=headers, proxies=proxies).post_res(url=f"https://pting.club/api/users/{userId}", json=data)
        else:
            res = RequestUtils(headers=headers).post_res(url=f"https://pting.club/api/users/{userId}", json=data)

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
        if self._enabled and self._cron:
            return [{
                "id": "FengchaoSignin",
                "name": "蜂巢签到服务",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.__signin,
                "kwargs": {}
            }]
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VCard',
                        'props': {
                            'variant': 'outlined',
                            'class': 'mb-3'
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
                                                    'md': 6
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
                                                    'cols': 12
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VAlert',
                                                        'props': {
                                                            'type': 'info',
                                                            'variant': 'tonal',
                                                            'density': 'compact',
                                                            'class': 'mt-2'
                                                        },
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
                                                                            'class': 'mr-2'
                                                                        },
                                                                        'text': 'mdi-flower'
                                                                    },
                                                                    {
                                                                        'component': 'span',
                                                                        'text': '每日签到可获得10花粉奖励'
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
                    },
                    {
                        'component': 'VCard',
                        'props': {
                            'variant': 'outlined'
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
                                        'text': 'mdi-cookie'
                                    },
                                    {
                                        'component': 'span',
                                        'text': '账号设置'
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
                                                    'cols': 12
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VTextField',
                                                        'props': {
                                                            'model': 'cookie',
                                                            'label': 'Cookie',
                                                            'placeholder': '输入蜂巢Cookie'
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
                                                        'component': 'VAlert',
                                                        'props': {
                                                            'type': 'info',
                                                            'variant': 'tonal',
                                                            'density': 'compact',
                                                            'text': '蜂巢Cookie获取方法：浏览器登录蜂巢，F12控制台，Network标签，刷新页面，找到pting.club请求，右键Copy -> Copy as cURL，从复制内容中找到cookie: 后的内容'
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
                                                        'component': 'div',
                                                        'props': {
                                                            'class': 'text-caption text-grey text-right mt-2'
                                                        },
                                                        'text': 'Plugin improved by: thsrite'
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
            "retry_interval": 2
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
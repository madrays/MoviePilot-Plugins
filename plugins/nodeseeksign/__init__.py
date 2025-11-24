"""
NodeSeek论坛签到插件
版本: 1.1.0
作者: Madrays
功能:
- 自动完成NodeSeek论坛每日签到
- 支持选择随机奖励或固定奖励
- 自动失败重试机制
- 定时签到和历史记录
- 支持绕过CloudFlare防护
"""
import time
import random
import traceback
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger
from app.schemas import NotificationType
import requests
from urllib.parse import urlencode
import json

# cloudscraper 作为 Cloudflare 备用方案
try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except Exception:
    HAS_CLOUDSCRAPER = False

# 尝试导入curl_cffi库，用于绕过CloudFlare防护
try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False


class nodeseeksign(_PluginBase):
    # 插件名称
    plugin_name = "NodeSeek论坛签到"
    # 插件描述
    plugin_desc = "懒羊羊定制：自动完成NodeSeek论坛每日签到，支持随机奖励和自动重试功能"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/nodeseeksign.png"
    # 插件版本
    plugin_version = "2.1.0"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "nodeseeksign_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _cookie = None
    _notify = False
    _onlyonce = False
    _clear_history = False  # 新增：是否清除历史记录
    _cron = None
    _random_choice = True  # 是否选择随机奖励，否则选择固定奖励
    _history_days = 30  # 历史保留天数
    _use_proxy = True     # 是否使用代理，默认启用
    _max_retries = 3      # 最大重试次数
    _retry_count = 0      # 当天重试计数
    _scheduled_retry = None  # 计划的重试任务
    _verify_ssl = False    # 是否验证SSL证书，默认禁用
    _min_delay = 5         # 请求前最小随机等待（秒）
    _max_delay = 12        # 请求前最大随机等待（秒）
    _member_id = ""       # NodeSeek 成员ID（可选，用于获取用户信息）
    _stats_days = 30

    _scraper = None        # cloudscraper 实例

    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None
    _manual_trigger = False

    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()

        logger.info("============= nodeseeksign 初始化 =============")
        try:
            if config:
                self._enabled = config.get("enabled")
                self._cookie = config.get("cookie")
                self._notify = config.get("notify")
                self._cron = config.get("cron")
                self._onlyonce = config.get("onlyonce")
                self._random_choice = config.get("random_choice")
                # 确保数值类型配置的安全性
                try:
                    self._history_days = int(config.get("history_days", 30))
                except (ValueError, TypeError):
                    self._history_days = 30
                    logger.warning("history_days 配置无效，使用默认值 30")
                
                self._use_proxy = config.get("use_proxy", True)
                
                try:
                    self._max_retries = int(config.get("max_retries", 3))
                except (ValueError, TypeError):
                    self._max_retries = 3
                    logger.warning("max_retries 配置无效，使用默认值 3")
                
                self._verify_ssl = config.get("verify_ssl", False)
                
                try:
                    self._min_delay = int(config.get("min_delay", 5))
                except (ValueError, TypeError):
                    self._min_delay = 5
                    logger.warning("min_delay 配置无效，使用默认值 5")
                
                try:
                    self._max_delay = int(config.get("max_delay", 12))
                except (ValueError, TypeError):
                    self._max_delay = 12
                    logger.warning("max_delay 配置无效，使用默认值 12")
                self._member_id = (config.get("member_id") or "").strip()
                self._clear_history = config.get("clear_history", False) # 初始化清除历史记录
                try:
                    self._stats_days = int(config.get("stats_days", 30))
                except (ValueError, TypeError):
                    self._stats_days = 30
                
                logger.info(f"配置: enabled={self._enabled}, notify={self._notify}, cron={self._cron}, "
                           f"random_choice={self._random_choice}, history_days={self._history_days}, "
                           f"use_proxy={self._use_proxy}, max_retries={self._max_retries}, verify_ssl={self._verify_ssl}, "
                           f"min_delay={self._min_delay}, max_delay={self._max_delay}, member_id={self._member_id or '未设置'}, clear_history={self._clear_history}")
                # 初始化 cloudscraper（可选，用于绕过 Cloudflare）
                if HAS_CLOUDSCRAPER:
                    try:
                        self._scraper = cloudscraper.create_scraper(browser="chrome")
                    except Exception:
                        try:
                            self._scraper = cloudscraper.create_scraper()
                        except Exception as e2:
                            logger.warning(f"cloudscraper 初始化失败: {str(e2)}")
                            self._scraper = None
                    if self._scraper:
                        proxies = self._get_proxies()
                        if proxies:
                            self._scraper.proxies = proxies
                            logger.info(f"cloudscraper 初始化代理: {self._scraper.proxies}")
                        logger.info("cloudscraper 初始化成功")
            
            if self._onlyonce:
                logger.info("执行一次性签到")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._manual_trigger = True
                self._scheduler.add_job(func=self.sign, trigger='date',
                                   run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                   name="NodeSeek论坛签到")
                self._onlyonce = False
                self.update_config({
                    "onlyonce": False,
                    "enabled": self._enabled,
                    "cookie": self._cookie,
                    "notify": self._notify,
                    "cron": self._cron,
                    "random_choice": self._random_choice,
                    "history_days": self._history_days,
                    "use_proxy": self._use_proxy,
                    "max_retries": self._max_retries,
                    "verify_ssl": self._verify_ssl,
                    "min_delay": self._min_delay,
                    "max_delay": self._max_delay,
                    "member_id": self._member_id,
                    "clear_history": self._clear_history,
                    "stats_days": self._stats_days
                })

                # 启动任务
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()

                # 如果需要清除历史记录，则清空
                if self._clear_history:
                    logger.info("检测到清除历史记录标志，开始清空数据...")
                    self.clear_sign_history()
                    logger.info("已清除签到历史记录")
                    # 保存配置，将 clear_history 设置为 False
                    self.update_config({
                        "onlyonce": False,
                        "enabled": self._enabled,
                        "cookie": self._cookie,
                        "notify": self._notify,
                        "cron": self._cron,
                        "random_choice": self._random_choice,
                        "history_days": self._history_days,
                        "use_proxy": self._use_proxy,
                        "max_retries": self._max_retries,
                        "verify_ssl": self._verify_ssl,
                        "min_delay": self._min_delay,
                        "max_delay": self._max_delay,
                        "member_id": self._member_id,
                        "clear_history": False,
                        "stats_days": self._stats_days
                    })
                    logger.info("已保存配置，clear_history 已重置为 False")

        except Exception as e:
            logger.error(f"nodeseeksign初始化错误: {str(e)}", exc_info=True)

    def sign(self):
        """
        执行NodeSeek签到
        """
        logger.info("============= 开始NodeSeek签到 =============")
        sign_dict = None
        
        try:
            # 检查Cookie
            if not self._cookie:
                logger.error("未配置Cookie")
                sign_dict = {
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败: 未配置Cookie",
                }
                self._save_sign_history(sign_dict)
                
                if self._notify:
                    self.post_message(
                        mtype=NotificationType.SiteMessage,
                        title="【NodeSeek论坛签到失败】",
                        text="未配置Cookie，请在设置中添加Cookie"
                    )
                return sign_dict
            
            # 请求前随机等待
            self._wait_random_interval()
            
            # 无论任何情况都尝试执行API签到
            result = self._run_api_sign()
            
            # 始终获取最新用户信息
            user_info = None
            try:
                if getattr(self, "_member_id", ""):
                    user_info = self._fetch_user_info(self._member_id)
            except Exception as e:
                logger.warning(f"获取用户信息失败: {str(e)}")
            
            # 始终获取签到记录以获取奖励和排名
            attendance_record = None
            try:
                attendance_record = self._fetch_attendance_record()
            except Exception as e:
                logger.warning(f"获取签到记录失败: {str(e)}")
            
            # 处理签到结果
            if result["success"]:
                # 保存签到记录（包含奖励信息）
                sign_dict = {
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到成功" if not result.get("already_signed") else "已签到",
                    "message": result.get("message", "")
                }
                
                # 添加奖励信息到历史记录
                if attendance_record and attendance_record.get("gain"):
                    sign_dict["gain"] = attendance_record.get("gain")
                    if attendance_record.get("rank"):
                        sign_dict["rank"] = attendance_record.get("rank")
                        sign_dict["total_signers"] = attendance_record.get("total_signers")
                elif result.get("gain"):
                    sign_dict["gain"] = result.get("gain")
                
                self._save_sign_history(sign_dict)
                self._save_last_sign_date()
                # 重置重试计数
                self._retry_count = 0

                # 发送通知
                if self._notify:
                    try:
                        self._send_sign_notification(sign_dict, result, user_info, attendance_record)
                        logger.info("签到成功通知发送成功")
                    except Exception as e:
                        logger.error(f"签到成功通知发送失败: {str(e)}")
                        # 通知失败不影响主流程，继续执行
                try:
                    stats = self._get_signin_stats(self._stats_days)
                    if stats:
                        self.save_data('last_signin_stats', stats)
                except Exception as e:
                    logger.warning(f"获取收益统计失败: {str(e)}")
            else:
                # 签到失败，安排重试
                sign_dict = {
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "签到失败",
                    "message": result.get("message", "")
                }
                
                # 最后兜底：通过签到记录进行时间验证或当日确认
                try:
                    if attendance_record and attendance_record.get("created_at"):
                        record_date = datetime.fromisoformat(attendance_record["created_at"].replace('Z', '+00:00'))
                        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        if record_date.date() == today.date():
                            logger.info(f"从签到记录确认今日已签到: {attendance_record}")
                            result["success"] = True
                            result["already_signed"] = True
                            result["message"] = "今日已签到（记录确认）"
                            sign_dict["status"] = "已签到（记录确认）"
                        else:
                            # 兜底时间验证：仅当无其它成功信号时，且时间差极小才认为成功
                            current_time = datetime.utcnow()
                            record_time = datetime.fromisoformat(attendance_record["created_at"].replace('Z', '+00:00')).replace(tzinfo=None)
                            time_diff = abs((current_time - record_time).total_seconds() / 3600)
                            logger.info(f"兜底时间验证差值: {time_diff:.2f}h")
                            if time_diff < 0.5:
                                logger.info("时间差 < 0.5h，作为最后兜底判定为成功")
                                result["success"] = True
                                result["signed"] = True
                                sign_dict["status"] = "签到成功（兜底时间验证）"
                                result["message"] = "签到成功（兜底时间验证）"
                    else:
                        logger.info("无有效签到记录用于兜底")
                except Exception as e:
                    logger.warning(f"兜底时间验证失败: {str(e)}")
                
                # 保存历史记录（包括可能通过兜底更改的状态）
                self._save_sign_history(sign_dict)
                try:
                    stats = self._get_signin_stats(self._stats_days)
                    if stats:
                        self.save_data('last_signin_stats', stats)
                except Exception as e:
                    logger.warning(f"获取收益统计失败: {str(e)}")
                
                # 检查是否需要重试
                # 确保 _max_retries 是整数类型
                max_retries = int(self._max_retries) if self._max_retries is not None else 0
                
                if max_retries and self._retry_count < max_retries:
                    self._retry_count += 1
                    retry_minutes = random.randint(5, 15)
                    retry_time = datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(minutes=retry_minutes)
                    
                    logger.info(f"签到失败，将在 {retry_minutes} 分钟后重试 (重试 {self._retry_count}/{max_retries})")
                    
                    # 安排重试任务
                    if not self._scheduler:
                        self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                        if not self._scheduler.running:
                            self._scheduler.start()
                    
                    # 移除之前计划的重试任务（如果有）
                    if self._scheduled_retry:
                        try:
                            self._scheduler.remove_job(self._scheduled_retry)
                        except Exception as e:
                            # 忽略移除不存在任务的错误
                            logger.warning(f"移除旧任务时出错 (可忽略): {str(e)}")
                    
                    # 添加新的重试任务
                    self._scheduled_retry = f"nodeseek_retry_{int(time.time())}"
                    self._scheduler.add_job(
                        func=self.sign,
                        trigger='date',
                        run_date=retry_time,
                        id=self._scheduled_retry,
                    name=f"NodeSeek论坛签到重试 {self._retry_count}/{max_retries}"
                    )
                    
                    if self._notify:
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【NodeSeek论坛签到失败】",
                            text=f"签到失败: {result.get('message', '未知错误')}\n将在 {retry_minutes} 分钟后进行第 {self._retry_count}/{max_retries} 次重试\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                else:
                    # 达到最大重试次数或未配置重试
                    if max_retries == 0:
                        logger.info("未配置自动重试 (max_retries=0)，本次结束")
                    else:
                        logger.warning(f"已达到最大重试次数 ({max_retries})，今日不再重试")
                    
                    if self._notify:
                        retry_text = "未配置自动重试" if max_retries == 0 else f"已达到最大重试次数 ({max_retries})"
                        self.post_message(
                            mtype=NotificationType.SiteMessage,
                            title="【NodeSeek论坛签到失败】",
                            text=f"签到失败: {result.get('message', '未知错误')}\n{retry_text}\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
            
            return sign_dict
        
        except Exception as e:
            logger.error(f"NodeSeek签到过程中出错: {str(e)}", exc_info=True)
            logger.error(f"错误类型: {type(e)}")
            logger.error(f"错误详情: {str(e)}")
            
            # 记录当前状态用于调试
            try:
                logger.error(f"当前 sign_dict: {sign_dict}")
                logger.error(f"当前 result: {result if 'result' in locals() else '未定义'}")
            except Exception as debug_e:
                logger.error(f"记录调试信息失败: {str(debug_e)}")
            
            sign_dict = {
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "status": f"签到出错: {str(e)}",
            }
            self._save_sign_history(sign_dict)
            
            if self._notify:
                self.post_message(
                    mtype=NotificationType.SiteMessage,
                    title="【NodeSeek论坛签到出错】",
                    text=f"签到过程中出错: {str(e)}\n⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            return sign_dict
    
    def _run_api_sign(self):
        """
        使用API执行NodeSeek签到
        """
        try:
            result = {"success": False, "signed": False, "already_signed": False, "message": ""}
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Content-Length': '0',
                'Content-Type': 'application/json',
                'Origin': 'https://www.nodeseek.com',
                'Referer': 'https://www.nodeseek.com/board',
                'Sec-CH-UA': '"Chromium";v="136", "Not:A-Brand";v="24", "Google Chrome";v="136"',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                'Cookie': self._cookie
            }
            random_param = "true" if self._random_choice else "false"
            url = f"https://www.nodeseek.com/api/attendance?random={random_param}"
            proxies = self._get_proxies()
            response = self._smart_post(url=url, headers=headers, data=b'', proxies=proxies, timeout=30)
            try:
                logger.info(f"签到响应状态码: {response.status_code}")
                ct = response.headers.get('Content-Type') or response.headers.get('content-type')
                if ct:
                    logger.info(f"签到响应Content-Type: {ct}")
            except Exception:
                pass
            try:
                data = response.json()
                msg = data.get('message', '')
                if data.get('success') is True:
                    result.update({"success": True, "signed": True, "message": msg})
                    gain = data.get('gain', 0)
                    current = data.get('current', 0)
                    if gain:
                        result.update({"gain": gain, "current": current})
                elif "鸡腿" in msg:
                    result.update({"success": True, "signed": True, "message": msg})
                elif "已完成签到" in msg:
                    result.update({"success": True, "already_signed": True, "message": msg})
                elif msg == "USER NOT FOUND" or data.get('status') == 404:
                    result.update({"message": "Cookie已失效，请更新"})
                elif "签到" in msg and ("成功" in msg or "完成" in msg):
                    result.update({"success": True, "signed": True, "message": msg})
                else:
                    result.update({"message": msg or f"未知响应: {response.status_code}"})
            except Exception:
                text = response.text or ""
                snippet = text[:400] if len(text) > 400 else text
                logger.warning(f"非JSON签到响应文本片段: {snippet}")
                self.save_data('last_sign_response', {
                    'status_code': getattr(response, 'status_code', None),
                    'content_type': response.headers.get('Content-Type', ''),
                    'text_snippet': snippet
                })
                try:
                    warm = self._scraper_warmup_and_attach_user_cookie()
                    if warm:
                        logger.info("尝试使用 cloudscraper 预热后携带用户Cookie再次POST")
                        headers_retry = dict(headers)
                        headers_retry.pop('Cookie', None)
                        resp_retry = warm.post(url, headers=headers_retry, timeout=30)
                        ct_retry = resp_retry.headers.get('Content-Type', '')
                        if 'application/json' in (ct_retry or '').lower():
                            data = resp_retry.json()
                            msg = data.get('message', '')
                            if data.get('success') is True:
                                result.update({"success": True, "signed": True, "message": msg})
                                gain = data.get('gain', 0)
                                current = data.get('current', 0)
                                if gain:
                                    result.update({"gain": gain, "current": current})
                                return result
                            elif "已完成签到" in msg:
                                result.update({"success": True, "already_signed": True, "message": msg})
                                return result
                except Exception as e2:
                    logger.warning(f"预热+重试失败: {str(e2)}")
                if any(k in text for k in ["鸡腿", "签到成功", "签到完成", "success"]):
                    result.update({"success": True, "signed": True, "message": text[:80]})
                elif "已完成签到" in text:
                    result.update({"success": True, "already_signed": True, "message": text[:80]})
                elif "Cannot GET /api/attendance" in text:
                    result.update({"message": "服务端拒绝GET，需要POST；可能被WAF拦截"})
                elif any(k in text for k in ["登录", "注册", "你好啊，陌生人"]):
                    result.update({"message": "未登录或Cookie失效，返回登录页"})
                else:
                    result.update({"message": f"非JSON响应({response.status_code})"})
            return result
        except Exception as e:
            logger.error(f"API签到出错: {str(e)}", exc_info=True)
            return {"success": False, "message": f"API签到出错: {str(e)}"}

    def _scraper_warmup_and_attach_user_cookie(self):
        try:
            if not (HAS_CLOUDSCRAPER and self._scraper):
                return None
            proxies = self._get_proxies()
            if proxies:
                self._scraper.proxies = self._normalize_proxies(proxies) or {}
            self._scraper.get('https://www.nodeseek.com/board', timeout=30)
            base = self._cookie or ''
            try:
                for part in base.split(';'):
                    kv = part.strip().split('=', 1)
                    if len(kv) == 2:
                        name, value = kv[0].strip(), kv[1].strip()
                        if name and value:
                            self._scraper.cookies.set(name, value, domain='www.nodeseek.com')
            except Exception:
                pass
            return self._scraper
        except Exception as e:
            logger.warning(f"cloudscraper 预热失败: {str(e)}")
            return None
    
    def _get_proxies(self):
        """
        获取代理设置
        """
        if not self._use_proxy:
            logger.info("未启用代理")
            return None
        try:
            if hasattr(settings, 'PROXY') and settings.PROXY:
                norm = self._normalize_proxies(settings.PROXY)
                if norm:
                    return norm
            logger.warning("系统代理未配置或无效")
            return None
        except Exception as e:
            logger.error(f"获取代理设置出错: {str(e)}")
            return None

    def _normalize_proxies(self, proxies_input):
        """
        归一化代理配置为 requests 兼容格式 {"http": url, "https": url}
        支持字符串或字典输入。
        """
        try:
            if not proxies_input:
                return None
            if isinstance(proxies_input, str):
                return {"http": proxies_input, "https": proxies_input}
            if isinstance(proxies_input, dict):
                http_url = proxies_input.get("http") or proxies_input.get("HTTP") or proxies_input.get("https") or proxies_input.get("HTTPS")
                https_url = proxies_input.get("https") or proxies_input.get("HTTPS") or proxies_input.get("http") or proxies_input.get("HTTP")
                if not http_url and not https_url:
                    return None
                return {"http": http_url or https_url, "https": https_url or http_url}
        except Exception as e:
            logger.warning(f"代理归一化失败，将忽略代理: {str(e)}")
        return None
    def _wait_random_interval(self):
        """
        在请求前随机等待，模拟人类行为
        """
        try:
            # 确保延迟参数是数值类型
            min_delay = float(self._min_delay) if self._min_delay is not None else 5.0
            max_delay = float(self._max_delay) if self._max_delay is not None else 12.0
            
            if max_delay >= min_delay and min_delay > 0:
                delay = random.uniform(min_delay, max_delay)
                logger.info(f"请求前随机等待 {delay:.2f} 秒...")
                time.sleep(delay)
            else:
                logger.warning(f"延迟参数无效: min_delay={min_delay}, max_delay={max_delay}，跳过随机等待")
        except Exception as e:
            logger.debug(f"随机等待失败（忽略）：{str(e)}")

    def _smart_post(self, url, headers=None, data=None, json=None, proxies=None, timeout=30):
        """
        统一的POST请求适配器：
        1) curl_cffi (impersonate Chrome)
        2) cloudscraper
        3) requests
        """
        last_error = None

        # 1) cloudscraper 优先
        if HAS_CLOUDSCRAPER and self._scraper:
            try:
                logger.info("使用 cloudscraper 发送请求")
                if proxies:
                    self._scraper.proxies = self._normalize_proxies(proxies) or {}
                    if self._scraper.proxies:
                        logger.info(f"cloudscraper 已应用代理: {self._scraper.proxies}")
                resp = self._scraper.post(url, headers=headers, data=data, json=json, timeout=timeout) if not self._verify_ssl else self._scraper.post(url, headers=headers, data=data, json=json, timeout=timeout, verify=True)
                ct = resp.headers.get('Content-Type') or resp.headers.get('content-type') or ''
                if resp.status_code in (400, 403) or ('text/html' in ct.lower()):
                    logger.info("cloudscraper 返回非预期，尝试 curl_cffi 回退")
                else:
                    return resp
            except Exception as e:
                last_error = e
                logger.warning(f"cloudscraper 请求失败，将回退：{str(e)}")

        # 2) curl_cffi 次选
        if HAS_CURL_CFFI:
            try:
                logger.info("使用 curl_cffi 发送请求 (Chrome-110 仿真)")
                session = curl_requests.Session(impersonate="chrome110")
                if proxies:
                    session.proxies = self._normalize_proxies(proxies) or {}
                    if session.proxies:
                        logger.info(f"curl_cffi 已应用代理: {session.proxies}")
                resp = session.post(url, headers=headers, data=data, json=json, timeout=timeout) if not self._verify_ssl else session.post(url, headers=headers, data=data, json=json, timeout=timeout, verify=True)
                ct = resp.headers.get('Content-Type') or resp.headers.get('content-type') or ''
                if resp.status_code in (400, 403) or ('text/html' in ct.lower()):
                    if proxies:
                        try:
                            logger.info("curl_cffi 返回非预期，尝试无代理回退")
                            resp2 = session.post(url, headers=headers, data=data, json=json, timeout=timeout) if not self._verify_ssl else session.post(url, headers=headers, data=data, json=json, timeout=timeout, verify=True)
                            ct2 = resp2.headers.get('Content-Type') or resp2.headers.get('content-type') or ''
                            if resp2.status_code not in (400, 403) and ('text/html' not in ct2.lower()):
                                return resp2
                        except Exception as e2:
                            logger.warning(f"无代理回退失败：{str(e2)}")
                    logger.info("curl_cffi 返回非预期，尝试 requests 回退")
                else:
                    return resp
            except Exception as e:
                last_error = e
                logger.warning(f"curl_cffi 请求失败，将回退：{str(e)}")

        # 3) requests 兜底
        try:
            norm = self._normalize_proxies(proxies)
            resp = requests.post(url, headers=headers, data=data, json=json, proxies=norm, timeout=timeout) if not self._verify_ssl else requests.post(url, headers=headers, data=data, json=json, proxies=norm, timeout=timeout, verify=True)
            ct = resp.headers.get('Content-Type') or resp.headers.get('content-type') or ''
            if resp.status_code in (400, 403) or ('text/html' in ct.lower()):
                logger.warning("requests 返回非预期，不再继续使用 requests")
                raise Exception("requests non-JSON/non-200")
            return resp
        except Exception as e:
            if last_error:
                logger.error(f"此前错误：{str(last_error)}")
            raise

    def _smart_get(self, url, headers=None, proxies=None, timeout=30):
        """
        统一的GET请求适配器（顺序同 _smart_post）
        """
        last_error = None
        if HAS_CLOUDSCRAPER and self._scraper:
            try:
                if proxies:
                    self._scraper.proxies = self._normalize_proxies(proxies) or {}
                    if self._scraper.proxies:
                        logger.info(f"cloudscraper 已应用代理: {self._scraper.proxies}")
                resp = self._scraper.get(url, headers=headers, timeout=timeout) if not self._verify_ssl else self._scraper.get(url, headers=headers, timeout=timeout, verify=True)
                ct = resp.headers.get('Content-Type') or resp.headers.get('content-type') or ''
                if resp.status_code in (400, 403) or ('text/html' in ct.lower()):
                    logger.info("cloudscraper GET 返回非预期，尝试 curl_cffi 回退")
                else:
                    return resp
            except Exception as e:
                last_error = e
                logger.warning(f"cloudscraper GET 失败，将回退：{str(e)}")
        if HAS_CURL_CFFI:
            try:
                session = curl_requests.Session(impersonate="chrome110")
                if proxies:
                    session.proxies = self._normalize_proxies(proxies) or {}
                    if session.proxies:
                        logger.info(f"curl_cffi 已应用代理: {session.proxies}")
                resp = session.get(url, headers=headers, timeout=timeout) if not self._verify_ssl else session.get(url, headers=headers, timeout=timeout, verify=True)
                ct = resp.headers.get('Content-Type') or resp.headers.get('content-type') or ''
                if resp.status_code in (400, 403) or ('text/html' in ct.lower()):
                    if proxies:
                        try:
                            logger.info("curl_cffi GET 返回非预期，尝试无代理回退")
                            resp2 = session.get(url, headers=headers, timeout=timeout) if not self._verify_ssl else session.get(url, headers=headers, timeout=timeout, verify=True)
                            ct2 = resp2.headers.get('Content-Type') or resp2.headers.get('content-type') or ''
                            if resp2.status_code not in (400, 403) and ('text/html' not in ct2.lower()):
                                return resp2
                        except Exception as e2:
                            logger.warning(f"无代理回退失败：{str(e2)}")
                    logger.info("curl_cffi GET 返回非预期，尝试 requests 回退")
                else:
                    return resp
            except Exception as e:
                last_error = e
                logger.warning(f"curl_cffi GET 失败，将回退：{str(e)}")
        try:
            norm = self._normalize_proxies(proxies)
            if norm:
                logger.info(f"requests 已应用代理: {norm}")
            if self._verify_ssl:
                return requests.get(url, headers=headers, proxies=norm, timeout=timeout, verify=True)
            return requests.get(url, headers=headers, proxies=norm, timeout=timeout)
        except Exception as e:
            logger.error(f"requests GET 失败：{str(e)}")
            if last_error:
                logger.error(f"此前错误：{str(last_error)}")
            raise

    def _fetch_user_info(self, member_id: str) -> dict:
        """
        拉取 NodeSeek 用户信息（可选）
        """
        if not member_id:
            return {}
        url = f"https://www.nodeseek.com/api/account/getInfo/{member_id}?readme=1"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://www.nodeseek.com",
            "Referer": f"https://www.nodeseek.com/space/{member_id}",
            "Sec-CH-UA": '"Chromium";v="136", "Not:A-Brand";v="24", "Google Chrome";v="136"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        }
        proxies = self._get_proxies()
        resp = self._smart_get(url=url, headers=headers, proxies=proxies, timeout=30)
        try:
            data = resp.json()
            detail = data.get("detail") or {}
            if detail:
                self.save_data('last_user_info', detail)
            return detail
        except Exception:
            return {}

    def _fetch_attendance_record(self) -> dict:
        """
        拉取签到记录页面作为兜底，获取签到奖励信息
        """
        try:
            url = "https://www.nodeseek.com/api/attendance/board?page=1"
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Origin": "https://www.nodeseek.com",
                "Referer": "https://www.nodeseek.com/board",
                "Sec-CH-UA": '"Chromium";v="136", "Not:A-Brand";v="24", "Google Chrome";v="136"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                "Cookie": self._cookie
            }
            proxies = self._get_proxies()
            resp = self._smart_get(url=url, headers=headers, proxies=proxies, timeout=30)
            
            # 处理可能的压缩响应
            content_encoding = resp.headers.get('content-encoding', '').lower()
            if content_encoding == 'br':
                try:
                    import brotli
                    decompressed_content = brotli.decompress(resp.content)
                    response_text = decompressed_content.decode('utf-8')
                except ImportError:
                    response_text = resp.text
                except Exception:
                    response_text = resp.text
            else:
                response_text = resp.text
            
            try:
                logger.info(f"签到记录响应状态码: {resp.status_code}")
                ct = resp.headers.get('Content-Type') or resp.headers.get('content-type')
                if ct:
                    logger.info(f"签到记录响应Content-Type: {ct}")
            except Exception:
                pass
            data = None
            try:
                data = resp.json()
            except Exception:
                try:
                    data = json.loads(response_text or "")
                except Exception:
                    snippet = (resp.text or "")[:400]
                    logger.warning(f"签到记录非JSON响应文本片段: {snippet}")
                    self.save_data('last_attendance_response', {
                        'status_code': getattr(resp, 'status_code', None),
                        'content_type': resp.headers.get('Content-Type', ''),
                        'text_snippet': snippet
                    })
                    cached = self.get_data('last_attendance_record') or {}
                    try:
                        if cached and cached.get('created_at'):
                            sh_tz = pytz.timezone('Asia/Shanghai')
                            rec_dt = datetime.fromisoformat(cached['created_at'].replace('Z', '+00:00')).astimezone(sh_tz)
                            if rec_dt.date() == datetime.now(sh_tz).date():
                                return cached
                    except Exception:
                        pass
                    return {}
            record = data.get("record", {})
            if record:
                # 获取用户排名信息
                try:
                    # 直接从API返回的数据中获取排名信息
                    if "order" in data:
                        record['rank'] = data.get("order")
                        record['total_signers'] = data.get("total")
                        logger.info(f"获取用户签到排名: 第{record['rank']}名，共{record['total_signers']}人")
                    else:
                        record['rank'] = None
                        record['total_signers'] = None
                        logger.info("API返回数据中未包含排名信息")
                except Exception as e:
                    logger.warning(f"获取签到排名失败: {str(e)}")
                    record['rank'] = None
                    record['total_signers'] = None
                
                self.save_data('last_attendance_record', record)
                try:
                    gain = record.get('gain', 0)
                    created_at = record.get('created_at', '')
                    rank_info = f"，排名第{record.get('rank', '?')}名" if record.get('rank') else ""
                    total_info = f"，共{record.get('total_signers', '?')}人" if record.get('total_signers') else ""
                    logger.info(f"获取签到记录: 获得{gain}个鸡腿，时间{created_at}{rank_info}{total_info}")
                except Exception as e:
                    logger.warning(f"记录签到记录信息失败: {str(e)}")
            return record
        except Exception as e:
            logger.warning(f"获取签到记录失败: {str(e)}")
            return {}

    def _save_sign_history(self, sign_data):
        """
        保存签到历史记录
        """
        try:
            logger.info(f"开始保存签到历史记录，输入数据: {sign_data}")
            logger.info(f"输入数据类型: {type(sign_data)}")
            
            # 读取现有历史
            history = self.get_data('sign_history') or []
            logger.info(f"读取到现有历史记录数量: {len(history)}")
            
            # 确保日期格式正确
            if "date" not in sign_data:
                sign_data["date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"添加日期字段: {sign_data['date']}")
                
            history.append(sign_data)
            logger.info(f"添加新记录后历史记录数量: {len(history)}")
            
            # 清理旧记录
            try:
                logger.info(f"开始清理旧记录，_history_days: {self._history_days} (类型: {type(self._history_days)})")
                retention_days = int(self._history_days) if self._history_days is not None else 30
                logger.info(f"计算得到保留天数: {retention_days}")
            except (ValueError, TypeError) as e:
                retention_days = 30
                logger.warning(f"history_days 类型转换失败: {str(e)}，使用默认值 30")
            
            now = datetime.now()
            valid_history = []
            
            logger.info(f"开始遍历 {len(history)} 条历史记录进行清理...")
            for i, record in enumerate(history):
                try:
                    logger.info(f"处理第 {i+1} 条记录: {record}")
                    # 尝试将记录日期转换为datetime对象
                    record_date = datetime.strptime(record["date"], '%Y-%m-%d %H:%M:%S')
                    # 检查是否在保留期内
                    days_diff = (now - record_date).days
                    logger.info(f"记录日期: {record_date}, 距今天数: {days_diff}, 保留天数: {retention_days}")
                    if days_diff < retention_days:
                        valid_history.append(record)
                        logger.info(f"保留此记录")
                    else:
                        logger.info(f"删除过期记录")
                except (ValueError, KeyError) as e:
                    # 如果记录日期格式不正确，尝试修复
                    logger.warning(f"历史记录日期格式无效: {record.get('date', '无日期')}, 错误: {str(e)}")
                    # 添加新的日期并保留记录
                    record["date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    valid_history.append(record)
                    logger.info(f"修复日期后保留此记录")
            
            logger.info(f"清理完成，有效记录数量: {len(valid_history)}")
            
            # 保存历史
            self.save_data(key="sign_history", value=valid_history)
            logger.info(f"保存签到历史记录，当前共有 {len(valid_history)} 条记录")
            
        except Exception as e:
            logger.error(f"保存签到历史记录失败: {str(e)}", exc_info=True)
            logger.error(f"错误类型: {type(e)}")
            logger.error(f"输入数据: {sign_data}")
            logger.error(f"当前 _history_days: {self._history_days} (类型: {type(self._history_days)})")

    def clear_sign_history(self):
        """
        清除所有签到历史记录
        """
        try:
            # 清空签到历史
            self.save_data(key="sign_history", value=[])
            # 清空最后签到时间
            self.save_data(key="last_sign_date", value="")
            # 清空用户信息
            self.save_data(key="last_user_info", value="")
            # 清空签到记录
            self.save_data(key="last_attendance_record", value="")
            logger.info("已清空所有签到相关数据")
        except Exception as e:
            logger.error(f"清除签到历史记录失败: {str(e)}", exc_info=True)

    def _send_sign_notification(self, sign_dict, result, user_info: dict = None, attendance_record: dict = None):
        """
        发送签到通知
        """
        logger.info(f"开始发送签到通知，参数: sign_dict={sign_dict}, result={result}")
        logger.info(f"user_info 类型: {type(user_info)}, attendance_record 类型: {type(attendance_record)}")
        
        if not self._notify:
            logger.info("通知未启用，跳过")
            return
            
        status = sign_dict.get("status", "未知")
        sign_time = sign_dict.get("date", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        logger.info(f"通知状态: {status}, 时间: {sign_time}")
        
        # 构建通知文本
        if "签到成功" in status:
            title = "【✅ NodeSeek论坛签到成功】"
            
            # 获取奖励信息和排名信息
            gain_info = ""
            rank_info = ""
            try:
                logger.info(f"开始构建奖励信息，result: {result}")
                if result.get("gain"):
                    gain_info = f"🎁 获得: {result.get('gain')}个鸡腿"
                elif attendance_record and attendance_record.get("gain"):
                    gain_info = f"🎁 今日获得: {attendance_record.get('gain')}个鸡腿"
                
                # 添加排名信息
                if attendance_record:
                    if attendance_record.get("rank"):
                        rank_info = f"🏆 排名: 第{attendance_record.get('rank')}名"
                        if attendance_record.get("total_signers"):
                            rank_info += f" (共{attendance_record.get('total_signers')}人)"
                    elif attendance_record.get("total_signers"):
                        rank_info = f"📊 今日共{attendance_record.get('total_signers')}人签到"
                
                # 组合奖励和排名信息
                if rank_info:
                    gain_info = f"{gain_info}\n{rank_info}\n"
                else:
                    gain_info = f"{gain_info}\n"
                    
                logger.info(f"最终 gain_info: '{gain_info}' (类型: {type(gain_info)})")
            except Exception as e:
                logger.warning(f"获取奖励信息失败: {str(e)}")
                gain_info = ""
            
            # 构建用户信息文本
            user_info_text = ""
            if user_info:
                try:
                    member_name = user_info.get('member_name', '未知')
                    rank = user_info.get('rank', '未知')
                    coin = user_info.get('coin', '未知')
                    user_info_text = f"👤 用户：{member_name}  等级：{rank}  鸡腿：{coin}\n"
                    logger.info(f"构建用户信息文本: {user_info_text}")
                except Exception as e:
                    logger.warning(f"构建用户信息文本失败: {str(e)}")
                    user_info_text = ""
            
            logger.info(f"开始构建通知文本，gain_info: '{gain_info}'")
            # 构建完整的通知文本
            text_parts = [
                f"📢 执行结果",
                f"━━━━━━━━━━",
                f"🕐 时间：{sign_time}",
                f"✨ 状态：{status}",
                user_info_text.rstrip('\n') if user_info_text else "",
                gain_info.rstrip('\n') if gain_info else "",
                f"━━━━━━━━━━"
            ]
            
            # 过滤空字符串并用换行符连接
            text = "\n".join([part for part in text_parts if part])
            logger.info(f"通知文本构建完成，长度: {len(text)}")
            
        elif "已签到" in status:
            title = "【ℹ️ NodeSeek论坛今日已签到】"
            
            # 获取奖励信息和排名信息
            gain_info = ""
            rank_info = ""
            try:
                logger.info(f"开始构建已签到状态的奖励信息，attendance_record: {attendance_record}")
                today_gain = None
                if attendance_record and attendance_record.get("gain"):
                    today_gain = attendance_record.get('gain')
                elif result and result.get("gain"):
                    today_gain = result.get("gain")
                else:
                    try:
                        history = self.get_data('sign_history') or []
                        today_str = datetime.now().strftime('%Y-%m-%d')
                        latest = None
                        for rec in history:
                            if rec.get("date", "").startswith(today_str) and rec.get("gain"):
                                latest = rec
                                break
                        if latest:
                            today_gain = latest.get('gain')
                    except Exception:
                        pass
                if today_gain is not None:
                    gain_info = f"🎁 今日获得: {today_gain}个鸡腿"
                
                # 添加排名信息
                if attendance_record.get("rank"):
                    rank_info = f"🏆 排名: 第{attendance_record.get('rank')}名"
                    if attendance_record.get("total_signers"):
                        rank_info += f" (共{attendance_record.get('total_signers')}人)"
                elif attendance_record.get("total_signers"):
                    rank_info = f"📊 今日共{attendance_record.get('total_signers')}人签到"
                else:
                    try:
                        cached = self.get_data('last_attendance_record') or {}
                        if cached and cached.get('created_at'):
                            sh_tz = pytz.timezone('Asia/Shanghai')
                            rec_dt = datetime.fromisoformat(cached['created_at'].replace('Z', '+00:00')).astimezone(sh_tz)
                            if rec_dt.date() == datetime.now(sh_tz).date():
                                if cached.get('rank'):
                                    rank_info = f"🏆 排名: 第{cached.get('rank')}名"
                                    if cached.get('total_signers'):
                                        rank_info += f" (共{cached.get('total_signers')}人)"
                                elif cached.get('total_signers'):
                                    rank_info = f"📊 今日共{cached.get('total_signers')}人签到"
                    except Exception:
                        pass
                    
                    # 组合奖励和排名信息
                    if rank_info:
                        gain_info = f"{gain_info}\n{rank_info}\n"
                    else:
                        gain_info = f"{gain_info}\n"
                        
                    logger.info(f"从 attendance_record 获取奖励信息: {gain_info}")
                logger.info(f"最终 gain_info: '{gain_info}' (类型: {type(gain_info)})")
            except Exception as e:
                logger.warning(f"获取奖励信息失败: {str(e)}")
                gain_info = ""
            
            logger.info(f"开始构建已签到状态通知文本，gain_info: '{gain_info}'")
            # 构建用户信息文本
            user_info_text = ""
            if user_info:
                try:
                    member_name = user_info.get('member_name', '未知')
                    rank = user_info.get('rank', '未知')
                    coin = user_info.get('coin', '未知')
                    user_info_text = f"👤 用户：{member_name}  等级：{rank}  鸡腿：{coin}\n"
                    logger.info(f"构建用户信息文本: {user_info_text}")
                except Exception as e:
                    logger.warning(f"构建用户信息文本失败: {str(e)}")
                    user_info_text = ""
            
            # 构建完整的通知文本
            text_parts = [
                f"📢 执行结果",
                f"━━━━━━━━━━",
                f"🕐 时间：{sign_time}",
                f"✨ 状态：{status}",
                user_info_text.rstrip('\n') if user_info_text else "",
                gain_info.rstrip('\n') if gain_info else "",
                f"ℹ️ 说明：今日已完成签到，显示当前状态和奖励信息",
                f"💡 提示：即使已签到，插件仍会获取并显示您的奖励情况",
                f"━━━━━━━━━━"
            ]
            
            # 过滤空字符串并用换行符连接
            text = "\n".join([part for part in text_parts if part])
            logger.info(f"已签到状态通知文本构建完成，长度: {len(text)}")
            
        else:
            title = "【❌ NodeSeek论坛签到失败】"
            
            # 获取签到记录信息（如果有的话）
            record_info = ""
            try:
                logger.info(f"开始构建失败状态的记录信息，attendance_record: {attendance_record}")
                if attendance_record and attendance_record.get("created_at"):
                    record_date = datetime.fromisoformat(attendance_record["created_at"].replace('Z', '+00:00'))
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    if record_date.date() == today.date():
                        record_info = f"📊 签到记录: 今日已获得{attendance_record.get('gain', 0)}个鸡腿"
                        
                        # 添加排名信息
                        if attendance_record.get("rank"):
                            record_info += f"，排名第{attendance_record.get('rank')}名"
                            if attendance_record.get("total_signers"):
                                record_info += f" (共{attendance_record.get('total_signers')}人)"
                        elif attendance_record.get("total_signers"):
                            record_info += f"，今日共{attendance_record.get('total_signers')}人签到"
                        
                        record_info += "\n"
                        logger.info(f"构建记录信息: {record_info}")
                logger.info(f"最终 record_info: '{record_info}' (类型: {type(record_info)})")
            except Exception as e:
                logger.warning(f"获取签到记录信息失败: {str(e)}")
                record_info = ""
            
            logger.info(f"开始构建失败状态通知文本，record_info: '{record_info}'")
            # 构建完整的通知文本
            text_parts = [
                f"📢 执行结果",
                f"━━━━━━━━━━",
                f"🕐 时间：{sign_time}",
                f"❌ 状态：{status}",
                record_info.rstrip('\n') if record_info else "",
                f"━━━━━━━━━━",
                f"💡 可能的解决方法",
                f"• 检查Cookie是否过期",
                f"• 确认站点是否可访问",
                f"• 检查代理设置是否正确",
                f"• 尝试手动登录网站",
                f"━━━━━━━━━━"
            ]
            
            # 过滤空字符串并用换行符连接
            text = "\n".join([part for part in text_parts if part])
            logger.info(f"失败状态通知文本构建完成，长度: {len(text)}")
            
        # 发送通知
        logger.info(f"准备发送通知，标题: {title}")
        logger.info(f"通知内容长度: {len(text)}")
        try:
            self.post_message(
                mtype=NotificationType.SiteMessage,
                title=title,
                text=text
            )
            logger.info("通知发送成功")
        except Exception as e:
            logger.error(f"通知发送失败: {str(e)}")
            logger.error(f"错误类型: {type(e)}")
    
    def _save_last_sign_date(self):
        """
        保存最后一次成功签到的日期和时间
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_data('last_sign_date', now)
        logger.info(f"记录签到成功时间: {now}")
        
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
            return True
            
        # 获取最后一次签到的日期和时间
        last_sign_date = self.get_data('last_sign_date')
        if last_sign_date:
            try:
                last_sign_datetime = datetime.strptime(last_sign_date, '%Y-%m-%d %H:%M:%S')
                last_sign_day = last_sign_datetime.strftime('%Y-%m-%d')
                
                # 如果最后一次签到是今天且是成功的
                if last_sign_day == today:
                    return True
            except Exception as e:
                logger.error(f"解析最后签到日期时出错: {str(e)}")
        
        return False

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            logger.info(f"注册定时服务: {self._cron}")
            return [{
                "id": "nodeseeksign",
                "name": "NodeSeek论坛签到",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self.sign,
                "kwargs": {}
            }]
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        # 状态提示移除CloudFlare相关文案
        curl_cffi_status = "✅ 已安装" if HAS_CURL_CFFI else "❌ 未安装"
        cloudscraper_status = "✅ 已启用" if HAS_CLOUDSCRAPER else "❌ 未启用"
        
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
                                            'model': 'random_choice',
                                            'label': '随机奖励',
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
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'use_proxy',
                                            'label': '使用代理',
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
                                            'model': 'verify_ssl',
                                            'label': '验证SSL证书',
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
                                            'model': 'clear_history',
                                            'label': '清除历史记录',
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
                                            'model': 'member_id',
                                            'label': '成员ID（可选）',
                                            'placeholder': '用于获取用户信息'
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
                                            'model': 'min_delay',
                                            'label': '最小随机延迟(秒)',
                                            'type': 'number',
                                            'placeholder': '5'
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
                                            'model': 'max_delay',
                                            'label': '最大随机延迟(秒)',
                                            'type': 'number',
                                            'placeholder': '12'
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
                                    'md': 4
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
                                    'md': 4
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
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'max_retries',
                                            'label': '失败重试次数',
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
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'stats_days',
                                            'label': '收益统计天数',
                                            'type': 'number',
                                            'placeholder': '30'
                                        }
                                    }
                                ]
                            },

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
                                            'text': f'【使用教程】\n1. 登录NodeSeek论坛网站，按F12打开开发者工具\n2. 在"网络"或"应用"选项卡中复制Cookie\n3. 粘贴Cookie到上方输入框\n4. 设置签到时间，建议早上8点(0 8 * * *)\n5. 启用插件并保存\n\n【功能说明】\n• 随机奖励：开启则使用随机奖励，关闭则使用固定奖励\n• 使用代理：开启则使用系统配置的代理服务器访问NodeSeek\n• 验证SSL证书：关闭可能解决SSL连接问题，但会降低安全性\n• 失败重试：设置签到失败后的最大重试次数，将在5-15分钟后随机重试\n• 随机延迟：请求前随机等待，降低被风控概率\n• 用户信息：配置成员ID后，通知中展示用户名/等级/鸡腿\n• 立即运行一次：手动触发一次签到\n• 清除历史记录：勾选后保存配置，插件将清空所有签到历史、用户信息等数据，使用后会自动关闭\n\n【环境状态】\n• curl_cffi: {curl_cffi_status}；cloudscraper: {cloudscraper_status}'
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
            "random_choice": True,
            "history_days": 30,
            "use_proxy": True,
            "max_retries": 3,
            "verify_ssl": False,
            "min_delay": 5,
            "max_delay": 12,
            "member_id": "",
            "clear_history": False,
            "stats_days": 30
        }

    def get_page(self) -> List[dict]:
        """
        构建插件详情页面，展示签到历史
        """
        # 读取缓存的用户信息
        user_info = self.get_data('last_user_info') or {}
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
            
            # 判断状态颜色：所有成功状态都是绿色，失败状态是红色
            success_statuses = ["签到成功", "已签到", "签到成功（时间验证）", "已签到（从记录确认）"]
            status_color = "success" if status_text in success_statuses else "error"
            
            # 获取奖励信息
            reward_info = "-"
            try:
                # 检查是否为成功状态（包括新增的时间验证状态）
                if any(success_status in status_text for success_status in success_statuses):
                    # 尝试从历史记录中获取奖励信息
                    if "gain" in history:
                        reward_info = f"{history.get('gain', 0)}个鸡腿"
                        # 如果有排名信息，也显示
                        if "rank" in history and "total_signers" in history:
                            reward_info += f" (第{history.get('rank')}名，共{history.get('total_signers')}人)"
                    else:
                        # 如果没有直接的奖励信息，尝试从签到记录中获取
                        attendance_record = self.get_data('last_attendance_record') or {}
                        if attendance_record and attendance_record.get('gain'):
                            reward_info = f"{attendance_record.get('gain')}个鸡腿"
                            # 如果有排名信息，也显示
                            if attendance_record.get('rank') and attendance_record.get('total_signers'):
                                reward_info += f" (第{attendance_record.get('rank')}名，共{attendance_record.get('total_signers')}人)"
            except Exception as e:
                logger.warning(f"获取奖励信息失败: {str(e)}")
                reward_info = "-"
            
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
                    # 奖励列
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'VChip',
                                'props': {
                                    'color': 'amber-darken-2' if reward_info != "-" else 'grey',
                                    'size': 'small',
                                    'variant': 'outlined'
                                },
                                'text': reward_info
                            }
                        ]
                    },
                    # 消息列
                    {
                        'component': 'td',
                        'text': history.get('message', '-')
                    }
                ]
            })
        
        # 用户信息卡片（可选）
        user_info_card = []
        
        # 初始化用户信息相关变量，避免未定义错误
        member_id = ""
        avatar_url = None
        user_name = "-"
        rank = "-"
        coin = "-"
        npost = "-"
        ncomment = "-"
        sign_rank = None
        total_signers = None
        
        if user_info:
            member_id = str(user_info.get('member_id') or getattr(self, '_member_id', '') or '').strip()
            avatar_url = f"https://www.nodeseek.com/avatar/{member_id}.png" if member_id else None
            user_name = user_info.get('member_name', '-')
            rank = str(user_info.get('rank', '-'))
            coin = str(user_info.get('coin', '-'))
            npost = str(user_info.get('nPost', '-'))
            ncomment = str(user_info.get('nComment', '-'))
            
            # 获取签到排名信息
            attendance_record = self.get_data('last_attendance_record') or {}
            sign_rank = attendance_record.get('rank')
            total_signers = attendance_record.get('total_signers')
            
            user_info_card = [
                {
                    'component': 'VCard',
                    'props': {'variant': 'outlined', 'class': 'mb-4'},
                    'content': [
                        {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '👤 NodeSeek 用户信息'},
                        {
                            'component': 'VCardText',
                            'content': [
                                {
                                    'component': 'VRow',
                                    'props': {'align': 'center'},
                                    'content': [
                                        {
                                            'component': 'VCol',
                                            'props': {'cols': 12, 'md': 2},
                                            'content': [
                                                (
                                                    {
                                                        'component': 'VAvatar',
                                                        'props': {'size': 72, 'class': 'mx-auto'},
                                                        'content': [
                                                            {
                                                                'component': 'VImg',
                                                                'props': {'src': avatar_url} if avatar_url else {}
                                                            }
                                                        ]
                                                    } if avatar_url else {
                                                        'component': 'VAvatar',
                                                        'props': {'size': 72, 'color': 'grey-lighten-2', 'class': 'mx-auto'},
                                                        'text': user_name[:1]
                                                    }
                                                )
                                            ]
                                        },
                                        {
                                            'component': 'VCol',
                                            'props': {'cols': 12, 'md': 10},
                                            'content': [
                                                {
                                                    'component': 'VRow',
                                                    'props': {'class': 'mb-2'},
                                                    'content': [
                                                        {'component': 'span', 'props': {'class': 'text-subtitle-1 mr-4'}, 'text': user_name},
                                                        {'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': 'primary', 'class': 'mr-2'}, 'text': f'等级 {rank}'},
                                                        {'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': 'amber-darken-2', 'class': 'mr-2'}, 'text': f'鸡腿 {coin}'},
                                                        {'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'class': 'mr-2'}, 'text': f'主题 {npost}'},
                                                        {'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined'}, 'text': f'评论 {ncomment}'}
                                                    ] + ([
                                                        # 添加签到排名信息
                                                        {'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': 'success', 'class': 'mr-2'}, 'text': f'签到排名 {sign_rank}'},
                                                        {'component': 'VChip', 'props': {'size': 'small', 'variant': 'outlined', 'color': 'info', 'class': 'mr-2'}, 'text': f'总人数 {total_signers}'}
                                                    ] if sign_rank and total_signers else [])
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

        stats = self.get_data('last_signin_stats') or {}

        stats_card = []
        if stats:
            period = stats.get('period') or f"近{self._stats_days}天"
            days_count = stats.get('days_count', 0)
            total_amount = stats.get('total_amount', 0)
            average = stats.get('average', 0)
            stats_card = [
                {
                    'component': 'VCard',
                    'props': {'variant': 'outlined', 'class': 'mb-4'},
                    'content': [
                        {'component': 'VCardTitle', 'props': {'class': 'text-h6'}, 'text': '📈 NodeSeek收益统计'},
                        {
                            'component': 'VCardText',
                            'content': [
                                {'component': 'div', 'props': {'class': 'mb-2'}, 'text': f'{period} 已签到 {days_count} 天'},
                                {
                                    'component': 'VRow',
                                    'content': [
                                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VChip', 'props': {'variant': 'outlined', 'color': 'amber-darken-2'}, 'text': f'总鸡腿 {total_amount}'}]},
                                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VChip', 'props': {'variant': 'outlined', 'color': 'primary'}, 'text': f'平均/日 {average}'}]},
                                        {'component': 'VCol', 'props': {'cols': 12, 'md': 4}, 'content': [{'component': 'VChip', 'props': {'variant': 'outlined'}, 'text': f'统计天数 {days_count}'}]},
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]

        return user_info_card + stats_card + [
            # 标题
            {
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'text-h6'},
                        'text': '📊 NodeSeek论坛签到历史'
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
                                                    {'component': 'th', 'text': '奖励'},
                                                    {'component': 'th', 'text': '消息'}
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
        """
        退出插件，停止定时任务
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"退出插件失败: {str(e)}")

    def get_command(self) -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return [] 

    def _get_signin_stats(self, days: int = 30) -> dict:
        if not self._cookie:
            return {}
        if days <= 0:
            days = 1
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'origin': 'https://www.nodeseek.com',
            'referer': 'https://www.nodeseek.com/board',
            'Cookie': self._cookie
        }
        tz = pytz.timezone('Asia/Shanghai')
        now_shanghai = datetime.now(tz)
        query_start_time = now_shanghai - timedelta(days=days)
        all_records = []
        page = 1
        proxies = self._get_proxies()
        try:
            while page <= 20:
                url = f'https://www.nodeseek.com/api/account/credit/page-{page}'
                resp = self._smart_get(url=url, headers=headers, proxies=proxies, timeout=30)
                data = {}
                try:
                    data = resp.json()
                except Exception:
                    break
                if not data.get('success') or not data.get('data'):
                    break
                records = data.get('data', [])
                if not records:
                    break
                try:
                    last_record_time = datetime.fromisoformat(records[-1][3].replace('Z', '+00:00')).astimezone(tz)
                except Exception:
                    break
                if last_record_time < query_start_time:
                    for record in records:
                        try:
                            record_time = datetime.fromisoformat(record[3].replace('Z', '+00:00')).astimezone(tz)
                        except Exception:
                            continue
                        if record_time >= query_start_time:
                            all_records.append(record)
                    break
                else:
                    all_records.extend(records)
                page += 1
        except Exception:
            pass
        signin_records = []
        for record in all_records:
            try:
                amount, balance, description, timestamp = record
                record_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).astimezone(tz)
            except Exception:
                continue
            if record_time >= query_start_time and ('签到收益' in description and '鸡腿' in description):
                signin_records.append({'amount': amount, 'date': record_time.strftime('%Y-%m-%d'), 'description': description})
        period_desc = f'近{days}天' if days != 1 else '今天'
        if not signin_records:
            try:
                history = self.get_data('sign_history') or []
                success_statuses = ["签到成功", "已签到", "签到成功（时间验证）", "已签到（从记录确认）"]
                fallback_records = []
                for rec in history:
                    try:
                        rec_dt = datetime.strptime(rec.get('date', ''), '%Y-%m-%d %H:%M:%S').astimezone(tz)
                    except Exception:
                        continue
                    if rec_dt >= query_start_time and rec.get('status') in success_statuses and rec.get('gain'):
                        fallback_records.append({'amount': rec.get('gain', 0), 'date': rec_dt.strftime('%Y-%m-%d'), 'description': '本地历史-签到收益'})
                if not fallback_records:
                    return {'total_amount': 0, 'average': 0, 'days_count': 0, 'records': [], 'period': period_desc}
                total_amount = sum(r['amount'] for r in fallback_records)
                days_count = len(fallback_records)
                average = round(total_amount / days_count, 2) if days_count > 0 else 0
                return {'total_amount': total_amount, 'average': average, 'days_count': days_count, 'records': fallback_records, 'period': period_desc}
            except Exception:
                return {'total_amount': 0, 'average': 0, 'days_count': 0, 'records': [], 'period': period_desc}
        total_amount = sum(r['amount'] for r in signin_records)
        days_count = len(signin_records)
        average = round(total_amount / days_count, 2) if days_count > 0 else 0
        return {'total_amount': total_amount, 'average': average, 'days_count': days_count, 'records': signin_records, 'period': period_desc}
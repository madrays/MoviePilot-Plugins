import json
import os
import re
import time
import random
import calendar
import uuid
import math
import hashlib
import hmac
import base64
import threading
from secrets import compare_digest
from datetime import datetime, timedelta, date
from urllib.parse import urlencode, urlparse, urlunparse

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from app import schemas
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger
from app.schemas import NotificationType
from fastapi import Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field
import requests


# 论坛正式 API 地址固定内置；仅部署负责人可通过环境变量覆盖。
MOVIEPILOT_API_BASE = "https://pting.club"
MOVIEPILOT_API_BASE_OVERRIDE = os.getenv("FENGCHAO_API_BASE", "").strip()
FORUM_NOTIFICATION_CARD_IMAGE = "https://cdn.pting.club/site-logo/site-logo-7d1d31b822cddca4.jpg"


def _resolve_api_base():
    """允许 HTTPS 或显式配置的 HTTP 端点（仅限临时直连测试）；仍拒绝带账号/路径等可疑地址。"""
    candidate = (MOVIEPILOT_API_BASE_OVERRIDE or MOVIEPILOT_API_BASE).rstrip("/")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password or parsed.fragment or parsed.query or parsed.path not in {"", "/"}:
        logger.warning("蜂巢 API 地址不是受信任端点，回退到内置地址")
        return MOVIEPILOT_API_BASE.rstrip("/")
    if parsed.scheme != "https":
        logger.warning("蜂巢 API 使用明文 HTTP（IP 直连测试）；正式环境应使用 HTTPS")
    return candidate


def _safe_config_int(value, default, minimum=0, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    if parsed < minimum:
        return minimum
    if maximum is not None and parsed > maximum:
        return maximum
    return parsed


def _safe_config_bool(value, default):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


def _safe_cron(value, default):
    candidate = str(value or "").strip()
    try:
        CronTrigger.from_crontab(candidate)
        return candidate
    except (TypeError, ValueError):
        logger.warning("无效的 cron 配置 %r，回退到 %s", value, default)
        return default


def _cron_trigger_with_jitter(expression, jitter_seconds):
    """Build the jitter into CronTrigger; add_job ignores trigger kwargs for trigger objects."""
    minute, hour, day, month, day_of_week = str(expression).split()
    return CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
        timezone=settings.TZ,
        jitter=jitter_seconds,
    )


def _safe_nonnegative_int(value):
    """把 MP 统计模型中的异常数值（NaN/Infinity/负数）安全归一化。"""
    try:
        parsed = float(value or 0)
        if not math.isfinite(parsed):
            return 0
        return max(0, int(parsed))
    except (TypeError, ValueError, OverflowError):
        return 0


def _safe_positive_int(value):
    """Strict identifier parsing for webhook account binding."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value if value > 0 else 0
    if isinstance(value, str) and re.fullmatch(r"[1-9]\d*", value.strip()):
        try:
            return int(value.strip())
        except (TypeError, ValueError, OverflowError):
            return 0
    return 0


def _safe_uuid4(value):
    try:
        parsed = uuid.UUID(str(value or "").strip())
        return str(parsed) if parsed.version == 4 else ""
    except (AttributeError, TypeError, ValueError):
        return ""


def _safe_bonus(value):
    """将 MP 魔力值限制为论坛 Decimal(38,4) 可接受的非负有限数。"""
    try:
        text = str(value or "0").strip()
        if not re.fullmatch(r"\d{1,34}(\.\d{1,4})?", text):
            return "0"
        return text
    except Exception:
        return "0"


class FengchaoWebhookPayload(BaseModel):
    """蜂巢论坛发送的站外通知。"""

    event: str = Field(..., min_length=1, max_length=64)
    notification: Optional[Dict[str, Any]] = None
    message: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None
    recipient: Dict[str, Any] = Field(default_factory=dict)


class FengchaoSignin(_PluginBase):
    # 插件名称
    plugin_name = "蜂巢签到"
    # 插件描述
    plugin_desc = "蜂巢论坛签到。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/fengchao.png"
    # 插件版本
    plugin_version = "3.1.2"
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
    _enabled = True
    # 任务执行间隔
    _cron = None
    _api_key = ""
    _instance_id = ""
    _onlyonce = False
    _update_info_now = False
    _force_refresh = False
    _notify = True
    _history_days = None
    # 签到重试相关
    _retry_count = 1  # 最大重试次数；默认至少重试一次
    _current_retry = 0  # 当前重试次数
    _retry_interval = 2  # 重试间隔(小时)
    # MoviePilot数据推送相关
    _mp_push_enabled = True  # 是否启用数据推送
    _mp_push_interval = 1  # 推送间隔(天)
    _last_push_time = None  # 上次推送时间
    # 代理相关
    _use_proxy = False  # Bearer Key 默认直连；仅在用户明确开启时使用代理
    # 定时 PT 人生快照同步相关
    _timed_update_enabled = True
    _timed_update_cron = "0 3 * * *"
    _timed_update_retry_count = 0
    _timed_update_retry_interval = 0
    _timed_update_current_retry = 0
    # 论坛通知 webhook 相关
    _webhook_enabled = False
    _webhook_system_notification = True
    _webhook_reply_notification = True
    _webhook_private_message = True
    _webhook_public_url = ""
    _webhook_mp_api_key = ""
    _webhook_test_now = False
    _webhook_lock = threading.Lock()
    _webhook_rate_window_started = 0.0
    _webhook_rate_count = 0

    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None

    # 存储当前生效的配置，用于检测变更
    _active_enabled = None
    _active_cron = None
    _active_timed_update_enabled = None
    _active_timed_update_cron = None

    def init_plugin(self, config: dict = None):
        """
        插件初始化
        """
        # 接收参数
        if config:
            self._enabled = _safe_config_bool(config.get("enabled", True), True)
            self._notify = _safe_config_bool(config.get("notify", True), True)
            self._cron = _safe_cron(config.get("cron", "30 8 * * *"), "30 8 * * *")
            self._onlyonce = _safe_config_bool(config.get("onlyonce", False), False)
            self._update_info_now = _safe_config_bool(config.get("update_info_now", False), False)
            self._force_refresh = _safe_config_bool(config.get("force_refresh", False), False)
            self._api_key = str(config.get("api_key") or "").strip()
            previous_key_prefix = str(self.get_data("api_key_prefix") or "")
            previous_key_fingerprint = str(self.get_data("api_key_fingerprint") or "")
            current_key_fingerprint = hashlib.sha256(self._api_key.encode("utf-8")).hexdigest() if self._api_key else ""
            configured_instance_id = _safe_uuid4(config.get("instance_id"))
            persisted_instance_id = _safe_uuid4(self.get_data("instance_id"))
            key_changed = bool(
                current_key_fingerprint and (
                    (previous_key_fingerprint and previous_key_fingerprint != current_key_fingerprint)
                    or (not previous_key_fingerprint and previous_key_prefix and previous_key_prefix != self._api_key[:20])
                )
            )
            if key_changed:
                # The same MP host may be pointed at another forum account;
                # never reuse an instance UUID that is already bound there.
                self._instance_id = str(uuid.uuid4())
                # The forum key rotation also unbinds the old instance. Drop
                # owner/status freshness markers so the next scheduled run
                # performs a new /me bind and cannot reuse the old account's
                # cached avatar, badges, qualification or snapshot result.
                for cache_key in ("last_status", "last_push_time", "last_push_result", "last_sync_request"):
                    self.save_data(cache_key, None)
            else:
                self._instance_id = configured_instance_id or persisted_instance_id or str(uuid.uuid4())
            self._history_days = _safe_config_int(config.get("history_days", 30), 30, 1, 3650)
            self._retry_count = _safe_config_int(config.get("retry_count", 1), 1, 0, 10)
            self._retry_interval = _safe_config_int(config.get("retry_interval", 2), 2, 1, 24)
            self._mp_push_enabled = _safe_config_bool(config.get("mp_push_enabled", True), True)
            self._mp_push_interval = _safe_config_int(config.get("mp_push_interval", 1), 1, 1, 7)
            self._use_proxy = _safe_config_bool(config.get("use_proxy", False), False)
            # PT 人生快照只通过 MP API Key 同步。
            self._timed_update_enabled = _safe_config_bool(config.get("timed_update_enabled", True), True)
            self._timed_update_cron = _safe_cron(config.get("timed_update_cron", "0 3 * * *"), "0 3 * * *")
            self._timed_update_retry_count = _safe_config_int(config.get("timed_update_retry_count", 1), 1, 0, 10)
            self._timed_update_retry_interval = _safe_config_int(config.get("timed_update_retry_interval", 2), 2, 1, 24)
            self._webhook_enabled = _safe_config_bool(config.get("webhook_enabled", False), False)
            self._webhook_system_notification = _safe_config_bool(config.get("webhook_system_notification", True), True)
            self._webhook_reply_notification = _safe_config_bool(config.get("webhook_reply_notification", True), True)
            self._webhook_private_message = _safe_config_bool(config.get("webhook_private_message", True), True)
            self._webhook_public_url = str(config.get("webhook_public_url") or "").strip()
            self._webhook_mp_api_key = str(config.get("webhook_mp_api_key") or "").strip()
            self._webhook_test_now = _safe_config_bool(config.get("webhook_test_now", False), False)
            self._last_push_time = self.get_data('last_push_time')

        if not self._instance_id:
            self._instance_id = str(uuid.uuid4())
        # Keep the local instance UUID stable across MoviePilot restarts even
        # when the host has not persisted the optional advanced config field.
        self.save_data("instance_id", self._instance_id)
        if self._api_key:
            self.save_data("api_key_fingerprint", hashlib.sha256(self._api_key.encode("utf-8")).hexdigest())
            self.save_data("api_key_prefix", None)

        # 重置即时任务的重试计数
        self._current_retry = 0
        self._timed_update_current_retry = 0

        if not self._scheduler or not self._scheduler.running:
            self.stop_service()
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            logger.info("调度器未运行，已创建新的实例。")
            # 强制首次加载时任务被更新
            self._active_enabled = not self._enabled

        signin_job_id = "fengchao_signin_cron"
        signin_config_changed = (self._enabled != self._active_enabled or self._cron != self._active_cron)
        if signin_config_changed:
            logger.info("检测到签到任务配置变更，正在更新...")
            if self._scheduler.get_job(signin_job_id):
                self._scheduler.remove_job(signin_job_id)
                logger.info("已移除旧的签到周期任务。")
            if self._enabled and self._cron:
                self._scheduler.add_job(
                    func=self.__signin,
                    trigger=_cron_trigger_with_jitter(self._cron, 1800),
                    name="蜂巢签到",
                    id=signin_job_id,
                    # Tens of thousands of installations commonly keep the
                    # default cron. Spread forum writes over 30 minutes.
                )
                logger.info(f"已添加新的签到周期任务，周期：{self._cron}")

        info_update_job_id = "fengchao_info_update_cron"
        info_update_config_changed = (
                self._enabled != self._active_enabled or
                self._timed_update_enabled != self._active_timed_update_enabled or
                self._timed_update_cron != self._active_timed_update_cron
        )
        if info_update_config_changed:
            logger.info("检测到 PT 人生同步任务配置变更，正在更新...")
            if self._scheduler.get_job(info_update_job_id):
                self._scheduler.remove_job(info_update_job_id)
                logger.info("已移除旧的 PT 人生同步周期任务。")
            if self._enabled and self._timed_update_enabled:
                cron_to_use = self._timed_update_cron if self._timed_update_cron else "0 3 * * *"
                self._scheduler.add_job(
                    func=self.__sync_pt_life,
                    kwargs={'is_scheduled_run': True},
                    trigger=_cron_trigger_with_jitter(cron_to_use, 7200),
                    name="蜂巢 PT 人生快照定时同步",
                    id=info_update_job_id,
                    # All MoviePilot instances commonly share the same
                    # default cron. Spread the heavier daily snapshot uploads
                    # across two hours so the forum never sees a 03:00 spike.
                )
                logger.info(f"已添加新的 PT 人生同步周期任务，周期：{cron_to_use}")

        if self._update_info_now:
            logger.info("蜂巢插件：立即同步 PT 人生")
            self._scheduler.add_job(func=self.__sync_pt_life, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="蜂巢 PT 人生快照同步")
            self._update_info_now = False
            self.update_config(self.get_config_dict())

        if self._force_refresh:
            logger.info("蜂巢插件：强制刷新论坛信息")
            self._scheduler.add_job(func=self._force_refresh_info, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="蜂巢论坛信息强制刷新（一次性）")
            self._force_refresh = False
            self.update_config(self.get_config_dict())

        if self._onlyonce:
            logger.info(f"蜂巢插件启动，立即运行一次（签到和信息更新）")
            self._scheduler.add_job(func=self.__signin, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="蜂巢签到与信息更新（单次）")
            self._onlyonce = False
            self.update_config(self.get_config_dict())

        previously_registered = bool(self.get_data("webhook_registered"))
        previous_webhook_fingerprint = str(self.get_data("webhook_registration_fingerprint") or "")
        verified_webhook_fingerprint = str(self.get_data("webhook_verified_fingerprint") or "")
        try:
            current_webhook_fingerprint = self._webhook_registration_fingerprint()
        except Exception:
            current_webhook_fingerprint = ""
        webhook_config_changed = self._webhook_enabled and (
            not previously_registered or current_webhook_fingerprint != previous_webhook_fingerprint
        )
        webhook_verification_pending = self._webhook_enabled and (
            not current_webhook_fingerprint or current_webhook_fingerprint != verified_webhook_fingerprint
        )
        webhook_disable_pending = not self._webhook_enabled and previously_registered
        if webhook_config_changed or webhook_verification_pending or webhook_disable_pending or self._webhook_test_now:
            self._scheduler.add_job(
                func=self._sync_notification_webhook,
                kwargs={"send_test": self._webhook_enabled and (self._webhook_test_now or webhook_verification_pending)},
                trigger="date",
                run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=5),
                name="蜂巢论坛通知配置同步",
                id="fengchao_notification_webhook_sync",
                replace_existing=True,
            )
            if self._webhook_test_now:
                self._webhook_test_now = False
                self.update_config(self.get_config_dict())

        if self._scheduler and not self._scheduler.running and self._scheduler.get_jobs():
            self._scheduler.print_jobs()
            self._scheduler.start()

        self._active_enabled = self._enabled
        self._active_cron = self._cron
        self._active_timed_update_enabled = self._timed_update_enabled
        self._active_timed_update_cron = self._timed_update_cron

    def get_config_dict(self):
        """获取当前配置字典，用于更新"""
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "cron": self._cron,
            "onlyonce": self._onlyonce,
            "update_info_now": False,
            "force_refresh": False,
            "history_days": self._history_days,
            "retry_count": self._retry_count,
            "retry_interval": self._retry_interval,
            "mp_push_enabled": self._mp_push_enabled,
            "mp_push_interval": self._mp_push_interval,
            "api_key": self._api_key,
            "instance_id": self._instance_id,
            "use_proxy": self._use_proxy,
            "timed_update_enabled": self._timed_update_enabled,
            "timed_update_cron": self._timed_update_cron,
            "timed_update_retry_count": self._timed_update_retry_count,
            "timed_update_retry_interval": self._timed_update_retry_interval,
            "webhook_enabled": self._webhook_enabled,
            "webhook_system_notification": self._webhook_system_notification,
            "webhook_reply_notification": self._webhook_reply_notification,
            "webhook_private_message": self._webhook_private_message,
            "webhook_public_url": self._webhook_public_url,
            "webhook_mp_api_key": self._webhook_mp_api_key,
            "webhook_test_now": False,
        }

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

    def _schedule_retry(self, hours=None):
        """
        安排签到重试任务
        :param hours: 重试间隔小时数，如果不指定则使用配置的_retry_interval
        """
        if not self._scheduler:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)

        # 计算下次重试时间
        retry_interval = hours if hours is not None else self._retry_interval
        next_run_time = datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(hours=retry_interval)

        # 安排重试任务
        self._scheduler.add_job(
            func=self.__signin,
            kwargs={'is_retry': True},
            trigger='date',
            run_date=next_run_time,
            name=f"蜂巢签到重试 ({self._current_retry}/{self._retry_count})",
            id="fengchao_signin_retry",
            replace_existing=True,
        )

        logger.info(f"蜂巢签到失败，将在{retry_interval}小时后重试，当前重试次数: {self._current_retry}/{self._retry_count}")

        # 启动定时器（如果未启动）
        if not self._scheduler.running:
            self._scheduler.start()

    def _send_signin_failure_notification(self, reason: str, attempt: int):
        """
        发送签到失败的通知
        :param reason: 失败原因
        :param attempt: 当前尝试次数
        """
        if self._notify:
            retry_info = ""
            retry_scheduled = bool(self._scheduler and self._scheduler.get_job("fengchao_signin_retry"))
            if retry_scheduled:
                next_retry_hours = self._retry_interval
                retry_info = (
                    f"🔄 重试信息\n"
                    f"• 已安排 {next_retry_hours} 小时后的延迟重试\n"
                    f"• 重试进度: {attempt}/{self._retry_count}\n"
                    f"━━━━━━━━━━\n"
                )

            self._send_notification(
                title="【❌ 蜂巢签到失败】",
                text=(
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"❌ 状态：签到请求失败\n"
                    f"💬 原因：{reason}\n"
                    f"━━━━━━━━━━\n"
                    f"{retry_info}"
                )
            )

    def _schedule_info_update_retry(self, batch_id: str):
        """
        安排用户信息更新的重试任务
        """
        if not self._scheduler:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)

        retry_interval_hours = self._timed_update_retry_interval
        if retry_interval_hours <= 0:
            logger.warning("信息更新重试间隔配置为0或负数，不安排重试")
            return

        next_run_time = datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(hours=retry_interval_hours)

        self._scheduler.add_job(
            func=self.__sync_pt_life,
            kwargs={'is_scheduled_run': True, 'is_retry': True, 'retry_batch_id': batch_id},
            trigger='date',
            run_date=next_run_time,
            name=f"蜂巢信息更新重试 ({self._timed_update_current_retry}/{self._timed_update_retry_count})",
            id="fengchao_info_update_retry",
            replace_existing=True,
        )

        logger.info(
            f"蜂巢PT 人生同步失败，将在{retry_interval_hours}小时后重试，当前重试次数: {self._timed_update_current_retry}/{self._timed_update_retry_count}")

        if not self._scheduler.running:
            self._scheduler.start()

    def _send_info_update_failure_notification(self, reason: str):
        """
        发送PT 人生同步失败的通知
        :param reason: 失败原因
        """
        if self._notify:
            retry_info = ""
            retry_scheduled = bool(self._scheduler and self._scheduler.get_job("fengchao_info_update_retry"))
            if retry_scheduled:
                next_retry_hours = self._timed_update_retry_interval
                retry_info = (
                    f"🔄 重试信息\n"
                    f"• 已安排 {next_retry_hours} 小时后的延迟重试\n"
                    f"• 重试进度: {self._timed_update_current_retry}/{self._timed_update_retry_count}\n"
                    f"━━━━━━━━━━\n"
                )

            self._send_notification(
                title="【❌ 蜂巢信息定时更新失败】",
                text=(
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"❌ 状态：PT 人生同步失败\n"
                    f"💬 原因：{reason}\n"
                    f"━━━━━━━━━━\n"
                    f"{retry_info}"
                )
            )

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
                # Proxy URLs can contain credentials; never write them to the
                # MoviePilot log.
                logger.info("蜂巢 API 已使用 MoviePilot 系统代理")
                return settings.PROXY
            else:
                logger.warning("系统代理未配置")
                return None
        except Exception as e:
            logger.error(f"获取代理设置出错: {str(e)}")
            return None

    def __sync_pt_life(self, is_scheduled_run: bool = False, is_retry: bool = False, retry_batch_id: str = None):
        """手动/定时同步：只通过 MP 本地统计模型上传 PT 人生快照。"""
        if is_scheduled_run and not is_retry:
            self._timed_update_current_retry = 0
        if not self._api_key:
            reason = "未配置 MP 专用 API Key，请先在论坛“隐秘的角落”生成并粘贴"
            logger.warning(reason)
            if is_scheduled_run:
                self._send_info_update_failure_notification(reason)
            return False
        if not self._mp_push_enabled:
            logger.info("蜂巢 PT 人生同步已关闭，跳过定时快照上传")
            return False
        batch_id = retry_batch_id or f"{self._instance_id}-{datetime.now(tz=pytz.UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:12]}"
        try:
            # A failed daily write is rescheduled below instead of sleeping in
            # APScheduler's worker thread. This keeps one bounded request per
            # attempt and prevents retry storms during a forum outage.
            result = self.__push_stats_with_retries(retry_count=0, batch_id=batch_id)
            try:
                self._notify_status_transition(self._sync_if_requested(self.__api_request("GET", "/api/integrations/moviepilot/v1/status")))
            except Exception as status_error:
                logger.warning(f"读取蜂巢 PT 资格状态失败: {status_error}")
            self._timed_update_current_retry = 0
            if self._scheduler and self._scheduler.get_job("fengchao_info_update_retry"):
                self._scheduler.remove_job("fengchao_info_update_retry")
            self._send_notification(
                title="【✅ 蜂巢 PT 人生同步成功】",
                text=f"已上传 {result.get('siteCount', 0)} 个站点的最新快照。",
            )
            return result
        except Exception as exc:
            logger.error(f"蜂巢 PT 人生同步失败: {exc}")
            if is_scheduled_run and self._timed_update_current_retry < self._timed_update_retry_count:
                self._timed_update_current_retry += 1
                try:
                    self._schedule_info_update_retry(batch_id)
                except Exception as schedule_error:
                    self._timed_update_current_retry -= 1
                    logger.error(f"安排蜂巢 PT 人生延迟重试失败: {schedule_error}")
            self._send_info_update_failure_notification(str(exc))
            return False

    def __signin(self, retry_count=0, max_retries=3, is_retry=False):
        """
        蜂巢签到
        """
        if not is_retry:
            self._current_retry = 0
        return self.__api_signin()
    def __api_headers(self):
        if not self._api_key:
            raise RuntimeError("未配置 MP 专用 API Key，请在论坛“隐秘的角落”生成并粘贴 API Key")
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"MoviePilot-FengchaoSignin/{self.plugin_version}",
            "X-MoviePilot-Instance-Id": self._instance_id,
            "X-MoviePilot-Plugin-Version": self.plugin_version,
            "X-MoviePilot-Version": str(getattr(settings, "VERSION_FLAG", "")),
        }

    def __api_request(self, method, path, payload=None):
        base_url = _resolve_api_base()
        response = requests.request(method, f"{base_url}{path}", headers=self.__api_headers(), json=payload, timeout=(5, 30), proxies=self._get_proxies() if self._use_proxy else None, allow_redirects=False)
        try:
            result = response.json() or {}
        except Exception as exc:
            raise RuntimeError(f"论坛返回非 JSON 响应（HTTP {response.status_code}）") from exc
        if response.status_code >= 400 or result.get("code") not in (None, 0):
            raise RuntimeError(result.get("message") or f"论坛 API 请求失败（HTTP {response.status_code}）")
        return result.get("data") or {}

    def __api_signin(self):
        if getattr(self, "_signing_in", False):
            logger.info("已有签到任务在执行，跳过当前任务")
            return False
        self._signing_in = True
        started = datetime.now()
        self._current_batch_id = f"{self._instance_id}-{started.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:12]}"
        # Network failures are retried by a dated scheduler job instead of a
        # long sleep loop. One invocation therefore issues at most one
        # check-in write; the forum endpoint remains idempotent by user/day.
        max_attempts = 1
        last_error = None
        try:
            for attempt in range(max_attempts):
                try:
                    # /me binds the instance and returns the owner card. Once
                    # that cache is fresh, check-in/snapshot/status are enough;
                    # revalidate at most once per day to reduce forum load.
                    if self._identity_refresh_due():
                        identity = self.__api_request("GET", "/api/integrations/moviepilot/v1/me")
                        identity_status = identity.get("status") if isinstance(identity, dict) and isinstance(identity.get("status"), dict) else identity
                        self._notify_status_transition(identity_status)
                    result = self.__api_request("POST", "/api/integrations/moviepilot/v1/check-in", {})
                    self._cache_checkin_result(result)
                    pushed_snapshot = False
                    snapshot_error = None
                    if self._mp_push_enabled and (not self._timed_update_enabled or self._snapshot_refresh_due()):
                        try:
                            # A snapshot failure must not retry an already
                            # successful check-in. The daily snapshot job has
                            # its own bounded retry policy.
                            snapshot = self.__push_stats_with_retries(retry_count=0)
                            pushed_snapshot = True
                        except Exception as exc:
                            snapshot_error = exc
                            snapshot = self.get_data("last_push_result") or {}
                            logger.warning(f"签到成功，但 PT 人生快照同步失败：{exc}")
                    else:
                        snapshot = self.get_data("last_push_result") or {}
                    # Qualification can only change after a snapshot (apart
                    # from administrative actions). Poll status after a push,
                    # otherwise at most every 12 hours. The check-in response
                    # already carried the authoritative streak summary.
                    if pushed_snapshot or self._status_refresh_due():
                        try:
                            self._notify_status_transition(self._sync_if_requested(self.__api_request("GET", "/api/integrations/moviepilot/v1/status")))
                        except Exception as status_error:
                            # A successful check-in must never be retried just
                            # because the optional status refresh failed.
                            logger.warning(f"蜂巢签到成功，但读取资格状态失败：{status_error}")
                    break
                except Exception as exc:
                    last_error = exc
                    if attempt + 1 >= max_attempts:
                        raise
                    logger.warning(f"蜂巢 API 签到第 {attempt + 1} 次失败，将重试：{exc}")
                    backoff_seconds = min(max(1, int(self._retry_interval or 1) * 3600) * (2 ** attempt), 1800)
                    time.sleep(backoff_seconds + random.uniform(0, min(30, backoff_seconds * 0.1)))
            already = bool(result.get("alreadyCheckedIn"))
            status_text = "已签到" if already else "签到成功"
            reward = result.get("reward", 0)
            streak = result.get("currentStreak", 0)
            sync_line = f"📊 PT 站点：{snapshot.get('siteCount', 0)} 个" if not snapshot_error else "📊 PT 同步：本次失败，将由独立同步任务重试"
            self._send_notification(title=f"【✅ 蜂巢{status_text}】", text=(f"📢 执行结果\n━━━━━━━━━━\n🕐 时间：{started.strftime('%Y-%m-%d %H:%M:%S')}\n✨ 状态：{status_text}\n🎁 奖励：{reward}\n📆 连续签到：{streak}\n{sync_line}\n━━━━━━━━━━"))
            self._save_history({"date": started.strftime('%Y-%m-%d %H:%M:%S'), "status": status_text, "reward": reward, "currentStreak": streak, "siteCount": snapshot.get("siteCount", 0), "failure_count": 0})
            self._current_retry = 0
            if self._scheduler and self._scheduler.get_job("fengchao_signin_retry"):
                self._scheduler.remove_job("fengchao_signin_retry")
            return True
        except Exception as exc:
            logger.error(f"蜂巢 API Key 签到失败: {exc}")
            if self._current_retry < self._retry_count:
                self._current_retry += 1
                try:
                    self._schedule_retry()
                except Exception as schedule_error:
                    self._current_retry -= 1
                    logger.error(f"安排蜂巢签到延迟重试失败: {schedule_error}")
            self._save_history({"date": started.strftime('%Y-%m-%d %H:%M:%S'), "status": "签到失败", "reason": str(last_error or exc), "failure_count": self._current_retry or 1})
            self._send_signin_failure_notification(str(last_error or exc), self._current_retry)
            return False
        finally:
            self._signing_in = False
            self._current_batch_id = None

    def __api_push_stats(self):
        raw = self._get_site_statistics() or {}
        managed = {}
        try:
            from app.helper.sites import SitesHelper
            managed = {str(item.get("name")): item for item in SitesHelper().get_indexers() if item.get("name")}
        except Exception:
            managed = {}
        normalized = []
        for site in (raw.get("sites", []) if isinstance(raw, dict) else [])[:200]:
            if not isinstance(site, dict) or not site.get("name") or site.get("error"):
                continue
            config = managed.get(str(site.get("name"))) or {}
            normalized.append({"name": str(site.get("name")), "domain": str(config.get("url") or ""), "mpSiteId": str(config.get("id") or ""), "username": str(site.get("username") or ""), "userLevel": str(site.get("user_level") or ""), "upload": _safe_nonnegative_int(site.get("upload")), "download": _safe_nonnegative_int(site.get("download")), "bonus": _safe_bonus(site.get("bonus")), "seeding": _safe_nonnegative_int(site.get("seeding")), "seedingSize": _safe_nonnegative_int(site.get("seeding_size"))})
        now = datetime.now(tz=pytz.UTC).isoformat()
        result = self.__api_request("PUT", "/api/integrations/moviepilot/v1/pt-life/snapshot", {"schemaVersion": 1, "instanceId": self._instance_id, "pluginVersion": self.plugin_version, "moviePilotVersion": str(getattr(settings, "VERSION_FLAG", "")), "clientBatchId": getattr(self, "_current_batch_id", None) or f"{self._instance_id}-{now[:19]}", "collectedAt": now, "sites": normalized})
        self._last_push_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_data("last_push_time", self._last_push_time)
        self.save_data("last_push_result", result)
        return result

    def __push_stats_with_retries(self, retry_count=None, retry_interval=None, batch_id=None):
        """上传 PT 人生快照，并复用原插件的失败重试设置。"""
        if getattr(self, "_pushing_stats", False):
            logger.info("已有 PT 人生同步任务在执行，复用最近结果")
            cached = self.get_data("last_push_result")
            if isinstance(cached, dict):
                return cached
            raise RuntimeError("已有 PT 人生同步任务正在执行")
        self._pushing_stats = True
        owns_batch_id = not bool(getattr(self, "_current_batch_id", None))
        if owns_batch_id:
            started = datetime.now(tz=pytz.UTC)
            self._current_batch_id = batch_id or f"{self._instance_id}-{started.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:12]}"
        configured_retries = self._retry_count if retry_count is None else retry_count
        configured_interval = self._retry_interval if retry_interval is None else retry_interval
        max_attempts = max(1, int(configured_retries or 0) + 1)
        last_error = None
        try:
            for attempt in range(max_attempts):
                try:
                    return self.__api_push_stats()
                except Exception as exc:
                    last_error = exc
                    if attempt + 1 >= max_attempts:
                        raise
                    # Reuse the same client batch ID for every retry. A lost
                    # response can therefore never create a second snapshot.
                    base_delay = min(max(1, int(configured_interval or 1)) * 60, 900)
                    delay = min(base_delay * (2 ** attempt), 1800)
                    logger.warning(f"蜂巢 PT 人生同步第 {attempt + 1} 次失败，将重试：{exc}")
                    time.sleep(delay + random.uniform(0, min(30, delay * 0.1)))
            raise last_error or RuntimeError("蜂巢 PT 人生同步失败")
        finally:
            self._pushing_stats = False
            if owns_batch_id:
                self._current_batch_id = None

    def _notify_status_transition(self, status):
        if not isinstance(status, dict):
            return
        previous = self.get_data("last_status") or {}
        previous_circle = bool(previous.get("ptCircle")) if isinstance(previous, dict) else False
        current_circle = bool(status.get("ptCircle"))
        if current_circle and not previous_circle:
            self._send_notification("【✅ 蜂巢 PT 圈子认证通过】", "你的 PT 人生已满足圈子认证规则，隐藏圈子权限已按后台规则开放。")
        elif previous_circle and not current_circle:
            self._send_notification("【⚠️ 蜂巢 PT 圈子资格暂停】", "当前同步结果不再满足圈子条件或已进入宽限期，请查看论坛 PT 人生认证中心。")
        previous_qualifications = {str(item.get("ruleId")): item.get("state") for item in previous.get("qualifications", []) if isinstance(item, dict)} if isinstance(previous, dict) else {}
        rule_names = {
            str(item.get("ruleId")): str(item.get("name") or "圈子认证规则")
            for item in (status.get("qualificationRules") if isinstance(status.get("qualificationRules"), list) else [])
            if isinstance(item, dict) and item.get("ruleId")
        }
        for item in status.get("qualifications", []) if isinstance(status.get("qualifications"), list) else []:
            if not isinstance(item, dict) or not item.get("ruleId"):
                continue
            state = item.get("state")
            if state in {"GRACE", "SUSPENDED"} and previous_qualifications.get(str(item["ruleId"])) not in {state, "GRACE", "SUSPENDED"}:
                state_text = "进入宽限期" if state == "GRACE" else "资格已暂停"
                self._send_notification("【⚠️ 蜂巢 PT 认证状态变化】", f"{rule_names.get(str(item['ruleId']), '圈子认证')}：{state_text}。请在论坛认证中心查看原因和恢复条件。")
        # Keep a small owner-only cache for the plugin page.  The cache is
        # intentionally bounded and contains no site usernames or raw
        # snapshots, so rendering the original plugin UI never needs another
        # forum request.
        qualifications = status.get("qualifications", []) if isinstance(status.get("qualifications"), list) else []
        compact_qualifications = [item for item in qualifications[:30] if isinstance(item, dict)]
        account_fresh = isinstance(status.get("account"), dict)
        account = status.get("account") if account_fresh else (previous.get("account") if isinstance(previous, dict) and isinstance(previous.get("account"), dict) else None)
        compact_account = None
        if account:
            compact_account = {
                "uid": _safe_nonnegative_int(account.get("uid")),
                "username": str(account.get("username") or ""),
                "displayName": str(account.get("displayName") or account.get("username") or ""),
                "avatarPath": account.get("avatarPath") if isinstance(account.get("avatarPath"), str) else None,
                "vipLevel": _safe_nonnegative_int(account.get("vipLevel")),
                "level": _safe_nonnegative_int(account.get("level")),
                "levelName": str(account.get("levelName") or ""),
                "levelIcon": str(account.get("levelIcon") or "🌱"),
                "levelColor": str(account.get("levelColor") or "#64748b"),
                "points": _safe_nonnegative_int(account.get("points")),
                "postCount": _safe_nonnegative_int(account.get("postCount")),
                "commentCount": _safe_nonnegative_int(account.get("commentCount")),
                "likeReceivedCount": _safe_nonnegative_int(account.get("likeReceivedCount")),
                "favoriteCount": _safe_nonnegative_int(account.get("favoriteCount")),
                "followerCount": _safe_nonnegative_int(account.get("followerCount")),
                "boardCount": _safe_nonnegative_int(account.get("boardCount")),
                "receivedTipCount": _safe_nonnegative_int(account.get("receivedTipCount")),
                "acceptedAnswerCount": _safe_nonnegative_int(account.get("acceptedAnswerCount")),
                "joinedAt": account.get("joinedAt") if isinstance(account.get("joinedAt"), str) else None,
                "lastLoginAt": account.get("lastLoginAt") if isinstance(account.get("lastLoginAt"), str) else None,
                "radar": [
                    {
                        "key": str(item.get("key") or ""),
                        "label": str(item.get("label") or ""),
                        "score": _safe_nonnegative_int(item.get("score")),
                        "displayScore": _safe_nonnegative_int(item.get("displayScore", item.get("score"))),
                        "detail": str(item.get("detail") or ""),
                    }
                    for item in (account.get("radar") if isinstance(account.get("radar"), list) else [])[:6]
                    if isinstance(item, dict)
                ],
                "badges": [
                    {
                        "id": str(item.get("id") or ""),
                        "code": str(item.get("code") or ""),
                        "name": str(item.get("name") or "勋章"),
                        "description": str(item.get("description") or ""),
                        "iconText": item.get("iconText") if isinstance(item.get("iconText"), str) else None,
                        "iconPath": item.get("iconPath") if isinstance(item.get("iconPath"), str) else None,
                        "imageUrl": item.get("imageUrl") if isinstance(item.get("imageUrl"), str) else None,
                        "color": str(item.get("color") or "primary"),
                        "category": str(item.get("category") or "社区成就"),
                        "hidden": bool(item.get("hidden")),
                        "isDisplayed": bool(item.get("isDisplayed", True)),
                        "source": str(item.get("source") or ""),
                        "systemState": item.get("systemState") if isinstance(item.get("systemState"), str) else None,
                    }
                    for item in (account.get("badges") if isinstance(account.get("badges"), list) else [])[:60]
                    if isinstance(item, dict)
                ],
                "recentCheckIns": [
                    {
                        "date": str(item.get("date") or ""),
                        "reward": _safe_nonnegative_int(item.get("reward")),
                        "isMakeUp": bool(item.get("isMakeUp")),
                    }
                    for item in (account.get("recentCheckIns") if isinstance(account.get("recentCheckIns"), list) else [])[:31]
                    if isinstance(item, dict) and item.get("date")
                ],
            }
        self.save_data("last_status", {
            "ptCircle": current_circle,
            "qualifications": compact_qualifications,
            "checkIn": status.get("checkIn") if isinstance(status.get("checkIn"), dict) else (previous.get("checkIn") if isinstance(previous, dict) and isinstance(previous.get("checkIn"), dict) else None),
            "account": compact_account,
            "connected": bool(status.get("connected")),
            "active": bool(status.get("active")),
            "state": status.get("state"),
            "lastSeenAt": status.get("lastSeenAt"),
            "lastSnapshotAt": status.get("lastSnapshotAt"),
            "cachedAt": datetime.now(tz=pytz.UTC).isoformat(),
            "identityRefreshedAt": datetime.now(tz=pytz.UTC).isoformat() if account_fresh else (previous.get("identityRefreshedAt") if isinstance(previous, dict) else None),
        })

    def _get_cached_status(self):
        status = self.get_data("last_status") or {}
        return status if isinstance(status, dict) else {}

    def _force_refresh_info(self):
        """一次性强制刷新：重新拉取身份卡、签到摘要与圈子状态并更新本地缓存。"""
        try:
            identity = self.__api_request("GET", "/api/integrations/moviepilot/v1/me")
            status = identity.get("status") if isinstance(identity, dict) and isinstance(identity.get("status"), dict) else identity
            if not isinstance(status, dict) or not isinstance(status.get("account"), dict):
                raise RuntimeError("论坛未返回身份卡数据")
            self._notify_status_transition(status)
            try:
                self._notify_status_transition(self._sync_if_requested(self.__api_request("GET", "/api/integrations/moviepilot/v1/status")))
            except Exception as status_error:
                logger.warning(f"蜂巢强制刷新成功，但读取圈子状态失败：{status_error}")
            self._send_notification("【✅ 蜂巢信息已刷新】", "已强制重新拉取论坛身份卡、签到摘要与圈子状态。")
        except Exception as exc:
            logger.error(f"蜂巢强制刷新论坛信息失败: {exc}")
            self._send_notification("【⚠️ 蜂巢信息刷新失败】", str(exc))

    def _identity_refresh_due(self, max_age_hours: int = 24) -> bool:
        """Whether the local owner/instance cache needs a heartbeat."""
        status = self._get_cached_status()
        refreshed_at = status.get("identityRefreshedAt")
        if not isinstance(status.get("account"), dict) or not isinstance(refreshed_at, str) or not refreshed_at:
            return True
        try:
            parsed = datetime.fromisoformat(refreshed_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=pytz.UTC)
            return (datetime.now(tz=pytz.UTC) - parsed).total_seconds() >= max_age_hours * 3600
        except (TypeError, ValueError, OverflowError):
            return True

    def _status_refresh_due(self, max_age_hours: int = 12) -> bool:
        """Bound status polling while still seeing admin actions promptly."""
        cached_at = self._get_cached_status().get("cachedAt")
        if not isinstance(cached_at, str) or not cached_at:
            return True
        try:
            parsed = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=pytz.UTC)
            return (datetime.now(tz=pytz.UTC) - parsed).total_seconds() >= max_age_hours * 3600
        except (TypeError, ValueError, OverflowError):
            return True

    def _cache_checkin_result(self, result):
        """Merge the check-in write response into the owner-only local cache."""
        if not isinstance(result, dict):
            return
        previous = self._get_cached_status()
        summary = result.get("checkIn") if isinstance(result.get("checkIn"), dict) else {}
        if not summary:
            summary = {
                "checkedInToday": True,
                "todayReward": _safe_nonnegative_int(result.get("reward")),
                "todayIsMakeUp": False,
                "currentStreak": _safe_nonnegative_int(result.get("currentStreak")),
                "maxStreak": _safe_nonnegative_int(result.get("maxStreak")),
                "lastCheckInDate": result.get("date"),
            }
        previous["checkIn"] = summary
        account = previous.get("account") if isinstance(previous.get("account"), dict) else None
        date_key = str(result.get("date") or datetime.now().strftime("%Y-%m-%d"))[:10]
        if account and date_key:
            rows = [item for item in account.get("recentCheckIns", []) if isinstance(item, dict) and str(item.get("date") or "") != date_key]
            rows.insert(0, {
                "date": date_key,
                "reward": _safe_nonnegative_int(result.get("reward")),
                "isMakeUp": False,
            })
            account["recentCheckIns"] = rows[:31]
            previous["account"] = account
        self.save_data("last_status", previous)

    def _snapshot_refresh_due(self, max_age_hours: int = 18) -> bool:
        """Avoid a second full snapshot when the timed job ran recently."""
        last_push = self.get_data("last_push_time")
        if not isinstance(last_push, str) or not last_push:
            return True
        try:
            pushed_at = datetime.strptime(last_push, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
            return (datetime.now(tz=pytz.UTC) - pushed_at).total_seconds() >= max_age_hours * 3600
        except (TypeError, ValueError, OverflowError):
            return True

    def _sync_if_requested(self, status):
        """后台要求重新同步时，在下一个插件周期主动上传一次快照。"""
        if not isinstance(status, dict):
            return status
        request = status.get("syncRequest")
        requested_at = request.get("requestedAt") if isinstance(request, dict) else None
        if not requested_at or requested_at == self.get_data("last_sync_request"):
            return status
        try:
            self.__push_stats_with_retries(retry_count=0)
            self.save_data("last_sync_request", requested_at)
            return self.__api_request("GET", "/api/integrations/moviepilot/v1/status")
        except Exception as exc:
            logger.warning(f"蜂巢后台要求同步，但快照上传失败: {exc}")
            return status

    def _normalized_webhook_public_url(self):
        """规范化 MP 公网入口；派生密钥只允许通过 HTTPS 发送。"""
        candidate = self._webhook_public_url.strip().rstrip("/")
        parsed = urlparse(candidate)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise RuntimeError("MP 公网地址必须是无账号、参数和片段的 HTTPS 地址")
        path = parsed.path.rstrip("/")
        return urlunparse(("https", parsed.netloc, path, "", "", ""))

    def _webhook_token(self):
        """由 MP APIKEY 派生实例专用密钥，主 APIKEY 不离开 MoviePilot。"""
        if len(self._webhook_mp_api_key) < 16 or len(self._webhook_mp_api_key) > 512:
            raise RuntimeError("请填写有效的 MP APIKEY")
        message = f"fengchao-webhook:{self._instance_id}".encode("utf-8")
        return hmac.new(self._webhook_mp_api_key.encode("utf-8"), message, hashlib.sha256).hexdigest()

    def _build_notification_webhook_url(self):
        base_url = self._normalized_webhook_public_url()
        query = urlencode({"instance": self._instance_id})
        fragment = urlencode({"token": self._webhook_token()})
        return f"{base_url}/api/v1/plugin/FengchaoSignin/fengchao_webhook?{query}#{fragment}"

    def _webhook_registration_fingerprint(self):
        """Only synchronize forum settings when the effective callback changes."""
        config = {
            "enabled": self._webhook_enabled,
            "events": {
                "systemNotification": self._webhook_system_notification,
                "replyNotification": self._webhook_reply_notification,
                "privateMessage": self._webhook_private_message,
            },
            "url": self._build_notification_webhook_url() if self._webhook_enabled else "",
        }
        encoded = json.dumps(config, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _save_webhook_status(self, **values):
        current = self.get_data("webhook_status") or {}
        current = current if isinstance(current, dict) else {}
        current.update(values)
        current["updatedAt"] = datetime.now(tz=pytz.UTC).isoformat()
        self.save_data("webhook_status", current)

    def _notify_webhook_configuration_failure(self, reason):
        """Notify once per distinct failure within six hours without exposing secrets."""
        safe_reason = self._clean_webhook_text(reason, 500)
        safe_reason = re.sub(r"(?i)(token=)[a-f0-9]{64}", r"\1[已隐藏]", safe_reason)
        fingerprint = hashlib.sha256(safe_reason.encode("utf-8")).hexdigest()
        previous = self.get_data("webhook_failure_notice") or {}
        previous = previous if isinstance(previous, dict) else {}
        previous_at = previous.get("at") if isinstance(previous.get("at"), (int, float)) else 0
        if previous.get("fingerprint") == fingerprint and time.time() - float(previous_at) < 6 * 3600:
            return
        self.post_message(
            mtype=NotificationType.SiteMessage,
            title="【⚠️ 蜂巢论坛通知连接失败】",
            text=(
                f"论坛通知尚未连通：{safe_reason or '未知错误'}\n\n"
                "请检查 MoviePilot 公网 HTTPS 地址、反向代理路径和 MoviePilot APIKEY。"
                "修正后保存插件配置，会自动重新注册并测试。"
            ),
        )
        self.save_data("webhook_failure_notice", {"fingerprint": fingerprint, "at": time.time()})

    def _sync_notification_webhook(self, send_test=False):
        """先验证候选地址，再原子更新当前账号的站外通知设置。"""
        if not self._api_key:
            self._save_webhook_status(enabled=False, configured=False, error="请先配置论坛 MP 专用 API Key")
            logger.warning("蜂巢论坛通知配置失败：未配置论坛 MP 专用 API Key")
            self._notify_webhook_configuration_failure("请先配置论坛 MP 专用 API Key")
            return False

        callback_url = ""
        if self._webhook_enabled:
            if not any((self._webhook_system_notification, self._webhook_reply_notification, self._webhook_private_message)):
                self._save_webhook_status(enabled=False, configured=False, error="至少选择一种论坛通知")
                logger.warning("蜂巢论坛通知配置失败：未选择通知类型")
                self._notify_webhook_configuration_failure("至少选择一种论坛通知")
                return False
            try:
                callback_url = self._build_notification_webhook_url()
            except Exception as exc:
                self._save_webhook_status(enabled=False, configured=False, error=str(exc))
                logger.warning("蜂巢论坛通知配置失败：%s", exc)
                self._notify_webhook_configuration_failure(str(exc))
                return False

        events = {
            "systemNotification": self._webhook_system_notification,
            "replyNotification": self._webhook_reply_notification,
            "privateMessage": self._webhook_private_message,
        }

        if not self._webhook_enabled:
            try:
                result = self.__api_request("PUT", "/api/integrations/moviepilot/v1/notification-webhook", {
                    "enabled": False,
                    "url": "",
                    "events": events,
                })
            except Exception as exc:
                self._save_webhook_status(enabled=False, configured=False, verified=False, error=str(exc))
                logger.warning("关闭蜂巢论坛通知失败：%s", exc)
                self._notify_webhook_configuration_failure(str(exc))
                return False

            self.save_data("webhook_registered", False)
            self.save_data("webhook_registration_fingerprint", None)
            self.save_data("webhook_verified_fingerprint", None)
            self.save_data("webhook_failure_notice", None)
            self._save_webhook_status(
                enabled=False,
                configured=bool(result.get("configured")) if isinstance(result, dict) else False,
                verified=False,
                tested=False,
                testError="",
                events=events,
                error="",
            )
            logger.info("蜂巢论坛通知已关闭")
            return True

        previous_registered = bool(self.get_data("webhook_registered"))
        current_fingerprint = self._webhook_registration_fingerprint()
        try:
            identity = self.__api_request("GET", "/api/integrations/moviepilot/v1/me")
            forum_user_id = _safe_positive_int(identity.get("userId")) if isinstance(identity, dict) else 0
            if forum_user_id <= 0:
                identity_status = identity.get("status") if isinstance(identity, dict) and isinstance(identity.get("status"), dict) else {}
                account = identity_status.get("account") if isinstance(identity_status.get("account"), dict) else {}
                forum_user_id = _safe_positive_int(account.get("uid"))
            if forum_user_id <= 0:
                raise RuntimeError("论坛没有返回当前绑定账号")
            self.save_data("webhook_forum_user_id", forum_user_id)

            # 候选地址只做一次性投递测试；论坛端不会在这一步保存或启用它。
            self.__api_request("POST", "/api/integrations/moviepilot/v1/notification-webhook", {
                "url": callback_url,
            })
        except Exception as exc:
            self._save_webhook_status(
                enabled=previous_registered,
                requestedEnabled=True,
                configured=False,
                verified=False,
                tested=False,
                testError=str(exc),
                events=events,
                error="候选地址端到端测试未通过，论坛未启用该地址",
            )
            logger.warning("蜂巢论坛通知候选地址测试失败，论坛未启用该地址：%s", exc)
            self._notify_webhook_configuration_failure(str(exc))
            return False

        try:
            result = self.__api_request("PUT", "/api/integrations/moviepilot/v1/notification-webhook", {
                "enabled": True,
                "url": callback_url,
                "events": events,
            })
        except Exception as exc:
            self._save_webhook_status(
                enabled=previous_registered,
                requestedEnabled=True,
                configured=False,
                verified=False,
                tested=True,
                testedAt=datetime.now(tz=pytz.UTC).isoformat(),
                testError="",
                events=events,
                error="候选地址已连通，但论坛保存配置失败",
            )
            logger.warning("蜂巢论坛通知候选地址已连通，但保存配置失败：%s", exc)
            self._notify_webhook_configuration_failure(str(exc))
            return False

        self.save_data("webhook_registered", True)
        self.save_data("webhook_registration_fingerprint", current_fingerprint)
        self.save_data("webhook_verified_fingerprint", current_fingerprint)
        self.save_data("webhook_failure_notice", None)
        self._save_webhook_status(
            enabled=True,
            requestedEnabled=True,
            configured=bool(result.get("configured")) if isinstance(result, dict) else True,
            verified=True,
            tested=True,
            testedAt=datetime.now(tz=pytz.UTC).isoformat(),
            testError="",
            events=events,
            error="",
        )
        logger.info("蜂巢论坛通知候选地址测试通过并已启用")
        return True

    def _verify_webhook_access(
        self,
        instance: str = Query(..., min_length=36, max_length=36),
        token: str = Header(..., alias="X-Fengchao-Webhook-Token", min_length=64, max_length=64),
    ):
        if not self._webhook_enabled:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="蜂巢论坛通知未启用")
        try:
            expected_token = self._webhook_token()
        except Exception:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="蜂巢论坛通知尚未完成配置")
        if not compare_digest(instance, self._instance_id) or not compare_digest(token, expected_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Webhook 鉴权失败")
        return instance

    @staticmethod
    def _clean_webhook_text(value, limit):
        text = str(value or "")
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text).strip()
        return text[:limit]

    @staticmethod
    def _format_webhook_time(value):
        text = str(value or "").strip()
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.astimezone(pytz.timezone(settings.TZ)).strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError, OverflowError):
            return text[:32] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _safe_forum_inbox_url(value, fallback_path="/notifications"):
        fallback = f"{_resolve_api_base()}{fallback_path}"
        try:
            target = urlparse(str(value or ""))
            forum = urlparse(_resolve_api_base())
            if target.scheme != "https" or target.netloc.lower() != forum.netloc.lower() or target.username or target.password:
                return fallback
            return urlunparse((target.scheme, target.netloc, target.path or "/inbox", "", target.query, ""))
        except Exception:
            return fallback

    def _render_forum_webhook(self, payload):
        event = payload.event
        recipient_id = _safe_positive_int(payload.recipient.get("userId")) if isinstance(payload.recipient, dict) else 0
        expected_user_id = _safe_positive_int(self.get_data("webhook_forum_user_id"))
        if expected_user_id <= 0 or recipient_id != expected_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Webhook 接收账号与论坛绑定不一致")

        if event == "integration.webhook.test":
            notification = payload.notification if isinstance(payload.notification, dict) else {}
            event_id = self._clean_webhook_text(notification.get("id"), 128)
            occurred_at = self._format_webhook_time(notification.get("createdAt"))
            return event_id, "✅ 蜂巢论坛通知已连通", (
                "🔔 论坛通知接入成功\n\n"
                "当前 MoviePilot 公网地址与实例密钥均已通过端到端验证。\n\n"
                f"🕒 验证时间：{occurred_at}\n"
                "👉 点击卡片可前往蜂巢论坛"
            ), _resolve_api_base()

        if event == "system.notification.created" and self._webhook_system_notification:
            notification = payload.notification if isinstance(payload.notification, dict) else {}
            event_id = self._clean_webhook_text(notification.get("id"), 128)
            title = self._clean_webhook_text(notification.get("title") or "系统通知", 120)
            content = self._clean_webhook_text(notification.get("content") or "你收到一条新的论坛通知。", 1800)
            occurred_at = self._format_webhook_time(notification.get("createdAt"))
            inbox_url = self._safe_forum_inbox_url(notification.get("inboxUrl"))
            return event_id, "🔔 蜂巢论坛 · 系统通知", (
                f"📌 {title}\n\n"
                f"{content}\n\n"
                f"🕒 通知时间：{occurred_at}\n"
                "👉 点击卡片查看通知详情"
            ), inbox_url

        if event == "reply.notification.created" and self._webhook_reply_notification:
            notification = payload.notification if isinstance(payload.notification, dict) else {}
            event_id = self._clean_webhook_text(notification.get("id"), 128)
            title_raw = notification.get("title") or "你收到一条新回复"
            title = self._clean_webhook_text(title_raw, 120)
            content = self._clean_webhook_text(notification.get("content") or "论坛讨论有了新回复。", 1800)
            occurred_at = self._format_webhook_time(notification.get("createdAt"))
            inbox_url = self._safe_forum_inbox_url(notification.get("inboxUrl"))
            return event_id, "💬 蜂巢论坛 · 新回复", (
                f"📝 {title}\n\n"
                f"{content}\n\n"
                f"🕒 回复时间：{occurred_at}\n"
                "👉 点击卡片查看完整讨论"
            ), inbox_url

        if event == "private.message.created" and self._webhook_private_message:
            message = payload.message if isinstance(payload.message, dict) else {}
            sender = payload.sender if isinstance(payload.sender, dict) else {}
            event_id = self._clean_webhook_text(message.get("id"), 128)
            display_name_raw = sender.get("displayName") or sender.get("username") or "论坛用户"
            display_name = self._clean_webhook_text(display_name_raw, 80)
            username = self._clean_webhook_text(sender.get("username") or "", 80)
            preview = self._clean_webhook_text(message.get("preview") or message.get("content") or "你收到一条新私信。", 1200)
            occurred_at = self._format_webhook_time(message.get("createdAt"))
            inbox_url = self._safe_forum_inbox_url(message.get("inboxUrl"), "/inbox")
            sender_line = f"👤 发件人：{display_name}" + (f"（@{username}）" if username else "")
            return event_id, "✉️ 蜂巢论坛 · 新私信", (
                f"{sender_line}\n\n"
                f"💭 {preview}\n\n"
                f"🕒 发送时间：{occurred_at}\n"
                "👉 点击卡片打开私信会话"
            ), inbox_url

        if event not in {"integration.webhook.test", "system.notification.created", "reply.notification.created", "private.message.created"}:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="不支持的论坛通知类型")
        return None

    def receive_forum_webhook(
        self,
        payload: FengchaoWebhookPayload,
        idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key", max_length=300),
    ) -> schemas.Response:
        """接收论坛 POST JSON，并投递到 MoviePilot 已启用的通知渠道。"""
        now = time.monotonic()
        with self._webhook_lock:
            if now - self._webhook_rate_window_started >= 60:
                self._webhook_rate_window_started = now
                self._webhook_rate_count = 0
            if self._webhook_rate_count >= 120:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Webhook 请求过于频繁")
            self._webhook_rate_count += 1

        rendered = self._render_forum_webhook(payload)
        if rendered is None:
            return schemas.Response(success=True, message="该通知类型未订阅")
        event_id, title, text, link = rendered
        if not event_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="论坛通知缺少事件 ID")

        recipient_id = _safe_positive_int(payload.recipient.get("userId"))
        delivery_key = hashlib.sha256(f"{payload.event}:{recipient_id}:{event_id}".encode("utf-8")).hexdigest()
        now = time.time()
        with self._webhook_lock:
            recent = self.get_data("webhook_deliveries") or []
            recent = [
                item for item in recent
                if isinstance(item, dict) and isinstance(item.get("at"), (int, float)) and now - float(item["at"]) <= 7 * 86400
            ]
            if any(compare_digest(str(item.get("key") or ""), delivery_key) for item in recent):
                return schemas.Response(success=True, message="通知已处理")
            self.post_message(
                mtype=NotificationType.SiteMessage,
                title=title,
                text=text,
                image=FORUM_NOTIFICATION_CARD_IMAGE,
                link=link,
                parse_mode="plain",
            )
            recent.append({"key": delivery_key, "at": now})
            self.save_data("webhook_deliveries", recent[-200:])

        logger.info("蜂巢论坛通知已提交到 MoviePilot 通知链，事件=%s，幂等键=%s", payload.event, bool(idempotency_key))
        return schemas.Response(success=True, message="通知已提交")

    def _save_history(self, record: Dict[str, Any]):
        """
        保存签到历史记录，确保同一天只有一条记录（以日期为Key）
        """
        history = self.get_data('history') or []
        
        # 提取传入记录的日期部分 (YYYY-MM-DD)
        try:
            record_date = record.get("date", "").split(" ")[0]
        except Exception:
            record_date = date.today().strftime('%Y-%m-%d')

        # 在历史记录中查找同日期的记录索引
        existing_index = -1
        for i, item in enumerate(history):
            if item.get("date", "").startswith(record_date):
                existing_index = i
                break

        is_new_success = "成功" in record.get("status", "") or "已签到" in record.get("status", "")

        if existing_index != -1:
            last_record = history[existing_index]
            is_last_success = "成功" in last_record.get("status", "") or "已签到" in last_record.get("status", "")

            if is_new_success:
                # 只要新记录是成功的，就覆盖旧记录（无论是之前是失败还是成功）
                if not is_last_success:
                    record['failure_count'] = last_record.get('failure_count', 0)
                history[existing_index] = record
                logger.info(f"更新日期 {record_date} 的签到记录 (状态: {record.get('status')})")
            else:
                # 新记录是失败
                if not is_last_success:
                    # 如果旧记录也是失败，累加失败次数并更新时间
                    last_record["failure_count"] = last_record.get("failure_count", 0) + 1
                    last_record["date"] = record["date"]
                    last_record["reason"] = record.get("reason", "")
                    logger.info(f"更新日期 {record_date} 的失败记录，累计次数: {last_record['failure_count']}")
                else:
                    # 如果旧记录是成功，新记录是失败（可能是重复重试导致的），忽略新记录
                    logger.info(f"日期 {record_date} 已有成功记录，忽略新的失败记录")
        else:
            # 没有当天的记录，直接追加
            history.append(record)

        # 失败记录添加重试信息
        if "失败" in record.get("status", ""):
            record["retry"] = {
                "enabled": self._retry_count > 0,
                "current": self._current_retry,
                "max": self._retry_count,
                "interval": self._retry_interval
            }

        # 保留指定天数的记录
        if self._history_days:
            try:
                thirty_days_ago = time.time() - int(self._history_days) * 24 * 60 * 60
                history = [r for r in history if
                           datetime.strptime(r["date"], '%Y-%m-%d %H:%M:%S').timestamp() >= thirty_days_ago]
            except Exception as e:
                logger.error(f"清理历史记录异常: {str(e)}")

        self.save_data("history", history)

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/fengchao_test", "endpoint": self.api_test, "methods": ["GET"], "summary": "测试蜂巢连接", "description": "使用 MP 专用 API Key 测试论坛连接"},
            {"path": "/fengchao_checkin", "endpoint": self.api_checkin, "methods": ["POST"], "summary": "立即蜂巢签到", "description": "调用论坛原生签到 API，并保留通知与历史记录"},
            {"path": "/fengchao_sync", "endpoint": self.api_sync, "methods": ["POST"], "summary": "立即同步 PT 人生", "description": "从 MoviePilot 本地统计模型上传一份幂等快照"},
            {"path": "/fengchao_status", "endpoint": self.api_status, "methods": ["GET"], "summary": "查看蜂巢最近结果", "description": "返回最近同步结果和本地签到历史摘要"},
            {
                "path": "/fengchao_webhook",
                "endpoint": self.receive_forum_webhook,
                "methods": ["POST"],
                "allow_anonymous": True,
                "dependencies": [Depends(self._verify_webhook_access)],
                "response_model": schemas.Response,
                "summary": "接收蜂巢论坛通知",
                "description": "使用实例专用派生密钥接收论坛通知并投递到 MoviePilot 通知渠道",
            },
        ]

    def api_test(self) -> schemas.Response:
        try:
            payload = self.__api_request("GET", "/api/integrations/moviepilot/v1/me")
            status = payload.get("status") if isinstance(payload, dict) and isinstance(payload.get("status"), dict) else payload
            self._notify_status_transition(status)
            return schemas.Response(success=True, data={"connected": True, "status": status})
        except Exception as exc:
            return schemas.Response(success=False, message=str(exc))

    def api_checkin(self) -> schemas.Response:
        return schemas.Response(success=self.__signin(), data={"history": self.get_data("history") or []})

    def api_sync(self) -> schemas.Response:
        try:
            result = self.__push_stats_with_retries(retry_count=0)
            self._notify_status_transition(self._sync_if_requested(self.__api_request("GET", "/api/integrations/moviepilot/v1/status")))
            return schemas.Response(success=True, data=result)
        except Exception as exc:
            return schemas.Response(success=False, message=str(exc))

    def api_status(self) -> schemas.Response:
        return schemas.Response(success=True, data={
            "lastSync": self.get_data("last_push_result") or {},
            "history": self.get_data("history") or [],
            "status": self._get_cached_status(),
            "webhook": self.get_data("webhook_status") or {},
        })

    def get_service(self) -> List[Dict[str, Any]]:
        """任务由插件内的单一调度器管理，避免宿主再次注册同一任务。"""
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """MoviePilot 原生配置页：真实蜂巢 Logo + 分区卡片，次要设置折叠。"""
        version = getattr(settings, "VERSION_FLAG", "v1")
        cron_field_component = "VCronField" if version == "v2" else "VTextField"
        logo_url = "https://cdn.pting.club/site-logo/site-logo-e4ebd6b95befd416.png"
        forum_url = _resolve_api_base()

        def rgba(hex_color, alpha):
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"

        def field(model, label, **props):
            return {
                "component": "VTextField",
                "props": {
                    "model": model, "label": label, "variant": "outlined", "density": "comfortable",
                    **{key.replace("_", "-"): value for key, value in props.items()},
                },
            }

        def column(content, cols=12, md=None):
            props = {"cols": cols}
            if md:
                props["md"] = md
            return {"component": "VCol", "props": props, "content": content}

        def switch(model, label, color, hint=None):
            props = {"model": model, "label": label, "color": color, "hide-details": True}
            if hint:
                props.pop("hide-details")
                props.update({"hint": hint, "persistent-hint": True})
            return {"component": "VSwitch", "props": props}

        def info_card(text, icon, color, extra_class=""):
            return {
                "component": "div",
                "props": {"class": f"d-flex align-center ga-3 w-100 {extra_class}".strip(), "style": f"background: {rgba(color, 0.08)}; border: 1px solid {rgba(color, 0.22)}; border-radius: 12px; padding: 12px 16px;"},
                "content": [
                    {"component": "VIcon", "props": {"size": 22, "color": color}, "text": icon},
                    {"component": "div", "props": {"class": "text-body-2 text-medium-emphasis"}, "text": text},
                ],
            }

        def info_block(title, text, icon, color):
            return {
                "component": "div",
                "props": {"class": "d-flex align-center ga-3", "style": f"background: {rgba(color, 0.08)}; border: 1px solid {rgba(color, 0.22)}; border-radius: 12px; padding: 14px 16px;"},
                "content": [
                    {"component": "div", "props": {"class": "d-flex align-center justify-center", "style": f"width: 40px; height: 40px; border-radius: 12px; background: {rgba(color, 0.16)};"}, "content": [
                        {"component": "VIcon", "props": {"size": 22, "color": color}, "text": icon},
                    ]},
                    {"component": "div", "content": [
                        {"component": "div", "props": {"class": "text-body-2 font-weight-medium"}, "text": title},
                        {"component": "div", "props": {"class": "text-caption text-medium-emphasis mt-1"}, "text": text},
                    ]},
                ],
            }

        def icon_tile(icon, color, size=36):
            return {
                "component": "div",
                "props": {"class": "d-flex align-center justify-center", "style": f"width: {size}px; height: {size}px; border-radius: 10px; background: {rgba(color, 0.12)};"},
                "content": [
                    {"component": "VIcon", "props": {"size": int(size * 0.56), "color": color}, "text": icon},
                ],
            }

        def section(title, icon, color, rows):
            return {
                "component": "VCard",
                "props": {
                    "variant": "flat", "rounded": "xl", "class": "mb-3 overflow-hidden",
                    "style": "border: 1px solid rgba(128, 128, 128, 0.18);",
                },
                "content": [
                    {"component": "div", "props": {"class": "d-flex align-center ga-3 px-4 pt-4 pb-3"}, "content": [
                        icon_tile(icon, color),
                        {"component": "div", "props": {"class": "text-subtitle-1 font-weight-bold"}, "text": title},
                    ]},
                    {"component": "VDivider"},
                    {"component": "VCardText", "props": {"class": "px-4 pt-3 pb-4"}, "content": rows},
                ],
            }

        def panel(title, icon, color, caption, rows):
            return {
                "component": "VExpansionPanel",
                "content": [
                    {"component": "VExpansionPanelTitle", "content": [
                        {"component": "div", "props": {"class": "d-flex align-center ga-3"}, "content": [
                            icon_tile(icon, color, 30),
                            {"component": "span", "text": title},
                            {"component": "span", "props": {"class": "text-caption text-medium-emphasis ml-1"}, "text": caption},
                        ]},
                    ]},
                    {"component": "VExpansionPanelText", "content": rows},
                ],
            }

        hero = {
            "component": "VCard",
            "props": {
                "variant": "flat", "rounded": "xl", "class": "mb-4 overflow-hidden",
                "style": "position: relative; border: 1px solid rgba(128, 128, 128, 0.18);",
            },
            "content": [
                {"component": "div", "props": {"class": "d-none d-sm-flex", "style": "position: absolute; width: 150px; height: 150px; border-radius: 50%; background: rgba(249, 115, 22, 0.08); top: -60px; left: -40px;"}, "content": []},
                {"component": "div", "props": {"class": "d-none d-sm-flex", "style": "position: absolute; width: 190px; height: 190px; border-radius: 50%; background: rgba(14, 165, 233, 0.07); bottom: -75px; right: -55px;"}, "content": []},
                {"component": "div", "props": {"class": "d-flex flex-column align-center justify-center pa-5", "style": "position: relative;"}, "content": [
                    {"component": "VImg", "props": {"src": logo_url, "width": 146, "height": 40, "contain": True}},
                    {"component": "div", "props": {"class": "d-flex align-center ga-2 mt-3"}, "content": [
                        {"component": "div", "props": {"style": "width: 4px; height: 4px; border-radius: 50%; background: #f97316;"}, "content": []},
                        {"component": "span", "props": {"class": "text-caption text-medium-emphasis"}, "text": "专注长期讨论与高质量交流"},
                        {"component": "div", "props": {"style": "width: 4px; height: 4px; border-radius: 50%; background: #0ea5e9;"}, "content": []},
                    ]},
                    {"component": "div", "props": {"class": "d-flex align-center justify-center mt-1", "style": "color: rgba(128, 128, 128, 0.78);"}, "content": [
                        {"component": "span", "props": {"class": "text-caption"}, "text": "蜂巢论坛出品"},
                        {"component": "span", "props": {"class": "text-caption ml-1", "style": "opacity: 0.5;"}, "text": "· @madrays"},
                    ]},
                ]},
                {"component": "VBtn", "props": {
                    "href": forum_url, "target": "_blank", "rel": "noopener",
                    "size": "small", "variant": "tonal", "color": "#f97316",
                    "prepend-icon": "mdi-open-in-new",
                    "style": "position: absolute; top: 14px; right: 14px;",
                }, "text": "前往论坛"},
            ],
        }

        form = [{
            "component": "VForm",
            "content": [
                hero,
                section("基础设置", "mdi-tune-variant", "#6366f1", [
                    {"component": "VRow", "content": [
                        column([switch("enabled", "启用蜂巢", "#f97316")], md=4),
                        column([switch("mp_push_enabled", "同步 PT 人生", "#0ea5e9")], md=4),
                        column([switch("notify", "发送结果通知", "#6366f1")], md=4),
                    ]},
                    {"component": "VRow", "content": [
                        column([switch("onlyonce", "立即签到一次", "#f59e0b")], md=4),
                        column([switch("update_info_now", "立即同步一次", "#14b8a6")], md=4),
                    ]},
                ]),
                section("API 接入", "mdi-key-variant", "#0ea5e9", [
                    {"component": "VRow", "content": [
                        column([info_block("如何获取 API Key", "首次生成：论坛「隐秘的角落」；后续轮换：论坛「PT 人生」。Key 仅用于接口鉴权，不含登录密码，泄露后请及时轮换。", "mdi-key-variant", "#0ea5e9")]),
                    ]},
                    {"component": "VRow", "content": [
                        column([field(
                            "api_key", "MP 专用 API Key", type="password",
                            placeholder="粘贴论坛「隐秘的角落」生成的 Key",
                            prepend_inner_icon="mdi-key-variant",
                            hint="用于蜂巢接口鉴权", persistent_hint=True,
                            autocomplete="off", clearable=True,
                        )]),
                    ]},
                ]),
                section("论坛通知", "mdi-bell-outline", "#14b8a6", [
                    {"component": "VRow", "content": [
                        column([switch(
                            "webhook_enabled", "接收论坛通知", "#14b8a6",
                            hint="保存后自动在论坛启用或关闭，无需手动填写 Webhook",
                        )], md=4),
                        column([switch("webhook_system_notification", "系统通知", "#6366f1")], md=4),
                        column([switch(
                            "webhook_reply_notification", "帖子与评论回复", "#f59e0b",
                            hint="包含帖子回复、评论回复和私密回复，不包含私信",
                        )], md=4),
                    ]},
                    {"component": "VRow", "content": [
                        column([switch("webhook_private_message", "私信", "#0ea5e9")], md=4),
                        column([switch(
                            "webhook_test_now", "发送测试通知", "#f97316",
                            hint="保存后测试一次并自动复位",
                        )], md=4),
                    ]},
                    {"component": "VRow", "content": [
                        column([field(
                            "webhook_public_url", "MoviePilot 公网地址", type="url",
                            placeholder="https://mp.example.com",
                            prepend_inner_icon="mdi-web",
                            hint="填写反向代理后的 HTTPS 地址，可包含固定路径前缀",
                            persistent_hint=True, clearable=True,
                        )], md=6),
                        column([field(
                            "webhook_mp_api_key", "MoviePilot APIKEY", type="password",
                            placeholder="填写 MoviePilot 主程序 APIKEY",
                            prepend_inner_icon="mdi-shield-key-outline",
                            hint="仅保存在本机，用于派生当前实例的 Webhook 密钥，不会发送给论坛",
                            persistent_hint=True, autocomplete="off", clearable=True,
                        )], md=6),
                    ]},
                ]),
                {"component": "VExpansionPanels", "props": {"variant": "accordion", "class": "mt-1"}, "content": [
                    panel("定时任务", "mdi-calendar-month-outline", "#f59e0b", "签到与 PT 人生数据的定时同步", [
                        {"component": "VRow", "content": [
                            column([{"component": cron_field_component, "props": {
                                "model": "cron", "label": "签到时间", "placeholder": "30 8 * * *",
                                "hint": "默认每日 08:30", "persistent-hint": True,
                                "variant": "outlined", "density": "comfortable",
                            }}], md=4),
                            column([{"component": cron_field_component, "props": {
                                "model": "timed_update_cron", "label": "PT 人生同步时间", "placeholder": "0 3 * * *",
                                "hint": "默认每日 03:00", "persistent-hint": True,
                                "variant": "outlined", "density": "comfortable",
                            }}], md=4),
                            column([field("mp_push_interval", "PT 人生推送间隔（天）", type="number", min=1, max=7)], md=4),
                        ]},
                        {"component": "VRow", "content": [
                            column([switch("timed_update_enabled", "独立同步任务", "#f59e0b", hint="关闭后仅在签到时同步")], md=4),
                            column([info_card("PT 人生数据推送间隔：1-7 天，默认每 1 天推送一次。", "mdi-sync", "#f59e0b", extra_class="h-100")], md=8),
                        ]},
                    ]),
                    panel("重试与记录", "mdi-history", "#a855f7", "失败重试策略与记录留存", [
                        {"component": "VRow", "content": [
                            column([field("retry_count", "签到重试次数", type="number", min=0, max=10)], md=6),
                            column([field("retry_interval", "签到重试间隔（小时）", type="number", min=1, max=24)], md=6),
                        ]},
                        {"component": "VRow", "content": [
                            column([field("timed_update_retry_count", "同步重试次数", type="number", min=0, max=10)], md=4),
                            column([field("timed_update_retry_interval", "同步重试间隔（小时）", type="number", min=1, max=24)], md=4),
                            column([field("history_days", "签到记录保留天数", type="number", min=1, max=3650)], md=4),
                        ]},
                        {"component": "VRow", "content": [
                            column([info_card("签到记录会展示在详情页的签到日历与历史列表中；超出保留天数的历史记录会被自动清理。", "mdi-calendar-check-outline", "#a855f7")]),
                        ]},
                    ]),
                    panel("行为", "mdi-toggle-switch-outline", "#14b8a6", "网络代理与一次性刷新", [
                        {"component": "VRow", "content": [
                            column([{"component": "VSwitch", "props": {
                                "model": "use_proxy", "label": "使用系统代理", "color": "#14b8a6",
                                "hint": "开启后 Bearer Key 会经系统代理转发", "persistent-hint": True,
                            }}], md=6),
                            column([{"component": "VSwitch", "props": {
                                "model": "force_refresh", "label": "强制刷新论坛信息（一次性）", "color": "#f97316",
                                "hint": "保存后立即重新拉取身份、签到与圈子状态，执行后自动复位",
                                "persistent-hint": True,
                            }}], md=6),
                        ]},
                    ]),
                ]},
            ],
        }]
        defaults = {
            "enabled": True, "notify": True, "cron": "30 8 * * *",
            "onlyonce": False, "update_info_now": False, "force_refresh": False,
            "api_key": "", "instance_id": "", "history_days": 30,
            "retry_count": 1, "retry_interval": 2,
            "mp_push_enabled": True, "mp_push_interval": 1,
            "use_proxy": False, "timed_update_enabled": True,
            "timed_update_cron": "0 3 * * *",
            "timed_update_retry_count": 1, "timed_update_retry_interval": 2,
            "webhook_enabled": False,
            "webhook_system_notification": True,
            "webhook_reply_notification": True,
            "webhook_private_message": True,
            "webhook_public_url": "",
            "webhook_mp_api_key": "",
            "webhook_test_now": False,
        }
        return form, defaults

    def _format_reward(self, value: Any) -> str:
        """格式化论坛签到奖励。"""
        if value is None:
            return '—'
        try:
            num = float(value)
            if num == int(num):
                return str(int(num))
            else:
                return f'{round(num, 3):g}'
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _format_bytes(value: Any) -> str:
        """Format forum byte counters without losing precision."""
        try:
            number = int(str(value))
        except (TypeError, ValueError):
            return '—'
        if number < 0:
            return '—'
        units = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB')
        amount = float(number)
        unit = 0
        while amount >= 1024 and unit < len(units) - 1:
            amount /= 1024
            unit += 1
        return f'{amount:.2f}'.rstrip('0').rstrip('.') + f' {units[unit]}'

    def get_page(self) -> List[dict]:
        """保留原插件的信息密度，以 API Key 缓存渲染档案卡、能力画像、勋章、月历和历史。

        页面只读本地缓存，不因打开页面请求论坛；勋章过多时在固定高度区域内滚动。
        """
        history = [item for item in (self.get_data("history") or []) if isinstance(item, dict)]
        status = self._get_cached_status()
        account = status.get("account") if isinstance(status.get("account"), dict) else None
        check_in = status.get("checkIn") if isinstance(status.get("checkIn"), dict) else {}
        snapshot = self.get_data("last_push_result") or {}
        if not isinstance(snapshot, dict):
            snapshot = {}

        if account:
            by_day = {str(item.get("date") or "")[:10]: item for item in history if str(item.get("date") or "")[:10]}
            for item in account.get("recentCheckIns", []) if isinstance(account.get("recentCheckIns"), list) else []:
                if not isinstance(item, dict):
                    continue
                day = str(item.get("date") or "")[:10]
                if not day:
                    continue
                by_day[day] = {
                    **by_day.get(day, {}),
                    "date": str(by_day.get(day, {}).get("date") or day),
                    "status": "补签" if item.get("isMakeUp") else "已签到",
                    "reward": _safe_nonnegative_int(item.get("reward")),
                    "failure_count": 0,
                    "forumVerified": True,
                }
            history = list(by_day.values())

        api_base = _resolve_api_base()

        def asset_url(value):
            if not isinstance(value, str) or not value.strip():
                return ""
            value = value.strip()
            if value.startswith("data:"):
                return ""
            if value.startswith(("http://", "https://")):
                source, target = urlparse(api_base), urlparse(value)
                if target.scheme not in {"http", "https"} or (source.scheme == "https" and target.scheme != "https"):
                    return ""
                return value
            return f"{api_base}/{value.lstrip('/')}"

        def fmt_iso(value):
            """ISO 时间转本地展示文本；解析失败时原样截断。"""
            if not value:
                return "—"
            try:
                parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
                if parsed.tzinfo:
                    parsed = parsed.astimezone(pytz.timezone(settings.TZ))
                return parsed.strftime("%Y-%m-%d %H:%M")
            except (TypeError, ValueError):
                return str(value)[:16]

        surface = "background-color: rgb(var(--v-theme-surface)); color: rgb(var(--v-theme-on-surface)); border: 1px solid rgba(var(--v-theme-on-surface), 0.12); border-radius: 8px;"
        glass = "background-color: rgba(var(--v-theme-surface), 0.72); color: rgb(var(--v-theme-on-surface)); border: 1px solid rgba(var(--v-theme-on-surface), 0.10); border-radius: 10px;"

        def xml_escape(value):
            return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

        def build_radar_svg(dimensions):
            """与论坛 UserProfileRadarPanel 完全一致的六维雷达 SVG（论坛浅色主题色值）。"""
            size = 198
            center = size / 2.0
            radius = 56.0
            label_radius = 62.0
            total = len(dimensions)

            def radar_point(index, distance):
                angle = (-math.pi / 2.0) + ((math.pi * 2.0 * index) / total)
                return angle, center + math.cos(angle) * distance, center + math.sin(angle) * distance

            def to_points(points):
                return " ".join(f"{x:.2f},{y:.2f}" for _, x, y in points)

            parts = []
            for level in range(1, 5):
                ring_radius = radius * (level / 4.0)
                ring_points = [radar_point(i, ring_radius) for i in range(total)]
                fill = ' fill="#f5f5f5" fill-opacity="0.35"' if level == 4 else ' fill="none"'
                parts.append(f'<polygon points="{to_points(ring_points)}" stroke="#e0e0e0" stroke-width="0.9"{fill}/>')
            for i in range(total):
                _, x, y = radar_point(i, radius)
                parts.append(f'<line x1="{center:.2f}" y1="{center:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="#e0e0e0" stroke-width="0.9"/>')
            value_points = []
            for i, dimension in enumerate(dimensions[:total]):
                score = min(max(_safe_nonnegative_int(dimension.get("score")), 0), 10)
                value_points.append(radar_point(i, (score / 10.0) * radius))
            parts.append(f'<polygon points="{to_points(value_points)}" fill="#141414" fill-opacity="0.08" stroke="#141414" stroke-width="1.5"/>')
            for _, x, y in value_points:
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="#ffffff" stroke="#141414" stroke-width="1.4"/>')
            parts.append(f'<circle cx="{center:.2f}" cy="{center:.2f}" r="6" fill="#ffffff" stroke="#e0e0e0" stroke-width="0.9"/>')
            for i, dimension in enumerate(dimensions[:total]):
                angle, x, y = radar_point(i, label_radius)
                anchor = "middle" if abs(math.cos(angle)) < 0.2 else "start" if math.cos(angle) > 0 else "end"
                vertical_offset = 8 if math.sin(angle) > 0.85 else -3 if math.sin(angle) < -0.85 else 2
                label = f"{xml_escape(dimension.get('label') or '—')} {_safe_nonnegative_int(dimension.get('displayScore', dimension.get('score')))}"
                parts.append(f'<text x="{x:.2f}" y="{y + vertical_offset:.2f}" text-anchor="{anchor}" fill="#6b6b6b" font-size="10" font-weight="600">{label}</text>')
            return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">' + "".join(parts) + "</svg>"

        def stat(icon, label, value, color=None, cols=6, md=None):
            props = {"cols": cols, "class": "pa-1"}
            if md is not None:
                props["md"] = md
            icon_props = {"size": 15, "class": "flex-shrink-0", "style": f"color: {color};" if color else "color: rgb(var(--v-theme-primary));"}
            return {"component": "VCol", "props": props, "content": [
                {"component": "div", "props": {"class": "d-flex flex-column align-center justify-center pa-1", "style": glass}, "content": [
                    {"component": "div", "props": {"class": "d-flex align-center justify-center ga-1"}, "content": [
                        {"component": "VIcon", "props": icon_props, "text": icon},
                        {"component": "span", "props": {"class": "text-subtitle-2 font-weight-bold", "style": "line-height: 1.15;"}, "text": str(value)},
                    ]},
                    {"component": "div", "props": {"class": "text-caption text-medium-emphasis mt-1", "style": "line-height: 1.2;"}, "text": label},
                ]},
            ]}

        def section_title(icon, text, extra=None):
            return {"component": "div", "props": {"class": "d-flex align-center mb-2"}, "content": [
                {"component": "VIcon", "props": {"size": "small", "class": "mr-2", "style": "color: rgb(var(--v-theme-primary));"}, "text": icon},
                {"component": "span", "props": {"class": "font-weight-bold"}, "text": text},
                {"component": "VSpacer"},
                *([extra] if extra else []),
            ]}

        now = datetime.now()
        month_key = now.strftime("%Y-%m")
        signed_days = {}
        for record in history:
            date_text = str(record.get("date") or "")
            if not date_text.startswith(month_key):
                continue
            try:
                day = int(date_text[:10].split("-")[2])
            except (ValueError, IndexError):
                continue
            raw_status = str(record.get("status") or "")
            tone = "error" if "失败" in raw_status else "info" if "已签到" in raw_status or "补签" in raw_status else "success"
            signed_days[day] = {"tone": tone, "reward": self._format_reward(record.get("reward", record.get("lastCheckinMoney", record.get("money", 0))))}

        calendar_rows = [{"component": "div", "props": {"class": "d-flex justify-space-between mb-1"}, "content": [
            {"component": "div", "props": {"class": "text-caption text-center text-medium-emphasis", "style": "width: 14.285%;"}, "text": label}
            for label in ["日", "一", "二", "三", "四", "五", "六"]
        ]}]
        for week in calendar.Calendar(firstweekday=6).monthdayscalendar(now.year, now.month):
            cells = []
            for day in week:
                if day == 0:
                    cells.append({"component": "div", "props": {"style": "width: 14.285%; height: 38px;"}})
                    continue
                item = signed_days.get(day)
                tone = item.get("tone") if item else None
                day_style = "width: 30px; height: 34px; border-radius: 6px; border: 1px solid rgba(var(--v-theme-on-surface), 0.10);"
                if tone:
                    day_style += f" background-color: rgba(var(--v-theme-{tone}), 0.12); color: rgb(var(--v-theme-{tone})); border-color: rgba(var(--v-theme-{tone}), 0.28);"
                elif day == now.day:
                    day_style += " border-color: rgb(var(--v-theme-primary));"
                content = [{"component": "div", "props": {"class": "text-caption", "style": "line-height: 1;"}, "text": str(day)}]
                reward = item.get("reward") if item else ""
                if reward and reward not in {"0", "—"}:
                    content.append({"component": "div", "props": {"class": "font-weight-bold", "style": "font-size: 9px; line-height: 1; white-space: nowrap;"}, "text": f"+{reward}"})
                cells.append({"component": "div", "props": {"class": "d-flex align-center justify-center", "style": "width: 14.285%; height: 38px;"}, "content": [
                    {"component": "div", "props": {"class": "d-flex flex-column align-center justify-center", "style": day_style}, "content": content},
                ]})
            calendar_rows.append({"component": "div", "props": {"class": "d-flex justify-space-between mb-1"}, "content": cells})

        update_time = status.get("cachedAt") or self.get_data("last_push_time") or ""
        calendar_panel = {"component": "div", "props": {"class": "pa-3", "style": f"{surface} height: 100%;"}, "content": [
            {"component": "div", "props": {"class": "d-flex align-center mb-2"}, "content": [
                {"component": "VIcon", "props": {"size": "small", "class": "mr-2", "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-calendar-month-outline"},
                {"component": "span", "props": {"class": "font-weight-bold"}, "text": f"{now.year} 年 {now.month} 月"},
                {"component": "VSpacer"},
                {"component": "span", "props": {"class": "text-caption text-medium-emphasis"}, "text": f"{len(signed_days)} 天 · 连签 {check_in.get('currentStreak', 0)}"},
            ]},
            {"component": "VDivider", "props": {"class": "mb-2"}},
            *calendar_rows,
            {"component": "div", "props": {"class": "d-flex justify-center flex-wrap ga-2 mt-2"}, "content": [
                {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "success"}, "text": "成功"},
                {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "info"}, "text": "已签 / 补签"},
                {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "error"}, "text": "未签"},
                {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "default"}, "text": "无数据"},
            ]},
            {"component": "div", "props": {"class": "text-caption text-medium-emphasis mt-2", "style": "text-align: right;"}, "text": f"数据更新：{fmt_iso(update_time)}"},
        ]}


        identity_block = None
        stat_cards = []
        radar_items = []
        radar_img = ""
        badge_panels = []
        badge_count = 0
        account_state = "等待同步"

        if account:
            display_name = str(account.get("displayName") or account.get("username") or "蜂巢用户")
            username = str(account.get("username") or "—")
            avatar = asset_url(account.get("avatarPath"))
            avatar_content = [{"component": "VImg", "props": {"src": avatar, "alt": display_name, "cover": True}}] if avatar else [{"component": "VIcon", "props": {"size": 46, "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-account"}]
            account_state = "圈内用户" if status.get("ptCircle") else "MP 已接通" if status.get("active") else "等待同步"

            level = _safe_nonnegative_int(account.get("level"))
            level_name = str(account.get("levelName") or "")
            level_icon = str(account.get("levelIcon") or "⭐")
            vip_level = _safe_nonnegative_int(account.get("vipLevel"))
            uid = str(account.get("uid") or "") or "—"
            joined_at = fmt_iso(account.get("joinedAt"))
            last_login = fmt_iso(account.get("lastLoginAt"))

            badge_items = [item for item in (account.get("badges") if isinstance(account.get("badges"), list) else []) if isinstance(item, dict)]
            badge_items = sorted(badge_items, key=lambda b: str(b.get("category") or "").strip() or "社区成就")
            badge_count = len(badge_items)
            radar_items = [item for item in (account.get("radar") if isinstance(account.get("radar"), list) else []) if isinstance(item, dict)][:6]
            if radar_items:
                radar_img = "data:image/svg+xml;base64," + base64.b64encode(build_radar_svg(radar_items).encode("utf-8")).decode("ascii")

            name_chips = [
                {"component": "VChip", "props": {"size": "small", "variant": "tonal", "color": "primary", "class": "mr-1 mb-1", "title": "论坛等级"}, "text": f"{level_icon} Lv.{level} {level_name}".strip()},
            ]
            if vip_level > 0:
                name_chips.append({"component": "VChip", "props": {"size": "small", "variant": "tonal", "color": "purple", "class": "mr-1 mb-1", "title": "VIP 等级"}, "content": [
                    {"component": "VIcon", "props": {"size": 14, "class": "mr-1"}, "text": "mdi-crown"},
                    {"component": "span", "text": f"VIP {vip_level}"},
                ]})
            name_chips.append({"component": "VChip", "props": {"size": "small", "variant": "tonal", "color": "primary", "class": "mr-1 mb-1"}, "text": account_state})

            def info_chip(icon, color, text, title):
                return {"component": "VChip", "props": {"size": "small", "variant": "outlined", "class": "mr-1 mb-1", "title": title, "color": color}, "content": [
                    {"component": "VIcon", "props": {"size": 14, "class": "mr-1", "style": f"color: {color};"}, "text": icon},
                    {"component": "span", "props": {"class": "text-caption"}, "text": text},
                ]}

            info_chips = [
                info_chip("mdi-identifier", "#7c3aed", f"UID {uid}", "用户 UID"),
                info_chip("mdi-calendar-account", "#16a34a", f"注册 {joined_at}", "注册时间"),
                info_chip("mdi-clock-outline", "#2563eb", f"最后访问 {last_login}", "最后访问"),
                info_chip("mdi-medal-outline", "#ea580c", f"勋章 {badge_count}", "勋章总数"),
            ]

            identity_block = [
                {"component": "div", "props": {"class": "d-flex flex-column pa-3", "style": f"{glass} height: 100%;"}, "content": [
                    {"component": "div", "props": {"class": "d-flex align-center ga-4"}, "content": [
                        {"component": "VAvatar", "props": {"size": 84, "color": "surface-variant", "class": "flex-shrink-0"}, "content": avatar_content},
                        {"component": "div", "props": {"class": "min-w-0"}, "content": [
                            {"component": "div", "props": {"class": "text-h5 font-weight-bold", "style": "overflow-wrap: anywhere;"}, "text": display_name},
                            {"component": "div", "props": {"class": "text-caption text-medium-emphasis mt-1"}, "text": f"@{username}"},
                            {"component": "div", "props": {"class": "d-flex flex-wrap align-center mt-2"}, "content": name_chips},
                        ]},
                    ]},
                    {"component": "div", "props": {"class": "d-flex flex-wrap mt-auto pt-3"}, "content": info_chips},
                ]},
            ]

            stat_cards = [
                stat("mdi-coins", "积分", account.get("points", "—"), "#0d9488"),
                stat("mdi-file-document-outline", "主题", account.get("postCount", "—"), "#4f46e5"),
                stat("mdi-message-reply-outline", "回复", account.get("commentCount", "—"), "#0891b2"),
                stat("mdi-star-outline", "收藏", account.get("favoriteCount", "—"), "#9333ea"),
                stat("mdi-thumb-up-outline", "获赞", account.get("likeReceivedCount", "—"), "#db2777"),
                stat("mdi-account-heart-outline", "粉丝", account.get("followerCount", "—"), "#14b8a6"),
            ]

            grouped = {}
            for badge in badge_items:
                cat = str(badge.get("category") or "").strip() or "社区成就"
                grouped.setdefault(cat, []).append(badge)
            if grouped:
                columns = [[] for _ in range(3)]
                col_heights = [0.0] * 3
                for cat, items in grouped.items():
                    badge_cells = []
                    for badge in items:
                        icon_path = asset_url(badge.get("imageUrl")) or asset_url(badge.get("iconPath"))
                        if icon_path:
                            icon = {"component": "VImg", "props": {"src": icon_path, "alt": str(badge.get("name") or "勋章"), "width": 40, "height": 40, "contain": True}}
                        elif badge.get("iconText"):
                            icon_text = str(badge.get("iconText"))
                            if icon_text.startswith(("http://", "https://", "//")):
                                icon = {"component": "VIcon", "props": {"size": 32, "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-medal-outline"}
                            else:
                                icon = {"component": "span", "props": {"style": "font-size: 26px; line-height: 1;"}, "text": icon_text}
                        else:
                            icon = {"component": "VIcon", "props": {"size": 32, "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-medal-outline"}
                        badge_cells.append({"component": "div", "props": {"class": "d-flex flex-column align-center justify-start", "style": "box-sizing: border-box; padding: 6px 4px; border-radius: 8px; border: 1px solid rgba(var(--v-theme-on-surface), 0.10); overflow: hidden; flex: 1 1 76px; min-width: 76px;", "title": str(badge.get("description") or badge.get("name") or "勋章")}, "content": [
                            {"component": "div", "props": {"class": "d-flex align-center justify-center flex-shrink-0", "style": "width: 40px; height: 40px;"}, "content": [icon]},
                            {"component": "div", "props": {"class": "text-center", "style": "font-size: 11px; line-height: 1.25; margin-top: 3px; max-width: 100%; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; word-break: break-all;"}, "text": str(badge.get("name") or "勋章")},
                        ]})
                    card = {"component": "div", "props": {"style": f"{glass} padding: 10px;", "title": cat}, "content": [
                        {"component": "div", "props": {"class": "text-caption text-medium-emphasis mb-1"}, "text": f"{cat} · {len(items)}"},
                        {"component": "div", "props": {"class": "d-flex flex-wrap ga-2"}, "content": badge_cells},
                    ]}
                    idx = min(range(3), key=lambda i: col_heights[i])
                    columns[idx].append(card)
                    col_heights[idx] += 26 + 20 + 12 + ((len(items) + 1) // 2) * 78 + ((len(items) + 1) // 2 - 1) * 8
                badge_panels = [{"component": "div", "props": {"class": "d-flex flex-column", "style": "flex: 1 1 240px; min-width: 240px; gap: 12px;"}, "content": col} for col in columns]
        else:
            identity_block = [
                {"component": "div", "props": {"class": "d-flex align-center ga-3 pa-3", "style": f"{glass} height: 100%;"}, "content": [
                    {"component": "VAvatar", "props": {"size": 64, "color": "surface-variant"}, "content": [{"component": "VIcon", "props": {"size": 34, "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-hexagon-multiple-outline"}]},
                    {"component": "div", "content": [{"component": "div", "props": {"class": "text-h6 font-weight-bold"}, "text": "蜂巢"}, {"component": "div", "props": {"class": "text-caption text-medium-emphasis"}, "text": "等待 MP 专用 Key 完成首次连接"}]},
                ]},
            ]

        radar_panel = {"component": "div", "props": {"style": f"{glass} position: absolute; top: 4px; right: 4px; bottom: 4px; left: 4px; overflow: hidden;"}, "content": [
            {"component": "div", "props": {"class": "d-flex align-center", "style": "position: absolute; top: 8px; left: 10px; z-index: 1; padding: 2px 8px; border-radius: 99px; background-color: rgba(var(--v-theme-surface), 0.78); border: 1px solid rgba(var(--v-theme-on-surface), 0.10);"}, "content": [
                {"component": "VIcon", "props": {"size": "small", "class": "mr-1", "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-radar"},
                {"component": "span", "props": {"class": "font-weight-bold", "style": "font-size: 12px;"}, "text": "能力画像"},
            ]},
            {"component": "div", "props": {"class": "d-flex justify-center align-center", "style": "height: 100%; min-height: 0;"}, "content": [
                {"component": "VImg", "props": {"src": radar_img, "alt": "能力画像", "width": "100%", "height": "100%", "contain": True, "max-width": "100%", "max-height": "100%"}} if radar_img else {"component": "div", "props": {"class": "text-caption text-medium-emphasis text-center"}, "text": "完成首次连接后展示六维画像"},
            ]},
        ]}

        # 第一行：身份区 + 能力画像（雷达） + 论坛数据（紧凑统计卡）
        main_content = [{"component": "VRow", "props": {"class": "ma-0"}, "content": [
            {"component": "VCol", "props": {"cols": 12, "md": 4, "class": "pa-3"}, "content": identity_block},
            {"component": "VCol", "props": {"cols": 12, "md": 4, "class": "pa-3", "style": "position: relative;"}, "content": [radar_panel]},
            {"component": "VCol", "props": {"cols": 12, "md": 4, "class": "pa-3"}, "content": [
                {"component": "div", "props": {"class": "d-flex flex-column pa-3", "style": f"{glass} height: 100%;"}, "content": [
                    section_title("mdi-chart-box-outline", "论坛数据"),
                    {"component": "div", "props": {"class": "d-flex flex-grow-1 flex-column justify-center"}, "content": [
                        {"component": "VRow", "props": {"dense": True, "class": "mx-n1"}, "content": stat_cards},
                    ]},
                ]},
            ]},
        ]}]

        # 第二行：勋章（左，可能很多，限高滚动，占更宽） + 签到日历（右，与雷达同宽）
        main_content.append({"component": "VRow", "props": {"class": "ma-0"}, "content": [
            {"component": "VCol", "props": {"cols": 12, "md": 8, "class": "pa-3"}, "content": [
                section_title("mdi-medal-outline", "我的勋章", {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "primary"}, "text": f"{badge_count} 枚"}),
                {"component": "div", "props": {"class": "d-flex flex-wrap align-start", "style": "gap: 12px; max-height: 340px; overflow-y: auto; scrollbar-width: thin; padding-right: 4px;"}, "content": badge_panels or [
                    {"component": "div", "props": {"class": "text-caption text-medium-emphasis"}, "text": "完成首次连接后展示论坛勋章"},
                ]},
            ]},
            {"component": "VCol", "props": {"cols": 12, "md": 4, "class": "pa-3"}, "content": [calendar_panel]},
        ]})

        if snapshot:
            main_content.extend([
                {"component": "VDivider"},
                {"component": "div", "props": {"class": "pa-3"}, "content": [
                    {"component": "div", "props": {"class": "d-flex align-center flex-wrap ga-2 mb-2"}, "content": [
                        {"component": "VIcon", "props": {"size": "small", "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-chart-box-outline"},
                        {"component": "span", "props": {"class": "font-weight-bold"}, "text": "PT 人生"},
                        {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "primary"}, "text": f"{snapshot.get('siteCount', 0)} 个站点"},
                        {"component": "VSpacer"},
                        {"component": "span", "props": {"class": "text-caption text-medium-emphasis"}, "text": f"同步于 {self.get_data('last_push_time') or '—'}"},
                    ]},
                    {"component": "VRow", "props": {"dense": True, "class": "mx-n1"}, "content": [
                        stat("mdi-upload", "上传", self._format_bytes(snapshot.get("totalUpload", "0")), "#10b981", md=3),
                        stat("mdi-download", "下载", self._format_bytes(snapshot.get("totalDownload", "0")), "#3b82f6", md=3),
                        stat("mdi-swap-vertical-bold", "分享率", snapshot.get("ratio", "—"), "#f59e0b", md=2),
                        stat("mdi-seed-outline", "做种", snapshot.get("totalSeeding", 0), "#14b8a6", md=2),
                        stat("mdi-database-outline", "做种体积", self._format_bytes(snapshot.get("totalSeedingSize", "0")), "#8b5cf6", md=2),
                    ]},
                ]},
            ])

        components = [
            {
                "component": "VCard",
                "props": {"variant": "outlined", "class": "mb-4", "style": surface},
                "content": [
                    {"component": "VCardText", "props": {"class": "pa-0"}, "content": main_content},
                ],
            },
        ]

        if not history:
            components.append({"component": "VAlert", "props": {"type": "info", "variant": "tonal", "density": "compact", "text": "暂无签到记录", "prepend-icon": "mdi-information-outline"}})
            return components

        history = sorted(history, key=lambda item: str(item.get("date") or ""), reverse=True)
        total = len(history)
        rows = []
        for record in history[:90]:
            state = str(record.get("status") or "未知")
            tone = "error" if "失败" in state else "info" if "已签到" in state or "补签" in state else "success"
            rows.append({"component": "tr", "content": [
                {"component": "td", "props": {"style": "white-space: nowrap;"}, "text": str(record.get("date") or "")},
                {"component": "td", "content": [{"component": "VChip", "props": {"size": "small", "variant": "tonal", "color": tone}, "text": state}]},
                {"component": "td", "props": {"style": "white-space: nowrap;"}, "text": self._format_reward(record.get("reward", record.get("lastCheckinMoney", record.get("money", 0))))},
                {"component": "td", "content": [{"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "success" if record.get("forumVerified") else "secondary"}, "text": "论坛记录" if record.get("forumVerified") else "插件记录"}]},
                {"component": "td", "props": {"style": "white-space: nowrap;"}, "text": str(record.get("siteCount", "—"))},
            ]})
        components.append({"component": "VCard", "props": {"variant": "outlined", "class": "mb-4"}, "content": [
            {"component": "VCardTitle", "props": {"class": "d-flex align-center py-3"}, "content": [{"component": "VIcon", "props": {"size": "small", "class": "mr-2", "style": "color: rgb(var(--v-theme-primary));"}, "text": "mdi-history"}, {"component": "span", "props": {"class": "text-subtitle-1 font-weight-bold"}, "text": "签到记录"}, {"component": "VSpacer"}, {"component": "VChip", "props": {"size": "x-small", "variant": "tonal"}, "text": f"最近 {len(rows)} / 共 {total}"}]},
            {"component": "VDivider"},
            {"component": "div", "props": {"style": "max-height: 520px; overflow: auto; scrollbar-width: thin;"}, "content": [{"component": "VTable", "props": {"hover": True, "density": "comfortable", "fixed-header": True, "style": "min-width: 680px;"}, "content": [
                {"component": "thead", "content": [{"component": "tr", "content": [{"component": "th", "text": "时间"}, {"component": "th", "text": "状态"}, {"component": "th", "text": "奖励"}, {"component": "th", "text": "来源"}, {"component": "th", "text": "同步站点"}]}]},
                {"component": "tbody", "content": rows},
            ]}]},
        ]})
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

    def __check_and_push_mp_stats(self, hours=None, jitter=None):
        if not self._enabled or not self._mp_push_enabled or not self._api_key:
            return None
        # MoviePilot's interval service can start every installed plugin at
        # the same instant. Apply a bounded one-time offset per process so
        # the forum sees a naturally distributed request pattern.
        if jitter and not getattr(self, "_service_jitter_applied", False):
            self._service_jitter_applied = True
            delay = random.uniform(0, min(60, max(0, float(jitter))))
            if delay:
                time.sleep(delay)
        now = datetime.now()
        if self._last_push_time and self._mp_push_interval:
            try:
                last_push = datetime.strptime(self._last_push_time, "%Y-%m-%d %H:%M:%S")
                if (now - last_push).total_seconds() < int(self._mp_push_interval) * 86400:
                    # Keep the administrator resync path responsive even
                    # when the normal daily snapshot interval has not elapsed,
                    # but do not turn a short host interval into repeated forum
                    # polling. A 12-hour heartbeat is enough for admin actions.
                    if self._status_refresh_due():
                        try:
                            status = self._sync_if_requested(self.__api_request("GET", "/api/integrations/moviepilot/v1/status"))
                            self._notify_status_transition(status)
                        except Exception as status_error:
                            logger.debug(f"读取蜂巢同步请求失败：{status_error}")
                    return None
            except (TypeError, ValueError):
                pass
        try:
            result = self.__push_stats_with_retries(retry_count=0)
            try:
                self._notify_status_transition(self._sync_if_requested(self.__api_request("GET", "/api/integrations/moviepilot/v1/status")))
            except Exception as status_error:
                logger.warning(f"读取蜂巢 PT 资格状态失败: {status_error}")
            return result
        except Exception as exc:
            logger.error(f"蜂巢 PT 人生定时同步失败: {exc}")
            if self._notify:
                self._send_notification("【❌ 蜂巢 PT 人生同步失败】", f"同步失败：{exc}")
            return None
    def _get_site_statistics(self):
        """获取站点统计数据（参考站点统计插件实现）"""
        try:
            # 导入SiteOper类和SitesHelper
            from app.db.site_oper import SiteOper
            from app.helper.sites import SitesHelper
            site_oper, sites_helper = SiteOper(), SitesHelper()
            managed_sites = sites_helper.get_indexers()
            managed_site_names = [s.get("name") for s in managed_sites if s.get("name")]
            raw_data_list = site_oper.get_userdata()
            if not raw_data_list:
                logger.error("未获取到站点数据")
                return None
            data_dict = {f"{d.updated_day}_{d.name}": d for d in raw_data_list}
            data_list = sorted(list(data_dict.values()), key=lambda x: x.updated_day, reverse=True)
            site_names = set()
            latest_site_data = []
            for data in data_list:
                if data.name not in site_names and data.name in managed_site_names:
                    site_names.add(data.name)
                    latest_site_data.append(data)
            sites = []
            for site_data in latest_site_data:
                site_dict = site_data.to_dict() if hasattr(site_data, "to_dict") else site_data.__dict__
                if "_sa_instance_state" in site_dict: site_dict.pop("_sa_instance_state")
                sites.append(site_dict)
            return {"sites": sites}
        except Exception as e:
            logger.error(f"获取 MoviePilot 本地站点统计数据出错: {str(e)}")
            return None

"""
工具类模块
"""
import time
from datetime import datetime
from typing import Optional, Any

try:
    from app.sdk.events import eventmanager
except ImportError:
    from app.core.event import eventmanager
from app.schemas.types import NotificationType, EventType
try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger


class NotificationHelper:
    """
    通知助手类
    """
    
    def __init__(self, plugin):
        """
        初始化通知助手
        :param plugin: 插件实例
        """
        self.plugin = plugin
    
    def send_notification(self, title: str, text: str, notify_switch: bool = True, 
                          channel: str = None, image: str = None, force: bool = False):
        """
        发送通知
        :param title: 通知标题
        :param text: 通知内容
        :param notify_switch: 通知开关
        :param channel: 通知渠道
        :param image: 图片URL
        :param force: 是否强制发送（忽略通知开关）
        """
        # 如果通知开关关闭且不是强制发送，则不发送通知
        if not notify_switch and not force:
            return
        
        try:
            # 记录到日志
            logger.info(f"发送通知: {title}")
            
            # 仅使用事件管理器发送通知，不再使用plugin.post_message
            # 因为plugin.post_message会在refresh_all_sites中直接调用，这里只需记录日志
            # 避免在多处发送导致重复通知
            logger.debug(f"通知内容: {text}")
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")


class SiteHelper:
    """
    站点助手类
    """
    
    @staticmethod
    def format_timestamp(timestamp: int) -> str:
        """
        格式化时间戳为可读字符串
        :param timestamp: 时间戳
        :return: 格式化后的时间字符串
        """
        if not timestamp:
            return ""
        
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.error(f"格式化时间戳失败: {str(e)}")
            return str(timestamp)
    
    @staticmethod
    def is_cache_valid(last_update: int, cache_ttl: int = 21600) -> bool:
        """
        检查缓存是否有效
        :param last_update: 最后更新时间
        :param cache_ttl: 缓存有效期(秒)，默认6小时
        :return: 是否有效
        """
        if not last_update:
            return False
        
        current_time = int(time.time())
        return (current_time - last_update) < cache_ttl

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        格式化文件大小
        :param size_bytes: 字节数
        :return: 格式化后的大小字符串
        """
        try:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} PB"
        except:
            return "0 B"
    
    @staticmethod
    def is_nexusphp(site_url: str) -> bool:
        """
        判断是否为NexusPHP站点
        :param site_url: 站点URL
        :return: 是否为NexusPHP站点
        """
        return "php" in site_url.lower() 
import datetime
import hashlib
import os
import re
import threading
import traceback
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Set

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app import schemas
try:
    from app.sdk.config import settings
except ImportError:
    from app.core.config import settings
try:
    from app.sdk.events import eventmanager, Event
except ImportError:
    from app.core.event import eventmanager, Event
try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType, NotificationType
from app.utils.system import SystemUtils

lock = threading.Lock()


class smarthardlink(_PluginBase):
    # 插件名称
    plugin_name = "智能硬链接"
    # 插件描述
    plugin_desc = "通过计算文件SHA1，将指定目录中相同SHA1的文件只保留一个，其他的用硬链接替换，用来清理重复占用的磁盘空间。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/hardlink.png"
    # 插件版本
    plugin_version = "3.0.0"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays/MoviePilot-Plugins"
    # 插件配置项ID前缀
    plugin_config_prefix = "smarthardlink_"
    # 加载顺序
    plugin_order = 11
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _scheduler = None
    _enabled = False
    _onlyonce = False
    _cron = None
    _scan_dirs = ""
    _min_size = 1024  # 默认最小文件大小，单位KB
    _exclude_dirs = ""
    _exclude_extensions = ""
    _exclude_keywords = ""
    _hash_buffer_size = 65536  # 计算哈希时的缓冲区大小，默认64KB
    _dry_run = True  # 默认为试运行模式，不实际创建硬链接
    _hash_cache = {}  # 保存文件哈希值的缓存
    _process_count = 0  # 处理的文件计数
    _hardlink_count = 0  # 创建的硬链接计数
    _saved_space = 0  # 节省的空间统计，单位字节
    _skipped_hardlinks_count = 0 # 新增：跳过的已存在硬链接计数

    # 退出事件
    _event = threading.Event()

    def init_plugin(self, config: dict = None):
        """
        插件初始化
        """
        # --- 添加日志: 打印接收到的配置 ---
        logger.info(f"SmartHardlink init_plugin received config: {config}")
        # --- 日志结束 ---

        # 读取配置
        if config:
            self._enabled = config.get("enabled")
            self._onlyonce = config.get("onlyonce")
            self._cron = config.get("cron")
            self._scan_dirs = config.get("scan_dirs") or ""
            # --- 加固 min_size 加载逻辑 ---
            min_size_val = config.get("min_size")
            try:
                # 尝试转换为整数，如果值存在且非空
                self._min_size = int(min_size_val) if min_size_val else 1024
            except (ValueError, TypeError):
                # 如果转换失败或类型错误，使用默认值
                logger.warning(f"无法将配置中的 min_size '{min_size_val}' 解析为整数，使用默认值 1024")
                self._min_size = 1024
            # --- 加固结束 ---
            self._exclude_dirs = config.get("exclude_dirs") or ""
            self._exclude_extensions = config.get("exclude_extensions") or ""
            self._exclude_keywords = config.get("exclude_keywords") or ""
            # --- 加固 hash_buffer_size 加载逻辑 (类似处理) ---
            hash_buffer_size_val = config.get("hash_buffer_size")
            try:
                self._hash_buffer_size = int(hash_buffer_size_val) if hash_buffer_size_val else 65536
            except (ValueError, TypeError):
                logger.warning(f"无法将配置中的 hash_buffer_size '{hash_buffer_size_val}' 解析为整数，使用默认值 65536")
                self._hash_buffer_size = 65536
            # --- 加固结束 ---
            self._dry_run = bool(config.get("dry_run"))

        # 停止现有任务
        self.stop_service()

        if self._enabled or self._onlyonce:
            # 定时服务管理器
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)

            # 运行一次定时服务
            if self._onlyonce:
                logger.info("智能硬链接服务启动，立即运行一次")
                self._scheduler.add_job(
                    name="智能硬链接",
                    func=self.scan_and_process,
                    trigger="date",
                    run_date=datetime.datetime.now(tz=pytz.timezone(settings.TZ))
                    + datetime.timedelta(seconds=3),
                )
                # 关闭一次性开关
                self._onlyonce = False
                # 保存配置
                self.__update_config()

            # 启动定时服务
            if self._scheduler.get_jobs():
                self._scheduler.print_jobs()
                self._scheduler.start()

    def __update_config(self):
        """
        更新配置
        """
        self.update_config(
            {
                "enabled": self._enabled,
                "onlyonce": self._onlyonce,
                "cron": self._cron,
                "scan_dirs": self._scan_dirs,
                "min_size": self._min_size,
                "exclude_dirs": self._exclude_dirs,
                "exclude_extensions": self._exclude_extensions,
                "exclude_keywords": self._exclude_keywords,
                "hash_buffer_size": self._hash_buffer_size,
                "dry_run": self._dry_run,
            }
        )

    @eventmanager.register(EventType.PluginAction)
    def remote_scan(self, event: Event):
        """
        远程扫描处理
        """
        if event:
            event_data = event.event_data
            if not event_data or event_data.get("action") != "hardlink_scan":
                return
            self.post_message(
                channel=event.event_data.get("channel"),
                title="开始扫描目录并处理重复文件 ...",
                userid=event.event_data.get("user"),
            )
        
        # 记录开始时间
        start_time = datetime.datetime.now()
        
        # 执行扫描和处理
        self.scan_and_process()
        
        # 计算耗时
        elapsed_time = datetime.datetime.now() - start_time
        elapsed_seconds = elapsed_time.total_seconds()
        elapsed_formatted = self._format_time(elapsed_seconds)
        
        if event:
            # 发送美观的通知
            title = "【✅ 智能硬链接处理完成】"
            text = (
                f"📢 执行结果\n"
                f"━━━━━━━━━━\n"
                f"🕐 时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⏱️ 耗时：{elapsed_formatted}\n"
                f"📁 文件数：{self._process_count} 个\n"
                f"🔗 硬链接：{self._hardlink_count} 个\n"
                f"💾 节省空间：{self._format_size(self._saved_space)}\n"
                f"📊 处理模式：{'试运行' if self._dry_run else '实际运行'}\n"
                f"━━━━━━━━━━"
            )
            
            self.post_message(
                channel=event.event_data.get("channel"),
                mtype=NotificationType.SiteMessage,
                title=title,
                text=text,
                userid=event.event_data.get("user"),
            )

    @staticmethod
    def _format_time(seconds):
        """
        格式化时间显示
        """
        if seconds < 60:
            return f"{seconds:.1f} 秒"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{int(minutes)} 分 {int(remaining_seconds)} 秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{int(hours)} 小时 {int(minutes)} 分"

    @staticmethod
    def _format_size(size_bytes):
        """
        格式化文件大小显示
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def calculate_file_hash(self, file_path):
        """
        计算文件的SHA1哈希值
        """
        # 检查缓存
        if file_path in self._hash_cache:
            return self._hash_cache[file_path]

        try:
            hash_sha1 = hashlib.sha1()
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(self._hash_buffer_size)
                    if not data:
                        break
                    hash_sha1.update(data)
            
            file_hash = hash_sha1.hexdigest()
            # 保存到缓存
            self._hash_cache[file_path] = file_hash
            return file_hash
        except Exception as e:
            logger.error(f"计算文件 {file_path} 哈希值失败: {str(e)}")
            return None

    def is_excluded(self, file_path: str) -> bool:
        """
        检查文件是否应该被排除
        """
        # 检查排除目录
        if self._exclude_dirs:
            for exclude_dir in self._exclude_dirs.split("\n"):
                if exclude_dir and file_path.startswith(exclude_dir):
                    return True

        # 检查排除文件扩展名
        if self._exclude_extensions:
            file_ext = os.path.splitext(file_path)[1].lower()
            extensions = [f".{ext.strip().lower()}" for ext in self._exclude_extensions.split(",")]
            if file_ext in extensions:
                return True

        # 检查排除关键词
        if self._exclude_keywords:
            for keyword in self._exclude_keywords.split("\n"):
                if keyword and re.findall(keyword, file_path):
                    return True

        return False

    def _save_link_history(self, summary: Dict[str, Any]):
        """
        保存硬链接操作历史记录
        :param summary: 包含本次运行摘要信息的字典
        """
        try:
            # 读取现有历史，最多保留最近 100 条
            history = self.get_data('link_history') or []
            history.append(summary)
            # 保留最新的 N 条记录 (例如 100)
            max_history = 100
            if len(history) > max_history:
                history = history[-max_history:]
            self.save_data(key="link_history", value=history)
            logger.info(f"保存硬链接历史记录，当前共有 {len(history)} 条记录")
        except Exception as e:
            logger.error(f"保存硬链接历史记录失败: {str(e)}", exc_info=True)

    def scan_and_process(self):
        """
        扫描目录并处理重复文件
        """
        run_start_time = datetime.datetime.now() # Record start time for duration
        run_status = "失败" # Default status
        error_message = ""
        try:
            # 重置计数器
            self._process_count = 0
            self._hardlink_count = 0
            self._saved_space = 0
            self._hash_cache = {}
            self._skipped_hardlinks_count = 0 # 重置跳过计数
            
            logger.info("开始扫描目录并处理重复文件 ...")
            logger.warning("提醒：本插件仍处于开发试验阶段，请确保数据安全")
            
            if not self._scan_dirs:
                logger.error("未配置扫描目录，无法执行")
                run_status = "失败 (未配置目录)"
                error_message = "未配置扫描目录"
                # --- 在此处也保存历史记录 ---
                run_end_time = datetime.datetime.now()
                self._save_link_history({
                    "start_time": run_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "end_time": run_end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "duration": self._format_time((run_end_time - run_start_time).total_seconds()),
                    "status": run_status,
                    "processed_files": self._process_count,
                    "hardlinks_created": self._hardlink_count,
                    "skipped_hardlinks": self._skipped_hardlinks_count,
                    "space_saved": self._saved_space,
                    "space_saved_formatted": self._format_size(self._saved_space),
                    "mode": "试运行" if self._dry_run else "实际运行",
                    "error": error_message
                })
                # --- 历史保存结束 ---
                return
            
            scan_dirs = self._scan_dirs.split("\n")
            
            # 第一步：收集所有文件并计算哈希值
            file_hashes = {}  # {hash: [(file_path, file_size), ...]}
            all_files = []  # 存储所有符合条件的文件路径和大小
            
            # 首先收集所有文件信息，避免在遍历时计算哈希
            for scan_dir in scan_dirs:
                if not scan_dir or not os.path.exists(scan_dir):
                    logger.warning(f"扫描目录不存在: {scan_dir}")
                    continue
                    
                logger.info(f"扫描目录: {scan_dir}")
                file_count = 0
                
                try:
                    for root, dirs, files in os.walk(scan_dir):
                        # 定期报告进度
                        if file_count > 0 and file_count % 1000 == 0:
                            logger.info(f"目录 {scan_dir} 已发现 {file_count} 个文件")
                            
                        for file_name in files:
                            file_count += 1
                            file_path = os.path.join(root, file_name)
                            
                            # 跳过符号链接
                            if os.path.islink(file_path):
                                continue
                                
                            # 检查排除条件
                            if self.is_excluded(file_path):
                                continue
                                
                            try:
                                # 检查文件大小
                                file_size = os.path.getsize(file_path)
                                if file_size < self._min_size * 1024:  # 转换为字节
                                    continue
                                    
                                # 添加到待处理文件列表
                                all_files.append((file_path, file_size))
                                
                            except Exception as e:
                                logger.error(f"获取文件信息失败 {file_path}: {str(e)}")
                    
                    logger.info(f"目录 {scan_dir} 扫描完成，共发现 {file_count} 个文件")
                except Exception as e:
                    logger.error(f"扫描目录 {scan_dir} 时出错: {str(e)}")
            
            # 报告收集到的文件总数
            total_files = len(all_files)
            logger.info(f"符合条件的文件总数: {total_files}")
            
            # 根据文件大小排序，优先处理大文件，可以更快发现重复文件节省空间
            all_files.sort(key=lambda x: x[1], reverse=True)
            
            # 处理文件并计算哈希值
            for idx, (file_path, file_size) in enumerate(all_files):
                # 定期报告进度
                if idx > 0 and (idx % 100 == 0 or idx == total_files - 1):
                    logger.info(f"已处理 {idx}/{total_files} 个文件 ({(idx/total_files*100):.1f}%)")
                
                try:
                    # 计算哈希值
                    file_hash = self.calculate_file_hash(file_path)
                    if not file_hash:
                        continue
                        
                    # 记录文件信息
                    if file_hash not in file_hashes:
                        file_hashes[file_hash] = []
                    file_hashes[file_hash].append((file_path, file_size))
                    
                    self._process_count += 1
                except Exception as e:
                    logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
            
            # 找出重复文件的数量
            duplicate_count = sum(len(files) - 1 for files in file_hashes.values() if len(files) > 1)
            logger.info(f"发现 {duplicate_count} 个重复文件")
            
            # 没有重复文件时发送通知 and save history
            if duplicate_count == 0:
                logger.info("没有发现重复文件")
                run_status = "完成 (无重复)"
                notification_title = "【✅ 智能硬链接扫描完成】"
                notification_text = (
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"📁 已扫描：{self._process_count} 个文件\n"
                    f"🔍 结果：未发现重复文件\n"
                    f"━━━━━━━━━━"
                )
                self._send_notify_message(notification_title, notification_text)
                return
            
            # 第二步：处理重复文件
            processed_count = 0
            for file_hash, files in file_hashes.items():
                if len(files) <= 1:
                    continue  # 没有重复
                
                processed_count += len(files) - 1
                if processed_count % 10 == 0 or processed_count == duplicate_count:
                    logger.info(f"已处理 {processed_count}/{duplicate_count} 个重复文件 ({(processed_count/duplicate_count*100):.1f}%)")
                    
                # 按文件路径排序，保持第一个文件作为源文件
                files.sort(key=lambda x: x[0])
                source_file, source_size = files[0]
                
                logger.info(f"发现重复文件组 (SHA1: {file_hash}):")
                logger.info(f"  保留源文件: {source_file}")
                
                # --- 获取源文件的 inode 和设备号 ---
                try:
                    source_stat = os.stat(source_file)
                    source_inode = source_stat.st_ino
                    source_dev = source_stat.st_dev
                except OSError as e:
                    logger.error(f"  无法获取源文件 {source_file} 的状态信息: {e}，跳过此组")
                    continue
                # --- 获取结束 ---
                
                # 处理重复文件
                for dup_file, dup_size in files[1:]:
                    logger.info(f"  检查重复文件: {dup_file}")
                    
                    # --- 检查是否已是硬链接 ---
                    try:
                        dup_stat = os.stat(dup_file)
                        # 必须在同一设备上且 inode 相同
                        if dup_stat.st_dev == source_dev and dup_stat.st_ino == source_inode:
                            logger.info(f"  文件 {dup_file} 已是源文件的硬链接，跳过")
                            self._skipped_hardlinks_count += 1
                            continue # 跳过此文件，处理下一个重复文件
                    except OSError as e:
                        logger.warning(f"  无法获取重复文件 {dup_file} 的状态信息: {e}，继续尝试硬链接")
                    # --- 检查结束 ---
                    
                    if self._dry_run:
                        logger.info(f"  试运行模式：将创建从 {source_file} 到 {dup_file} 的硬链接")
                        self._hardlink_count += 1
                        self._saved_space += dup_size
                    else:
                        try:
                            # 创建临时备份文件名
                            temp_file = f"{dup_file}.temp_{int(time.time())}"
                            
                            # 重命名原文件为临时文件
                            os.rename(dup_file, temp_file)
                            
                            # 创建硬链接（保持原文件名）
                            os.link(source_file, dup_file)
                            
                            # 删除临时文件
                            os.remove(temp_file)
                            
                            logger.info(f"  已创建硬链接: {dup_file} -> {source_file}")
                            self._hardlink_count += 1
                            self._saved_space += dup_size
                        except Exception as e:
                            # 如果出错，尝试恢复原文件
                            if 'temp_file' in locals() and os.path.exists(temp_file):
                                try:
                                    if os.path.exists(dup_file):
                                        # 如果硬链接意外创建成功但后续步骤失败，先删除错误的硬链接
                                        try:
                                            dup_stat_after_link = os.stat(dup_file)
                                            if dup_stat_after_link.st_dev == source_dev and dup_stat_after_link.st_ino == source_inode:
                                                os.remove(dup_file)
                                        except OSError:
                                            pass # 如果获取状态或删除失败，继续尝试恢复
                                    os.rename(temp_file, dup_file)
                                    logger.error(f"  创建硬链接失败，已恢复原文件: {str(e)}")
                                except Exception as recover_err:
                                    logger.error(f"  创建硬链接失败且恢复原文件也失败: {str(recover_err)}，原文件位于: {temp_file}")
                            else:
                                logger.error(f"  创建硬链接失败: {str(e)}")
            
            mode_str = "试运行" if self._dry_run else "实际运行"
            logger.info(f"处理完成！({mode_str}模式) 共处理文件 {self._process_count} 个，创建硬链接 {self._hardlink_count} 个，节省空间 {self._format_size(self._saved_space)}")
            run_status = f"完成 ({mode_str})"

            # 发送通知
            self._send_completion_notification()
            
        except Exception as e:
            run_status = "失败"
            error_message = str(e)
            logger.error(f"扫描处理失败: {error_message}\n{traceback.format_exc()}")
            # 发送错误通知
            self._send_notify_message(
                title="【❌ 智能硬链接处理失败】",
                text=(
                    f"📢 执行结果\n"
                    f"━━━━━━━━━━\n"
                    f"🕐 时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"❌ 错误：{error_message}\n"
                    f"━━━━━━━━━━\n"
                    f"💡 可能的解决方法\n"
                    f"• 检查目录权限\n"
                    f"• 确认磁盘空间充足\n"
                    f"• 查看日志获取详细错误信息"
                )
            )
        finally:
            # --- 统一保存历史记录 (无论成功或失败) ---
            run_end_time = datetime.datetime.now()
            self._save_link_history({
                "start_time": run_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": run_end_time.strftime('%Y-%m-%d %H:%M:%S'),
                "duration": self._format_time((run_end_time - run_start_time).total_seconds()),
                "status": run_status,
                "processed_files": self._process_count,
                "hardlinks_created": self._hardlink_count, # Record count even in dry run
                "skipped_hardlinks": self._skipped_hardlinks_count, # 添加跳过计数
                "space_saved": self._saved_space,
                "space_saved_formatted": self._format_size(self._saved_space), # Record saved space even in dry run
                "mode": "试运行" if self._dry_run else "实际运行",
                "error": error_message
            })
            # --- 历史保存结束 ---

    def _send_completion_notification(self):
        """
        发送任务完成通知
        """
        # 构建通知内容
        if self._dry_run:
            title = "【✅ 智能硬链接扫描完成】"
            text = (
                f"📢 执行结果（试运行模式）\n"
                f"━━━━━━━━━━\n"
                f"🕐 时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📁 扫描文件：{self._process_count} 个\n"
                f"🔍 重复文件：{self._hardlink_count} 个\n"
                f"⏭️ 已跳过链接：{self._skipped_hardlinks_count} 个\n"
                f"💾 可节省空间：{self._format_size(self._saved_space)}\n"
                f"━━━━━━━━━━\n"
                f"⚠️ 这是试运行模式，没有创建实际硬链接\n"
                f"💡 在设置中关闭试运行模式可实际执行硬链接操作"
            )
        else:
            title = "【✅ 智能硬链接处理完成】"
            text = (
                f"📢 执行结果\n"
                f"━━━━━━━━━━\n"
                f"🕐 时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📁 扫描文件：{self._process_count} 个\n"
                f"🔗 已创建硬链接：{self._hardlink_count} 个\n"
                f"⏭️ 已跳过链接：{self._skipped_hardlinks_count} 个\n"
                f"💾 已节省空间：{self._format_size(self._saved_space)}\n"
                f"━━━━━━━━━━"
            )
        
        self._send_notify_message(title, text)

    def _send_notify_message(self, title, text):
        """
        发送通知消息
        """
        try:
            self.post_message(
                mtype=NotificationType.SiteMessage,
                title=title,
                text=text
            )
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        :return: 命令关键字、事件、描述、附带数据
        """
        return [
            {
                "cmd": "/hardlink_scan",
                "event": EventType.PluginAction,
                "desc": "智能硬链接扫描",
                "category": "",
                "data": {"action": "hardlink_scan"},
            }
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/hardlink_scan",
                "endpoint": self.api_scan,
                "methods": ["GET"],
                "summary": "智能硬链接扫描",
                "description": "扫描目录并处理重复文件",
            }
        ]

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        if self._enabled and self._cron:
            return [
                {
                    "id": "smarthardlink",
                    "name": "智能硬链接定时扫描服务",
                    "trigger": CronTrigger.from_crontab(self._cron),
                    "func": self.scan_and_process,
                    "kwargs": {},
                }
            ]
        return []

    def api_scan(self) -> schemas.Response:
        """
        API调用扫描处理
        """
        self.scan_and_process()
        return schemas.Response(success=True, data={
            "processed": self._process_count,
            "hardlinked": self._hardlink_count,
            "saved_space": self._saved_space,
            "saved_space_formatted": self._format_size(self._saved_space)
        })

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        # --- Reverting Switch style and making Alerts more compact --- 
        return [
            # --- Alerts with reduced margin ---
            {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {'cols': 12},
                        'content': [
                            {
                                'component': 'VAlert',
                                'props': {
                                    'type': 'info',
                                    'variant': 'tonal',
                                    'class': 'mb-2', # Reduced margin
                                    'density': 'compact', # Make alert denser
                                    'icon': 'mdi-information',
                                    'text': "硬链接要求源文件和目标文件必须在同一个文件系统/分区上，否则会创建失败。本插件硬链接过程会保持文件名不变，以防止做种报错。⚠️插件运行时间根据扫描文件体积大小而增长，会很久很久，不要着急"
                                },
                            }
                        ],
                    }
                ],
            },
            {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {'cols': 12},
                        'content': [
                            {
                                'component': 'VAlert',
                                'props': {
                                    'type': 'warning',
                                    'variant': 'tonal',
                                    'class': 'mb-3', # Reduced margin
                                    'density': 'compact', # Make alert denser
                                    'icon': 'mdi-alert',
                                    'text': "本插件仍处于开发试验阶段，不排除与其他监控类、硬链接类插件冲突，使用前请务必考虑好数据安全，如有损失，本插件概不负责。强烈建议先在不重要的目录进行测试。",
                                },
                            }
                        ],
                    }
                ],
            },
            # --- Basic Settings Section ---
            {
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'd-flex align-center text-h6 py-3'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-cog', 'color': 'primary', 'class': 'mr-2'}},
                            {'component': 'span', 'text': '基础设置'}
                        ]
                    },
                    {'component': 'VDivider'},
                    {
                        'component': 'VCardText',
                        'content': [
                            # Switches Row (Reverted style)
                            {
                                'component': 'VRow',
                                'class': 'align-center mb-2',
                                'content': [
                                    {
                                        'component': 'VCol',
                                        'props': {"cols": 12, "sm": 4},
                                        'content': [
                                            {
                                                'component': 'VSwitch',
                                                'props': {
                                                    'model': 'enabled',
                                                    'label': '启用插件',
                                                    'color': 'primary',
                                                    # 'inset': False, # Reverted
                                                    # 'hide-details': False # Reverted
                                                },
                                            }
                                        ],
                                    },
                                    {
                                        'component': 'VCol',
                                        'props': {"cols": 12, "sm": 4},
                                        'content': [
                                            {
                                                'component': 'VSwitch',
                                                'props': {
                                                    'model': 'onlyonce',
                                                    'label': '立即运行一次',
                                                    # 'inset': False,
                                                    # 'hide-details': False
                                                },
                                            }
                                        ],
                                    },
                                    {
                                        'component': 'VCol',
                                        'props': {"cols": 12, "sm": 4},
                                        'content': [
                                            {
                                                'component': 'VSwitch',
                                                'props': {
                                                    'model': 'dry_run',
                                                    'label': '试运行模式',
                                                    'hint': '开启后不实际创建链接', # Reverted to hint
                                                    # 'inset': False,
                                                    'persistent-hint': True
                                                },
                                            }
                                        ],
                                    },
                                ],
                            },
                            # Cron and Min Size Row (Removed dense)
                            {
                                'component': 'VRow',
                                'class': 'mb-2',
                                'content': [
                                     {
                                        'component': 'VCol',
                                        'props': {"cols": 12, "sm": 6},
                                        'content': [
                                            {
                                                'component': 'VCronField',
                                                'props': {
                                                    'model': 'cron',
                                                    'label': '定时扫描周期',
                                                    'placeholder': '5位cron表达式，留空关闭',
                                                    'variant': 'outlined' 
                                                },
                                            }
                                        ],
                                    },
                                    {
                                        'component': 'VCol',
                                        'props': {"cols": 12, "sm": 6},
                                        'content': [
                                            {
                                                'component': 'VTextField',
                                                'props': {
                                                    'model': 'min_size',
                                                    'label': '最小文件大小（KB）',
                                                    'placeholder': '1024',
                                                    'type': 'number',
                                                    'hint': '小于此大小的文件将被忽略',
                                                    'persistent-hint': True, 
                                                    'variant': 'outlined'
                                                },
                                            }
                                        ],
                                    },
                                ],
                            },
                            # Hash Buffer Size Row (Removed dense)
                            {
                                'component': 'VRow',
                                'class': 'mb-2',
                                'content': [
                                      {
                                        'component': 'VCol',
                                        'props': {'cols': 12},
                                        'content': [
                                            {
                                                'component': 'VTextField',
                                                'props': {
                                                    'model': 'hash_buffer_size',
                                                    'label': '哈希缓冲区大小（字节）',
                                                    'placeholder': '65536',
                                                    'type': 'number',
                                                    'hint': '计算文件哈希时每次读取的字节数。增大可加快I/O速度（需足够内存），减小可降低内存占用。建议默认65536 (64KB)。',
                                                    'persistent-hint': True,
                                                    # 'density': 'compact',
                                                    'variant': 'outlined'
                                                },
                                            }
                                        ],
                                    },
                                ]
                            },
                        ]
                    }
                ]
            },
            # --- Path Settings Section ---
            {
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'd-flex align-center text-h6 py-3'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-folder-settings-outline', 'color': 'primary', 'class': 'mr-2'}},
                            {'component': 'span', 'text': '路径设置'}
                        ]
                    },
                    {'component': 'VDivider'},
                    {
                        'component': 'VCardText',
                        'content': [
                             # Scan Dirs (Removed dense)
                            {
                                'component': 'VRow',
                                'class': 'mb-2',
                                'content': [
                                    {
                                        'component': 'VCol',
                                        'props': {"cols": 12},
                                        'content': [
                                            {
                                                'component': 'VTextarea',
                                                'props': {
                                                    'model': 'scan_dirs',
                                                    'label': '扫描目录',
                                                    'rows': 5,
                                                    'placeholder': '每行一个目录路径',
                                                    'prependInnerIcon': 'mdi-folder-search',
                                                    'variant': 'outlined'
                                                },
                                            }
                                        ],
                                    }
                                ],
                            },
                             # Exclude Dirs (Removed dense)
                            {
                                'component': 'VRow',
                                'class': 'mb-2',
                                'content': [
                                    {
                                        'component': 'VCol',
                                        'props': {"cols": 12},
                                        'content': [
                                            {
                                                'component': 'VTextarea',
                                                'props': {
                                                    'model': 'exclude_dirs',
                                                    'label': '排除目录',
                                                    'rows': 3,
                                                    'placeholder': '每行一个目录路径，排除这些目录及其子目录下的所有文件',
                                                    'prependInnerIcon': 'mdi-folder-remove',
                                                    'variant': 'outlined'
                                                },
                                            }
                                        ],
                                    }
                                ],
                            },
                        ]
                    }
                ]
            },
             # --- Exclusion Rules Section ---
            {
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'd-flex align-center text-h6 py-3'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-filter-variant-remove', 'color': 'primary', 'class': 'mr-2'}},
                            {'component': 'span', 'text': '排除规则'}
                        ]
                    },
                    {'component': 'VDivider'},
                    {
                        'component': 'VCardText',
                        'content': [
                            # Exclude Extensions (Removed dense)
                            {
                                'component': 'VRow',
                                'class': 'mb-2',
                                'content': [
                                    {
                                        'component': 'VCol',
                                        'props': {"cols": 12},
                                        'content': [
                                            {
                                                'component': 'VTextField',
                                                'props': {
                                                    'model': 'exclude_extensions',
                                                    'label': '排除文件类型 (扩展名)',
                                                    'placeholder': 'jpg,png,gif,nfo',
                                                    'hint': '用逗号分隔，不带点，忽略大小写',
                                                    'persistent-hint': True,
                                                    # 'density': 'compact',
                                                    'variant': 'outlined'
                                                },
                                            }
                                        ],
                                    },
                                ]
                            },
                            # Exclude Keywords (Removed dense)
                            {
                                'component': 'VRow',
                                'class': 'mb-2',
                                'content': [
                                    {
                                        'component': 'VCol',
                                        'props': {
                                            'cols': 12,
                                        },
                                        'content': [
                                            {
                                                'component': 'VTextarea',
                                                'props': {
                                                    'model': 'exclude_keywords',
                                                    'label': '排除路径包含关键词 (正则表达式)',
                                                    'rows': 2,
                                                    'placeholder': '每行一个正则表达式，例如 \\\\.partial$ 或 sample',
                                                    'hint': '匹配完整文件路径，区分大小写，支持正则',
                                                    'persistent-hint': True,
                                                    'variant': 'outlined'
                                                },
                                            }
                                        ],
                                    }
                                ],
                            }
                        ]
                    }
                ]
            },
            # --- Alerts are at the top ---
        ], {
            # Default values remain the same
            "enabled": False,
            "onlyonce": False,
            "dry_run": True,
            "cron": "",
            "scan_dirs": "",
            "min_size": 1024,
            "exclude_dirs": "",
            "exclude_extensions": "",
            "exclude_keywords": "",
            "hash_buffer_size": 65536,
        }

    def get_page(self) -> List[dict]:
        """
        构建插件详情页面，展示硬链接历史
        """
        # 获取历史记录
        historys = self.get_data('link_history') or []

        # 如果没有历史记录
        if not historys:
            return [
                {
                    'component': 'VAlert',
                    'props': {
                        'type': 'info',
                        'variant': 'tonal',
                        'text': '暂无硬链接操作记录',
                        'class': 'mb-2',
                        'prepend-icon': 'mdi-history'
                    }
                }
            ]

        # 按时间倒序排列历史
        historys = sorted(historys, key=lambda x: x.get("end_time", ""), reverse=True)

        # 构建历史记录表格行 (添加图标和颜色)
        history_rows = []
        for history in historys:
            # --- Status chip logic (unchanged) ---
            status_text = history.get("status", "未知")
            status_color = "info" # Default
            status_icon = "mdi-information"
            if "失败" in status_text:
                status_color = "error"
                status_icon = "mdi-close-circle"
            elif "完成" in status_text:
                 status_color = "success"
                 status_icon = "mdi-check-circle"
            error_text = history.get("error", "")

            # --- Mode chip logic ---
            mode_text = history.get("mode", "")
            mode_color = "grey" # Default
            mode_icon = "mdi-help-circle-outline"
            if mode_text == "试运行":
                mode_color = "info"
                mode_icon = "mdi-test-tube"
            elif mode_text == "实际运行":
                mode_color = "primary"
                mode_icon = "mdi-cogs"

            # --- Format other data (unchanged) ---
            space_saved_fmt = history.get("space_saved_formatted", "0 B")
            skipped_count = history.get("skipped_hardlinks", 0)
            processed_count = history.get("processed_files", 0)
            created_count = history.get("hardlinks_created", 0)
            duration_text = history.get("duration", "N/A")

            history_rows.append({
                'component': 'tr',
                'content': [
                    # 完成时间
                    {
                        'component': 'td',
                        'props': {'class': 'text-caption'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-calendar-check', 'size': 'x-small', 'class': 'mr-1', 'color': 'grey'}},
                            {'component': 'span', 'text': history.get("end_time", "N/A")}
                        ]
                    },
                    # 耗时
                    {
                        'component': 'td',
                        'props': {'class': 'text-caption'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-clock-outline', 'size': 'x-small', 'class': 'mr-1', 'color': 'grey'}},
                            {'component': 'span', 'text': duration_text}
                        ]
                    },
                    # 状态
                    {
                        'component': 'td',
                        'content': [
                             {
                                'component': 'VChip',
                                'props': {
                                    'color': status_color,
                                    'size': 'small',
                                    'variant': 'elevated', 
                                    'prepend-icon': status_icon
                                },
                                'text': status_text
                            },
                            {
                                'component': 'div',
                                'props': {'class': 'text-caption text-error mt-1'},
                                'text': error_text if error_text else ""
                            }
                        ]
                    },
                     # 模式
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'VChip', 
                                'props': {
                                    'color': mode_color,
                                    'size': 'small',
                                    'variant': 'outlined', # Use outlined for mode maybe?
                                    'prepend-icon': mode_icon
                                },
                                'text': mode_text
                            } if mode_text else {'component': 'span', 'text': 'N/A', 'class': 'text-caption'}
                        ]
                    },
                    # 处理文件数
                    {
                        'component': 'td',
                        'props': {'class': 'text-center text-caption'},
                        'content': [
                             {'component': 'VIcon', 'props': {'icon': 'mdi-file-document-multiple-outline', 'size': 'x-small', 'class': 'mr-1', 'color': 'grey'}},
                             {'component': 'span', 'text': str(processed_count)}
                        ]
                    },
                    # 创建链接数
                    {
                        'component': 'td',
                        'props': {'class': 'text-center text-caption'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-link-variant-plus', 'size': 'x-small', 'class': 'mr-1', 'color': 'success'}},
                            {'component': 'span', 'text': str(created_count)}
                        ]
                    },
                    # 已跳过链接数
                    {
                        'component': 'td',
                        'props': {'class': 'text-center text-caption'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-link-variant-off', 'size': 'x-small', 'class': 'mr-1', 'color': 'orange'}},
                            {'component': 'span', 'text': str(skipped_count)}
                        ]
                    },
                    # 节省空间
                    {
                        'component': 'td',
                        'props': {'class': 'text-caption'},
                        'content': [
                            {'component': 'VIcon', 'props': {'icon': 'mdi-content-save-outline', 'size': 'x-small', 'class': 'mr-1', 'color': 'green'}},
                            {'component': 'span', 'props': {'class': 'text-green-darken-1 font-weight-medium'}, 'text': space_saved_fmt} # Green text
                        ]
                    },
                ]
            })

        # --- 最终页面组装 (优化 VCardTitle 和 Table Header) ---
        return [
            {
                'component': 'VCard',
                'props': {'variant': 'outlined', 'class': 'mb-4'},
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {'class': 'd-flex align-center text-h6 py-3'},
                        'content': [
                             {
                                'component': 'VIcon',
                                'props': {'icon': 'mdi-history', 'class': 'mr-2', 'color': 'primary'},
                            },
                            {'component': 'span', 'text': '智能硬链接历史记录'}
                        ]
                    },
                    {
                        'component': 'VDivider'
                    },
                    {
                        'component': 'VCardText',
                        'props': {'class': 'pa-0'},
                        'content': [
                            {
                                'component': 'VTable',
                                'props': {
                                    'hover': True,
                                    'density': 'comfortable' 
                                },
                                'content': [
                                    # 表头 (Using text for icon AND props.color for color)
                                    {
                                        'component': 'thead',
                                        'content': [
                                            {
                                                'component': 'tr',
                                                'props': {'class': 'bg-grey-lighten-5'},
                                                'content': [
                                                    # --- Modified headers below ---
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'grey'}, 'text': 'mdi-calendar-check'}, # text + props.color
                                                                    {'component': 'span', 'text': '完成时间'}
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'grey'}, 'text': 'mdi-clock-outline'}, # text + props.color
                                                                    {'component': 'span', 'text': '耗时'}
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'grey'}, 'text': 'mdi-list-status'}, # text + props.color
                                                                    {'component': 'span', 'text': '状态'}
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'grey'}, 'text': 'mdi-cogs'}, # text + props.color
                                                                    {'component': 'span', 'text': '模式'}
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center justify-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'grey'}, 'text': 'mdi-file-document-multiple-outline'}, # text + props.color
                                                                    {'component': 'span', 'text': '处理'}
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center justify-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'success'}, 'text': 'mdi-link-variant-plus'}, # text + props.color
                                                                    {'component': 'span', 'text': '创建'}
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center justify-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'orange'}, 'text': 'mdi-link-variant-off'}, # text + props.color
                                                                    {'component': 'span', 'text': '跳过'}
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {'class': 'text-caption', 'style': 'white-space: nowrap; padding: 4px 8px;'},
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {'class': 'd-flex align-center'},
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'size': '14', 'class': 'mr-1', 'color': 'green'}, 'text': 'mdi-content-save-outline'}, # text + props.color
                                                                    {'component': 'span', 'text': '节省'}
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                    # --- End of modified headers ---
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
        退出插件
        """
        if self._scheduler:
            self._scheduler.remove_all_jobs()
            if self._scheduler.running:
                self._event.set()
                self._scheduler.shutdown()
                self._event.clear()
            self._scheduler = None 

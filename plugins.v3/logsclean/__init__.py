from datetime import datetime, timedelta
import os
from pydantic import BaseModel

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from app.utils.string import StringUtils
from app.helper.plugin import PluginHelper
try:
    from app.sdk.config import settings
except ImportError:
    from app.core.config import settings
try:
    from app.sdk.plugins import PluginManager
except ImportError:
    from app.core.plugin import PluginManager
from app.db.systemconfig_oper import SystemConfigOper
try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import SystemConfigKey
from app.schemas import NotificationType

import re


# --- Add Pydantic model for config ---
class LogsCleanConfig(BaseModel):
    enable: bool = False
    notify: bool = False
    cron: str = '30 3 * * *'
    rows: int = 300
    selected_ids: List[str] = []
    onlyonce: bool = False


# --- Plugin Class ---
class LogsClean(_PluginBase):
    # 插件名称
    plugin_name = "日志清理vue"
    # 插件描述
    plugin_desc = "定时清理插件产生的日志"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/clean.png"
    # 插件版本
    plugin_version = "3.0.0"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "logsclean_"
    # 加载顺序
    plugin_order = 50
    # 可使用的用户级别
    auth_level = 1

    _enable = False
    _cron = '30 3 * * *'
    _selected_ids: List[str] = []
    _rows = 300
    _notify = False
    _onlyonce = False

    _scheduler: Optional[BackgroundScheduler] = None
    _plugin_dir: Path = Path(__file__).parent

    def init_plugin(self, config: dict = None):
        self.stop_service()

        if config:
            self._enable = config.get('enable', False)
            self._selected_ids = config.get('selected_ids', [])
            self._rows = int(config.get('rows', 300))
            self._cron = config.get('cron', '30 3 * * *')
            self._notify = config.get('notify', False)
            self._onlyonce = config.get('onlyonce', False)
            
        # 定时服务
        self._scheduler = BackgroundScheduler(timezone=settings.TZ)
        
        # 正常启动定时任务
        if self._enable and self._cron:
            try:
                self._scheduler.add_job(func=self._task,
                                        trigger=CronTrigger.from_crontab(self._cron),
                                        name=self.plugin_name)
                logger.info(f"{self.plugin_name}: 已按 CRON '{self._cron}' 计划定时任务。")
            except Exception as err:
                logger.error(f"{self.plugin_name}: 定时任务配置错误: {err}")
        
        # 启动任务
        if self._scheduler.get_jobs():
            self._scheduler.print_jobs()
            self._scheduler.start()
        else:
            # Log if no jobs are scheduled
            logger.info(f"{self.plugin_name}: 没有计划任务需要启动。启动时配置: Enable={config.get('enable', False) if config else 'N/A'}, Cron='{self._cron}'")

    def _task(self, manual_run: bool = False, specific_plugin_id: str = None):
        log_prefix = f"{self.plugin_name}{' (手动)' if manual_run else ''}"
        logger.info(f"{log_prefix}: 开始执行清理任务...")

        # 如果指定了具体插件，则只清理该插件
        if specific_plugin_id:
            clean_plugin_ids = [specific_plugin_id]
            logger.info(f"{log_prefix}: 将只清理 {specific_plugin_id} 的日志")
        # 否则，使用配置中的插件列表或所有已安装插件
        elif self._selected_ids:
            clean_plugin_ids = self._selected_ids[:]
            logger.info(f"{log_prefix}: 将按配置清理 {len(clean_plugin_ids)} 个插件的日志")
        else:
            clean_plugin_ids = []
            try:
                # 获取所有已安装插件
                plugin_manager = PluginManager()
                local_plugin_instances = plugin_manager.get_local_plugins() or []
                
                # 明确标记日志
                logger.info(f"{log_prefix}: 开始获取已安装插件列表...")
                
                # 过滤出已安装的插件
                installed_plugins = [p for p in local_plugin_instances if getattr(p, 'installed', False)]
                
                # 获取插件ID并转为小写存储
                clean_plugin_ids = [getattr(p, 'id', '').lower() for p in installed_plugins if getattr(p, 'id', None)]
                # 去除空项
                clean_plugin_ids = [pid for pid in clean_plugin_ids if pid]
                
                logger.info(f"{log_prefix}: 未指定插件，将尝试清理所有 {len(clean_plugin_ids)} 个已安装插件的日志: {', '.join(clean_plugin_ids)}")
            except Exception as e:
                logger.error(f"{log_prefix}: 获取已安装插件列表失败: {e}")
                return {"status": "error", "message": f"获取已安装插件列表失败: {e}"}

        run_results = []
        total_cleaned_lines_this_run = 0
        processed_files = 0

        # 确保日志目录存在
        log_dir = settings.LOG_PATH / Path("plugins")
        if not log_dir.exists():
            logger.warning(f"{log_prefix}: 插件日志目录不存在: {log_dir}，尝试创建")
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"{log_prefix}: 创建插件日志目录失败: {e}")
                return {"status": "error", "message": f"创建插件日志目录失败: {e}"}

        # 记录将要处理的插件数量
        logger.info(f"{log_prefix}: 将处理 {len(clean_plugin_ids)} 个插件日志")

        # 检查是否需要获取所有日志文件
        get_all_logs = not clean_plugin_ids or specific_plugin_id is None
        
        # 如果是"清理全部"操作，则处理所有日志文件，包括特殊日志（如plugin.log）
        if get_all_logs and manual_run:
            try:
                # 获取插件日志目录下的所有日志文件
                all_log_files = list(log_dir.glob("*.log"))
                special_log_names = []
                
                # 检查是否有不在clean_plugin_ids中的日志文件
                for log_file in all_log_files:
                    log_name = log_file.stem.lower()
                    if log_name not in clean_plugin_ids:
                        special_log_names.append(log_name)
                
                if special_log_names:
                    logger.info(f"{log_prefix}: 发现特殊日志文件: {', '.join(special_log_names)}，将添加到清理列表")
                    clean_plugin_ids.extend(special_log_names)
            except Exception as e:
                logger.error(f"{log_prefix}: 获取所有日志文件失败: {e}")

        for plugin_id in clean_plugin_ids:
            if not plugin_id:
                logger.warning(f"{log_prefix}: 发现一个空的插件ID，跳过。")
                continue

            # 确保plugin_id是小写
            plugin_id = plugin_id.lower()
            log_path = log_dir / f"{plugin_id}.log"
            
            if not log_path.exists():
                logger.debug(f"{log_prefix}: {plugin_id} 日志文件不存在: {log_path}，跳过")
                continue

            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()

                original_lines = len(lines)
                rows_to_keep = int(self._rows)
                if rows_to_keep < 0: rows_to_keep = 0

                kept_lines = 0
                if rows_to_keep > 0:
                    top_lines = lines[-min(rows_to_keep, original_lines):]
                    kept_lines = len(top_lines)
                else:
                    top_lines = []
                    
                cleaned_lines = original_lines - kept_lines

                if cleaned_lines > 0:
                    with open(log_path, 'w', encoding='utf-8') as file:
                        file.writelines(top_lines)
                    logger.info(f"{log_prefix}: 已清理 {plugin_id}: 保留 {kept_lines}/{original_lines} 行，清理 {cleaned_lines} 行")
                    total_cleaned_lines_this_run += cleaned_lines
                    run_results.append({
                        'plugin_id': plugin_id,
                        'original_lines': original_lines,
                        'kept_lines': kept_lines,
                        'cleaned_lines': cleaned_lines
                    })
                    processed_files += 1
                else:
                    logger.debug(f"{log_prefix}: {plugin_id} 日志行数 ({original_lines}) 未超过保留行数 ({rows_to_keep})，无需清理")
            except Exception as e:
                logger.error(f"{log_prefix}: 处理 {plugin_id} 日志文件 {log_path} 时出错: {e}", exc_info=True)

        self.save_data('last_run_results', run_results)
        logger.info(f"{log_prefix}: 本次任务共处理 {processed_files} 个插件日志，清理 {total_cleaned_lines_this_run} 行")

        if total_cleaned_lines_this_run > 0 or processed_files > 0:
            try:
                history = self.get_data('cleaning_history') or []
                history.insert(0, {
                    'timestamp': datetime.now(tz=pytz.timezone(settings.TZ)).strftime('%Y-%m-%d %H:%M:%S'),
                    'total_plugins_processed': processed_files,
                    'total_lines_cleaned': total_cleaned_lines_this_run,
                })
                max_history = 10
                history = history[:max_history]
                self.save_data('cleaning_history', history)
                logger.info(f"{log_prefix}: 清理历史记录已更新，当前共 {len(history)} 条记录")
            except Exception as e:
                logger.error(f"{log_prefix}: 更新清理历史记录失败: {e}", exc_info=True)

        if self._notify and (total_cleaned_lines_this_run > 0 or processed_files > 0):
            try:
                title = "✅ 插件日志清理完成"
                text = (
                    f"🧹 清理任务已完成！{' (手动触发)' if manual_run else ''}\n"
                    f"--------------------\n"
                    f"⏱️ 时间: {datetime.now(tz=pytz.timezone(settings.TZ)).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"📁 处理插件: {processed_files} 个\n"
                    f"🗑️ 清理行数: {total_cleaned_lines_this_run} 行\n"
                    f"--------------------"
                )
                self.post_message(
                    mtype=NotificationType.SiteMessage,
                    title=title,
                    text=text
                )
                logger.info(f"{log_prefix}: 已发送清理完成通知")
            except Exception as e:
                logger.error(f"{log_prefix}: 发送清理通知失败: {e}", exc_info=True)

        logger.info(f"{log_prefix}: 清理任务执行完毕")
        return {"status": "completed", "processed_files": processed_files, "cleaned_lines": total_cleaned_lines_this_run}

    # --- 获取插件日志信息 ---
    def _get_plugins_logs_stats(self) -> List[Dict[str, Any]]:
        """获取所有插件日志的统计信息（大小、行数等）"""
        result = []
        try:
            # 获取已安装插件列表及其中文名称
            plugin_name_map = {}
            plugin_manager = PluginManager()
            local_plugin_instances = plugin_manager.get_local_plugins() or []
            installed_plugins = [p for p in local_plugin_instances if getattr(p, 'installed', False)]
            
            # 记录日志
            logger.info(f"{self.plugin_name}: 获取到 {len(installed_plugins)} 个已安装插件")
            
            # 构建ID到中文名的映射 - 同时以原始ID和小写ID为键
            installed_plugin_ids = []  # 用于过滤已删除插件日志
            for plugin in installed_plugins:
                plugin_id = getattr(plugin, 'id', None)
                plugin_name = getattr(plugin, 'plugin_name', plugin_id)
                if plugin_id and plugin_name:
                    plugin_name_map[plugin_id] = plugin_name
                    plugin_name_map[plugin_id.lower()] = plugin_name
                    installed_plugin_ids.append(plugin_id.lower())  # 收集已安装插件ID
            
            # 添加特殊日志文件的显示名称映射
            special_logs_map = {
                'plugin': '系统插件日志',
                'system': '系统日志',
                'main': '主程序日志',
                'error': '错误日志',
            }
            
            logger.info(f"{self.plugin_name}: 已构建插件名称映射，共 {len(plugin_name_map)} 项")

            # 扫描plugins目录下的所有日志文件
            log_dir = settings.LOG_PATH / Path("plugins")
            if not log_dir.exists():
                logger.warning(f"{self.plugin_name}: 插件日志目录不存在: {log_dir}")
                return []

            # 扫描所有日志文件 - 同时包括 *.log 和 *.log.* 分割日志
            all_log_files = []
            # 首先获取所有标准日志文件
            standard_logs = list(log_dir.glob("*.log"))
            all_log_files.extend(standard_logs)
            
            # 获取所有分割日志文件
            split_logs = list(log_dir.glob("*.log.*"))
            all_log_files.extend(split_logs)
            
            logger.info(f"{self.plugin_name}: 找到 {len(standard_logs)} 个标准日志文件，{len(split_logs)} 个分割日志文件")

            for log_file in all_log_files:
                file_name = log_file.name
                
                # 判断是否为分割日志
                is_split_log = bool(re.match(r"^.+\.log\.\d+$", file_name))
                
                if is_split_log:
                    # 分割日志文件: 提取基础插件ID
                    plugin_id = re.match(r"^(.+)\.log\.\d+$", file_name).group(1)
                    original_id = plugin_id  # 保留原始ID以便后续使用
                else:
                    # 标准日志文件: 直接获取stem
                    plugin_id = log_file.stem
                    original_id = plugin_id
                
                # 获取文件大小
                file_size = os.path.getsize(log_file)
                
                # 获取行数
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        lines_count = len(lines)
                except Exception as e:
                    logger.error(f"{self.plugin_name}: 读取日志文件 {log_file} 失败: {e}")
                    lines_count = -1
                
                # 获取插件中文名 - 先检查是否是特殊日志
                plugin_name = None
                
                # 检查是否是特殊日志文件
                if plugin_id.lower() in special_logs_map:
                    plugin_name = special_logs_map[plugin_id.lower()]
                else:
                    # 尝试用小写ID查找已安装插件的中文名
                    plugin_name = plugin_name_map.get(plugin_id) or plugin_name_map.get(plugin_id.lower())
                
                # 如果仍未找到名称，使用首字母大写的ID作为默认名称
                if not plugin_name:
                    plugin_name = plugin_id.capitalize()
                
                # 为分割日志文件添加序号标记
                if is_split_log:
                    split_num = re.match(r"^.+\.log\.(\d+)$", file_name).group(1)
                    plugin_name = f"{plugin_name} (分割{split_num}号)"

                # 过滤策略：对于已删除插件的日志，如果行数小于等于10，则不显示
                is_special_log = plugin_id.lower() in special_logs_map
                is_deleted_plugin = not is_special_log and not any(
                    plugin_id.lower() == p_id or plugin_id.lower().startswith(p_id) or p_id.startswith(plugin_id.lower())
                    for p_id in installed_plugin_ids
                )

                # 如果是已删除插件的日志且行数 <= 10，则跳过不显示
                if is_deleted_plugin and lines_count != -1 and lines_count <= 10:
                    logger.debug(f"{self.plugin_name}: 跳过已删除插件的少量日志: {plugin_id} (行数: {lines_count})")
                    continue

                # 生成结果项
                result.append({
                    "id": file_name.replace(".log", ""),  # 使用文件全名作为唯一ID
                    "name": plugin_name,
                    "size": file_size,
                    "lines_count": lines_count,
                    "path": str(log_file),
                    "is_special": is_special_log,
                    "is_split": is_split_log,
                    "original_id": original_id,  # 存储原始插件ID
                    "file_name": file_name  # 存储完整文件名
                })
                
                logger.debug(f"{self.plugin_name}: 处理日志文件 {file_name} -> 名称: {plugin_name}, 大小: {file_size}, 行数: {lines_count}, 是否分割: {is_split_log}")
            
            # 按名称排序，但将特殊日志放在前面，分割日志按序号排序
            result.sort(key=lambda x: (
                0 if x.get("is_special") else 1,  # 先特殊日志
                x.get("original_id", "").lower(),  # 然后按插件ID
                x.get("is_split", False),  # 先标准日志，后分割日志
                x.get("file_name", "")  # 最后按文件名排序
            ))
            
            logger.info(f"{self.plugin_name}: 获取插件日志信息完成，共 {len(result)} 个日志文件")
            return result
        except Exception as e:
            logger.error(f"{self.plugin_name}: 获取插件日志统计信息失败: {e}", exc_info=True)
            return []

    # --- 清理特定插件日志 ---
    def _clean_specific_plugin(self, payload: dict) -> Dict[str, Any]:
        """清理指定插件的日志"""
        plugin_id = payload.get("plugin_id")
        if not plugin_id:
            return {"status": "error", "message": "未指定插件ID"}
        
        if not self._enable:
            return {"status": "error", "message": "插件已禁用，无法执行清理"}
        
        try:
            # 调用_task方法，传入specific_plugin_id参数
            result = self._task(manual_run=True, specific_plugin_id=plugin_id)
            return {
                "status": "success", 
                "message": f"已完成清理 {plugin_id} 的日志",
                "result": result
            }
        except Exception as e:
            logger.error(f"{self.plugin_name}: 清理插件 {plugin_id} 日志失败: {e}", exc_info=True)
            return {"status": "error", "message": f"清理失败: {str(e)}"}

    @staticmethod
    def _get_installed_plugins():
        plugin_list = []
        try:
            plugin_manager = PluginManager()
            plugins = plugin_manager.get_local_plugins()
            
            logger.info(f"正在获取已安装插件列表...")
            
            installed_count = 0
            if plugins:
                for p in plugins:
                    if not getattr(p, 'installed', False) or not p.id:
                        continue
                        
                    installed_count += 1
                    # 获取插件中文名
                    plugin_name = getattr(p, 'plugin_name', None)
                    plugin_id = p.id
                    plugin_version = getattr(p, 'plugin_version', '未知')
                    
                    # 确保有正确的标题显示
                    display_title = f"{plugin_name or plugin_id} v{plugin_version}"
                    
                    plugin_list.append({
                        'title': display_title,
                        'value': plugin_id  # 使用原始ID作为value
                    })
                
            # 按title排序
            plugin_list.sort(key=lambda x: x.get('title', '').lower())
            
            logger.info(f"获取到 {installed_count} 个已安装插件，返回 {len(plugin_list)} 个有效插件数据")
            
        except Exception as e:
            logger.error(f"获取本地插件列表失败: {e}")
        return plugin_list

    def get_state(self) -> bool:
        return self._enable

    # --- Instance methods for API endpoints ---
    def _get_config(self) -> Dict[str, Any]:
        """API Endpoint: Returns current plugin configuration."""
        return {
            "enable": self._enable,
            "notify": self._notify,
            "cron": self._cron,
            "rows": self._rows,
            "selected_ids": self._selected_ids,
            "onlyonce": False  # 始终返回False
        }

    def _save_config(self, config_payload: dict) -> Dict[str, Any]:
        """API Endpoint: Saves plugin configuration. Expects a dict payload."""
        logger.info(f"{self.plugin_name}: 收到配置保存请求: {config_payload}")
        try:
            # Update instance variables directly from payload, defaulting to current values if key is missing
            self._enable = config_payload.get('enable', self._enable)
            self._notify = config_payload.get('notify', self._notify)
            self._cron = config_payload.get('cron', self._cron)
            self._rows = int(config_payload.get('rows', self._rows))
            self._selected_ids = config_payload.get('selected_ids', self._selected_ids)
            
            # 忽略onlyonce参数

            # Prepare config to save
            config_to_save = {
                "enable": self._enable,
                "notify": self._notify,
                "cron": self._cron,
                "rows": self._rows,
                "selected_ids": self._selected_ids,
                "onlyonce": False  # 始终设为False
            }
            
            # 保存配置
            self.update_config(config_to_save)
            
            # 重新初始化插件
            self.stop_service()
            self.init_plugin(self.get_config())
            
            logger.info(f"{self.plugin_name}: 配置已保存并通过 init_plugin 重新初始化。当前内存状态: enable={self._enable}")
            
            # 返回最终状态
            return {"message": "配置已成功保存", "saved_config": self._get_config()}

        except Exception as e:
            logger.error(f"{self.plugin_name}: 保存配置时发生错误: {e}", exc_info=True)
            # Return current in-memory config on error
            return {"message": f"保存配置失败: {e}", "error": True, "saved_config": self._get_config()}

    def _trigger_manual_clean(self) -> Dict[str, Any]:
        """API Endpoint: Triggers a manual clean task."""
        logger.info(f"{self.plugin_name}: 收到手动清理请求...")
        if not self._enable:
             logger.warning(f"{self.plugin_name}: 插件当前已禁用，无法执行手动清理。")
             return {"message": "插件已禁用，无法执行清理", "error": True}
        try:
            # 暂存原始配置
            original_selected_ids = self._selected_ids
            
            # 临时设置为空列表，强制清理所有插件
            self._selected_ids = []
            logger.info(f"{self.plugin_name}: 强制清理所有插件，暂时忽略配置中的插件列表")
            
            # 明确传递specific_plugin_id=None以清理所有插件
            result = self._task(manual_run=True, specific_plugin_id=None)
            
            # 恢复原始配置
            self._selected_ids = original_selected_ids
            
            return {"message": "清理任务已完成", "result": result}
        except Exception as e:
            logger.error(f"{self.plugin_name}: 手动清理任务失败: {e}", exc_info=True)
            return {"message": f"手动清理失败: {e}", "error": True}

    def _get_status(self) -> Dict[str, Any]:
        """API Endpoint: Returns current plugin status and history."""
        last_run = self.get_data('last_run_results') or []
        history = self.get_data('cleaning_history') or []
        next_run_time = None
        if self._scheduler and self._scheduler.running:
            jobs = self._scheduler.get_jobs()
            if jobs:
                next_run_time_dt = jobs[0].next_run_time
                if next_run_time_dt:
                     # Format with timezone explicitly if possible
                     try:
                         tz = pytz.timezone(settings.TZ)
                         localized_time = tz.localize(next_run_time_dt.replace(tzinfo=None)) # Assume naive, make aware
                         next_run_time = localized_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                     except Exception: # Fallback for any timezone issue
                         next_run_time = next_run_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    next_run_time = "无计划运行"
            else:
                 next_run_time = "无计划任务"
        else:
            if not self._enable: next_run_time = "插件已禁用"
            else: next_run_time = "调度器未运行"

        return {
            "enabled": self._enable,
            "cron": self._cron,
            "rows": self._rows,
            "next_run_time": next_run_time,
            "last_run_results": last_run,
            "cleaning_history": history
        }

    # --- 删除指定日志文件 ---
    def _delete_log_file(self, payload: dict) -> Dict[str, Any]:
        """删除指定的日志文件"""
        log_id = payload.get("log_id")
        if not log_id:
            return {"status": "error", "message": "未指定要删除的日志文件ID"}
        
        logger.info(f"{self.plugin_name}: 收到删除日志文件请求，日志ID: {log_id}")
        
        try:
            # 确保日志目录存在
            log_dir = settings.LOG_PATH / Path("plugins")
            if not log_dir.exists():
                return {"status": "error", "message": f"插件日志目录不存在: {log_dir}"}
            
            # 判断提供的log_id格式
            if ".log." in log_id:
                # 分割日志文件格式：xxx.log.1, xxx.log.2 - 直接使用全路径
                log_path = log_dir / log_id
                logger.info(f"{self.plugin_name}: 检测到分割日志文件格式: {log_id}")
            elif log_id.endswith(".log"):
                # 已经包含.log扩展名的格式
                log_path = log_dir / log_id
                logger.info(f"{self.plugin_name}: 检测到完整日志文件格式: {log_id}")
            else:
                # 标准格式：仅插件ID，需要添加.log扩展名
                log_path = log_dir / f"{log_id}.log"
                logger.info(f"{self.plugin_name}: 处理标准日志ID: {log_id} -> {log_path}")
            
            # 检查文件是否存在
            if not log_path.exists():
                logger.error(f"{self.plugin_name}: 日志文件不存在: {log_path}")
                return {"status": "error", "message": f"日志文件不存在: {log_path}"}
            
            # 删除文件
            log_path.unlink()
            logger.info(f"{self.plugin_name}: 已成功删除日志文件: {log_path}")
            
            return {
                "status": "success", 
                "message": f"已成功删除日志文件: {log_path.name}"
            }
        except Exception as e:
            logger.error(f"{self.plugin_name}: 删除日志文件失败: {e}", exc_info=True)
            return {"status": "error", "message": f"删除日志文件失败: {str(e)}"}

    # --- 删除指定插件的所有分割日志文件 ---
    def _delete_split_logs(self, payload: dict) -> Dict[str, Any]:
        """删除指定插件的所有分割日志文件 (xxx.log.1, xxx.log.2等)"""
        base_id = payload.get("base_id")
        if not base_id:
            return {"status": "error", "message": "未指定要删除的日志基础ID"}
        
        logger.info(f"{self.plugin_name}: 收到删除分割日志文件请求，基础ID: {base_id}")
        
        try:
            # 确保日志目录存在
            log_dir = settings.LOG_PATH / Path("plugins")
            if not log_dir.exists():
                return {"status": "error", "message": f"插件日志目录不存在: {log_dir}"}
            
            # 查找所有匹配的分割日志文件
            pattern = f"{base_id}.log.*"
            matching_files = list(log_dir.glob(pattern))
            
            if not matching_files:
                return {"status": "warning", "message": f"未找到匹配的分割日志文件: {pattern}"}
            
            # 删除所有匹配的文件
            deleted_count = 0
            for log_path in matching_files:
                try:
                    log_path.unlink()
                    deleted_count += 1
                    logger.info(f"{self.plugin_name}: 已删除分割日志文件: {log_path}")
                except Exception as e:
                    logger.error(f"{self.plugin_name}: 删除分割日志文件失败: {log_path} - {e}")
            
            return {
                "status": "success", 
                "message": f"已成功删除 {deleted_count} 个分割日志文件",
                "deleted_count": deleted_count
            }
        except Exception as e:
            logger.error(f"{self.plugin_name}: 删除分割日志文件失败: {e}", exc_info=True)
            return {"status": "error", "message": f"删除分割日志文件失败: {str(e)}"}

    # --- 批量删除日志文件 ---
    def _batch_delete_logs(self, payload: dict) -> Dict[str, Any]:
        """批量删除日志文件，支持删除已删除插件日志和分割日志"""
        delete_type = payload.get("type")
        if not delete_type:
            return {"status": "error", "message": "未指定批量删除类型"}
        
        logger.info(f"{self.plugin_name}: 收到批量删除请求，类型: {delete_type}")
        
        try:
            # 确保日志目录存在
            log_dir = settings.LOG_PATH / Path("plugins")
            if not log_dir.exists():
                return {"status": "error", "message": f"插件日志目录不存在: {log_dir}"}
            
            # 获取所有日志文件
            log_files_stats = self._get_plugins_logs_stats()
            
            # 标记要删除的文件
            files_to_delete = []
            
            # 获取已安装的插件ID列表（用于判断是否为已删除插件）
            installed_plugins = []
            try:
                plugin_manager = PluginManager()
                local_plugin_instances = plugin_manager.get_local_plugins() or []
                installed_plugins = [p.id.lower() for p in local_plugin_instances 
                                   if getattr(p, 'installed', False) and hasattr(p, 'id')]
            except Exception as e:
                logger.error(f"{self.plugin_name}: 获取已安装插件列表失败: {e}")
            
            # 判断日志文件是否属于已删除插件的函数
            def is_deleted_plugin_log(plugin_info):
                # 系统日志不算已删除插件
                if plugin_info.get("is_special", False):
                    return False
                
                # 获取基础ID
                base_id = plugin_info.get("original_id", plugin_info.get("id", "")).lower()
                
                # 检查是否不在已安装插件列表中
                return not any(base_id == p_id or base_id.startswith(p_id) or p_id.startswith(base_id) 
                            for p_id in installed_plugins)
            
            # 根据批量删除类型收集要删除的文件
            if delete_type == "deleted" or delete_type == "all":
                # 收集已删除插件的日志
                for log_info in log_files_stats:
                    if is_deleted_plugin_log(log_info) and not log_info.get("is_split", False):
                        files_to_delete.append(log_info)
            
            if delete_type == "split" or delete_type == "all":
                # 收集分割日志文件
                for log_info in log_files_stats:
                    if log_info.get("is_split", False):
                        files_to_delete.append(log_info)
            
            # 执行删除操作
            deleted_count = 0
            for file_info in files_to_delete:
                file_path = file_info.get("path")
                if not file_path:
                    continue
                
                try:
                    file_path = Path(file_path)
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"{self.plugin_name}: 已批量删除日志文件: {file_path}")
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"{self.plugin_name}: 批量删除日志文件失败: {file_path} - {e}")
            
            # 构建响应消息
            message = ""
            if delete_type == "deleted":
                message = f"已成功删除 {deleted_count} 个已删除插件的日志文件"
            elif delete_type == "split":
                message = f"已成功删除 {deleted_count} 个分割日志文件"
            elif delete_type == "all":
                message = f"已成功删除 {deleted_count} 个日志文件（含已删除插件日志和分割日志）"
            
            return {
                "status": "success",
                "message": message,
                "deleted_count": deleted_count
            }
        except Exception as e:
            logger.error(f"{self.plugin_name}: 批量删除日志文件失败: {e}", exc_info=True)
            return {"status": "error", "message": f"批量删除日志文件失败: {str(e)}"}

    # --- Abstract/Base Methods Implementation ---
    
    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """Returns None for Vue form, but provides initial config data."""
        # This dict is passed as initialConfig to Config.vue by the host
        return None, self._get_config()

    def get_page(self) -> Optional[List[dict]]:
        """Vue mode doesn't use Vuetify page definitions."""
        return None

    def get_api(self) -> List[Dict[str, Any]]:
        """Defines API endpoints accessible via props.api in Vue components."""
        return [
            {
                "path": "/config",
                "endpoint": self._get_config,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取当前配置"
            },
            {
                "path": "/config",
                "endpoint": self._save_config,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "保存配置"
            },
            {
                "path": "/clean",
                "endpoint": self._trigger_manual_clean,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "触发手动清理"
            },
            {
                "path": "/status",
                "endpoint": self._get_status,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取状态和历史"
            },
            {
                "path": "/installed_plugins",
                "endpoint": self._get_installed_plugins,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取已安装插件列表"
            },
            {
                "path": "/logs_stats", 
                "endpoint": self._get_plugins_logs_stats,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取插件日志统计信息"
            },
            {
                "path": "/clean_plugin",
                "endpoint": self._clean_specific_plugin,
                "methods": ["POST"],
                "auth": "bear", 
                "summary": "清理指定插件日志"
            },
            {
                "path": "/delete_log",
                "endpoint": self._delete_log_file,
                "methods": ["POST"],
                "auth": "bear", 
                "summary": "删除指定日志文件"
            },
            {
                "path": "/delete_split_logs",
                "endpoint": self._delete_split_logs,
                "methods": ["POST"],
                "auth": "bear", 
                "summary": "删除指定插件的所有分割日志文件"
            },
            {
                "path": "/batch_delete",
                "endpoint": self._batch_delete_logs,
                "methods": ["POST"],
                "auth": "bear", 
                "summary": "批量删除日志文件"
            }
        ]

    # --- V2 Vue Interface Method ---
    @staticmethod
    def get_render_mode() -> Tuple[str, Optional[str]]:
        """Declare Vue rendering mode and assets path."""
        return "vue", "dist/assets"

    # --- Other Base Methods ---
    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return [] # No commands defined for this plugin

    def stop_service(self):
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
                self._scheduler = None
                logger.info(f"{self.plugin_name}: 定时任务已停止")
            except Exception as e:
                logger.error(f"{self.plugin_name}: 停止定时任务失败: {e}")

    def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
        """
        获取插件仪表盘元信息
        返回示例：
            [{
                "key": "dashboard1", // 仪表盘的key，在当前插件范围唯一
                "name": "仪表盘1" // 仪表盘的名称
            }, {
                "key": "dashboard2",
                "name": "仪表盘2"
            }]
        """
        return [
            {
                "key": "dashboard1",
                "name": "插件日志清理"
            }
        ]

    def get_dashboard(self, key: str, **kwargs) -> Optional[
        Tuple[Dict[str, Any], Dict[str, Any], Optional[List[dict]]]]:
        """
        获取插件仪表盘页面，需要返回：1、仪表板col配置字典；2、全局配置（布局、自动刷新等）；3、仪表板页面元素配置含数据json（vuetify）或 None（vue模式）
        1、col配置参考：
        {
            "cols": 12, "md": 6
        }
        2、全局配置参考：
        {
            "refresh": 10, // 自动刷新时间，单位秒
            "border": True, // 是否显示边框，默认True，为False时取消组件边框和边距，由插件自行控制
            "title": "组件标题", // 组件标题，如有将显示该标题，否则显示插件名称
            "subtitle": "组件子标题", // 组件子标题，缺省时不展示子标题
        }
        3、vuetify模式页面配置使用Vuetify组件拼装，参考：https://vuetifyjs.com/；vue模式为None

        kwargs参数可获取的值：1、user_agent：浏览器UA

        :param key: 仪表盘key，根据指定的key返回相应的仪表盘数据，缺省时返回一个固定的仪表盘数据（兼容旧版）
        """
        return {
            "cols": 12,
            "md": 6
        }, {
            "refresh": 10,
            "border": True,
            "title": "插件日志清理",
            "subtitle": "定时清理插件产生的日志"
        }, None

import shutil
from pathlib import Path
from typing import Any, List, Dict, Tuple, Optional

try:
    from app.sdk.config import settings
except ImportError:
    from app.core.config import settings
try:
    from app.sdk.plugins import PluginManager
except ImportError:
    from app.core.plugin import PluginManager
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.plugin import PluginHelper
try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas.types import SystemConfigKey


class PluginManagerVue(_PluginBase):
    # 插件名称
    plugin_name = "插件管理中心"
    # 插件描述
    plugin_desc = "集成插件热重载、彻底卸载、重装等功能，支持本地和在线插件管理。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/manager.png"
    # 插件版本
    plugin_version = "3.0.0"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "pluginmanagervue_"
    # 加载顺序
    plugin_order = 11
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _last_reload_plugins = []

    def init_plugin(self, config: dict = None):
        if config:
            self._last_reload_plugins = config.get("last_reload_plugins") or []

    def get_state(self) -> bool:
        return True

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/plugins",
                "endpoint": self.get_plugins,
                "methods": ["GET"],
                "summary": "获取插件列表",
                "description": "获取已安装的插件和本地插件，不显示未安装的在线插件",
                "auth": "bear",
            },
            {
                "path": "/status",
                "endpoint": self.get_status,
                "methods": ["GET"],
                "summary": "获取插件状态",
                "description": "获取插件管理器状态信息",
                "auth": "bear",
            },
            {
                "path": "/reload",
                "endpoint": self.reload_plugin,
                "methods": ["POST"],
                "summary": "重载插件",
                "description": "重载指定插件",
                "auth": "bear",
            },
            {
                "path": "/uninstall",
                "endpoint": self.uninstall_plugin,
                "methods": ["POST"],
                "summary": "卸载插件",
                "description": "彻底卸载插件，包括文件和配置",
                "auth": "bear",
            },
            {
                "path": "/last_reload",
                "endpoint": self.get_last_reload,
                "methods": ["GET"],
                "summary": "获取上次重载的插件",
                "description": "获取上次重载的插件列表",
                "auth": "bear",
            },
            {
                "path": "/reinstall",
                "endpoint": self.reinstall_plugin,
                "methods": ["POST"],
                "summary": "重装插件",
                "description": "重新安装指定插件",
                "auth": "bear",
            },
            {
                "path": "/online_info/{plugin_id}",
                "endpoint": self.get_online_plugin_info,
                "methods": ["GET"],
                "summary": "获取在线插件信息",
                "description": "获取指定插件的在线版本信息",
                "auth": "bear",
            },

        ]

    def get_plugins(self) -> Dict[str, Any]:
        """获取插件列表 - 显示已安装的插件和本地插件，不显示未安装的在线插件"""
        try:
            plugin_manager = PluginManager()
            
            # 获取插件目录中的所有有效插件
            local_plugins = plugin_manager.get_local_plugins()
            if not local_plugins:
                return {
                    "success": True,
                    "data": []
                }
            
            # 获取在线插件市场插件ID列表
            market_plugin_ids = set()
            try:
                online_plugins = plugin_manager.get_online_plugins()
                if online_plugins:
                    market_plugin_ids = {plugin.id for plugin in online_plugins}
            except Exception as e:
                logger.warning(f"获取在线插件市场失败: {e}")
            
            all_plugins = []
            
            # 获取已安装插件列表
            installed_plugins = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
            
            for plugin in local_plugins:
                # 检查插件文件是否真实存在
                plugin_dir = Path(settings.ROOT_PATH) / "app" / "plugins" / plugin.id.lower()
                if not plugin_dir.exists():
                    logger.debug(f"插件目录不存在，跳过: {plugin.id}")
                    continue
                
                # 判断插件类型：在市场中的是在线插件，不在市场中的是本地插件
                plugin_type = "online" if plugin.id in market_plugin_ids else "local"
                
                # 判断安装状态：以已安装列表为准
                is_installed = plugin.id in installed_plugins

                # 过滤策略：不显示未安装的在线插件
                # 只显示：1. 已安装的插件（不管是在线还是本地）2. 本地插件（不管是否安装）
                if plugin_type == "online" and not is_installed:
                    logger.debug(f"跳过未安装的在线插件: {plugin.id}")
                    continue

                plugin_data = {
                    "id": plugin.id,
                    "name": plugin.plugin_name or plugin.id,
                    "version": plugin.plugin_version or "1.0",
                    "author": plugin.plugin_author or "未知",
                    "desc": plugin.plugin_desc or "",
                    "icon": plugin.plugin_icon or "",
                    "order": plugin.plugin_order or 1000,
                    "installed": is_installed,
                    "running": plugin.state if hasattr(plugin, 'state') and is_installed else False,
                    "type": plugin_type,
                    "status": "running" if (hasattr(plugin, 'state') and plugin.state and is_installed) else ("installed" if is_installed else "stopped"),
                    "repo_url": plugin.repo_url or "",
                    "has_update": plugin.has_update or False
                }
                all_plugins.append(plugin_data)
            
            # 按安装状态和类型排序：已安装优先，然后本地优先
            all_plugins.sort(key=lambda x: (
                0 if x['installed'] else 1,  # 已安装优先
                0 if x['type'] == 'local' else 1,  # 本地优先
                x['order'],  # 按order排序
                x['name']  # 按名称排序
            ))
            
            return {
                "success": True,
                "data": all_plugins
            }
            
        except Exception as e:
            logger.error(f"获取插件列表失败: {e}")
            return {
                "success": False,
                "message": f"获取插件列表失败: {str(e)}"
            }

    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        try:
            plugin_manager = PluginManager()
            installed_plugins = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
            local_plugins = plugin_manager.get_local_plugins() or []
            
            # 统计插件目录中的插件数量
            plugin_dir = Path(settings.ROOT_PATH) / "app" / "plugins"
            directory_plugins = 0
            if plugin_dir.exists():
                directory_plugins = len([d for d in plugin_dir.iterdir() 
                                       if d.is_dir() and not d.name.startswith('_')])
            
            return {
                "success": True,
                "data": {
                    "enabled": True,
                    "total_plugins": len(local_plugins),
                    "installed_plugins": len(installed_plugins),
                    "directory_plugins": directory_plugins,
                    "last_reload_count": len(self._last_reload_plugins)
                }
            }
            
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {
                "success": False,
                "message": f"获取状态失败: {str(e)}"
            }

    def reload_plugin(self, payload: dict) -> Dict[str, Any]:
        """重载插件"""
        try:
            plugin_id = payload.get('plugin_id')
            if not plugin_id:
                return {
                    "success": False,
                    "message": "插件ID不能为空"
                }
            
            logger.info(f"准备热加载插件: {plugin_id}")

            # 加载插件到内存
            try:
                PluginManager().reload_plugin(plugin_id)
                logger.info(f"成功热加载插件: {plugin_id} 到内存")
            except Exception as e:
                logger.error(f"失败热加载插件: {plugin_id} 到内存. 错误信息: {e}")
                return {
                    "success": False,
                    "message": f"重载插件失败: {str(e)}"
                }

            # 注册插件服务
            try:
                Scheduler().update_plugin_job(plugin_id)
                logger.info(f"成功热加载插件到插件服务: {plugin_id}")
            except Exception as e:
                logger.error(f"失败热加载插件到插件服务: {plugin_id}. 错误信息: {e}")
                return {
                    "success": False,
                    "message": f"重载插件服务失败: {str(e)}"
                }

            logger.info(f"已完成插件热加载: {plugin_id}")
            
            # 记录重载历史
            if plugin_id not in self._last_reload_plugins:
                self._last_reload_plugins.insert(0, plugin_id)
            else:
                # 移动到最前面
                self._last_reload_plugins.remove(plugin_id)
                self._last_reload_plugins.insert(0, plugin_id)
            
            # 只保留最近10个
            self._last_reload_plugins = self._last_reload_plugins[:10]
            
            # 保存配置
            self.update_config({
                "last_reload_plugins": self._last_reload_plugins
            })
            
            return {
                "success": True,
                "message": f"插件 {plugin_id} 重载成功"
            }
                
        except Exception as e:
            logger.error(f"重载插件失败: {e}")
            return {
                "success": False,
                "message": f"重载插件失败: {str(e)}"
            }

    def reinstall_plugin(self, payload: dict) -> Dict[str, Any]:
        """重装插件"""
        try:
            plugin_id = payload.get('plugin_id')
            if not plugin_id:
                return {
                    "success": False,
                    "message": "插件ID不能为空"
                }
            
            logger.info(f"准备重装插件: {plugin_id}")
            
            # 获取插件信息
            plugin_manager = PluginManager()
            local_plugins = plugin_manager.get_local_plugins()
            target_plugin = None
            
            for plugin in local_plugins:
                if plugin.id == plugin_id:
                    target_plugin = plugin
                    break
            
            if not target_plugin:
                return {
                    "success": False,
                    "message": f"未找到插件: {plugin_id}"
                }
            
            # 检查是否为本地插件
            if target_plugin.repo_url == "local":
                return {
                    "success": False,
                    "message": "本地插件不支持重装"
                }
            
            # 获取插件仓库URL
            repo_url = target_plugin.repo_url
            if not repo_url:
                # 尝试从插件市场获取
                try:
                    online_plugins = plugin_manager.get_online_plugins()
                    for online_plugin in online_plugins:
                        if online_plugin.id == plugin_id:
                            repo_url = online_plugin.repo_url
                            break
                except Exception as e:
                    logger.warning(f"获取在线插件信息失败: {e}")
            
            if not repo_url:
                return {
                    "success": False,
                    "message": f"无法获取插件 {plugin_id} 的仓库地址"
                }
            
            logger.info(f"开始重装插件 {target_plugin.plugin_name} v{target_plugin.plugin_version}")
            
            # 使用PluginHelper重新安装插件
            try:
                state, msg = PluginHelper().install(pid=plugin_id, repo_url=repo_url)
                if not state:
                    logger.error(f"插件 {target_plugin.plugin_name} 重装失败: {msg}")
                    return {
                        "success": False,
                        "message": f"重装失败: {msg}"
                    }
                
                logger.info(f"插件 {target_plugin.plugin_name} 重装成功")
                
                # 重装成功后自动重载插件
                try:
                    PluginManager().reload_plugin(plugin_id)
                    Scheduler().update_plugin_job(plugin_id)
                    logger.info(f"插件 {plugin_id} 重载成功")
                except Exception as e:
                    logger.warning(f"重装后重载插件失败: {e}")
                
                # 记录重载历史
                if plugin_id not in self._last_reload_plugins:
                    self._last_reload_plugins.insert(0, plugin_id)
                else:
                    self._last_reload_plugins.remove(plugin_id)
                    self._last_reload_plugins.insert(0, plugin_id)
                
                # 只保留最近10个
                self._last_reload_plugins = self._last_reload_plugins[:10]
                
                # 保存配置
                self.update_config({
                    "last_reload_plugins": self._last_reload_plugins
                })
                
                return {
                    "success": True,
                    "message": f"插件 {target_plugin.plugin_name} 重装成功"
                }
                
            except Exception as e:
                logger.error(f"重装插件失败: {e}")
                return {
                    "success": False,
                    "message": f"重装失败: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"重装插件失败: {e}")
            return {
                "success": False,
                "message": f"重装插件失败: {str(e)}"
            }

    def uninstall_plugin(self, payload: dict) -> Dict[str, Any]:
        """卸载/清理插件"""
        try:
            plugin_id = payload.get('plugin_id')
            clear_config = payload.get('clear_config', False)
            clear_data = payload.get('clear_data', False)
            force_clean = payload.get('force_clean', False)  # 强制清理文件
            
            if not plugin_id:
                return {
                    "success": False,
                    "message": "插件ID不能为空"
                }
            
            # 获取已安装插件列表
            installed_plugins = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
            is_installed = plugin_id in installed_plugins
            
            # 如果插件已安装，执行正常卸载流程
            if is_installed:
                # 1. 先移除插件服务
                try:
                    Scheduler().remove_plugin_job(plugin_id)
                    logger.info(f"移除插件服务: {plugin_id}")
                except Exception as e:
                    logger.warning(f"移除插件服务失败: {e}")
                
                # 2. 从内存中移除插件
                try:
                    PluginManager().remove_plugin(plugin_id)
                    logger.info(f"从内存移除插件: {plugin_id}")
                except Exception as e:
                    logger.warning(f"从内存移除插件失败: {e}")
                
                # 3. 从已安装列表中移除（这是关键步骤）
                new_installed_plugins = [p for p in installed_plugins if p != plugin_id]
                SystemConfigOper().set(SystemConfigKey.UserInstalledPlugins, new_installed_plugins)
                logger.info(f"从已安装列表移除插件: {plugin_id}")
                
                # 4. 删除插件文件
                plugin_dir = Path(settings.ROOT_PATH) / "app" / "plugins" / plugin_id.lower()
                if plugin_dir.exists():
                    shutil.rmtree(plugin_dir, ignore_errors=True)
                    logger.info(f"删除插件目录: {plugin_dir}")
                
                # 5. 清除配置
                if clear_config:
                    try:
                        PluginManager().delete_plugin_config(plugin_id)
                        logger.info(f"清除插件 {plugin_id} 配置")
                    except Exception as e:
                        logger.warning(f"清除配置失败: {e}")
                
                # 6. 清除数据
                if clear_data:
                    try:
                        PluginManager().delete_plugin_data(plugin_id)
                        logger.info(f"清除插件 {plugin_id} 数据")
                    except Exception as e:
                        logger.warning(f"清除数据失败: {e}")
                
                # 7. 从重载历史中移除
                if plugin_id in self._last_reload_plugins:
                    self._last_reload_plugins.remove(plugin_id)
                    self.update_config({
                        "last_reload_plugins": self._last_reload_plugins
                    })
                
                logger.info(f"插件 {plugin_id} 卸载成功")
                return {
                    "success": True,
                    "message": f"插件 {plugin_id} 卸载成功"
                }
            
            # 如果插件未安装但要强制清理文件
            elif force_clean:
                plugin_dir = Path(settings.ROOT_PATH) / "app" / "plugins" / plugin_id.lower()
                if plugin_dir.exists():
                    shutil.rmtree(plugin_dir, ignore_errors=True)
                    logger.info(f"强制删除插件目录: {plugin_dir}")
                
                # 清除配置
                if clear_config:
                    try:
                        PluginManager().delete_plugin_config(plugin_id)
                        logger.info(f"清除插件 {plugin_id} 配置")
                    except Exception as e:
                        logger.warning(f"清除配置失败: {e}")
                
                # 清除数据
                if clear_data:
                    try:
                        PluginManager().delete_plugin_data(plugin_id)
                        logger.info(f"清除插件 {plugin_id} 数据")
                    except Exception as e:
                        logger.warning(f"清除数据失败: {e}")
                
                logger.info(f"插件 {plugin_id} 文件清理成功")
                return {
                    "success": True,
                    "message": f"插件 {plugin_id} 文件清理成功"
                }
            else:
                return {
                    "success": False,
                    "message": f"插件 {plugin_id} 未安装，如需清理文件请勾选强制清理选项"
                }
            
        except Exception as e:
            logger.error(f"卸载/清理插件失败: {e}")
            return {
                "success": False,
                "message": f"操作失败: {str(e)}"
            }

    def get_online_plugin_info(self, plugin_id: str) -> Dict[str, Any]:
        """获取在线插件信息"""
        try:
            logger.info(f"获取在线插件信息: {plugin_id}")
            
            plugin_manager = PluginManager()
            online_plugins = plugin_manager.get_online_plugins()
            
            if not online_plugins:
                return {
                    "success": False,
                    "message": "无法获取在线插件列表"
                }
            
            # 查找指定插件
            target_plugin = None
            for plugin in online_plugins:
                if plugin.id == plugin_id:
                    target_plugin = plugin
                    break
            
            if not target_plugin:
                return {
                    "success": False,
                    "message": f"未找到在线插件: {plugin_id}"
                }
            
            # 返回插件信息
            plugin_info = {
                "id": target_plugin.id,
                "plugin_name": target_plugin.plugin_name,
                "plugin_version": target_plugin.plugin_version,
                "plugin_author": target_plugin.plugin_author,
                "plugin_desc": target_plugin.plugin_desc,
                "repo_url": target_plugin.repo_url,
                "has_update": target_plugin.has_update,
                "history": target_plugin.history
            }
            
            logger.info(f"找到在线插件: {target_plugin.plugin_name} v{target_plugin.plugin_version}")
            
            return {
                "success": True,
                "data": plugin_info
            }
            
        except Exception as e:
            logger.error(f"获取在线插件信息失败: {e}")
            return {
                "success": False,
                "message": f"获取在线插件信息失败: {str(e)}"
            }

    def get_last_reload(self) -> Dict[str, Any]:
        """获取上次重载的插件"""
        try:
            plugin_manager = PluginManager()
            local_plugins = {getattr(p, 'id'): p for p in plugin_manager.get_local_plugins() or []}
            
            last_reload_info = []
            for plugin_id in self._last_reload_plugins:
                if plugin_id in local_plugins:
                    plugin = local_plugins[plugin_id]
                    last_reload_info.append({
                        "id": plugin_id,
                        "name": getattr(plugin, 'plugin_name', plugin_id),
                        "version": getattr(plugin, 'plugin_version', 'N/A'),
                        "icon": getattr(plugin, 'plugin_icon', '')
                    })
            
            return {
                "success": True,
                "data": last_reload_info
            }
            
        except Exception as e:
            logger.error(f"获取上次重载插件失败: {e}")
            return {
                "success": False,
                "message": f"获取上次重载插件失败: {str(e)}"
            }

    @staticmethod
    def get_render_mode() -> Tuple[str, Optional[str]]:
        """Declare Vue rendering mode and assets path."""
        return "vue", "dist/assets"
    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """Returns None for Vue form, but provides initial config data."""
        # This dict is passed as initialConfig to Config.vue by the host
        return None, self._get_config()

    def get_page(self) -> Optional[List[dict]]:
        """Vue mode doesn't use Vuetify page definitions."""
        return None



    def stop_service(self):
        """退出插件"""
        pass

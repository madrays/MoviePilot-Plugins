"""
NexusPHP站点邀请系统管理插件
"""
import pytz
import os
import re
import json
import time
import threading
from typing import Any, List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import traceback

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from app.log import logger
from app.schemas import Response
from app.schemas.types import NotificationType, EventType
from app.db.site_oper import SiteOper
from app.helper.sites import SitesHelper

from plugins.nexusinvitee.data import DataManager
from plugins.nexusinvitee.utils import NotificationHelper, SiteHelper
from plugins.nexusinvitee.module_loader import ModuleLoader

class Prescription():
    def __init__(self):
        self._cache = {}
    
    def _tag(self,site_name,key,value):
        if site_name not in self._cache:
            self._cache[site_name] = {}
        self._cache[site_name][key] = value
    def setP(self,site_name,value):
        self._tag(site_name,"p",value)
    def setT(self,site_name,value):
        self._tag(site_name,"t",value)
    def setCBP(self,site_name,value):
        self._tag(site_name,"cbp",value)
    def setCBT(self,site_name,value):
        self._tag(site_name,"cbt",value)
    def setCanInvite(self,site_name,value):
        self._tag(site_name,"can_invite",value)
    def setMTBuyable(self,site_name,value):
        self._tag(site_name,"mt_buyable",value)
    def setFailed(self,site_name,value):
        self._tag(site_name,"error",value or "获取失败")

    def _export(self):
        med_list = []
        failed_list = []
        total_remain = 0
        total_can_buy = 0
        
        for k in self._cache:
            site_name = k
            site_error = self._cache[k].get('error')
            if site_error:
                failed_list.append({
                    "site": site_name,
                    "remain": 0,
                    "can_buy": 0,
                    "error": str(site_error)
                })
                continue

            site_remain = self._cache[k].get('p', 0) + self._cache[k].get('t', 0)
            # 合并普通可购买和MT可购买的数量
            site_can_buy = 0 
            if 'cbp' in self._cache[k]:
                site_can_buy += self._cache[k].get("cbp", 0) + self._cache[k].get("cbt", 0)
            if 'mt_buyable' in self._cache[k]:
                site_can_buy += self._cache[k].get("mt_buyable", 0)
            
            if site_remain + site_can_buy > 0:
                site_content = {
                    "site": site_name,
                    "remain": site_remain,
                    "can_buy": site_can_buy,
                    "error": ""
                }
                med_list.append(site_content)
                total_remain += site_remain
                total_can_buy += site_can_buy
                
        return {
            "total": {
                "remain": total_remain,
                "can_buy": total_can_buy,
                "failed": len(failed_list)
            },
            "details": (
                sorted(med_list, key=lambda x: (-x['remain'], -x['can_buy'], x['site'])) +
                sorted(failed_list, key=lambda x: x['site'])
            )
        }

    def getExportText(self):
        med_data = self._export()
        med_text = ""
        for site in med_data["details"]:
            if site.get("error"):
                med_text += f"站点[{site['site']}]: 获取失败[{site['error']}]\r\n"
            else:
                med_text += f"站点[{site['site']}]: 剩余[{site['remain']}]个. 可购买[{site['can_buy']}]个\r\n"
        return med_text
    
    def getComponent(self):
        med_data = self._export()
        if not med_data["details"]:
            return None
            
        # 生成药单内容字符串 - 保持统一的格式
        med_text = self.getExportText()
            
        # 使用 json.dumps 来安全地将 Python 字符串嵌入 JS 字符串
        js_safe_med_text = json.dumps(med_text)
        
        # 构建健壮的 onclick JavaScript 代码
        onclick_js = f"""
        (function(button) {{
            button.disabled = true; // 禁用按钮防止重复点击
            const originalText = button.textContent;
            const textToCopy = {js_safe_med_text};
            navigator.clipboard.writeText(textToCopy).then(() => {{
                button.textContent = '已复制';
                setTimeout(() => {{ button.textContent = originalText; button.disabled = false; }}, 1500);
            }}).catch(err => {{
                console.error('Clipboard API 失败:', err);
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                textArea.style.position = 'fixed'; textArea.style.left = '-9999px';
                document.body.appendChild(textArea);
                textArea.focus(); textArea.select();
                try {{
                    const successful = document.execCommand('copy');
                    if (successful) {{
                        button.textContent = '已复制(FB)';
                        setTimeout(() => {{ button.textContent = originalText; button.disabled = false; }}, 1500);
                    }} else {{
                        alert('复制失败: execCommand 未成功'); button.disabled = false;
                    }}
                }} catch (err) {{
                    console.error('Fallback 复制失败:', err);
                    alert('复制失败: ' + err); button.disabled = false;
                }}
                document.body.removeChild(textArea);
            }});
        }})(this);
        """
        
        # 生成药单容器
        return {
            "component": "VCard",
            "props": {
                "variant": "flat",
                "class": "mt-4"
            },
            "content": [
                {
                    "component": "VCardItem",
                    "content": [
                        {
                            "component": "VCardTitle",
                            "props": {
                                "class": "text-h6"
                            },
                            "text": "药单信息"
                        }
                    ]
                },
                {
                    "component": "VCardText",
                    "content": [
                        {
                            "component": "VRow",
                            "props": {
                                "justify": "space-around",
                                "align": "center",
                                "class": "mb-2",
                                "dense": True
                            },
                            "content": [
                                {
                                    "component": "VCol",
                                    "props": {
                                        "cols": "auto"
                                    },
                                    "content": [
                                        {
                                            "component": "VChip",
                                            "props": {
                                                "color": "primary",
                                                "variant": "flat",
                                                "size": "default",
                                                "prepend-icon": "mdi-package-variant-closed"
                                            },
                                            "text": f"总剩余: {med_data['total']['remain']}"
                                        }
                                    ]
                                },
                                {
                                    "component": "VCol",
                                    "props": {
                                        "cols": "auto"
                                    },
                                    "content": [
                                        {
                                            "component": "VChip",
                                            "props": {
                                                "color": "success",
                                                "variant": "flat",
                                                "size": "default",
                                                "prepend-icon": "mdi-cart-plus"
                                            },
                                            "text": f"总可购买: {med_data['total']['can_buy']}"
                                        }
                                    ]
                                },
                                {
                                    "component": "VCol",
                                    "props": {
                                        "cols": "auto"
                                    },
                                    "content": [
                                        {
                                            "component": "VBtn",
                                            "props": {
                                                "color": "primary",
                                                "size": "default",
                                                "variant": "tonal",
                                                "prepend-icon": "mdi-content-copy",
                                                "onclick": onclick_js
                                            },
                                            "text": "复制药单"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "component": "VExpansionPanels",
                            "props": {
                                "variant": "accordion",
                                "class": "mt-2"
                            },
                            "content": [
                                {
                                    "component": "VExpansionPanel",
                                    "content": [
                                        {
                                            "component": "VExpansionPanelTitle",
                                            # 模仿站点卡片样式添加图标
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "start": True,
                                                        "icon": "mdi-pill",
                                                        "color": "blue-grey"
                                                    }
                                                },
                                                {
                                                    "component": "span",
                                                    "text": "药单详情"
                                                }
                                            ]
                                        },
                                        {
                                            "component": "VExpansionPanelText",
                                            # 移除内边距以使表格更紧凑
                                            "props": {
                                                "class": "pa-0"
                                            },
                                            "content": [
                                                {
                                                    "component": "VTable",
                                                    "props": {
                                                        "density": "compact",
                                                        "hover": True
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "thead",
                                                            "content": [
                                                                {
                                                                    "component": "tr",
                                                                    "content": [
                                                                        {
                                                                            "component": "th",
                                                                            "text": "站点"
                                                                        },
                                                                        {
                                                                            "component": "th",
                                                                            "text": "剩余"
                                                                        },
                                                                        {
                                                                            "component": "th",
                                                                            "text": "可购买"
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "component": "tbody",
                                                            "content": [
                                                                {
                                                                    "component": "tr",
                                                                    "content": [
                                                                        {
                                                                            "component": "td",
                                                                            "text": site["site"]
                                                                        },
                                                                        {
                                                                            "component": "td",
                                                                            "text": "获取失败" if site.get("error") else str(site["remain"])
                                                                        },
                                                                        {
                                                                            "component": "td",
                                                                            "text": site.get("error") or str(site["can_buy"])
                                                                        }
                                                                    ]
                                                                } for site in med_data["details"]
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
            ]
        }

def get_nested_value(data_dict: dict, key_path: List[str], default: Any = None) -> Any:
    """
    递归获取嵌套字典中的值
    :param data_dict: 要查询的字典
    :param key_path: 键路径列表
    :param default: 默认返回值
    :return: 找到的值或默认值
    """
    if not data_dict or not isinstance(data_dict, dict):
        return default
    
    if len(key_path) == 1:
        return data_dict.get(key_path[0], default)
    
    next_dict = data_dict.get(key_path[0], {})
    return get_nested_value(next_dict, key_path[1:], default)


def get_site_error(cache: dict) -> str:
    """
    从缓存包装或站点数据中提取刷新失败信息。
    """
    if not cache or not isinstance(cache, dict):
        return ""

    candidates = [cache]
    data = cache.get("data", {})
    if isinstance(data, dict):
        candidates.append(data)
        nested_data = data.get("data", {})
        if isinstance(nested_data, dict):
            candidates.append(nested_data)

    for candidate in candidates:
        for key in ("error", "fetch_error"):
            error = candidate.get(key)
            if error:
                return str(error)

        if candidate.get("fetch_failed"):
            invite_status = candidate.get("invite_status", {})
            if isinstance(invite_status, dict):
                reason = invite_status.get("reason")
                if reason:
                    return str(reason)
            return "获取失败"

    return ""


class nexusinvitee(_PluginBase):
    # 插件名称
    plugin_name = "后宫管理系统"
    # 插件描述
    plugin_desc = "管理添加到MP站点的邀请系统，包括邀请名额、已邀请用户状态等"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/nexusinvitee.png"
    # 插件版本
    plugin_version = "1.2.7"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "nexusinvitee_"
    # 加载顺序
    plugin_order = 21
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _notify = False
    _cron = "0 9 * * *"  # 默认每天早上9点检查一次
    _onlyonce = False
    _nexus_sites = []  # 支持多选的站点列表
    
    # 站点助手
    sites: SitesHelper = None
    siteoper: SiteOper = None
    
    # 配置和数据管理器
    data_manager: DataManager = None
    
    # 通知助手
    notify_helper: NotificationHelper = None
    
    # 站点处理器列表
    _site_handlers = []

    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None

    presc : Prescription = None

    def init_plugin(self, config=None):
        """
        插件初始化
        """
        # 动态重载模块
        self.__reload_modules()
        
        self.sites = SitesHelper()
        self.siteoper = SiteOper()
        self.presc = Prescription()
        
        # 获取数据目录
        data_path = self.get_data_path()
        
        # 确保目录存在
        if not os.path.exists(data_path):
            try:
                os.makedirs(data_path)
            except Exception as e:
                logger.error(f"创建数据目录失败: {str(e)}")
        
        # 初始化数据管理器（仅保留数据存储，移除配置存储）
        self.data_manager = DataManager(data_path)
        
        # 初始化通知助手
        self.notify_helper = NotificationHelper(self)
        
        # 加载站点处理器
        self._site_handlers = ModuleLoader.load_site_handlers()
        logger.info(f"加载了 {len(self._site_handlers)} 个站点处理器")

        # 停止现有服务
        self.stop_service()

        # 处理传入的配置参数
        if config:
            self._enabled = config.get("enabled", False)
            self._notify = config.get("notify", False)
            self._cron = config.get("cron", "0 9 * * *")
            self._onlyonce = config.get("onlyonce", False)
            
            # 处理站点ID
            self._nexus_sites = []
            if "site_ids" in config:
                for site_id in config.get("site_ids", []):
                    # 确保site_id为整数
                    try:
                        if isinstance(site_id, str) and site_id.isdigit():
                            self._nexus_sites.append(int(site_id))
                        elif isinstance(site_id, int):
                            self._nexus_sites.append(site_id)
                    except:
                        pass           
            # 保存配置
            self.__update_config()
        
        # 如果启用了插件
        if self._enabled:
            # 检查是否配置了站点
            if not self._nexus_sites:
                logger.info("未选择任何站点，将使用所有站点")
            else:
                logger.info(f"后宫管理系统初始化完成，已选择 {len(self._nexus_sites)} 个站点")

        # 立即运行一次
        if self._onlyonce:
            try:
                # 定时服务
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                logger.debug("立即运行一次开关已开启，将在3秒后执行刷新")
                self._scheduler.add_job(func=self.refresh_all_sites, trigger='date',
                                      run_date=datetime.now(pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                      name="后宫管理系统")
                
                # 关闭一次性开关
                self._onlyonce = False
                # 保存配置
                self.__update_config()
                
                # 启动任务
                if self._scheduler and self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()
            except Exception as e:
                logger.error(f"启动一次性任务失败: {str(e)}")

    def __reload_modules(self):
        """
        动态重载所有模块，确保更新时能加载最新代码
        """
        try:
            import sys
            import importlib
            
            # 记录开始重载
            logger.debug("后宫管理系统开始动态重载模块...")
            
            # 1. 清理模块缓存 - 从sys.modules中删除相关模块
            modules_to_reload = []
            for module_name in list(sys.modules.keys()):
                if module_name.startswith('plugins.nexusinvitee.') and module_name != 'plugins.nexusinvitee':
                    modules_to_reload.append(module_name)
                    # 从sys.modules中删除模块以强制重新导入
                    del sys.modules[module_name]
                    logger.info(f"从缓存中移除模块: {module_name}")
            
            # 2. 重新导入核心模块
            logger.debug("重新导入核心模块...")
            importlib.import_module('plugins.nexusinvitee.data')
            importlib.import_module('plugins.nexusinvitee.utils')
            importlib.import_module('plugins.nexusinvitee.module_loader')
            
            # 3. 更新全局引用以确保使用的是最新版本
            logger.debug("更新全局模块引用...")
            global DataManager, NotificationHelper, ModuleLoader
            try:
                from plugins.nexusinvitee.data import DataManager
                from plugins.nexusinvitee.utils import NotificationHelper
                from plugins.nexusinvitee.module_loader import ModuleLoader
                logger.debug("核心模块引用更新成功")
            except Exception as e:
                logger.error(f"更新核心模块引用失败: {str(e)}")
            
            # 记录完成信息
            logger.info(f"后宫管理系统成功重载 {len(modules_to_reload)} 个模块")
        except Exception as e:
            logger.error(f"动态重载模块失败: {str(e)}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")

    def __update_config(self):
        """
        更新配置到MoviePilot系统
        """
        # 保存配置到MP
        config = {
            "enabled": self._enabled,
            "notify": self._notify,
            "cron": self._cron,
            "onlyonce": self._onlyonce,
            "site_ids": self._nexus_sites
        }
        # 使用父类的update_config方法而不是自己的方法，避免递归
        super().update_config(config)

    def get_state(self) -> bool:
        """
        获取插件状态
        """
        return self._enabled

    def get_command(self) -> List[Dict[str, Any]]:
        """
        注册插件命令
        """
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        """
        return [{
            "path": "/config",
            "endpoint": self.get_config,
            "methods": ["GET"],
            "summary": "获取配置",
            "description": "获取后宫管理系统配置数据",
        }, {
            "path": "/update_config",
            "endpoint": self.update_config,
            "methods": ["POST"],
            "summary": "更新配置",
            "description": "更新后宫管理系统配置数据",
        }, {
            "path": "/get_invitees",
            "endpoint": self.get_invitees,
            "methods": ["GET"],
            "summary": "获取被邀请人列表",
            "description": "获取所有站点的被邀请人列表及状态",
        }, {
            "path": "/refresh_data",
            "endpoint": self.refresh_data,
            "methods": ["GET"],
            "summary": "刷新数据",
            "description": "强制刷新所有站点数据",
        }]

    def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
        """
        获取插件仪表盘元信息
        """
        return [{
            "key": "nexusinvitee_dashboard",
            "name": "后宫管理系统"
        }]
        
    def get_dashboard(self, key: str, **kwargs) -> Optional[Tuple[Dict[str, Any], Dict[str, Any], List[dict]]]:
        """
        获取插件仪表盘页面
        """
        if key != "nexusinvitee_dashboard":
            return None
            
        try:
            # 从data_manager获取站点数据
            cached_data = {}
            site_data = self.data_manager.get_site_data()
            for site_name, site_info in site_data.items():
                cached_data[site_name] = site_info
                
            last_update = "未知"
            if cached_data:
                # 找出最新更新时间
                update_times = [cache.get("last_update", 0)
                                for cache in cached_data.values() if cache]
                if update_times:
                    last_update = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(max(update_times)))

            # 计算所有站点统计信息
            total_sites = len(cached_data)
            total_invitees = 0
            total_low_ratio = 0
            total_banned = 0
            total_perm_invites = 0
            total_temp_invites = 0
            total_no_data = 0  # 添加无数据计数器

            for site_name, cache in cached_data.items():
                site_cache_data = cache.get("data", {})
                invitees = []
                
                # 尝试不同的数据结构路径获取邀请列表
                possible_paths = [
                    ["invitees"],
                    ["data", "invitees"],
                    ["data", "data", "invitees"]
                ]
                
                for path in possible_paths:
                    result = get_nested_value(site_cache_data, path, [])
                    if result:
                        invitees = result
                        break

                # 统计各项数据
                total_invitees += len(invitees)
                
                # 获取邀请状态
                invite_status = {}
                status_paths = [
                    ["invite_status"],
                    ["data", "invite_status"],
                    ["data", "data", "invite_status"]
                ]
                
                for path in status_paths:
                    result = get_nested_value(site_cache_data, path, {})
                    if result and isinstance(result, dict):
                        invite_status = result
                        break

                # 统计邀请数量
                total_perm_invites += invite_status.get("permanent_count", 0)
                total_temp_invites += invite_status.get("temporary_count", 0)

                # 统计用户状态 - 使用ratio_health字段
                banned_count = sum(1 for i in invitees if i.get('enabled', '').lower() == 'no')
                low_ratio_count = sum(1 for i in invitees if i.get('ratio_health') in ['warning', 'danger'])
                no_data_count = sum(1 for i in invitees if i.get('ratio_health') == 'neutral')

                # 累加到总数
                total_banned += banned_count
                total_low_ratio += low_ratio_count
                total_no_data += no_data_count


            # 列配置
            col_config = {
                "cols": 16,
                "md": 12
            }
            
            # 全局配置
            global_config = {
                "refresh": 3600,  # 1小时自动刷新一次
                "title": "后宫总览",
                "subtitle": f"更新时间: {last_update}",
                "border": False
            }
            
            # 页面元素
            elements = []
            
            # 添加全局统计信息 - 与详情页完全一致
            elements.append({
                "component": "VCard",
                "props": {
                    "class": "mb-4",
                    "variant": "flat"  # 修改为flat，去掉内边框
                },
"content": [
                    {
                        "component": "VCardTitle",
                        "text": "后宫总览"
                    },
                    {
                        "component": "VCardText",
                        "content": [
                            {
                                "component": "VRow",
                                "content": [
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#2196F3",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-domain"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 primary--text"},
                                                    "text": str(total_sites)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "站点数量"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#03A9F4",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-human-queue"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 info--text"},
                                                    "text": str(total_invitees)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "后宫成员"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#9C27B0",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-ticket-confirmation"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 purple--text"},
                                                    "text": str(total_perm_invites)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "永久邀请数"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#E91E63",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-ticket"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5", "style": "color: #E91E63"},
                                                    "text": str(total_temp_invites)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "临时邀请数"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#FF9800",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-alert-circle"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 warning--text"},
                                                    "text": str(total_low_ratio)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "低分享率"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#F44336",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-account-cancel"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 error--text"},
                                                    "text": str(total_banned)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "已禁用"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#9E9E9E",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-database-off"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"style": "color: #9E9E9E; font-size: 1.5rem; font-weight: 400; line-height: 2rem;"},
                                                    "text": str(total_no_data)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "无数据"
                                                }
                                            ]
                                        }]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            })
            
            # 如果没有数据，显示提示信息
            if not cached_data:
                elements = [{
                    "component": "VAlert",
                    "props": {
                        "type": "info",
                        "variant": "tonal",
                        "text": "暂无站点数据，请先在配置中选择要管理的站点。"
                    }
                }]
            
            return col_config, global_config, elements
            
        except Exception as e:
            logger.error(f"生成仪表盘失败: {str(e)}")
            return {
                "cols": 12,
                "md": 6
            }, {
                "refresh": 3600,
                "title": "后宫管理系统",
                "subtitle": "发生错误"
            }, [{
                "component": "VAlert",
                "props": {
                    "type": "error",
                    "variant": "tonal",
                    "text": f"生成仪表盘失败: {str(e)}"
                }
        }]

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        配置页面
        """
        # 获取支持的站点列表
        site_options = []
        for site in self.sites.get_indexers():
            site_name = site.get("name", "")
            site_options.append({
                "title": site_name,
                "value": site.get("id")
            })
        
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
                                            'label': '启用插件'
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
                                            'label': '发送通知'
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
                                            'label': '立即运行一次'
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'site_ids',
                                            'label': '选择站点',
                                            'items': site_options,
                                            'multiple': True,
                                            'chips': True,
                                            'clearable': True,
                                            'persistent-hint': True,
                                            'hint': '选择刷新的站点，支持多选，不选择则默认所有站点，刷新方式为增量刷新（不清空旧数据）'
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
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '执行周期'
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
                                            'text': '【使用说明】\n本插件适配各站点中，不排除bug，目前尚未适配ptt、ttg等，以及我没有的站点，欢迎大佬们报错时提交错误站点的邀请页和发邀页html结构\n1. 选择要管理的站点（支持多选，不选择则默认管理所有站点）\n2. 设置执行周期，建议每天早上9点执行一次\n3. 可选择开启通知，在状态变更时收到通知\n4. 本插件不会自动刷新数据，打开详情页也不会自动刷新数据，需手动刷新'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": self._enabled,
            "notify": self._notify,
            "cron": "0 9 * * *",
            "onlyonce": False,
            "site_ids": self._nexus_sites
        }

    def _is_nexusphp(self, site_url: str) -> bool:
        """
        判断是否为NexusPHP站点
        """
        # 简单判断，后续可以添加更多特征
        return "php" in site_url.lower()

    def get_page(self) -> List[dict]:
        """
        详情页面
        """
        import re  # 在函数内部也导入re模块，确保可用
        
        
        try:
            self.presc = Prescription()

            # 从data_manager获取站点数据
            cached_data = {}
            site_data = self.data_manager.get_site_data()
            for site_name, site_info in site_data.items():
                cached_data[site_name] = site_info
                
            last_update = "未知"
            if cached_data:
                # 找出最新更新时间
                update_times = [cache.get("last_update", 0)
                                for cache in cached_data.values() if cache]
                if update_times:
                    last_update = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(max(update_times)))

            # 准备页面内容
            page_content = []
            
            # 添加全局统计信息
            total_sites = len(cached_data)
            total_invitees = 0
            total_low_ratio = 0
            total_banned = 0
            total_perm_invites = 0
            total_temp_invites = 0
            total_no_data = 0

            for site_name, cache in cached_data.items():
                site_cache_data = cache.get("data", {})
                invitees = []
                
                # 获取邀请用户列表
                if "data" in site_cache_data:
                    invitees = site_cache_data.get("data", {}).get("invitees", [])
                else:
                    invitees = site_cache_data.get("invitees", [])

                # 统计各项数据
                total_invitees += len(invitees)
                
                # 统计用户状态
                banned_count = sum(1 for i in invitees if i.get('enabled', '').lower() == 'no')
                low_ratio_count = sum(1 for i in invitees if i.get('ratio_health') in ['warning', 'danger'])
                no_data_count = sum(1 for i in invitees if i.get('ratio_health') == 'neutral')

                # 累加到总数
                total_banned += banned_count
                total_low_ratio += low_ratio_count
                total_no_data += no_data_count

                # 获取邀请状态
                invite_status = {}
                if "data" in site_cache_data:
                    invite_status = site_cache_data.get("data", {}).get("invite_status", {})
                else:
                    invite_status = site_cache_data.get("invite_status", {})

                # 统计邀请数量
                total_perm_invites += invite_status.get("permanent_count", 0)
                total_temp_invites += invite_status.get("temporary_count", 0)

            # 添加统计卡片
            page_content.extend([
                {
                    "type": "div",
                    "class": "dashboard-stats",
                    "content": [
                        {
                            "type": "div",
                            "class": "dashboard-stats__item",
                            "content": [
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__title",
                                    "content": "站点数量"
                                },
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__value",
                                    "content": str(total_sites)
                                }
                            ]
                        },
                        {
                            "type": "div",
                            "class": "dashboard-stats__item",
                            "content": [
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__title",
                                    "content": "后宫成员"
                                },
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__value",
                                    "content": str(total_invitees)
                                }
                            ]
                        },
                        {
                            "type": "div",
                            "class": "dashboard-stats__item",
                            "content": [
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__title",
                                    "content": "永久邀请"
                                },
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__value",
                                    "content": str(total_perm_invites)
                                }
                            ]
                        },
                        {
                            "type": "div",
                            "class": "dashboard-stats__item",
                            "content": [
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__title",
                                    "content": "临时邀请"
                                },
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__value",
                                    "content": str(total_temp_invites)
                                }
                            ]
                        },
                        {
                            "type": "div",
                            "class": "dashboard-stats__item",
                            "content": [
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__title text-warning",
                                    "content": "低分享率"
                                },
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__value text-warning",
                                    "content": str(total_low_ratio)
                                }
                            ]
                        },
                        {
                            "type": "div",
                            "class": "dashboard-stats__item",
                            "content": [
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__title text-error",
                                    "content": "已禁用"
                                },
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__value text-error",
                                    "content": str(total_banned)
                                }
                            ]
                        },
                        {
                            "type": "div",
                            "class": "dashboard-stats__item",
                            "content": [
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__title text-grey",
                                    "content": "无数据"
                                },
                                {
                                    "type": "div",
                                    "class": "dashboard-stats__value text-grey",
                                    "content": str(total_no_data)
                                }
                            ]
                        }
                    ]
                }
            ])

            # 添加样式，优化表格
            page_content.extend([
                {
                    "type": "style",
                    "content": """
                        .dashboard-stats {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 1rem;
                            margin-bottom: 2rem;
                        }
                        .dashboard-stats__item {
                            flex: 1;
                            min-width: 120px;
                            padding: 1rem;
                            background: var(--v-surface-variant);
                            border-radius: 8px;
                            text-align: center;
                        }
                        .dashboard-stats__title {
                            font-size: 0.875rem;
                            margin-bottom: 0.5rem;
                            opacity: 0.7;
                        }
                        .dashboard-stats__value {
                            font-size: 1.5rem;
                            font-weight: bold;
                        }
                        .text-warning {
                            color: var(--v-warning);
                        }
                        .text-error {
                            color: var(--v-error);
                        }
                        .text-grey {
                            color: var(--v-grey);
                        }
                    """
                }
            ])

            # 添加头部信息和提示
            page_content.append({
                "component": "VAlert",
                "props": {
                    "type": "info",
                    "text": f"后宫管理系统 - 共 {len(cached_data)} 个站点，数据最后更新时间: {last_update}\n注: 本插件不会自动刷新数据，只显示在MP中已配置并选择的站点",
                    "variant": "tonal",
                    "class": "mb-4"
                }
            })

            # 添加说明提示
            page_content.append({
                "component": "VAlert",
                "props": {
                    "type": "warning",
                    "text": "如需刷新数据，请在配置页面打开\"立即运行一次\"开关并保存立即刷新数据",
                    "variant": "tonal",
                    "class": "mb-4"
                }
            })

            # 添加样式
            page_content.append({
                "component": "style",
                "text": """
                .site-invitees-table {
                    font-size: 12px !important;
                }
                .site-invitees-table td {
                    padding: 4px 8px !important;
                    height: 32px !important;
                }
                .site-invitees-table th {
                    height: 36px !important;
                }
                .site-invitees-table .v-btn {
                    font-size: 12px !important;
                    height: 24px !important;
                    min-width: 64px !important;
                }
                .site-invitees-table tr.error {
                    background-color: rgba(244, 67, 54, 0.12) !important;
                }
                .site-invitees-table tr.warning-lighten-4 {
                    background-color: rgba(255, 152, 0, 0.12) !important;
                }
                .site-invitees-table tr.grey-lighten-3 {
                    background-color: rgba(158, 158, 158, 0.12) !important;
                }
                .site-invitees-table tr.error-lighten-4 {
                    background-color: rgba(244, 67, 54, 0.08) !important;
                }
                .text-success {
                    color: #4CAF50 !important;
                }
                .text-warning {
                    color: #FF9800 !important;
                }
                .text-error {
                    color: #F44336 !important;
                }
                .text-grey {
                    color: #9E9E9E !important;
                }
                .font-weight-bold {
                    font-weight: bold !important;
                }
                /* 折叠面板样式 */
                .v-expansion-panel-title {
                    min-height: 48px !important;
                    padding: 0 16px !important;
                }
                .v-expansion-panel-text__wrapper {
                    padding: 0 !important;
                }
                .v-expansion-panel {
                    background-color: rgba(0, 0, 0, 0.02) !important;
                    margin-bottom: 8px !important;
                }
                """
            })

            # 准备站点卡片
            cards = []
            
            # 计算所有站点统计信息
            total_sites = len(cached_data)
            total_invitees = 0
            total_low_ratio = 0
            total_banned = 0
            total_perm_invites = 0
            total_temp_invites = 0
            total_no_data = 0

            for site_name, cache in cached_data.items():
                site_cache_data = cache.get("data", {})
                invitees = []
                
                # 获取邀请用户列表
                if "data" in site_cache_data:
                    invitees = site_cache_data.get("data", {}).get("invitees", [])
                else:
                    invitees = site_cache_data.get("invitees", [])

                # 统计各项数据
                total_invitees += len(invitees)
                
                # 统计用户状态 - 直接使用ratio_health字段
                banned_count = sum(1 for i in invitees if i.get('enabled', '').lower() == 'no')
                low_ratio_count = sum(1 for i in invitees if i.get('ratio_health') in ['warning', 'danger'])
                no_data_count = sum(1 for i in invitees if i.get('ratio_health') == 'neutral')

                # 累加到总数
                total_banned += banned_count
                total_low_ratio += low_ratio_count
                total_no_data += no_data_count

                # 获取邀请状态
                invite_status = {}
                if "data" in site_cache_data:
                    invite_status = site_cache_data.get("data", {}).get("invite_status", {})
                else:
                    invite_status = site_cache_data.get("invite_status", {})

                # 统计邀请数量
                total_perm_invites += invite_status.get("permanent_count", 0)
                total_temp_invites += invite_status.get("temporary_count", 0)
                # 向药单打标临药永药
                site_error = get_site_error(cache)
                if site_error:
                    self.presc.setFailed(site_name, site_error)
                else:
                    self.presc.setP(site_name,invite_status.get("permanent_count", 0))
                    self.presc.setT(site_name,invite_status.get("temporary_count", 0))


            # 添加全局统计信息
            page_content.append({
                "component": "VCard",
                "props": {
                    "class": "mb-4",
                    "variant": "flat"
                },
                "content": [
                    {
                        "component": "VCardTitle",
                        "text": "后宫总览"
                    },
                    {
                        "component": "VCardText",
                        "content": [
                            {
                                "component": "VRow",
                                "content": [
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#2196F3",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-domain"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 primary--text"},
                                                    "text": str(total_sites)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "站点数量"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#03A9F4",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-human-queue"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 info--text"},
                                                    "text": str(total_invitees)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "后宫成员"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#9C27B0",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-ticket-confirmation"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 purple--text"},
                                                    "text": str(total_perm_invites)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "永久邀请数"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#E91E63",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-ticket"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5", "style": "color: #E91E63"},
                                                    "text": str(total_temp_invites)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "临时邀请数"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#FF9800",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-alert-circle"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 warning--text"},
                                                    "text": str(total_low_ratio)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "低分享率"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#F44336",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-account-cancel"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-h5 error--text"},
                                                    "text": str(total_banned)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "已禁用"
                                                }
                                            ]
                                        }]
                                    },
                                    {
                                        "component": "VCol",
                                        "props": {"cols": 1.7},
                                        "content": [{
                                            "component": "div",
                                            "props": {
                                                "class": "text-center"
                                            },
                                            "content": [
                                                {
                                                    "component": "VIcon",
                                                    "props": {
                                                        "size": "36",
                                                        "color": "#9E9E9E",
                                                        "class": "mb-2"
                                                    },
                                                    "text": "mdi-database-off"
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"style": "color: #9E9E9E; font-size: 1.5rem; font-weight: 400; line-height: 2rem;"},
                                                    "text": str(total_no_data)
                                                },
                                                {
                                                    "component": "div",
                                                    "props": {"class": "text-caption"},
                                                    "text": "无数据"
                                                }
                                            ]
                                        }]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            })

            for site_name, cache in cached_data.items():
                invite_data = cache.get("data", {})

                # 获取站点信息
                site_info = None
                for site in self.sites.get_indexers():
                    if site.get("name") == site_name:
                        site_info = site
                        break
                
                if site_info:
                    # 获取站点数据
                    site_cache_data = cache.get("data", {})
                    
                    # 尝试不同的数据结构路径获取邀请列表
                    invitees = []
                    possible_paths = [
                        ["invitees"],
                        ["data", "invitees"],
                        ["data", "data", "invitees"]
                    ]
                    
                    for path in possible_paths:
                        result = get_nested_value(site_cache_data, path, [])
                        if result:
                            invitees = result
                            break
                    
                    # 同样处理邀请状态
                    invite_status = {}
                    status_paths = [
                        ["invite_status"],
                        ["data", "invite_status"],
                        ["data", "data", "invite_status"]
                    ]
                    
                    for path in status_paths:
                        result = get_nested_value(site_cache_data, path, {})
                        if result and isinstance(result, dict):
                            invite_status = result

                    # 计算此站点的统计信息
                    banned_count = sum(1 for i in invitees if i.get('enabled', '').lower() == 'no')
                    low_ratio_count = sum(1 for i in invitees if i.get('ratio_health') == 'warning' or i.get('ratio_health') == 'danger')
                    no_data_count = sum(1 for i in invitees if i.get('ratio_health') == 'neutral')

                    # 更新总计数
                    total_banned += banned_count
                    total_low_ratio += low_ratio_count
                    total_no_data += no_data_count

                    for invitee in invitees:
                        # 检查是否是无数据情况（上传下载都是0）
                        uploaded = invitee.get('uploaded', '0')
                        downloaded = invitee.get('downloaded', '0')
                        is_no_data = False
                        
                        # 简化判断逻辑，只关注字符串为"0"、"0.0"、"0B"或空字符串，或者数值为0的情况
                        if isinstance(uploaded, str) and isinstance(downloaded, str):
                            uploaded_zero = uploaded == '0' or uploaded == '' or uploaded == '0.0' or uploaded.lower() == '0b'
                            downloaded_zero = downloaded == '0' or downloaded == '' or downloaded == '0.0' or downloaded.lower() == '0b'
                            is_no_data = uploaded_zero and downloaded_zero
                        elif isinstance(uploaded, (int, float)) and isinstance(downloaded, (int, float)):
                            is_no_data = uploaded == 0 and downloaded == 0
                        
                        username = invitee.get('username', '未知')
                        # 强制输出日志，确保无数据用户被记录
                        if is_no_data:
                            logger.info(f"【总览】检测到无数据用户: {username}, 上传={uploaded}, 下载={downloaded}, 当前无数据总计={total_no_data+1}")
                            total_no_data += 1
                            continue
                        
                        # 处理分享率
                        ratio_str = invitee.get('ratio', '')
                        # 处理无限分享率情况 - 增强识别能力
                        if ratio_str == '∞' or ratio_str.lower() in ['inf.', 'inf', 'infinite', '无限']:
                            continue  # 无限分享率不计入低分享率
                        
                        try:
                            # 标准化字符串 - 正确处理千分位逗号
                            # 使用更好的方法完全移除千分位逗号
                            normalized_ratio = ratio_str
                            # 循环处理，直到没有千分位逗号
                            while ',' in normalized_ratio:
                                # 检查每个逗号是否是千分位分隔符
                                comma_positions = [pos for pos, char in enumerate(normalized_ratio) if char == ',']
                                for pos in comma_positions:
                                    # 如果逗号后面是数字，且前面也是数字，则视为千分位逗号
                                    if (pos > 0 and pos < len(normalized_ratio) - 1 and 
                                        normalized_ratio[pos-1].isdigit() and normalized_ratio[pos+1].isdigit()):
                                        normalized_ratio = normalized_ratio[:pos] + normalized_ratio[pos+1:]
                                        break
                                else:
                                    # 如果没有找到千分位逗号，退出循环
                                    break
                            
                            # 最后，将任何剩余的逗号替换为小数点（可能是小数点表示）
                            normalized_ratio = normalized_ratio.replace(',', '.')
                            ratio_val = float(normalized_ratio) if normalized_ratio else 0
                            if ratio_val < 1 and ratio_val > 0:  # 确保分享率大于0且小于1才算低分享率
                                low_ratio_count += 1
                                logger.info(f"【总览】检测到低分享率用户: {invitee.get('username', '未知')}, 分享率={ratio_str}({ratio_val})")
                        except (ValueError, TypeError) as e:
                            # 转换错误时记录警告
                            logger.warning(f"分享率转换失败: {ratio_str}, 错误: {str(e)}")

                    # 合并站点信息和数据到一张卡片
                    site_card = {
                        "component": "VCard",
                        "props": {
                            "class": "mb-4",
                            "variant": "flat"  # 修改为flat，去掉内边框
                        },
                        "content": [
                            # 站点信息头部
                            {
                                "component": "VCardItem",
                                "props": {
                                    "class": "py-2"
                                },
                                "content": [
                                    {
                                        "component": "VCardTitle",
                                        "content": [
                                            {
                                                "component": "div",
                                                "props": {
                                                    "class": "d-flex align-center"
                                                },
                                                "content": [
                                                    {
                                                        "component": "VIcon",
                                                        "props": {
                                                            "color": "primary",
                                                            "size": "24",
                                                            "class": "mr-2"
                                                        },
                                                        "text": "mdi-crown"
                                                    },
                                                    {
                                                        "component": "span",
                                                        "props": {
                                                            "class": "text-h6"
                                                        },
                                                        "text": site_info.get("name")
                                                    },
                                                    {
                                                        "component": "VSpacer"
                                                    },
                                                    {
                                                        "component": "div",
                                                        "props": {
                                                            "style": "display: flex; align-items: center; white-space: nowrap;"
                                                        },
                                                        "content": [
                                                            {
                                                                "component": "VIcon",
                                                                "props": {
                                                                    "size": "small",
                                                                    "color": "error",
                                                                    "class": "mr-1"
                                                                },
                                                                "text": "mdi-alert-circle" if low_ratio_count > 0 else ""
                                                            },
                                                            {
                                                                "component": "span",
                                                                "props": {"class": "text-caption mr-2"},
                                                                "text": f"{low_ratio_count}人低分享" if low_ratio_count > 0 else ""
                                                            },
                                                            {
                                                                "component": "VIcon",
                                                                "props": {
                                                                    "size": "small",
                                                                    "color": "error",
                                                                    "class": "mr-1"
                                                                },
                                                                "text": "mdi-block-helper" if banned_count > 0 else ""
                                                            },
                                                            {
                                                                "component": "span",
                                                                "props": {"class": "text-caption mr-2"},
                                                                "text": f"{banned_count}人禁用" if banned_count > 0 else ""
                                                            },
                                                            {
                                                                "component": "VIcon",
                                                                "props": {
                                                                    "size": "small",
                                                                    "color": "#9E9E9E",
                                                                    "class": "mr-1"
                                                                },
                                                                "text": "mdi-database-off" if no_data_count > 0 else ""
                                                            },
                                                            {
                                                                "component": "span",
                                                                "props": {"class": "text-caption"},
                                                                "text": f"{no_data_count}人无数据" if no_data_count > 0 else ""
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            # 邀请状态统计
                            {
                                "component": "VCardText",
                                "props": {
                                    "class": "pt-2 pb-0"
                                },
                                "content": [
                                    {
                                        "component": "VRow",
                                        "props": {
                                            "dense": True
                                        },
                                        "content": [
                                            {
                                                "component": "VCol",
                                                "props": {"cols": 3},
                                                "content": [{
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                    "props": {
                                                                "size": "24",
                                                                "color": "#9C27B0",
                                                                "class": "mr-2"
                                                    },
                                                            "text": "mdi-ticket-confirmation"
                                                        },
                                                        {
                                                            "component": "div",
                                                    "content": [
                                                        {
                                                            "component": "div",
                                                                    "props": {"class": "text-body-1 font-weight-medium purple--text"},
                                                                    "text": str(invite_status.get("permanent_count", 0))
                                                        },
                                                        {
                                                            "component": "div",
                                                            "props": {"class": "text-caption"},
                                                            "text": "永久邀请"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }]
                                            },
                                            {
                                                "component": "VCol",
                                                "props": {"cols": 3},
                                                "content": [{
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "size": "24",
                                                                "color": "#E91E63",
                                                                "class": "mr-2"
                                                            },
                                                            "text": "mdi-ticket"
                                                        },
                                                        {
                                                            "component": "div",
                                                            "content": [
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-body-1 font-weight-medium", "style": "color: #E91E63"},
                                                                    "text": str(invite_status.get("temporary_count", 0))
                                                        },
                                                        {
                                                            "component": "div",
                                                            "props": {"class": "text-caption"},
                                                            "text": "临时邀请"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }]
                                            },
                                            {
                                                "component": "VCol",
                                                "props": {"cols": 3},
                                                "content": [{
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "size": "24",
                                                                "color": "#4CAF50",
                                                                "class": "mr-2"
                                                            },
                                                            "text": "mdi-account-group"
                                                        },
                                                        {
                                                            "component": "div",
                                                            "content": [
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-body-1 font-weight-medium success--text"},
                                                                    "text": str(len(invitees))
                                                        },
                                                        {
                                                            "component": "div",
                                                            "props": {"class": "text-caption"},
                                                                    "text": "邀请人数"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }]
                                            },
                                            {
                                                "component": "VCol",
                                                "props": {"cols": 3},
                                                "content": [{
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "size": "24",
                                                                "color": "#4CAF50" if invite_status.get("can_invite") else "#F44336",
                                                                "class": "mr-2"
                                                            },
                                                            "text": "mdi-check-circle" if invite_status.get("can_invite") else "mdi-close-circle"
                                                        },
                                                        {
                                                            "component": "div",
                                                            "content": [
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-body-1 font-weight-medium " + 
                                                                            ("success--text" if invite_status.get("can_invite") else "error--text")},
                                                                    "text": "可邀请" if invite_status.get("can_invite") else "不可邀请"
                                                        },
                                                        {
                                                            "component": "div",
                                                            "props": {"class": "text-caption"},
                                                            "text": "邀请权限"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }

                    # 添加错误信息或不可邀请原因的显示部分
                    # 获取错误信息和不可邀请原因
                    error_message = get_site_error(cache)
                    
                    # 使用辅助函数检查不同路径的invite_status
                    invite_status_for_check = invite_status  # 使用上面已获取的invite_status
                    
                    can_invite = invite_status_for_check.get("can_invite", False)
                    # 向药单打标发药权限
                    self.presc.setCanInvite(site_name,can_invite)
                    reason = invite_status_for_check.get("reason", "")

                    # 确保能正确显示不可邀请原因
                    if not can_invite:
                        logger.debug(f"站点 {site_name} 不可邀请原因: {reason}")
                    
                    # 检查是否为M-Team站点
                    is_mteam_site = False
                    site_url_lower = site_info.get("url", "").lower()
                    mteam_features = ["m-team", "api.m-team.cc", "api.m-team.io"]
                    for feature in mteam_features:
                        if feature in site_url_lower:
                            is_mteam_site = True
                            break
                    
                    # 获取站点魔力值和邀请价格信息
                    bonus = invite_status.get("bonus", 0)
                    permanent_invite_price = invite_status.get("permanent_invite_price", 0)
                    temporary_invite_price = invite_status.get("temporary_invite_price", 0)
                    
                    # 添加不可邀请原因的显示
                    if not can_invite and reason and not is_mteam_site:  # 对于M-Team站点，我们会在后面特殊处理
                        site_card["content"].append({
                            "component": "VCardText",
                            "props": {
                                "class": "py-1"
                            },
                            "content": [
                                {
                                    "component": "VAlert",
                                    "props": {
                                        "type": "error",
                                        "variant": "tonal",
                                        "density": "compact",
                                        "class": "my-1 d-flex align-center"
                                    },
                                    "content": [
                                        {
                                            "component": "VIcon",
                                            "props": {
                                                "start": True,
                                                "size": "small"
                                            },
                                            "text": "mdi-alert-circle"
                                        },
                                        {
                                            "component": "span",
                                            "text": f"不可邀请原因: {reason}"
                                        }
                                    ]
                                }
                            ]
                        })
                    
                    # M-Team站点特殊处理
                    if is_mteam_site:
                        # 尝试从reason中提取用户等级和魔力值信息
                        import re

                        
                        # 提取用户等级
                        user_role = ""
                        level_match = re.search(r'用户等级\(([^)]+)\)', reason)
                        if level_match:
                            user_role = level_match.group(1)

                        
                        # 提取魔力值
                        user_bonus = ""
                        bonus_match = re.search(r'魔力值\(([0-9.]+)\)', reason)
                        if bonus_match:
                            user_bonus = bonus_match.group(1)                       
                        # 提取可购买邀请数
                        buyable_invites = 0
                        buy_match = re.search(r'可购买(\d+)个', reason)
                        if buy_match:
                            buyable_invites = int(buy_match.group(1))                           
                        # 计算MT可买药数量
                        mt_buyable = 0
                        if user_bonus and user_role:
                            try:
                                user_bonus_float = float(user_bonus)
                                # 每80000魔力可买一个
                                mt_buyable = int(user_bonus_float / 80000)
                                # 向药单打标MT可买药数量
                                self.presc.setMTBuyable(site_name, mt_buyable)
                            except (ValueError, TypeError):
                                user_bonus_float = 0                               
                        # 如果魔力值和用户等级有效
                        if user_bonus and user_role:                          
                            # 计算还需多少魔力
                            try:
                                user_bonus_float = float(user_bonus)
                                needed_bonus = 80000 - (user_bonus_float % 80000)
                                needed_bonus_text = f"(还需{needed_bonus:.1f}魔力)" if mt_buyable == 0 and user_bonus_float > 0 else ""
                            except (ValueError, TypeError):
                                user_bonus_float = 0
                            
                            # 添加用户等级卡片
                            site_card["content"].append({
                                "component": "VCardText",
                                "props": {
                                    "class": "py-0"
                                },
                                "content": [
                                    {
                                        "component": "VRow",
                                        "props": {
                                            "dense": True
                                        },
                                        "content": [
                                            # 用户等级
                                            {
                                                "component": "VCol",
                                                "props": {"cols": 3},
                                                "content": [{
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center py-2"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "color": "deep-purple",
                                                                "size": "small",
                                                                "class": "mr-2"
                                                            },
                                                            "text": "mdi-crown"
                                                        },
                                                        {
                                                            "component": "div",
                                                            "content": [
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-subtitle-2 font-weight-medium"},
                                                                    "text": user_role
                                                                },
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-caption"},
                                                                    "text": "用户等级"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }]
                                            },
                                            # 魔力值
                                            {
                                                "component": "VCol",
                                                "props": {"cols": 3},
                                                "content": [{
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center py-2"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "color": "orange",
                                                                "size": "small",
                                                                "class": "mr-2"
                                                            },
                                                            "text": "mdi-diamond"
                                                        },
                                                        {
                                                            "component": "div",
                                                            "content": [
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-subtitle-2 font-weight-medium"},
                                                                    "text": user_bonus
                                                                },
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-caption"},
                                                                    "text": "魔力值"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }]
                                            },
                                            # 可购买邀请
                                            {
                                                "component": "VCol",
                                                "props": {"cols": 6},
                                                "content": [{
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center py-2"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "color": "cyan",
                                                                "size": "small",
                                                                "class": "mr-2"
                                                            },
                                                            "text": "mdi-cart"
                                                        },
                                                        {
                                                            "component": "div",
                                                            "content": [
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-subtitle-2 font-weight-medium"},
                                                                    "text": str(buyable_invites) + " " + needed_bonus_text
                                                                },
                                                                {
                                                                    "component": "div",
                                                                    "props": {"class": "text-caption"},
                                                                    "text": "可购买邀请"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }]
                                            }
                                        ]
                                    }
                                ]
                            })
                            
                            # 添加提示信息
                            site_card["content"].append({
                                "component": "VCardText",
                                "props": {
                                    "class": "py-1"
                                },
                                "content": [
                                    {
                                        "component": "VAlert",
                                        "props": {
                                            "type": "info",
                                            "variant": "tonal",
                                            "density": "compact",
                                            "class": "my-1 d-flex align-center"
                                        },
                                        "content": [
                                            {
                                                "component": "VIcon",
                                                "props": {
                                                    "start": True,
                                                    "size": "small"
                                                },
                                                "text": "mdi-information"
                                            },
                                            {
                                                "component": "span",
                                                "props": {"class": "flex-grow-1"},
                                                "text": "M-Team每80000魔力可购买一个临时邀请"
                                            },
                                            {
                                                "component": "VBtn",
                                                "props": {
                                                    "variant": "text",
                                                    "density": "compact",
                                                    "color": "primary",
                                                    "href": site_url_lower + "mybonus",
                                                    "target": "_blank",
                                                    "size": "small"
                                                },
                                                "content": [
                                                    {
                                                        "component": "VIcon",
                                                        "props": {
                                                            "start": True,
                                                            "size": "small"
                                                        },
                                                        "text": "mdi-store"
                                                    },
                                                    {
                                                        "component": "span",
                                                        "text": "前往商店购买"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            })
                            
                            # M-Team特殊显示时跳过原来的警告提示
                            error_message = ""
                            reason = ""
                    
                    # 通用NexusPHP和蝶粉站点处理
                    elif bonus > 0 and (permanent_invite_price > 0 or temporary_invite_price > 0):
                        
                        # 计算可购买邀请数量
                        can_buy_permanent = 0
                        can_buy_temporary = 0
                        
                        if permanent_invite_price > 0:
                            can_buy_permanent = int(bonus / permanent_invite_price)
                        
                        if temporary_invite_price > 0:
                            can_buy_temporary = int(bonus / temporary_invite_price)
                        # 向药单打标可购买临药永药数量
                        self.presc.setCBP(site_name,can_buy_permanent)
                        self.presc.setCBT(site_name,can_buy_temporary)
                        # 计算购买邀请后剩余魔力
                        remaining_bonus = bonus
                        if can_buy_permanent > 0 and permanent_invite_price > 0:
                            remaining_bonus = bonus % permanent_invite_price
                        elif can_buy_temporary > 0 and temporary_invite_price > 0:
                            remaining_bonus = bonus % temporary_invite_price
                        
                        # 添加魔力值信息卡片
                        site_card["content"].append({
                            "component": "VCardText",
                            "props": {
                                "class": "py-0"
                            },
                            "content": [
                                {
                                    "component": "VRow",
                                    "props": {
                                        "dense": True
                                    },
                                    "content": [
                                        # 魔力值
                                        {
                                            "component": "VCol",
                                            "props": {"cols": 3},
                                            "content": [{
                                                "component": "div",
                                                "props": {
                                                    "class": "d-flex align-center py-2"
                                                },
                                                "content": [
                                                    {
                                                        "component": "VIcon",
                                                        "props": {
                                                            "color": "orange",
                                                            "size": "small",
                                                            "class": "mr-2"
                                                        },
                                                        "text": "mdi-diamond"
                                                    },
                                                    {
                                                        "component": "div",
                                                        "content": [
                                                            {
                                                                "component": "div",
                                                                "props": {"class": "text-subtitle-2 font-weight-medium"},
                                                                "text": str(bonus)
                                                            },
                                                            {
                                                                "component": "div",
                                                                "props": {"class": "text-caption"},
                                                                "text": "魔力值"
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }]
                                        },
                                        # 可购买永久邀请
                                        {
                                            "component": "VCol",
                                            "props": {"cols": {
                                                "cols": 4,
                                                "md": 3
                                            }},
                                            "content": [] if permanent_invite_price <= 0 else [{
                                                "component": "div",
                                                "props": {
                                                    "class": "d-flex align-center py-2"
                                                },
                                                "content": [
                                                    {
                                                        "component": "VIcon",
                                                        "props": {
                                                            "color": "purple",
                                                            "size": "small",
                                                            "class": "mr-2"
                                                        },
                                                        "text": "mdi-ticket-confirmation"
                                                    },
                                                    {
                                                        "component": "div",
                                                        "content": [
                                                            {
                                                                "component": "div",
                                                                "props": {"class": "text-subtitle-2 font-weight-medium"},
                                                                "text": f"{can_buy_permanent}个 ({permanent_invite_price}魔力/个)" if can_buy_permanent > 0 else f"0个 (需{permanent_invite_price}魔力)"
                                                            },
                                                            {
                                                                "component": "div",
                                                                "props": {"class": "text-caption"},
                                                                "text": "可购买永久邀请"
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }]
                                        },
                                        # 可购买临时邀请
                                        {
                                            "component": "VCol",
                                            "props": {"cols": {
                                                "cols": 4,
                                                "md": 3
                                            }},
                                            "content": [] if temporary_invite_price <= 0 else [{
                                                "component": "div",
                                                "props": {
                                                    "class": "d-flex align-center py-2"
                                                },
                                                "content": [
                                                    {
                                                        "component": "VIcon",
                                                        "props": {
                                                            "color": "pink",
                                                            "size": "small",
                                                            "class": "mr-2"
                                                        },
                                                        "text": "mdi-ticket"
                                                    },
                                                    {
                                                        "component": "div",
                                                        "content": [
                                                            {
                                                                "component": "div",
                                                                "props": {"class": "text-subtitle-2 font-weight-medium"},
                                                                "text": f"{can_buy_temporary}个 ({temporary_invite_price}魔力/个)" if can_buy_temporary > 0 else f"0个 (需{temporary_invite_price}魔力)"
                                                            },
                                                            {
                                                                "component": "div",
                                                                "props": {"class": "text-caption"},
                                                                "text": "可购买临时邀请"
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }]
                                        },
                                        # 按钮占位
                                        {
                                            "component": "VCol",
                                            "props": {"cols": 3},
                                            "content": []
                                        }
                                    ]
                                }
                            ]
                        })
                        
                        # 添加提示信息和购买按钮
                        if permanent_invite_price > 0 or temporary_invite_price > 0:
                            # 构造价格文本，确保类型转换
                            price_text = "站点商店邀请价格: "
                            parts = []
                            
                            if permanent_invite_price > 0:
                                parts.append(f"永久邀请 {permanent_invite_price} 魔力")
                            
                            if temporary_invite_price > 0:
                                parts.append(f"临时邀请 {temporary_invite_price} 魔力")
                            
                            price_text += "，".join(parts)
                            
                            site_card["content"].append({
                                "component": "VCardText",
                                "props": {
                                    "class": "py-1"
                                },
                                "content": [
                                    {
                                        "component": "VAlert",
                                        "props": {
                                            "type": "info",
                                            "variant": "tonal",
                                            "density": "compact",
                                            "class": "my-1 d-flex align-center"
                                        },
                                        "content": [
                                            {
                                                "component": "VIcon",
                                                "props": {
                                                    "start": True,
                                                    "size": "small"
                                                },
                                                "text": "mdi-information"
                                            },
                                            {
                                                "component": "span",
                                                "props": {"class": "flex-grow-1"},
                                                "text": price_text
                                            },
                                            {
                                                "component": "VBtn",
                                                "props": {
                                                    "variant": "text",
                                                    "density": "compact",
                                                    "color": "primary",
                                                    "href": site_url_lower + "mybonus.php",
                                                    "target": "_blank",
                                                    "size": "small"
                                                },
                                                "content": [
                                                    {
                                                        "component": "VIcon",
                                                        "props": {
                                                            "start": True,
                                                            "size": "small"
                                                        },
                                                        "text": "mdi-store"
                                                    },
                                                    {
                                                        "component": "span",
                                                        "text": "前往商店购买"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            })
                        

                    # 只有在有邀请列表时才添加表格
                    if invitees:
                        table_rows = []
                        for invitee in invitees:
                            # 判断用户是否被ban或分享率较低
                            is_banned = invitee.get('enabled', '').lower() == 'no'
                            
                            # 使用ratio_health和ratio_label字段
                            ratio_health = invitee.get('ratio_health', '')
                            ratio_label = invitee.get('ratio_label', ['', ''])

                            # 根据ratio_health设置行样式
                            row_class = ""
                            if is_banned:
                                row_class = "error"  # 被ban用户使用红色背景
                            elif ratio_health == "neutral":
                                row_class = "grey-lighten-3"  # 无数据使用灰色背景
                            elif ratio_health == "warning":
                                row_class = "warning-lighten-4"  # 警告使用橙色背景
                            elif ratio_health == "danger":
                                row_class = "error-lighten-4"  # 危险使用红色背景

                            # 设置分享率样式
                            ratio_class = ""
                            if ratio_health == "excellent":
                                ratio_class = "text-success font-weight-bold"
                            elif ratio_health == "good":
                                ratio_class = "text-success"
                            elif ratio_health == "warning":
                                ratio_class = "text-warning font-weight-bold"
                            elif ratio_health == "danger":
                                ratio_class = "text-error font-weight-bold"
                            elif ratio_health == "neutral":
                                ratio_class = "text-grey"

                            # 创建行
                            table_rows.append({
                                "component": "tr",
                                "props": {
                                    "class": row_class
                                },
                                "content": [
                                    {
                                        "component": "td",
                                        "content": [{
                                            "component": "VBtn",
                                            "props": {
                                                "variant": "text",
                                                "href": invitee.get("profile_url", ""),
                                                "target": "_blank",
                                                "density": "compact"
                                            },
                                            "text": invitee.get("username", "")
                                        }]
                                    },
                                    {"component": "td",
                                        "text": invitee.get("email", "")},
                                    {"component": "td", "text": invitee.get(
                                        "uploaded", "")},
                                    {"component": "td", "text": invitee.get(
                                        "downloaded", "")},
                                    {
                                        "component": "td",
                                        "props": {
                                            "class": ratio_class
                                        },
                                        "text": invitee.get("ratio", "")
                                    },
                                    {"component": "td", "text": invitee.get(
                                        "seeding", "")},
                                    {"component": "td", "text": invitee.get(
                                        "seeding_size", "")},
                                    {"component": "td", "text": invitee.get(
                                        "seed_magic", "") or invitee.get("magic", "") or invitee.get("seed_time", "")},
                                    {"component": "td", "text": invitee.get(
                                        "seed_bonus", "") or invitee.get("invitee_bonus", "") or invitee.get("bonus", "")},
                                    {"component": "td", "text": invitee.get(
                                        "last_seed_report", "") or invitee.get("last_seen", "")},
                                    {
                                        "component": "td",
                                        "props": {
                                            "class": ("text-success" if invitee.get('status') == '已确认' else "") +
                                                     (" text-error font-weight-bold" if invitee.get('enabled', '').lower() == 'no' else "")
                                        },
                                        "text": invitee.get("status", "") + (" (已禁用)" if invitee.get('enabled', '').lower() == 'no' else "")
                                    }
                                ]
                            })

                        site_card["content"].append({
                            "component": "VCardText",
                            "props": {
                                "class": "pt-0 px-2"
                            },
                            "content": [{
                                "component": "VExpansionPanels",
                                "props": {
                                    "variant": "accordion"
                                },
                                "content": [{
                                    "component": "VExpansionPanel",
                                    "content": [
                                        {
                                            "component": "VExpansionPanelTitle",
                                            "content": [
                                                {
                                                    "component": "div",
                                                    "props": {
                                                        "class": "d-flex align-center"
                                                    },
                                                    "content": [
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "color": "primary",
                                                                "size": "small",
                                                                "class": "mr-2"
                                                            },
                                                            "text": "mdi-account-group"
                                                        },
                                                        {
                                                            "component": "span",
                                                            "text": f"后宫成员列表 ({len(invitees)}人)"
                                                        },
                                                        {
                                                            "component": "VSpacer"
                                                        },
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "size": "small",
                                                                "color": "error",
                                                                "class": "mr-1"
                                                            },
                                                            "text": "mdi-alert-circle" if low_ratio_count > 0 else ""
                                                        },
                                                        {
                                                            "component": "span",
                                                            "props": {"class": "text-caption mr-3"},
                                                            "text": f"{low_ratio_count}人低分享" if low_ratio_count > 0 else ""
                                                        },
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "size": "small",
                                                                "color": "error",
                                                                "class": "mr-1"
                                                            },
                                                            "text": "mdi-account-cancel" if banned_count > 0 else ""
                                                        },
                                                        {
                                                            "component": "span",
                                                            "props": {"class": "text-caption mr-3"},
                                                            "text": f"{banned_count}人禁用" if banned_count > 0 else ""
                                                        },
                                                        {
                                                            "component": "VIcon",
                                                            "props": {
                                                                "size": "small",
                                                                "color": "#9E9E9E",
                                                                "class": "mr-1"
                                                            },
                                                            "text": "mdi-database-off" if no_data_count > 0 else ""
                                                        },
                                                        {
                                                            "component": "span",
                                                            "props": {"class": "text-caption"},
                                                            "text": f"{no_data_count}人无数据" if no_data_count > 0 else ""
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            "component": "VExpansionPanelText",
                                            "content": [{
                                                "component": "VTable",
                                                "props": {
                                                    "hover": True,
                                                    "density": "compact",
                                                    "fixed-header": False,
                                                    "class": "site-invitees-table text-caption",
                                                },
                                                "content": [{
                                                    "component": "thead",
                                                    "content": [{
                                                        "component": "tr",
                                                        "props": {
                                                            "class": "bg-primary-lighten-5"
                                                        },
                                                        "content": [
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#2196F3"
                                                                                },
                                                                                "text": "mdi-account"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "用户名"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#4CAF50"
                                                                                },
                                                                                "text": "mdi-email"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "邮箱"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#F44336"
                                                                                },
                                                                                "text": "mdi-arrow-up-thick"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "上传量"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#FF9800"
                                                                                },
                                                                                "text": "mdi-arrow-down-thick"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "下载量"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#2196F3"
                                                                                },
                                                                                "text": "mdi-poll"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "分享率"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#2196F3"
                                                                                },
                                                                                "text": "mdi-database"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "做种数"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#1976D2"
                                                                                },
                                                                                "text": "mdi-harddisk"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "做种体积"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#673AB7"
                                                                                },
                                                                                "text": "mdi-magic"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "魔力值"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#009688"
                                                                                },
                                                                                "text": "mdi-star"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "加成"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#607D8B"
                                                                                },
                                                                                "text": "mdi-clock"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "最后报告"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "th", 
                                                                "props": {"class": "text-caption", "style": "white-space: nowrap; padding: 4px 8px;"},
                                                                "content": [
                                                                    {
                                                                        "component": "div",
                                                                        "props": {
                                                                            "class": "d-flex align-center"
                                                                        },
                                                                        "content": [
                                                                            {
                                                                                "component": "VIcon",
                                                                                "props": {
                                                                                    "size": "14",
                                                                                    "class": "mr-1",
                                                                                    "color": "#00BCD4"
                                                                                },
                                                                                "text": "mdi-information"
                                                                            },
                                                                            {
                                                                                "component": "span",
                                                                                "text": "状态"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }]
                                                }, {
                                                    "component": "tbody",
                                                    "content": table_rows
                                                }]
                                            }]
                                        }
                                    ]
                                }]
                            }]
                        })
                    
                    cards.append(site_card)
                                # 添加药单组件到总览下方
            drug_component = self.presc.getComponent()
            if drug_component:
                page_content.append(drug_component)
            
            # 将站点卡片添加到页面
            page_content.extend(cards)

            # 添加说明提示
            if not cards:
                page_content.append({
                    "component": "VAlert",
                    "props": {
                        "type": "warning",
                        "text": "暂无数据，请先在配置中选择要管理的站点，并打开\"立即运行一次\"开关获取数据",
                        "variant": "tonal",
                        "class": "mt-4"
                    }
                })
            # 删除这行，因为我们已经在后宫总览下方添加了药单
            # page_content.insert(0,self.presc.getComponent())
            return page_content
            
        except Exception as e:
            logger.error(f"生成详情页面失败: {str(e)}")
            return [{
                "component": "VAlert",
                "props": {
                    "type": "error",
                    "text": f"生成详情页面失败: {str(e)}"
                }
            }]

    def stop_service(self):
        """
        停止现有服务
        """
        try:
            if hasattr(self, '_scheduler') and self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
                logger.info("后宫管理系统服务已停止")
        except Exception as e:
            logger.error(f"停止后宫管理系统服务失败: {str(e)}")

    def _get_site_invite_data(self, site_name):
        """
        获取站点邀请页面数据
        """
        try:
            # 获取站点信息
            site_info = None
            for indexer in self.sites.get_indexers():
                if indexer.get("name") == site_name:
                    site_info = indexer
                    break
                    
            if not site_info:
                logger.error(f"站点 {site_name} 信息不存在")
                return {
                    "error": "站点信息不存在",
                    "invite_status": {
                        "can_invite": False,
                        "permanent_count": 0,
                        "temporary_count": 0,
                        "reason": "站点信息不存在"
                    }
                }
                
            site_url = site_info.get("url", "").strip()
            site_cookie = site_info.get("cookie", "").strip()
            ua = site_info.get("ua", "").strip()
            site_id = site_info.get("id", "")
            
            # 检查是否是M-Team站点
            is_mteam = False
            site_url_lower = site_url.lower()
            mteam_features = ["m-team", "api.m-team.cc", "api.m-team.io"]
            for feature in mteam_features:
                if feature in site_url_lower:
                    is_mteam = True
                    logger.info(f"站点 {site_name} 匹配到M-Team特征: {feature}")
                    break
            
            # 如果是M-Team站点，检查API认证信息
            if is_mteam:
                api_key = site_info.get("apikey", "").strip()
                token = site_info.get("token", "").strip()
                
                if not all([site_url, api_key, token, ua]):
                    missing_fields = []
                    if not site_url:
                        missing_fields.append("站点URL")
                    if not api_key:
                        missing_fields.append("API Key")
                    if not token:
                        missing_fields.append("Authorization Token")
                    if not ua:
                        missing_fields.append("User-Agent")
                        
                    error_msg = f"M-Team API认证信息不完整: {', '.join(missing_fields)}"
                    logger.error(f"站点 {site_name} {error_msg}")
                    return {
                        "error": error_msg,
                        "invite_status": {
                            "can_invite": False,
                            "permanent_count": 0,
                            "temporary_count": 0,
                            "reason": error_msg
                        }
                    }
            # 对于非M-Team站点，检查Cookie
            elif not all([site_url, site_cookie, ua]):
                missing_fields = []
                if not site_url:
                    missing_fields.append("站点URL")
                if not site_cookie:
                    missing_fields.append("Cookie")
                if not ua:
                    missing_fields.append("User-Agent")
                    
                error_msg = f"站点信息不完整: {', '.join(missing_fields)}"
                logger.error(f"站点 {site_name} {error_msg}")
                return {
                    "error": error_msg,
                    "invite_status": {
                        "can_invite": False,
                        "permanent_count": 0,
                        "temporary_count": 0,
                        "reason": error_msg
                    }
                }

            # 先验证此站点是否在用户选择的站点列表中
            if self._nexus_sites and str(site_id) not in [str(x) for x in self._nexus_sites]:
                logger.warning(f"站点 {site_name} 不在用户选择的站点列表中，跳过处理")
                return {
                    "error": "站点未被选择",
                    "invite_status": {
                        "can_invite": False,
                        "permanent_count": 0,
                        "temporary_count": 0,
                        "reason": "站点未被选择"
                    }
                }

            # 构建请求Session
            session = requests.Session()
            
            # 根据站点类型设置不同的请求头
            if is_mteam:
                # M-Team站点使用API认证方式
                session.headers.update({
                    "Content-Type": "application/json",
                    "User-Agent": ua,
                    "Accept": "application/json, text/plain, */*",
                    "Authorization": token,
                    "API-Key": api_key,
                    "Referer": site_url
                })
                
                # 测试API认证是否有效
                test_url = site_url
                test_response = session.get(test_url, timeout=(10, 30))
                if test_response.status_code >= 400:
                    logger.error(f"站点 {site_name} API认证测试失败，状态码: {test_response.status_code}")
                    return {
                        "error": f"API认证失败，请检查Token是否有效，状态码: {test_response.status_code}",
                        "invite_status": {
                            "can_invite": False,
                            "permanent_count": 0,
                            "temporary_count": 0,
                            "reason": f"API认证失败，请检查Token是否有效，状态码: {test_response.status_code}"
                        }
                    }
            else:
                # 普通站点使用Cookie认证
                session.headers.update({
                    'User-Agent': ua,
                    'Cookie': site_cookie,
                    'Referer': site_url,
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin'
                })
                
                # 尝试验证Cookie有效性
                test_url = site_url
                test_response = session.get(test_url, timeout=(10, 30))
                if test_response.status_code >= 400:
                    logger.error(f"站点 {site_name} Cookie验证失败，状态码: {test_response.status_code}")
                    return {
                        "error": f"Cookie验证失败，状态码: {test_response.status_code}",
                        "invite_status": {
                            "can_invite": False,
                            "permanent_count": 0,
                            "temporary_count": 0,
                            "reason": f"Cookie验证失败，状态码: {test_response.status_code}"
                        }
                    }

            # 使用站点处理器
            logger.info(f"站点 {site_name} 开始处理邀请数据")
            
            # 根据站点类型选择不同的处理器
            if is_mteam:
                logger.info(f"站点 {site_name} 使用M-Team处理器")
                from plugins.nexusinvitee.sites.mteam import MTeamHandler
                handler = MTeamHandler()
            elif "hdchina" in site_url.lower():
                logger.info(f"站点 {site_name} 使用HDChina处理器")
                from plugins.nexusinvitee.sites.hdchina import HDChinaHandler
                handler = HDChinaHandler()
            else:
                # 查找匹配的处理器
                handler = ModuleLoader.get_handler_for_site(site_url, self._site_handlers)
                if not handler:
                    # 如果找不到合适的处理器，使用通用NexusPHP处理器
                    logger.info(f"站点 {site_name} 未找到专用处理器，使用默认NexusPHP处理器")
                    from plugins.nexusinvitee.sites.nexusphp import NexusPhpHandler
                    handler = NexusPhpHandler()
            
            # 使用处理器解析邀请页面
            site_data = handler.parse_invite_page(site_info, session)
            
            
            # 检查站点数据结构是否正确
            if "invite_status" in site_data:
                # 检查临时邀请数量
                temp_count = site_data["invite_status"].get("temporary_count", 0)
                if temp_count > 0:
                    logger.info(f"站点 {site_name} 有 {temp_count} 个临时邀请")
                
                # 确保不可邀请原因也被正确处理和显示
                if not site_data["invite_status"].get("can_invite", False):
                    reason = site_data["invite_status"].get("reason", "")
                    if reason:
                        logger.info(f"站点 {site_name} 不可邀请原因: {reason}")
            
            return site_data

        except Exception as e:
            logger.error(f"获取站点 {site_name} 邀请数据失败: {str(e)}")
            return {
                "error": f"获取站点邀请数据失败: {str(e)}",
                "invite_status": {
                    "can_invite": False,
                    "permanent_count": 0,
                    "temporary_count": 0,
                    "reason": f"获取站点邀请数据失败: {str(e)}"
                }
            }

    def get_invitees(self, apikey: str = None, site_name: str = None) -> dict:
        """
        获取后宫成员API接口
        """
        if apikey and apikey != settings.API_TOKEN:
            return {"code": 1, "message": "API令牌错误!"}
            
        try:
            # 从数据文件获取站点数据
            site_data = self.data_manager.get_site_data(site_name)
            
            # 获取最后更新时间
            last_update = self.data_manager.get_last_update_time()
            
            if not site_data:
                if site_name:
                    return {"code": 1, "message": f"站点 {site_name} 数据不存在"}
                else:
                    return {"code": 1, "message": "暂无站点数据"}

            return {
                "code": 0,
                "message": "获取成功",
                "data": {
                    "sites": site_data,
                    "last_update": last_update
            }
            }
        except Exception as e:
            logger.error(f"获取后宫成员失败: {str(e)}")
            return {"code": 1, "message": f"获取后宫成员失败: {str(e)}"}

    def refresh_data(self, apikey: str = None) -> dict:
        """
        强制刷新所有站点数据API接口
        """
        if apikey and apikey != settings.API_TOKEN:
            return {"code": 1, "message": "API令牌错误!"}

        try:
            # 重新加载站点处理器以确保使用最新的处理逻辑
            self._site_handlers = ModuleLoader.load_site_handlers()
            logger.info(f"已重新加载 {len(self._site_handlers)} 个站点处理器")
            
            # 调用refresh_all_sites方法刷新数据
            result = self.refresh_all_sites()

            if result and result.get("success", 0) > 0:
                # 获取最新的更新时间和站点数据
                site_data = self.data_manager.get_site_data()
                last_update = self.data_manager.get_last_update_time()

                return {
                    "code": 0,
                    "message": f"增量数据刷新成功: {result.get('success')}个站点, 失败: {result.get('error')}个站点",
                    "data": {
                        "last_update": last_update,
                        "site_count": len(site_data),
                        "success": result.get("success", 0),
                        "error": result.get("error", 0)
                    }
                }
            else:
                return {"code": 1, "message": "数据刷新失败，没有成功刷新的站点"}
            
        except Exception as e:
            logger.error(f"强制刷新数据失败: {str(e)}")
            return {"code": 1, "message": f"强制刷新数据失败: {str(e)}"}

    def _get_user_id(self, session: requests.Session, site_info: Dict[str, Any]) -> str:
        """
        从站点获取用户ID
        :param session: 请求会话
        :param site_info: 站点信息
        :return: 用户ID
        """
        try:
            site_url = site_info.get("url", "").strip()
            site_name = site_info.get("name", "")
            
            # 访问个人页面提取ID
            profile_url = urljoin(site_url, "index.php")
            response = session.get(profile_url, timeout=(5, 15))
            response.raise_for_status()
            html_content = response.text
            
            # 尝试从多种常见格式中提取用户ID
            # 方法1：从class="searchrecord td"中提取
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找欢迎语中的用户名和ID链接
            welcome_text = soup.select_one('.welcome')
            if welcome_text:
                user_link = welcome_text.select_one('a[href*="userdetails.php"]')
                if user_link:
                    href = user_link.get('href', '')
                    id_match = re.search(r'id=(\d+)', href)
                    if id_match:
                        return id_match.group(1)
            
            # 方法2：从个人资料链接中提取
            for pattern in [
                r'userdetails\.php\?id=(\d+)',
                r'getusertorrentlistajax\.php\?userid=(\d+)',
                r'<input[^>]*name=["\']passkey["\'][^>]*value=["\']([a-zA-Z0-9]+)["\']',
                r'passkey=([a-zA-Z0-9]+)',
                r'usercp\.php\?action=personal&userid=(\d+)',
                r'id=(\d+)',
                r'uid=(\d+)'
            ]:
                matches = re.search(pattern, html_content)
                if matches:
                    return matches.group(1)
            
            # 方法3：尝试通过访问具体的用户资料页面
            try:
                user_link = None
                # 找到包含用户名的链接
                for a_tag in soup.select('a[href*="userdetails.php"], a[href*="user.php"]'):
                    if a_tag.get_text().strip():
                        user_link = a_tag
                        break
                
                if user_link:
                    href = user_link.get('href', '')
                    if 'id=' in href:
                        id_match = re.search(r'id=(\d+)', href)
                        if id_match:
                            return id_match.group(1)
                    
                    # 访问用户链接，从重定向或内容中提取用户ID
                    user_response = session.get(urljoin(site_url, href), timeout=(5, 15))
                    user_response.raise_for_status()
                    user_content = user_response.text
                    
                    # 在返回的内容中搜索用户ID
                    for pattern in [r'userdetails\.php\?id=(\d+)', r'passkey=([a-zA-Z0-9]+)', r'id=(\d+)', r'uid=(\d+)']:
                        matches = re.search(pattern, user_content)
                        if matches:
                            return matches.group(1)
            except Exception as e:
                logger.warning(f"通过用户资料页面获取用户ID失败: {str(e)}")
            
            # 方法4：尝试从邀请页面获取
            try:
                invite_url = urljoin(site_url, "invite.php")
                invite_response = session.get(invite_url, timeout=(5, 15))
                invite_response.raise_for_status()
                invite_content = invite_response.text
                
                # 搜索邀请页面中的用户ID
                for pattern in [r'id=(\d+)', r'uid=(\d+)', r'user(?:id|_id)=(\d+)']:
                    matches = re.search(pattern, invite_content)
                    if matches:
                        return matches.group(1)
            except Exception as e:
                logger.warning(f"通过邀请页面获取用户ID失败: {str(e)}")
            
            # 未能从任何途径获取用户ID
            logger.error(f"无法从站点 {site_name} 获取用户ID")
            return ""
            
        except Exception as e:
            logger.error(f"获取用户ID失败: {str(e)}")
            return ""

    def refresh_all_sites(self) -> Dict[str, int]:
        """
        刷新所有站点数据
        """
        try:
            # 设置刷新标志防止重复刷新
            if hasattr(self, '_refreshing') and self._refreshing:
                logger.warning("后宫管理系统数据刷新已在进行中，跳过重复刷新")
                return {"success": 0, "error": 0, "message": "刷新已在进行中"}
            
            self._refreshing = True
            
            # 记录刷新开始 - 说明是增量更新模式
            logger.info("开始增量刷新站点数据，只更新选择的站点，失败时保留旧数据")
            
            # 重新加载站点处理器
            self._site_handlers = ModuleLoader.load_site_handlers()
            logger.info(f"加载了 {len(self._site_handlers)} 个站点处理器")
            
            # 获取所有站点配置
            all_sites = self.sites.get_indexers()
            
            # 筛选站点配置 - 如果_nexus_sites为空，则选择所有站点
            selected_sites = []
            if not self._nexus_sites:
                logger.info("未选择任何站点，将使用所有站点")
                selected_sites = all_sites
            else:
                for site in all_sites:
                    site_id = site.get("id")
                    # 转换为字符串进行比较
                    site_id_str = str(site_id)
                    nexus_sites_str = [str(x) for x in self._nexus_sites]
                    
                    # 调试输出当前站点ID
                    logger.debug(f"检查站点ID: {site_id}，类型: {type(site_id)}")
                    
                    if site_id_str in nexus_sites_str:
                        selected_sites.append(site)
                        logger.debug(f"匹配到站点: {site.get('name')} (ID: {site_id})")
            
            if selected_sites:
                logger.debug(f"将刷新 {len(selected_sites)} 个站点的数据: {', '.join([site.get('name', '') for site in selected_sites])}")
            else:
                logger.warning("没有发现可供刷新的站点，请检查站点选择配置")
                logger.debug(f"所有站点ID: {[site.get('id') for site in all_sites]}")
                logger.debug(f"选择的站点ID: {self._nexus_sites}")
                return {"success": 0, "error": 0, "message": "没有发现可供刷新的站点"}
            
            # 统计成功/失败站点数
            success_count = 0
            error_count = 0
            error_details = []
            
            # 获取现有数据
            existing_data = self.data_manager.get_site_data()
            
            # 逐个刷新站点数据
            for site in selected_sites:
                site_name = site.get("name", "")
                
                logger.debug(f"开始获取站点 {site_name} 的后宫数据...")
                
                site_data = self._get_site_invite_data(site_name)
                
                # --- 修改开始: 增强失败判断逻辑 ---
                is_successful = True
                error_msg = ""
                
                if "error" in site_data:
                    # 情况1: _get_site_invite_data 内部捕获到异常
                    is_successful = False
                    error_msg = site_data.get('error', '未知错误')
                else:
                    # 情况2: 检查 parse_invite_page 返回的 reason 是否表明失败
                    invite_status = site_data.get("invite_status", {})
                    reason = invite_status.get("reason", "")
                    
                    # 定义表明失败的关键字或模式 (即使没有异常)
                    # 使用 r 前缀确保是原始字符串，避免反斜杠转义问题
                    failure_indicators = [
                        r"访问邀请页面失败",
                        r"无法获取用户ID",
                        r"未登录或Cookie已失效",
                        r"初始化失败",
                        r"网络错误",
                        r"发生错误",
                        r"解析站点.*时发生意外错误",
                        r"站点信息不完整", # 加入对站点信息不完整的检查
                    ]
                    
                    # 使用正则表达式匹配，因为 "解析站点..." 包含变量
                    if reason and any(re.search(indicator, reason, re.IGNORECASE) for indicator in failure_indicators):
                        is_successful = False
                        error_msg = reason # 使用 handler 返回的具体原因作为错误消息
                        
                # --- 修改结束 ---
                        
                if not is_successful:
                    if not error_msg: # 确保总有一个错误消息
                        error_msg = "未知原因导致刷新失败"
                    logger.error(f"站点 {site_name} 数据刷新失败: {error_msg}")
                    error_count += 1
                    error_details.append({"site_name": site_name, "msg": error_msg})
                    
                    # 保留旧数据逻辑 (保持不变)
                    old_data = existing_data.get(site_name, {}).get("data", {})
                    if old_data:
                        old_invitees = old_data.get("invitees", [])
                        old_status = old_data.get("invite_status", {})
                        logger.info(f"站点 {site_name} 保留旧数据: {len(old_invitees)}人, "
                                   f"永久邀请:{old_status.get('permanent_count', 0)}个, "
                                   f"临时邀请:{old_status.get('temporary_count', 0)}个")
                    else:
                        logger.info(f"站点 {site_name} 无旧数据可保留")

                    failed_site_data = dict(old_data) if isinstance(old_data, dict) else {}
                    failed_status = failed_site_data.get("invite_status", {})
                    failed_status = dict(failed_status) if isinstance(failed_status, dict) else {}
                    failed_status.update({
                        "can_invite": False,
                        "reason": error_msg
                    })
                    failed_site_data["invite_status"] = failed_status
                    failed_site_data.setdefault("invitees", old_data.get("invitees", []) if isinstance(old_data, dict) else [])
                    failed_site_data["error"] = error_msg
                    failed_site_data["fetch_failed"] = True
                    self.data_manager.update_site_data(site_name, failed_site_data)
                else:
                    # 成功逻辑 (保持不变)
                    invite_status = site_data.get("invite_status", {})
                    invitees = site_data.get("invitees", [])
                    perm_count = invite_status.get("permanent_count", 0)
                    temp_count = invite_status.get("temporary_count", 0)
                    can_invite = invite_status.get("can_invite", False)
                    reason = invite_status.get("reason", "")
                    
                    logger.info(f"站点 {site_name} 数据刷新成功，已邀请 {len(invitees)} 人，永久邀请 {perm_count} 个，临时邀请 {temp_count} 个")
                    
                    # 在成功时也记录一下原因（例如 可购买邀请、具体原因）
                    if reason:
                        if can_invite:
                            logger.info(f"站点 {site_name} 可邀请原因: {reason}")
                        else:
                            logger.info(f"站点 {site_name} 不可邀请原因: {reason}")

                    # 保存站点数据 (保持不变)
                    self.data_manager.update_site_data(site_name, site_data)
                    success_count += 1
            
            # 发送通知
            if self._notify:
                self._send_refresh_notification(success_count, error_count, error_details)
            
            logger.info(f"增量刷新完成: 成功 {success_count} 个站点, 失败 {error_count} 个站点")
            
            return {"success": success_count, "error": error_count}
            
        finally:
            # 清除刷新标志
            self._refreshing = False
    
    def _send_refresh_notification(self, success_count, error_count,error_details:List=None):
        """
        发送刷新结果通知
        """
        try:
            # 从data_manager获取站点数据
            cached_data = {}
            site_data = self.data_manager.get_site_data()
            for site_name, site_info in site_data.items():
                cached_data[site_name] = site_info
                
            # 计算所有站点统计信息
            total_invitees = 0
            total_low_ratio = 0
            total_banned = 0
            total_no_data = 0

            for site_name, cache in cached_data.items():
                site_cache_data = cache.get("data", {})
                invitees = []
                
                # 尝试不同的数据结构路径获取邀请列表
                possible_paths = [
                    ["invitees"],
                    ["data", "invitees"],
                    ["data", "data", "invitees"]
                ]
                
                for path in possible_paths:
                    result = get_nested_value(site_cache_data, path, [])
                    if result:
                        invitees = result
                        break

                # 统计各项数据
                total_invitees += len(invitees)

                # 统计用户状态 - 使用ratio_health字段
                banned_count = sum(1 for i in invitees if i.get('enabled', '').lower() == 'no')
                low_ratio_count = sum(1 for i in invitees if i.get('ratio_health') in ['warning', 'danger'])
                no_data_count = sum(1 for i in invitees if i.get('ratio_health') == 'neutral')

                # 累加到总数
                total_banned += banned_count
                total_low_ratio += low_ratio_count
                total_no_data += no_data_count

                logger.info(f"站点 {site_name} 统计结果: 总人数={len(invitees)}, 低分享率={low_ratio_count}, 已禁用={banned_count}, 无数据={no_data_count}")
            
            title = "后宫管理系统 - 增量刷新结果"
            if success_count > 0 or error_count > 0:
                # --- 修改开始: 添加图标美化通知文本 ---
                text = f"刷新完成: ✅ 成功 {success_count} 个，❌ 失败 {error_count} 个站点\n"
                if error_details is not None and len(error_details) > 0:
                    text += "\n🔻失败详情🔻:\n"
                    for item in error_details:
                        # 使用 🔻 标记失败项
                        text += f"🔻 [{item['site_name']}]: {item['msg']}\n"
                    text += "\n"
                # 保持原有统计信息的图标
                text += f"👨‍👩‍👧‍👦 总邀请人数: {total_invitees}人\n"
                text += f"⚠️ 分享率低于1.0: {total_low_ratio}人\n"
                text += f"🚫 已禁用用户: {total_banned}人\n"
                text += f"🔄 无数据用户: {total_no_data}人\n\n"
                # --- 修改结束 ---
                
                # 添加刷新时间
                text += f"🕙 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                
                # 使用post_message发送通知
                self.post_message(
                    mtype=NotificationType.SiteMessage,
                    title=title,
                    text=text
                )
                logger.info(f"发送通知: {title} - {text}")
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
            
    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        if self._enabled and self._cron:
            try:
                # 检查是否为5位cron表达式
                if str(self._cron).strip().count(" ") == 4:
                    return [{
                        "id": "nexusinvitee",
                        "name": "后宫管理系统",
                        "trigger": CronTrigger.from_crontab(self._cron),
                        "func": self.refresh_all_sites,
                        "kwargs": {}
                    }]
                else:
                    logger.error("cron表达式格式错误")
                    return []
            except Exception as err:
                logger.error(f"定时任务配置错误：{str(err)}")
                return []
        return []
        
    @staticmethod
    def get_api_handlers():
        """
        获取API接口
        """
        return {
            "/get_invitees": {"func": nexusinvitee.get_invitees, "methods": ["GET"], "desc": "获取所有站点邀请数据"},
            "/refresh": {"func": nexusinvitee.refresh_data, "methods": ["GET"], "desc": "强制刷新站点数据"}
        }

    def update_config(self, request: dict) -> Response:
        """
        更新插件配置
        """
        try:
            # 读取配置
            self._enabled = request.get("enabled", False)
            self._notify = request.get("notify", False)
            self._cron = request.get("cron", "0 9 * * *")
            self._onlyonce = request.get("onlyonce", False)
            
            # 获取选中站点列表
            self._nexus_sites = []
            if "site_ids" in request:
                for site_id in request.get("site_ids", []):
                    # 确保site_id为整数
                    try:
                        if isinstance(site_id, str) and site_id.isdigit():
                            self._nexus_sites.append(int(site_id))
                        elif isinstance(site_id, int):
                            self._nexus_sites.append(site_id)
                    except:
                        pass
            
            # 记录站点ID，用于调试
            logger.info(f"已选择站点ID: {self._nexus_sites}")
            
            # 保存配置
            self.__update_config()
            
            # 如果开启了立即运行一次
            if self._onlyonce:
                try:
                    # 定时服务
                    if hasattr(self, '_scheduler') and self._scheduler:
                        self.stop_service()  # 先停止已有服务
                    
                    self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                    logger.debug("立即运行一次开关被打开，将在3秒后执行刷新")
                    self._scheduler.add_job(func=self.refresh_all_sites, trigger='date',
                                          run_date=datetime.now(pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                          name="后宫管理系统")
                    
                    # 关闭一次性开关
                    self._onlyonce = False
                    # 保存配置
                    self.__update_config()
                    
                    # 启动任务
                    if self._scheduler and self._scheduler.get_jobs():
                        self._scheduler.print_jobs()
                        self._scheduler.start()
                        
                    return {"code": 0, "msg": "配置已更新，将在3秒后执行刷新"}
                except Exception as e:
                    logger.error(f"启动一次性任务失败: {str(e)}")
                    return {"code": 1, "msg": f"配置已更新，但启动任务失败: {str(e)}"}
                
            return {"code": 0, "msg": "配置已更新"}
            
        except Exception as e:
            logger.error(f"更新配置失败: {str(e)}")
            return {"code": 1, "msg": f"更新配置失败: {str(e)}"}

    def _calculate_statistics(self, invitees):
        """
        计算用户统计数据
        """
        banned_count = sum(1 for i in invitees if i.get('enabled', '').lower() == 'no')
        low_ratio_count = sum(1 for i in invitees if i.get('ratio_health') in ['warning', 'danger'])
        no_data_count = sum(1 for i in invitees if i.get('ratio_health') == 'neutral')

        return {
            'banned': banned_count,
            'low_ratio': low_ratio_count,
            'no_data': no_data_count
        }

    def get_config(self, apikey: str) -> Response:
        """
        获取配置
        """
        if apikey != settings.API_TOKEN:
            return Response(success=False, message="API令牌错误!")
        
        try:
            # 直接返回当前配置，不再从文件读取
            config = {
                "enabled": self._enabled,
                "notify": self._notify,
                "cron": self._cron,
                "onlyonce": self._onlyonce,
                "site_ids": self._nexus_sites
            }
            return Response(success=True, message="获取成功", data=config)
        except Exception as e:
            logger.error(f"获取配置失败: {str(e)}")
            return Response(success=False, message=f"获取配置失败: {str(e)}")


# 插件类导出
plugin_class = nexusinvitee

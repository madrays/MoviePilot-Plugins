"""
两步验证码管理插件
"""
import hashlib
import json
import os
import time
import threading
import pyotp
from typing import Any, List, Dict, Tuple, Optional
import requests
import urllib.parse

try:
    from app.sdk.config import settings
except ImportError:
    from app.core.config import settings
from app.plugins import _PluginBase
try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from app.schemas import Response


class twofahelper(_PluginBase):
    # 插件名称
    plugin_name = "两步验证助手"
    # 插件描述
    plugin_desc = "懒人板2FA，配合浏览器扩展使用，支持自动弹出验证码一键复制"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/madrays/MoviePilot-Plugins/main/icons/2fa.png"
    # 插件版本
    plugin_version = "3.0.0"
    # 插件作者
    plugin_author = "madrays"
    # 作者主页
    author_url = "https://github.com/madrays"
    # 插件配置项ID前缀
    plugin_config_prefix = "twofahelper_"
    # 加载顺序
    plugin_order = 20
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _sites = {}
    
    # 配置文件路径
    config_file = None

    def init_plugin(self, config: dict = None):
        """
        插件初始化 - 简化版，不再需要同步任务
        """
        # 直接使用settings获取配置路径
        data_path = self.get_data_path()
        
        # 确保目录存在
        if not os.path.exists(data_path):
            try:
                os.makedirs(data_path)
            except Exception as e:
                logger.error(f"创建数据目录失败: {str(e)}")
        
        self.config_file = os.path.join(data_path, "twofahelper_sites.json")
        
        # 初始化时从文件加载配置到内存
        self._sync_from_file()
        
        # 如果内存中没有配置，添加预设站点配置
        if not self._sites:
            # 生成预设站点配置
            self._sites = self._generate_default_sites()
            # 写入配置文件
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._sites, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"写入配置文件失败: {str(e)}")
        
        logger.info(f"两步验证码助手初始化完成，已加载 {len(self._sites)} 个站点")
            
    def _generate_default_sites(self):
        """
        生成预设站点配置，用于新用户初始化
        
        :return: 预设站点配置字典
        """
        # Google图标的Base64编码 - 确保背景为白色
        google_icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAABWhJREFUWEe9V2lsVFUU/u55dGY67XRo2cpmsaLQCilSFVkkDY0WFTdwAYwRpCIKERAkNaYgEpCGkNCIibKESFg0JphoJAixJDaQYlFoUAxiC5WwlLIVOtPpdN65cod5M+9Np50paby/2jnb98757j3nCCR4pJRpAKYw8yQpZZ4QIhuAK2R+U0p5RghRQ0Q/A/hRCHEzEdcinpKUchgzlwCYTkSOePpKzswtAHbf1l8rhDjdmU2HAKSUTmZeBWAhEWmJBI7WYeYAgA1EtFwIoUC1OzEBSCkfYObviCj3bgLHAHKCiKYKIf6JlrUDIKUczcw/EVHvaGX94nm0HtyPtmNHEaivAzfdAKQEpbmhZWXDljca9sLJ0AYOboebmRuJ6EkhxHGz0AIg9OWHooPrly7As+kztFZWBAN2eoSAfXwBUuYthJY5wKIaAjHOnIkwACllCjP/Gp1234G9aC4vg/TFLGGHWESyE64lH8Fe8EQ0CFWOMQYnwgB0XV9PRO+btb1ffwXPls/vmgaOoilwfbA8VjnWaZq2TAmCAEJX7U8z29WX3yr7OGbwHtlDYXt0HLT+AwEhoF84D3/1YQRqIzfO8cyLcC0qCcpj3Q4iylGlCEp1Xd9GRLMMRUW268UzIFt9FlsVMHVRCWz5Y2IC8x+twq31q2GfUIDU+Us6zRwzb9U0rVhIKd3MfMn8yHjK34P3hyqLg6ScEXCvKYdwGY9fbP/S64FwpsQtGzN7iShTAZgJYKdhIVvqoFfmwlvRH61H+wR/poxeSN+8C+ROj+u4iwrTha7rW4hojmHIZz8F164I/uv/qye8e7OQunAFFKG6+zDzJhEIBKo1TXs4XP/fiyCvHwzH4puDYHv2b6BHj+6Or7h3RGXgKhFlGN4DlYMBf0M4mOj3ErQRuzoMXrjGkzCw0hfsKMiNfIh6mBQAPxElhQFUOADJYac0pAR03yfdAmBOgQ0zx4VDqa7p/18BvD4hCbMm2iLlDQG4QkS9OixB32nQRu7ulgzMK7Th5TGWDDS2J+GxyZDXKsIBG2w56Dv+NyRR10h4ppFRvNnaP1ZMtWPi8Igfg4RR17AMXFsaBLCvdRDKbuVh6SML8Hx2YcJkU4rfVLVhU4XfYrNzvhOZ7sjTHLyGUsoZAMI0ly1n4Tuciw3NudjjGxJ0kOFwY1fRevRy9EwIRLNPYvaXLbjmibTue3oTts1NjrZ/VQFICz3FYemGqlXYWV9jUR6eno2NBaVw2zp/itt0oPRbH6rrdIv924U2vGKtv3qK+xnNaCsRvWlYXPQ0Yvq+xfAGrM0o09kby/LfwuMD8mNm4vSNepT9UoUzfzwFIDJGZqQIbH8nGck2S/o3a5o212jH9zPzSaII0/bVV6K0qjxmoCFpAzE28yEMTs2EEAKXW67i2OWTqLlyChISmm8onA0LIAJ3esfKaQ5MGBYBxMxtoXZcax5I1hHRUnPEHae+R/nx7QnVPVpJ6C4kN7yL2fl5lruv9Jh5raZpH6q/zSOZGsOPENEIs7P9/x7C6uov4A10bSTThIbinNdQPPI5CzZmVsvLY0KIYH2jh9KhzHyYiO704dC55L2CjTU7cODcIXC8oRRAft8HsWjUG1DENR9mbiAiNZTWGb/HGstHMfP+aBDKQJFTgahuOIHapnO43toUHJLddheyXAMwqs9wFA4ai2Hp97YrWyh4kVrfzMKOFhOViT1ENPKuCBBlFEq7WkzCX95hBgyBlDKZmVcCWGy+HV0BpNh+e4FV0/ZKo+btyBrPoZRSZUMtpzOIyBlPP8RyrxrziKhMCFHbmU3c7diUEfUEPh21nrtD8iYpZZ1pPd8rhGhOBOx/iMlsM+yNfVQAAAAASUVORK5CYII="
        
        # GitHub图标的Base64编码 - 确保背景为白色
        github_icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAABRFJREFUWEetl11sU2UYx//POV23sq18jHN61nZYxoQ4EjAqEC+UmZgI8TN6YaIRMV44MGpiYtAYZYgYNcavIBIuMH7EG2JiiIqJJMwYNAN3IcYNdcIYpT09ZRvpVmR07V9O6Zbu9HTdZOeiF32fj9/zvM/zvs8rmOHX2trqHT5//g4C94FsBRCkSNBWFzIGIAaRHgEOLly8+EhPT8/lmZiWSkIRTTMuiWwn+QgAfyX5wnpKRL6sIXf0J5PmdDplAVpaWqpHU6mXATxPsnaGjqeIiUj6CvS7dX7/rr6+vjE3G64Ahai/Jrnu/zh26ohIVw35gFs2SgDCur5qnPyWQHgunE/YECDqEbk7alkniu1OAchHDhyfa+fFEDXAmuJMTAIU9vzH4rQL0AvgBETuJNkwy4xcEOAHAMsI3DQJIdJV5/evn6iJSQBD118j+UqxE0Xkqbhl7Wtra/P09vZuArkLpAGRUQCnhRwGQIosBHkdgPkiMgRy+yJN22e3YqOuP5gjv5qSdpGdpmW9mm9h+6dQdH3OahdVXWua5vEJ5VZNqxtS1SXt7e0nOzo6csVGSUo4HL5eVdXkwMCADZb/AoHAUuRypxwA6Rqyxd6KPICh6x+TbHemWPF4bonH492zTP0U8WAwuCSbyZxx6Yy9pmVtEfuEG0wmk26HjCKyKW5Zn18LgGEYG5nNfudiI9WgaZo06vpdOfJ7F8K0qOrKeDxeQj8boFAo1JDNZE6SXFySYZENYuj6RyS3ugBsMy3r7dk4KydraNoTBPa7+NgjhqYdIdDmXKyqrl4ejUb/nguASCSy4N90erIwi86FThvgTwLLnVUaTyTqRYRzAVAo9DMkl0zxA/wlAV0fAVnnADhtWlbzXDnPA2jaMQJrptgUGbVrIE1ynsPZSCKZnOnVOyNOQ9dPkVzqCPSiDVCSmryQogQSiYQ1I+sVhCKRSM2lixcvkKx2AJyxAbpIrnVpkcfilvXFXABM0+pd0qhpH+SAZ0taBDget6x1c1GIhq4fIrmhJEjgQ/sgKrksJttE5AXTst65liwYmraZwCduNhSRh2TFihX1F4aGzgGodxGiiLweamra2d3dnZkNSEdHh7J3zx57nHsTgOqiO9IABCcuo90kn84LibynivyaJbeBXJX/CzgLkf0KcFTxeruj0eiQG0xzc/P8dDp9swLcmiM3g2wpBy2KsttMJJ7JA4Q1rWVc5A+SXgGGFZGHF5C/DIr8BPJGR+8e3bJ16+3O67jQ666nakl9iYxVASvPWtY/xQPJDpL5IeHKJJzyeL0rRcQ3fvnyz8UXiaoo98cSiYNukRmG0cZs9kilrRKRHaZldRSye1XcHslGUqljRWnfbyaTTxaGlUdJNikiPbV+/6flRuxwOLwoMzY2OC2AyIl6v39tyUhmKwWDwaZsJtMFoBFAVlT1XtM0D1WKqHg9oGl2sXrK6MTVqqp1sVjs7GSnOQVDur56nLSdXoUQOQzgsAAjBAK3rV+/68CBA9lyUAFNGy9T9XGPyMZzlvVbsa7rwyQUCoXHM5lvQK52OmrQtOrp3n0BTbPhFEfh/q56PPfEYrGBkoIsF0lhTH8JwIvFZ7ivttbX399/aZoM2MNqPjARsR+ob9XMm/dGOZ2Kj9MmXV+WEXmOudzjEFFuaG1d2NnZaafZ9TN0fZCA3c6febze9ysNNRUBJrzYI/moz1dVPHK7Edjb5/P5Un19famZFO9/2SAgrr8DEI4AAAAASUVORK5CYII="
        
        # 微软图标的Base64编码 - 确保背景为白色
        microsoft_icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAAAXNSR0IArs4c6QAAAnpJREFUeF7t3W1RxDAYReHUADNYQBEC8IIZBPAXxGCBGQwsw0e22d06OA8Okl7y3nNSyvb1+HAasZ+714/taMnP7yO3F5sA7FEQgMhJ4ATYH7QTYAm9E8AJoAMUMmAEGAEo4D8DOoAOwAPMDCiBhQIwxtABdAAdQAe4Pe6MACOAByhkQAfQAXQAHUAH+NkBIogIIoKIoELzW9aoBCqBSqASqAQqgVcZYAIjXUAH0AF0AB1AB9ABdAAmcM2AEqgEug4uZAAFoAAUgAJQAApAASgABfhAxDkDMLCAAP4w5OIpeyXMK2FeCfNKWOTon8skgoggIogIIoKIICKICCKCiCAiKAYBvhCyPHAiiAgigoig2AwggoggIogIIoKIICKICCKCiCAiKAYBRBAR5J9GzQwwgUwgE8gExkoAE8gEMoFMIBPIBDKBTGDeBMb6n+Ve7cBhGbJLnR0QgM6zPlypAAhAfAfiy3cC5APw8pn7Nt54uj8M/ult5PZiGwJwPgMEoHIcOgHOT9oJsITeCeAE0AESGTACjICjoBsBiV//MWDg8kYQDNw3wwngBFACExlQApVAJfBvB4ggIshl0MyAEpgoADBwfcxGgBFgBBgBlaN/rhMGwkAYCANvMoACKqPACDACjAAjwAiggi8zoAPoAK6DExlQApVAJVAJVAKVQCXQbaDbQLeBbgMT1X9ZJApAASgABaAAFIACUAAKQAEoAAX87oDbwEoQYCAMhIEwEAbCQBgIA2EgDISBlfY/14kCUAAKQAEoAAWgABSAAlAACkABLoNSGYCBMBAGwkAYCANhIAyEgTAQBqYQwKdi18dtBBgBRoARYARkTeA3l4PYkqt6qqEAAAAASUVORK5CYII="
        
        # 生成有效的Base32密钥
        # Base32字符集只包含A-Z和2-7
        def generate_valid_base32_key():
            import random
            import string
            # 有效的Base32字符
            valid_chars = string.ascii_uppercase + "234567"
            # 生成16个随机字符作为密钥
            return ''.join(random.choice(valid_chars) for _ in range(16))
        
        # 默认站点配置 - 使用标准Base32格式的密钥
        default_sites = {
            "Google": {
                "secret": generate_valid_base32_key(),  # 使用有效的Base32密钥
                "urls": ["https://accounts.google.com"],
                "icon": google_icon  # 使用Base64编码的图标
            },
            "GitHub": {
                "secret": generate_valid_base32_key(),
                "urls": ["https://github.com"],
                "icon": github_icon
            },
            "Microsoft": {
                "secret": generate_valid_base32_key(),
                "urls": ["https://account.microsoft.com"],
                "icon": microsoft_icon
            }
        }
        
        return default_sites
            
    def _sync_from_file(self):
        """
        从配置文件同步到内存 - 精简版，移除多余日志
        """
        if not os.path.exists(self.config_file):
            # 清空内存中的配置
            if self._sites:
                self._sites = {}
            return False

        try:
            # 读取文件内容
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # 解析JSON
            new_sites = json.loads(file_content)
            
            # 更新内存中的配置
            self._sites = new_sites
            return True
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式解析失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"读取配置文件失败: {str(e)}")
            return False

    def _sync_to_file(self):
        """
        将内存中的配置同步到文件 - 精简版
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._sites, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"将内存配置同步到文件失败: {str(e)}")
            return False

    def get_state(self) -> bool:
        """
        获取插件状态
        """
        return True if self._sites else False

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        注册插件命令
        """
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        return []

    def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
        """
        获取插件仪表盘元信息
        返回示例：
            [{
                "key": "dashboard1", // 仪表盘的key，在当前插件范围唯一
                "name": "仪表盘1" // 仪表盘的名称
            }]
        """
        logger.info("获取仪表盘元信息")
        return [{
            "key": "totp_codes",
            "name": "两步验证码"
        }]

    def get_dashboard(self, key: str, **kwargs) -> Optional[Tuple[Dict[str, Any], Dict[str, Any], List[dict]]]:
        """
        获取插件仪表盘页面，需要返回：1、仪表板col配置字典；2、全局配置（自动刷新等）；3、仪表板页面元素配置json（含数据）
        """
        if key != "totp_codes":
            return None
        
        # 从文件重新加载配置，确保使用最新数据
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._sites = json.load(f)
                logger.info(f"仪表盘页面：从文件重新加载配置，站点数: {len(self._sites)}")
        except Exception as e:
            logger.error(f"仪表盘页面：重新加载配置文件失败: {str(e)}")
        
        # 获取验证码
        codes = self.get_all_codes()
        
        # 列配置 - 移除所有宽度限制，完全铺满屏幕
        col_config = {}  # 空字典表示不使用特定的列配置限制
        
        # 全局配置
        global_config = {
            "refresh": 5,  # 5秒自动刷新
            "title": "两步验证码",
            "border": True,
            "fullscreen": True,  # 使用全屏模式
            "style": "width: 100vw !important; max-width: 100% !important; padding: 0 !important; margin: 0 !important;"  # 确保容器充满屏幕宽度
        }
        
        # 页面元素
        elements = []
        
        # 首先添加强制样式覆盖所有容器限制
        elements.append({
            "component": "style",
            "text": """
            /* 覆盖所有容器宽度限制 */
            .dashboard-container,
            .dashboard-container > .container,
            .dashboard-container > .container > .row,
            .dashboard-container > .container > .row > div,
            .dashboard-card-container,
            .v-card,
            .v-container,
            .v-container > .row,
            .v-container > .row > div,
            .v-main > .v-container,
            .v-main > .v-container > .row,
            .dashboard-container > .v-container,
            .dashboard-container > .v-container > .row {
                max-width: 100% !important;
                width: 100% !important;
                padding-left: 8px !important;
                padding-right: 8px !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
            }
            
            .v-main__wrap {
                max-width: 100% !important;
            }
            
            /* 防止卡片过度拉伸 */
            .v-card {
                width: auto !important;
            }

            /* 减少标题与内容间的留白 */
            .v-toolbar__content {
                padding-bottom: 0 !important;
                min-height: 48px !important;
            }

            /* 减少dashboard顶部空间 */
            .dashboard-container {
                padding-top: 0 !important;
            }
            
            /* 移除标题下方的margin */
            .dashboard-title {
                margin-bottom: 0 !important;
            }
            """
        })
        
        if not codes:
            # 无验证码时显示提示信息
            elements.append({
                "component": "VAlert",
                "props": {
                    "type": "warning",
                    "text": "未配置任何站点或配置无效，请先添加站点配置。"
                }
            })
            return col_config, global_config, elements
        
        # 使用VRow和VCol创建网格布局
        row_content = []
        
        # 颜色循环，为每个卡片分配不同颜色
        colors = ["primary", "success", "info", "warning", "error", "secondary"]
        color_index = 0
        
        for site, code_info in codes.items():
            code = code_info.get("code", "")
            remaining_seconds = code_info.get("remaining_seconds", 0)
            urls = code_info.get("urls", [])
            
            # 获取站点URL用于点击跳转
            site_url = ""
            if urls and isinstance(urls, list) and len(urls) > 0:
                site_url = urls[0]
            
            # 循环使用颜色
            color = colors[color_index % len(colors)]
            color_index += 1
            
            # 获取站点图标信息 - 优先使用配置中的图标
            site_data = self._sites.get(site, {})
            favicon_info = self._get_favicon_url(urls, site, site_data)
            
            # 为每个站点创建一个卡片
            card = {
                "component": "VCol",
                "props": {
                    "cols": 12,  # 移动设备上单列
                    "sm": 6,     # 小屏幕每行2个
                    "md": 2,     # 中等屏幕每行3个
                    "lg": 2,     # 大屏幕每行4个
                    "xl": 2,     # 超大屏幕每行6个
                    "class": "pa-1"  # 减小内边距使卡片更紧凑
                },
                "content": [
                    {
                    "component": "VCard",
                    "props": {
                            "class": "mx-auto",
                            "elevation": 1,
                            "height": "160px",  # 固定高度确保显示完整
                        "variant": "outlined"
                        },
                        "content": [
                            {
                                "component": "VCardItem",
                                "props": {
                                    "class": "pa-1"  # 减小内边距
                    },
                    "content": [
                        {
                            "component": "VCardTitle",
                            "props": {
                                            "class": "d-flex align-center py-0"  # 减小顶部内边距
                                        },
                                        "content": [
                                            # 替换为自定义图标容器，避免CDN失败
                                            {
                                                "component": "div",
                                                "props": {
                                                    "class": "mr-2 d-flex align-center justify-center",
                                                    "style": f"width: 16px; height: 16px; border-radius: 2px; background-color: #ffffff; overflow: hidden;"
                                                },
                                                "content": [
                                                    {
                                                        "component": "span",
                                                        "props": {
                                                            "style": "color: white; font-size: 10px; font-weight: bold;"
                                                        },
                                                        "text": site[0].upper() if site else "?"
                                                    },
                                                    # 添加脚本处理图标加载
                                                    {
                                                        "component": "script",
                                                        "text": f'''
                                                        (() => {{
                                                          const loadImage = (url, callback) => {{
                                                            const img = new Image();
                                                            img.onload = () => callback(img, true);
                                                            img.onerror = () => callback(img, false);
                                                            img.src = url;
                                                          }};
                                                          
                                                          const container = document.currentScript.parentNode;
                                                          container.removeChild(document.currentScript);
                                                          
                                                          // 首先尝试base64图标
                                                          const base64Icon = "{favicon_info.get('base64', '')}";
                                                          if (base64Icon) {{
                                                            const img = new Image();
                                                            img.style.width = '100%';
                                                            img.style.height = '100%';
                                                            img.src = base64Icon;
                                                            container.innerHTML = '';
                                                            container.appendChild(img);
                                                            return;
                                                          }}
                                                          
                                                          // 尝试 favicon.ico
                                                          loadImage("{favicon_info.get('ico', '')}", (img, success) => {{
                                                            if (success) {{
                                                              container.innerHTML = '';
                                                              img.style.width = '100%';
                                                              img.style.height = '100%';
                                                              container.appendChild(img);
                                                            }} else {{
                                                              // 尝试 favicon.png
                                                              loadImage("{favicon_info.get('png', '')}", (img, success) => {{
                                                                if (success) {{
                                                                  container.innerHTML = '';
                                                                  img.style.width = '100%';
                                                                  img.style.height = '100%';
                                                                  container.appendChild(img);
                                                                }} else {{
                                                                  // 尝试 Google Favicon
                                                                  loadImage("{favicon_info.get('google', '')}", (img, success) => {{
                                                                    if (success) {{
                                                                      container.innerHTML = '';
                                                                      img.style.width = '100%';
                                                                      img.style.height = '100%';
                                                                      container.appendChild(img);
                                                                    }} else {{
                                                                      // 尝试 DuckDuckGo
                                                                      loadImage("{favicon_info.get('ddg', '')}", (img, success) => {{
                                                                        if (success) {{
                                                                          container.innerHTML = '';
                                                                          img.style.width = '100%';
                                                                          img.style.height = '100%';
                                                                          container.appendChild(img);
                                                                        }}
                                                                      }});
                                                                    }}
                                                                  }});
                                                                }}
                                                              }});
                                                            }}
                                                          }});
                                                        }})();
                                                        '''
                                                    }
                                                ]
                                            },
                                            {
                                                "component": "a",
                                                "props": {
                                                    "href": site_url,
                                                    "target": "_blank",
                                                    "class": "text-decoration-none text-caption text-truncate flex-grow-1",  # 使用更小的文字
                                                    "style": "max-width: 100%; color: inherit;",
                                                    "title": f"访问 {site}"
                                                },
                                                "text": site
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "component": "VDivider"
                        },
                        {
                            "component": "VCardText",
                            "props": {
                                    "class": "text-center py-1 px-2"  # 减小内边距
                            },
                            "content": [
                                {
                                    "component": "div",
                                    "props": {
                                            "class": "otp-code font-weight-bold",
                                            "id": f"code-{site}",
                                            "style": "white-space: pre; overflow: visible; font-family: monospace; letter-spacing: 2px; font-size: 1.6rem;"  # 增大字体和间距
                                    },
                                        "text": code
                                },
                                {
                                    "component": "VProgressLinear",
                                    "props": {
                                            "model-value": remaining_seconds / 30 * 100,
                                            "color": color,
                                            "height": 2,
                                            "class": "mt-1 mb-0",  # 减小间距
                                            "rounded": True
                                    }
                                },
                                {
                                    "component": "div",
                                    "props": {
                                            "class": "text-caption"
                                    },
                                        "text": f"{remaining_seconds}秒"
                                }
                            ]
                        },
                        {
                            "component": "VCardActions",
                            "props": {
                                    "class": "py-0 px-2 d-flex justify-center"  # 减小内边距
                            },
                            "content": [
                                {
                                    "component": "VBtn",
                                    "props": {
                                        "size": "small",  # 增大按钮尺寸
                                            "variant": "tonal",
                                            "color": color,
                                            "class": "copy-button",
                                            "block": True,
                                            "onclick": f"""
                                            var code = document.getElementById('code-{site}').textContent.trim();
                                            navigator.clipboard.writeText(code).then(() => {{
                                              this.textContent = '已复制';
                                              setTimeout(() => {{ this.textContent = '复制'; }}, 1000);
                                            }}).catch(() => {{
                                              var textArea = document.createElement('textarea');
                                              textArea.value = code;
                                              textArea.style.position = 'fixed';
                                              document.body.appendChild(textArea);
                                              textArea.focus();
                                              textArea.select();
                                              try {{
                                                document.execCommand('copy');
                                                this.textContent = '已复制';
                                                setTimeout(() => {{ this.textContent = '复制'; }}, 1000);
                                              }} catch (err) {{
                                                console.error('无法复制');
                                              }}
                                              document.body.removeChild(textArea);
                                            }});
                                            """
                                    },
                                    "text": "复制"
                                }
                            ]
                        }
                    ]
                    }
                ]
            }
            
            row_content.append(card)
        
        # 创建一个VRow包含所有卡片
        elements.append({
            "component": "VRow",
            "props": {
                "class": "ma-0",  # 移除外边距
                "dense": True     # 使行更密集
            },
            "content": row_content
        })
        
        # 添加自定义样式
        elements.append({
            "component": "style",
            "text": """
            .copy-button {
                min-width: 60px !important;
                letter-spacing: 0 !important;
                height: 28px !important;
                font-size: 0.875rem !important;
            }
            .otp-code {
                white-space: pre !important;
                font-family: 'Roboto Mono', monospace !important;
                letter-spacing: 2px !important;
                font-weight: 700 !important;
                display: block !important;
                width: 100% !important;
                text-align: center !important;
                font-size: 1.6rem !important;  /* 增大字体 */
                line-height: 1.4 !important;   /* 增加行高 */
                overflow: visible !important;
                padding: 6px 0 !important;
                margin: 0 !important;
                user-select: all !important;  /* 允许一键全选 */
            }
            .time-text {
                font-size: 0.75rem !important;
                margin-top: 4px !important;
            }
            """
        })
        
        logger.info(f"仪表盘页面：生成了 {len(codes)} 个站点的卡片")
        
        return col_config, global_config, elements

    def _get_favicon_url(self, urls: List[str], site_name: str, site_data: dict = None) -> dict:
        """
        获取站点的图标URL
        
        参数:
            urls: 站点URL列表
            site_name: 站点名称
            site_data: 站点配置数据，可能包含base64编码的图标
            
        返回:
            包含各种图标URL的字典
        """
        if not urls:
            return {
                'ico': '',
                'png': '',
                'google': '',
                'ddg': '',
                'base64': ''
            }
        
        # 首先检查是否在配置中有base64图标
        base64_icon = ''
        if site_data and isinstance(site_data, dict) and site_data.get("icon"):
            base64_icon = site_data.get("icon")
            # 确保base64图标有正确前缀
            if base64_icon and not base64_icon.startswith('data:image'):
                base64_icon = f'data:image/png;base64,{base64_icon}'
        
        # 获取第一个URL，用于其他图标服务
        url = urls[0] if urls else ""
        
        # 处理URL，确保包含协议前缀
        if url and not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
            
        try:
            # 解析URL以提取域名
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            
            # 如果域名为空（可能URL格式不正确），则使用原始URL
            if not domain:
                domain = url
                
            # 去除www前缀
            if domain.startswith('www.'):
                domain = domain[4:]
                
            # 构建favicon URL
            favicon_ico = f"{parsed_url.scheme}://{domain}/favicon.ico" if parsed_url.scheme else f"https://{domain}/favicon.ico"
            favicon_png = f"{parsed_url.scheme}://{domain}/favicon.png" if parsed_url.scheme else f"https://{domain}/favicon.png"
            
            # 使用Google和DuckDuckGo的favicon服务
            google_favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
            ddg_favicon = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
            
            return {
                'ico': favicon_ico,
                'png': favicon_png,
                'google': google_favicon,
                'ddg': ddg_favicon,
                'base64': base64_icon
            }
        except Exception as e:
            logger.error(f"解析站点 {site_name} 的URL出错: {e}")
            return {
                'ico': '',
                'png': '',
                'google': '',
                'ddg': '',
                'base64': base64_icon  # 仍然保留base64图标，如果有的话
            }

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        """
        return [{
            "path": "/config",
            "endpoint": self.get_config,
            "methods": ["GET"],
            "summary": "获取配置",
            "description": "获取2FA配置数据",
        }, {
            "path": "/update_config",
            "endpoint": self.update_config,
            "methods": ["POST"],
            "summary": "更新配置",
            "description": "更新2FA配置数据",
        }, {
            "path": "/get_codes",
            "endpoint": self.get_totp_codes,
            "methods": ["GET"],
            "summary": "获取所有TOTP验证码",
            "description": "获取所有站点的TOTP验证码",
        }]

    def get_config(self, apikey: str) -> Response:
        """
        获取配置文件内容
        """
        if apikey != settings.API_TOKEN:
            return Response(success=False, message="API令牌错误!")
        
        try:
            # 读取配置文件
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return Response(success=True, message="获取成功", data=config_data)
            else:
                return Response(success=True, message="配置文件不存在", data={})
        except Exception as e:
            logger.error(f"读取配置文件失败: {str(e)}")
            return Response(success=False, message=f"读取配置失败: {str(e)}")

    def update_config(self, apikey: str, request: dict) -> Response:
        """
        更新配置文件内容
        """
        if apikey != settings.API_TOKEN:
            return Response(success=False, message="API令牌错误!")
        
        try:
            # 更新内存中的配置
            self._sites = request
            
            # 写入配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(request, f, ensure_ascii=False, indent=2)
            
            return Response(success=True, message="更新成功")
        except Exception as e:
            logger.error(f"更新配置文件失败: {str(e)}")
            return Response(success=False, message=f"更新配置失败: {str(e)}")

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        配置页面 - 简化版，只显示当前配置
        """
        logger.info("开始生成配置页面...")
        
        # 每次都直接从文件读取，确保获取最新内容
        file_config = "{}"
        sites_count = 0
        site_names = []
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = f.read()
                logger.info(f"直接读取文件成功: {self.config_file}, 内容长度: {len(file_config)}")
                # 美化JSON格式
                try:
                    parsed = json.loads(file_config)
                    sites_count = len(parsed)
                    site_names = list(parsed.keys())
                    logger.info(f"读取到 {sites_count} 个站点: {site_names}")
                    # 重新格式化为美观的JSON
                    file_config = json.dumps(parsed, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.error(f"解析配置文件失败: {str(e)}")
            except Exception as e:
                logger.error(f"读取配置文件失败: {str(e)}")
        else:
            logger.warning(f"配置文件不存在: {self.config_file}")
        
        # 构造表单 - 只读模式，简化版
        form = [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'style',
                        'text': """
                        .code-block {
                            background-color: #272822; 
                            color: #f8f8f2; 
                            padding: 16px; 
                            border-radius: 4px; 
                            overflow: auto; 
                            font-family: monospace; 
                            max-height: 600px;
                        }
                        .security-alert {
                            background-color: #fffbef;
                            border: 2px solid #ffc107;
                            border-radius: 4px;
                            padding: 12px;
                            margin-bottom: 16px;
                        }
                        .security-title {
                            color: #e65100;
                            font-weight: bold;
                            margin-bottom: 8px;
                            font-size: 1.1rem;
                        }
                        .security-item {
                            margin-bottom: 6px;
                            padding-left: 20px;
                            position: relative;
                        }
                        .security-item:before {
                            content: "•";
                            position: absolute;
                            left: 6px;
                        }
                        """
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
                                            'class': 'security-alert'
                                        },
                                        'content': [
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'security-title'
                                                },
                                                'text': '⚠️ 重要安全提示 ⚠️'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'security-item'
                                                },
                                                'text': '本插件的主要目的：节省掏出手机打开验证器APP的时间，提高使用体验'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'security-item',
                                                    'style': 'color: #d32f2f; font-weight: bold;'
                                                },
                                                'text': '数据安全警告：请勿仅依赖本插件保存TOTP密钥，这可能导致无法挽回的数据丢失！'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'security-item'
                                                },
                                                'text': '强烈建议：将相同密钥同时绑定到可靠的手机验证器APP上(如Authy/Google Authenticator)作为最终备份'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'security-item'
                                                },
                                                'text': '定期备份：使用浏览器插件中的【导出配置】按钮导出JSON配置文件，并妥善保存'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'security-item'
                                                },
                                                'text': '安全知识：相同的TOTP密钥在不同的验证器中会生成完全相同的验证码，多处备份不会影响使用'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'security-item',
                                                    'style': 'margin-top: 10px;'
                                                },
                                                'text': '当前浏览器插件的最新版本为v1.2，请及时更新'
                                            }
                                        ]
                                    },
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'density': 'compact'
                                        },
                                        'content': [
                                            {
                                                'component': 'div',
                                                'text': f'两步验证助手 - 共 {sites_count} 个站点'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'mt-2',
                                                    'style': 'border: 1px solid #e0f7fa; padding: 8px; border-radius: 4px; background-color: #e1f5fe;'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'div',
                                                        'props': {
                                                            'class': 'font-weight-bold mb-1'
                                                        },
                                                        'text': '📌 浏览器扩展'
                                                    },
                                                    {
                                                        'component': 'div',
                                                        'props': {
                                                            'class': 'text-body-2'
                                                        },
                                                        'text': '本插件必须安装配套的浏览器扩展配合：'
                                                    },
                                                    {
                                                        'component': 'div',
                                                        'props': {
                                                            'class': 'mt-1 d-flex align-center flex-wrap'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'a',
                                                                'props': {
                                                                    'href': 'https://github.com/madrays/MoviePilot-Plugins/releases',
                                                                    'target': '_blank',
                                                                    'class': 'text-decoration-none mr-3 mb-1',
                                                                    'style': 'color: #1976d2; display: inline-flex; align-items: center;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'v-icon',
                                                                        'props': {
                                                                            'icon': 'mdi-download',
                                                                            'size': 'small',
                                                                            'class': 'mr-1'
                                                                        }
                                                                    },
                                                                    {
                                                                        'component': 'span',
                                                                        'text': '下载扩展'
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                'component': 'a',
                                                                'props': {
                                                                    'href': 'https://github.com/madrays/MoviePilot-Plugins/blob/main/README.md#totp浏览器扩展说明',
                                                                    'target': '_blank',
                                                                    'class': 'text-decoration-none mb-1',
                                                                    'style': 'color: #1976d2; display: inline-flex; align-items: center;'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'v-icon',
                                                                        'props': {
                                                                            'icon': 'mdi-information-outline',
                                                                            'size': 'small',
                                                                            'class': 'mr-1'
                                                                        }
                                                                    },
                                                                    {
                                                                        'component': 'span',
                                                                        'text': '安装说明'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'div',
                                                        'props': {
                                                            'class': 'text-caption mt-1',
                                                            'style': 'color: #546e7a;'
                                                        },
                                                        'text': '使用方法：下载后解压，在浏览器扩展管理页面选择"加载已解压的扩展程序"并选择解压后的文件夹。'
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
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'props': {
                                            'class': 'pa-2'
                                        },
                                        'content': [
                                            {
                                                'component': 'pre',
                                                'props': {
                                                    'class': 'code-block'
                                                },
                                                'text': file_config
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
        
        logger.info("配置页面生成完成")
        
        # 返回表单数据
        return form, {}

    def get_page(self) -> List[dict]:
        """
        详情页面 - 使用AJAX更新而非整页刷新
        """
        try:
            logger.info("生成验证码页面...")
            
            # 在生成页面前先同步一次配置
            self._sync_from_file()
            
            # 当前时间字符串，确保初始显示正确
            current_time = time.strftime("%H:%M:%S", time.localtime())
            
            # 添加样式
            style_text = """
            .otp-code {
                white-space: nowrap;
                font-family: monospace;
                letter-spacing: 1px;
                font-weight: 700;
                display: block;
                width: 100%;
                text-align: center;
                font-size: 1.5rem;
                overflow: visible;
            }
            
            .copy-button:active {
                transform: scale(0.98);
            }
            
            .totp-card {
                min-width: 120px;
            }
            """
            
            # 构建内容
            return [
                {
                    'component': 'div',
                    'props': {
                        'id': 'totp-container',
                        'style': 'width: 100%;'
                    },
                    'content': [
                        {
                            'component': 'style',
                            'text': style_text
                        },
                        {
                            'component': 'script',
                            'text': """
                            // 使用AJAX自动刷新验证码
                            function refreshTOTPCodes() {
                                // 创建AJAX请求
                                var xhr = new XMLHttpRequest();
                                xhr.open('GET', '/api/v1/plugin/twofahelper/get_codes', true);
                                
                                // 获取当前token
                                var token = localStorage.getItem('token');
                                if (token) {
                                    xhr.setRequestHeader('Authorization', 'Bearer ' + token);
                                }
                                
                                xhr.onload = function() {
                                    if (xhr.status === 200) {
                                        try {
                                            var response = JSON.parse(xhr.responseText);
                                            console.log('获取验证码响应:', response);
                                            
                                            var codes = null;
                                            if (response.data) {
                                                codes = response.data;
                                            } else if (response.code === 0 && response.data) {
                                                codes = response.data;
                                            }
                                            
                                            if (codes) {
                                                updateTOTPCards(codes);
                                            }
                                        } catch (e) {
                                            console.error('解析验证码失败:', e);
                                        }
                                    }
                                };
                                
                                xhr.send();
                                
                                // 5秒后再次刷新
                                setTimeout(refreshTOTPCodes, 5000);
                            }
                            
                            // 更新TOTP卡片
                            function updateTOTPCards(codes) {
                                // 获取当前时间
                                var now = Math.floor(Date.now() / 1000);
                                var timeStep = 30;
                                var nextStep = (Math.floor(now / timeStep) + 1) * timeStep;
                                var remainingSeconds = nextStep - now;
                                var progressPercent = ((timeStep - remainingSeconds) / timeStep) * 100;
                                
                                // 更新倒计时文本和进度条
                                var timeTexts = document.querySelectorAll('.time-text');
                                var progressBars = document.querySelectorAll('.progress-bar');
                                
                                timeTexts.forEach(function(el) {
                                    el.textContent = remainingSeconds + '秒';
                                });
                                
                                progressBars.forEach(function(el) {
                                    el.style.width = progressPercent + '%';
                                });
                                
                                // 更新验证码
                                for (var siteName in codes) {
                                    if (codes.hasOwnProperty(siteName)) {
                                        var codeEl = document.getElementById('code-' + siteName);
                                        if (codeEl) {
                                            codeEl.textContent = codes[siteName].code;
                                        }
                                    }
                                }
                                
                                // 更新刷新时间和站点数量
                                var lastRefreshEl = document.getElementById('last-refresh-time');
                                if (lastRefreshEl) {
                                    lastRefreshEl.textContent = new Date().toLocaleTimeString();
                                }
                                
                                var sitesCountEl = document.getElementById('sites-count');
                                if (sitesCountEl) {
                                    sitesCountEl.textContent = Object.keys(codes).length;
                                }
                            }
                            
                            // 页面加载完成后开始自动刷新
                            document.addEventListener('DOMContentLoaded', function() {
                                // 立即开始第一次刷新
                                setTimeout(refreshTOTPCodes, 1000);
                            });
                            """
                        },
                        {
                            'component': 'VAlert',
                            'props': {
                                'type': 'info',
                                'variant': 'tonal',
                                'class': 'mb-2',
                                'density': 'compact'
                            },
                            'content': [
                                {
                                    'component': 'div',
                                    'props': {
                                        'style': 'display: flex; justify-content: space-between; align-items: center;'
                                    },
                                    'content': [
                                        {
                                            'component': 'span',
                                            'content': [
                                                {
                                                    'component': 'span',
                                                    'text': '当前共有 '
                                                },
                                                {
                                                    'component': 'span',
                                                    'props': {
                                                        'id': 'sites-count'
                                                    },
                                                    'text': str(len(self._sites))
                                                },
                                                {
                                                    'component': 'span',
                                                    'text': ' 个站点'
                                                }
                                            ]
                                        },
                                        {
                                            'component': 'span',
                                            'content': [
                                                {
                                                    'component': 'span',
                                                    'text': '上次刷新: '
                                                },
                                                {
                                                    'component': 'span',
                                                    'props': {
                                                        'id': 'last-refresh-time'
                                                    },
                                                    'text': current_time
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'component': 'VRow',
                            'props': {
                                'dense': True
                            },
                            'content': self._generate_cards_for_page()
                        }
                    ]
                }
            ]
                
        except Exception as e:
            logger.error(f"生成验证码页面失败: {e}")
            return [{
                'component': 'VAlert',
                'props': {
                    'type': 'error',
                    'text': f'生成验证码失败: {e}',
                    'variant': 'tonal'
                }
            }]
    
    def _generate_cards_for_page(self) -> List[dict]:
        """
        为详情页面生成验证码卡片，支持AJAX更新
        """
        if not self._sites:
            return [
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
                                'text': '暂无配置的站点',
                                'variant': 'tonal'
                            }
                        }
                    ]
                }
            ]
        
        cards = []
        
        # 使用整数时间戳，确保与 Google Authenticator 同步
        current_time = int(time.time())
        time_step = 30
        
        # 计算下一个完整周期的时间
        next_valid_time = (current_time // time_step + 1) * time_step
        remaining_seconds = next_valid_time - current_time
        
        # 计算进度百分比
        progress_percent = 100 - ((remaining_seconds / time_step) * 100)
        
        # 为每个站点生成一个卡片
        card_index = 0
        colors = ['primary', 'success', 'info', 'warning', 'error', 'secondary']
        
        # 创建一个临时验证码字典
        verification_codes = {}
        
        for site, data in self._sites.items():
            try:
                # 获取密钥并确保正确的格式
                secret = data.get("secret", "").strip().upper()
                # 移除所有空格和破折号
                secret = secret.replace(" ", "").replace("-", "")
                
                # 确保密钥是有效的 Base32
                try:
                    import base64
                    # 添加填充
                    padding_length = (8 - (len(secret) % 8)) % 8
                    secret += '=' * padding_length
                    # 验证是否为有效的 Base32
                    base64.b32decode(secret, casefold=True)
                except Exception as e:
                    logger.error(f"站点 {site} 的密钥格式无效: {str(e)}")
                    continue

                # 计算当前时间戳对应的计数器值
                counter = current_time // 30

                # 使用标准 TOTP 参数
                totp = pyotp.TOTP(
                    secret,
                    digits=6,           # 标准 6 位验证码
                    interval=30,        # 30 秒更新间隔
                    digest=hashlib.sha1 # SHA1 哈希算法（RFC 6238 标准）
                )
                
                # 使用计数器值生成验证码
                now_code = totp.generate_otp(counter)  # 直接使用计数器生成验证码
                
                # 创建或更新站点的验证码信息
                if site in verification_codes and 'progress_percent' in verification_codes[site]:
                    verification_codes[site]["progress_percent"] = int(verification_codes[site]["progress_percent"])  # 转换为整数
                else:
                    verification_codes[site] = {
                        "code": now_code,
                        "site_name": site,
                        "urls": data.get("urls", []),
                        "remaining_seconds": remaining_seconds,
                        "progress_percent": int(((time_step - remaining_seconds) / time_step) * 100)
                    }
                
                logger.info(f"站点 {site} 生成验证码成功: counter={counter}, remaining={remaining_seconds}s")
                
                # 根据卡片序号选择不同的颜色
                color = colors[card_index % len(colors)]
                card_index += 1
                
                # 获取站点URL和图标信息
                urls = data.get("urls", [])
                site_url = ""
                if urls and isinstance(urls, list) and len(urls) > 0:
                    site_url = urls[0]
                
                # 获取站点图标信息 - 优先使用配置中的图标
                favicon_info = self._get_favicon_url(urls, site, data)
                
                # 构建美观卡片，确保验证码完整显示
                cards.append({
                    'component': 'VCol',
                    'props': {
                        'cols': 12,     # 移动设备上单列
                        'sm': 6,        # 小屏幕每行2个
                        'md': 4,        # 中等屏幕每行3个
                        'lg': 3,        # 大屏幕每行4个
                        'xl': 2,        # 超大屏幕每行6个
                        'class': 'pa-1'  # 减小内边距使卡片更紧凑
                    },
                    'content': [{
                        'component': 'VCard',
                        'props': {
                            'variant': 'outlined',
                            'class': 'ma-0 totp-card',  # 减小外边距
                            'elevation': 1,             # 减小阴影
                            'height': '160px'           # 固定高度确保所有卡片大小一致
                        },
                        'content': [
                            {
                                'component': 'VCardTitle',
                                'props': {
                                    'class': 'd-flex align-center py-2'  # 统一内边距
                                },
                                'content': [
                                    {
                                        'component': 'div',
                                        'props': {
                                            'class': 'mr-2 d-flex align-center justify-center',
                                            'style': f"width: 20px; height: 20px; border-radius: 3px; background-color: #ffffff; overflow: hidden;"
                                        },
                                        'content': [
                                            {
                                                'component': 'span',
                                                'props': {
                                                    'style': 'color: white; font-size: 12px; font-weight: bold;'
                                                },
                                                'text': site[0].upper() if site else "?"
                                            },
                                            # 添加脚本处理图标加载
                                            {
                                                'component': 'script',
                                                'text': f'''
                                                (() => {{
                                                  const loadImage = (url, callback) => {{
                                                    const img = new Image();
                                                    img.onload = () => callback(img, true);
                                                    img.onerror = () => callback(img, false);
                                                    img.src = url;
                                                  }};
                                                  
                                                  const container = document.currentScript.parentNode;
                                                  container.removeChild(document.currentScript);
                                                  
                                                  // 首先尝试base64图标
                                                  const base64Icon = "{favicon_info.get('base64', '')}";
                                                  if (base64Icon) {{
                                                    const img = new Image();
                                                    img.style.width = '100%';
                                                    img.style.height = '100%';
                                                    img.src = base64Icon;
                                                    container.innerHTML = '';
                                                    container.appendChild(img);
                                                    return;
                                                  }}
                                                  
                                                  // 尝试 favicon.ico
                                                  loadImage("{favicon_info.get('ico', '')}", (img, success) => {{
                                                    if (success) {{
                                                      container.innerHTML = '';
                                                      img.style.width = '100%';
                                                      img.style.height = '100%';
                                                      container.appendChild(img);
                                                    }} else {{
                                                      // 尝试 favicon.png
                                                      loadImage("{favicon_info.get('png', '')}", (img, success) => {{
                                                        if (success) {{
                                                          container.innerHTML = '';
                                                          img.style.width = '100%';
                                                          img.style.height = '100%';
                                                          container.appendChild(img);
                                                        }} else {{
                                                          // 尝试 Google Favicon
                                                          loadImage("{favicon_info.get('google', '')}", (img, success) => {{
                                                            if (success) {{
                                                              container.innerHTML = '';
                                                              img.style.width = '100%';
                                                              img.style.height = '100%';
                                                              container.appendChild(img);
                                                            }} else {{
                                                              // 尝试 DuckDuckGo
                                                              loadImage("{favicon_info.get('ddg', '')}", (img, success) => {{
                                                                if (success) {{
                                                                  container.innerHTML = '';
                                                                  img.style.width = '100%';
                                                                  img.style.height = '100%';
                                                                  container.appendChild(img);
                                                                }}
                                                              }});
                                                            }}
                                                          }});
                                                        }}
                                                      }});
                                                    }}
                                                  }});
                                                }})();
                                                '''
                                            }
                                        ]
                                    },
                                    {
                                        'component': 'a',
                                        'props': {
                                            'href': site_url,
                                            'target': '_blank',
                                            'class': 'text-decoration-none text-body-2 text-truncate flex-grow-1',  # 使用更小的文字
                                            'style': 'max-width: 100%; color: inherit;',
                                            'title': f'访问 {site}'
                                        },
                                        'text': site
                                    }
                                ]
                            },
                            {
                                'component': 'VDivider'
                            },
                            {
                                'component': 'VCardText',
                                'props': {
                                    'class': 'text-center py-2 px-2'  # 统一内边距
                                },
                                'content': [
                                    {
                                    'component': 'div',
                                    'props': {
                                        'class': 'otp-code font-weight-bold',
                                        'id': f'code-{site}',
                                        'style': 'white-space: pre; overflow: visible; font-family: monospace; letter-spacing: 2px; font-size: 1.5rem;'  # 统一字体大小
                                    },
                                    'text': now_code
                                    },
                                    {
                                        'component': 'VProgressLinear',
                                        'props': {
                                            'model-value': progress_percent,
                                            'color': color,
                                            'height': 3,  # 统一进度条高度
                                            'class': 'progress-bar mt-1',
                                            'rounded': True
                                        }
                                    },
                                    {
                                        'component': 'div',
                                        'props': {
                                            'class': 'text-caption text-center mt-1 time-text'  # 使用更小的字体
                                        },
                                        'text': f'{remaining_seconds}秒'
                                    }
                                ]
                            },
                            {
                                'component': 'VCardActions',
                                'props': {
                                    'class': 'py-1 px-2 d-flex justify-center'  # 统一内边距
                                },
                                'content': [
                                    {
                                        'component': 'VBtn',
                                        'props': {
                                            'size': 'small',  
                                            'variant': 'tonal',
                                            'color': color,
                                            'class': 'copy-button',
                                            'block': True,
                                            'onclick': f"""
                                            var code = document.getElementById('code-{site}').textContent.trim();
                                            navigator.clipboard.writeText(code).then(() => {{
                                              this.textContent = '已复制';
                                              setTimeout(() => {{ this.textContent = '复制'; }}, 1000);
                                            }}).catch(() => {{
                                              var textArea = document.createElement('textarea');
                                              textArea.value = code;
                                              textArea.style.position = 'fixed';
                                              document.body.appendChild(textArea);
                                              textArea.focus();
                                              textArea.select();
                                              try {{
                                                document.execCommand('copy');
                                                this.textContent = '已复制';
                                                setTimeout(() => {{ this.textContent = '复制'; }}, 1000);
                                              }} catch (err) {{
                                                console.error('无法复制');
                                              }}
                                              document.body.removeChild(textArea);
                                            }});
                                            """
                                        },
                                        'text': '复制'
                                    }
                                ]
                            }
                        ]
                    }]
                })
            except Exception as e:
                logger.error(f"生成站点 {site} 的验证码失败: {e}")
        
        return cards

    def stop_service(self):
        """
        退出插件
        """
        logger.info("两步验证助手插件停止服务")
        # 不再需要停止同步任务
        pass

    def get_all_codes(self):
        """
        获取所有站点的TOTP验证码
        """
        logger.info(f"获取验证码：当前内存中有 {len(self._sites)} 个站点")
        
        codes = {}
        # 使用整数时间戳，确保与 Google Authenticator 同步
        current_time = int(time.time())
        time_step = 30
        remaining_seconds = time_step - (current_time % time_step)
        
        for site, data in self._sites.items():
            try:
                # 获取密钥并确保正确的格式
                secret = data.get("secret", "").strip().upper()
                # 移除所有空格和破折号
                secret = secret.replace(" ", "").replace("-", "")
                
                # 确保密钥是有效的 Base32
                try:
                    import base64
                    # 添加填充
                    padding_length = (8 - (len(secret) % 8)) % 8
                    secret += '=' * padding_length
                    # 验证是否为有效的 Base32
                    base64.b32decode(secret, casefold=True)
                except Exception as e:
                    logger.error(f"站点 {site} 的密钥格式无效: {str(e)}")
                    continue

                # 计算当前时间戳对应的计数器值
                counter = current_time // 30

                # 使用标准 TOTP 参数
                totp = pyotp.TOTP(
                    secret,
                    digits=6,           # 标准 6 位验证码
                    interval=30,        # 30 秒更新间隔
                    digest=hashlib.sha1 # SHA1 哈希算法（RFC 6238 标准）
                )
                
                # 使用计数器值生成验证码
                now_code = totp.generate_otp(counter)  # 直接使用计数器生成验证码
                
                # 创建或更新站点的验证码信息
                if site in codes and 'progress_percent' in codes[site]:
                    codes[site]["progress_percent"] = int(codes[site]["progress_percent"])  # 转换为整数
                else:
                    codes[site] = {
                        "code": now_code,
                        "site_name": site,
                        "urls": data.get("urls", []),
                        "remaining_seconds": remaining_seconds,
                        "progress_percent": int(((time_step - remaining_seconds) / time_step) * 100)
                    }
                
                logger.info(f"站点 {site} 生成验证码成功: counter={counter}, remaining={remaining_seconds}s")
            except Exception as e:
                logger.error(f"生成站点 {site} 的验证码失败: {e}")
        
        logger.info(f"生成验证码成功，共 {len(codes)} 个站点")
        return codes

    def submit_params(self, params: Dict[str, Any]):
        """
        处理用户提交的参数 - 简化版，不再需要处理同步间隔
        """
        logger.info(f"接收到用户提交的参数: {params}")
        return {"code": 0, "message": "设置已保存"}

    def get_totp_codes(self, apikey: str = None):
        """
        API接口: 获取所有TOTP验证码
        """
        if apikey and apikey != settings.API_TOKEN:
            return {"code": 2, "message": "API令牌错误!"}
            
        try:
            # 确保首先加载最新配置
            self._sync_from_file()
            
            # 获取验证码列表
            codes = self.get_all_codes()
            
            # 增强输出内容
            for site, data in codes.items():
                # 添加额外信息
                data["site_name"] = site
                
                # 处理图标 - 优先使用配置中的base64图标
                if site in self._sites and "icon" in self._sites[site] and self._sites[site]["icon"].startswith("data:"):
                    # 直接使用配置中的base64图标
                    data["icon"] = self._sites[site]["icon"]
                # 如果没有图标但有URL，尝试获取favicon
                elif "urls" in data and data["urls"]:
                    favicon_info = self._get_favicon_url(data["urls"], site, self._sites.get(site, {}))
                    if isinstance(favicon_info, dict):
                        data["favicon_options"] = favicon_info
                        # 保留原始图标url以保持兼容性
                        data["icon"] = favicon_info.get("ico", "") 
                    else:
                        data["icon"] = favicon_info
            
            return {
                "code": 0, 
                "message": "成功",
                "data": codes
            }
        except Exception as e:
            logger.error(f"获取TOTP验证码失败: {str(e)}")
            return {
                "code": 1,
                "message": f"获取TOTP验证码失败: {str(e)}"
            }

    def _get_color_for_site(self, site_name):
        """
        根据站点名称生成一致的颜色
        
        :param site_name: 站点名称
        :return: HSL颜色字符串
        """
        # 改为白色背景
        return "#ffffff"


# 插件类导出
plugin_class = twofahelper 
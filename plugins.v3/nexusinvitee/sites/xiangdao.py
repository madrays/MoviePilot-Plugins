"""
象岛站点处理
"""
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from . import _ISiteHandler


class XiangdaoHandler(_ISiteHandler):
    """
    象岛站点处理类
    """
    # 站点类型标识
    site_schema = "xiangdao"
    
    @classmethod
    def match(cls, site_url: str) -> bool:
        """
        判断是否匹配象岛站点
        :param site_url: 站点URL
        :return: 是否匹配
        """
        # 象岛站点的特征 - 域名中包含ptvicomo或者站点名称为象岛
        xiangdao_features = [
            "ptvicomo",   # 象岛官方域名
            "xiangdao"    # 象岛可能的域名特征
        ]
        
        site_url_lower = site_url.lower()
        for feature in xiangdao_features:
            if feature in site_url_lower:
                logger.info(f"匹配到象岛站点特征: {feature}")
                return True
        
        return False
    
    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        """
        解析象岛站点邀请页面
        :param site_info: 站点信息
        :param session: 已配置好的请求会话
        :return: 解析结果
        """
        site_name = site_info.get("name", "")
        site_url = site_info.get("url", "")
        
        result = {
            "invite_status": {
                "can_invite": False,
                "reason": "",
                "permanent_count": 0,
                "temporary_count": 0,
                "bonus": 0,  # 魔力值
                "permanent_invite_price": 0,  # 永久邀请价格
                "temporary_invite_price": 0   # 临时邀请价格
            },
            "invitees": []
        }
        
        try:
            # 获取用户ID
            user_id = self._get_user_id(session, site_url)
            if not user_id:
                logger.error(f"站点 {site_name} 无法获取用户ID")
                result["invite_status"]["reason"] = "无法获取用户ID，请检查站点Cookie是否有效"
                return result
            
            # 获取用户详情页 - 从用户详情页获取邀请数量
            userdetails_url = urljoin(site_url, f"userdetails.php?id={user_id}")
            logger.info(f"站点 {site_name} 正在从用户详情页获取邀请数量: {userdetails_url}")
            
            try:
                userdetails_response = session.get(userdetails_url, timeout=(10, 30))
                userdetails_response.raise_for_status()
                
                # 解析用户详情页，获取邀请数量
                invite_counts = self._parse_xiangdao_userdetails_page(site_name, site_url, userdetails_response.text)
                
                # 更新邀请状态
                result["invite_status"]["permanent_count"] = invite_counts["permanent_count"]
                result["invite_status"]["temporary_count"] = invite_counts["temporary_count"]
                
                logger.info(f"站点 {site_name} 从用户详情页获取到邀请数量: 永久={invite_counts['permanent_count']}, 临时={invite_counts['temporary_count']}")
            except Exception as e:
                logger.error(f"站点 {site_name} 从用户详情页获取邀请数量失败: {str(e)}")
            
            # 获取邀请页面，检查邀请权限
            invite_url = urljoin(site_url, f"invite.php?id={user_id}")
            response = session.get(invite_url, timeout=(10, 30))
            response.raise_for_status()
            
            # 检查邀请权限
            invite_button_info = self._check_xiangdao_invite_permission(site_name, response.text)
            result["invite_status"]["can_invite"] = invite_button_info["can_invite"]
            
            # 如果可以邀请，设置原因
            if result["invite_status"]["can_invite"]:
                if result["invite_status"]["permanent_count"] > 0 or result["invite_status"]["temporary_count"] > 0:
                    result["invite_status"]["reason"] = f"可用邀请数: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}"
                else:
                    result["invite_status"]["reason"] = "可以邀请其他人"
            else:
                # 如果不能邀请，设置原因
                result["invite_status"]["reason"] = invite_button_info["reason"]
            
            # 获取被邀请人详细列表页面 - 从第一页开始
            invitee_url = urljoin(site_url, f"invite.php?id={user_id}&menu=invitee")
            invitee_response = session.get(invitee_url, timeout=(10, 30))
            invitee_response.raise_for_status()
            
            # 解析第一页被邀请人列表
            invitee_result = self._parse_xiangdao_invitee_page(site_name, site_url, invitee_response.text)
            result["invitees"] = invitee_result["invitees"]
            
            # 检查第一页后宫成员数量，如果少于50人，则不再翻页
            if len(result["invitees"]) < 50:
                logger.info(f"站点 {site_name} 首页后宫成员数量少于50人({len(result['invitees'])}人)，不再查找后续页面")
                # 如果成功解析到后宫成员，记录总数
                if result["invitees"]:
                    logger.info(f"站点 {site_name} 共解析到 {len(result['invitees'])} 个后宫成员")
            else:
                # 尝试获取更多页面的后宫成员
                next_page = 1  # 从第二页开始，因为第一页已经解析过了
                max_pages = 100  # 防止无限循环
                
                # 继续获取后续页面，直到没有更多数据或达到最大页数
                while next_page < max_pages:
                    next_page_url = urljoin(site_url, f"invite.php?id={user_id}&menu=invitee&page={next_page}")
                    logger.info(f"站点 {site_name} 正在获取第 {next_page+1} 页后宫成员数据: {next_page_url}")
                    
                    try:
                        next_response = session.get(next_page_url, timeout=(10, 30))
                        next_response.raise_for_status()
                        
                        # 解析下一页数据
                        next_page_result = self._parse_xiangdao_invitee_page(site_name, site_url, next_response.text)
                        
                        # 如果没有找到任何后宫成员，说明已到达最后一页
                        if not next_page_result["invitees"]:
                            logger.info(f"站点 {site_name} 第 {next_page+1} 页没有后宫成员数据，停止获取")
                            break
                        
                        # 如果当前页面后宫成员少于50人，默认认为没有下一页，避免错误进入下一页
                        if len(next_page_result["invitees"]) < 50:
                            logger.info(f"站点 {site_name} 第 {next_page+1} 页后宫成员数量少于50人({len(next_page_result['invitees'])}人)，默认没有下一页")
                            # 将当前页数据合并到结果中后退出循环
                            result["invitees"].extend(next_page_result["invitees"])
                            logger.info(f"站点 {site_name} 第 {next_page+1} 页解析到 {len(next_page_result['invitees'])} 个后宫成员")
                            break
                        
                        # 将下一页的后宫成员添加到结果中
                        result["invitees"].extend(next_page_result["invitees"])
                        logger.info(f"站点 {site_name} 第 {next_page+1} 页解析到 {len(next_page_result['invitees'])} 个后宫成员")
                        
                        # 继续下一页
                        next_page += 1
                        
                    except Exception as e:
                        logger.warning(f"站点 {site_name} 获取第 {next_page+1} 页数据失败: {str(e)}")
                        break
            
            # 获取魔力值商店页面，解析魔力值和邀请价格
            try:
                bonus_url = urljoin(site_url, "mybonus.php")
                bonus_response = session.get(bonus_url, timeout=(10, 30))
                if bonus_response.status_code == 200:
                    # 解析魔力值和邀请价格
                    bonus_data = self._parse_xiangdao_bonus_shop(site_name, bonus_response.text)
                    # 更新邀请状态
                    result["invite_status"]["bonus"] = bonus_data["bonus"]
                    result["invite_status"]["permanent_invite_price"] = bonus_data["permanent_invite_price"]
                    result["invite_status"]["temporary_invite_price"] = bonus_data["temporary_invite_price"]
                    
                    # 判断是否可以购买邀请
                    if bonus_data["bonus"] > 0:
                        # 计算可购买的邀请数量
                        can_buy_permanent = 0
                        can_buy_temporary = 0
                        
                        if bonus_data["permanent_invite_price"] > 0:
                            can_buy_permanent = int(bonus_data["bonus"] / bonus_data["permanent_invite_price"])
                        
                        if bonus_data["temporary_invite_price"] > 0:
                            can_buy_temporary = int(bonus_data["bonus"] / bonus_data["temporary_invite_price"])
                            
                        # 更新邀请状态的原因字段
                        if result["invite_status"]["reason"] and not result["invite_status"]["can_invite"]:
                            # 如果有原因且不能邀请
                            if can_buy_temporary > 0 or can_buy_permanent > 0:
                                invite_method = ""
                                if can_buy_temporary > 0 and bonus_data["temporary_invite_price"] > 0:
                                    invite_method += f"临时邀请({can_buy_temporary}个,{bonus_data['temporary_invite_price']}魔力/个)"
                                
                                if can_buy_permanent > 0 and bonus_data["permanent_invite_price"] > 0:
                                    if invite_method:
                                        invite_method += ","
                                    invite_method += f"永久邀请({can_buy_permanent}个,{bonus_data['permanent_invite_price']}魔力/个)"
                                
                                if invite_method:
                                    result["invite_status"]["reason"] += f"，但您的魔力值({bonus_data['bonus']})可购买{invite_method}"
                        else:
                            # 如果没有原因或者已经可以邀请
                            if can_buy_temporary > 0 or can_buy_permanent > 0:
                                invite_method = ""
                                if can_buy_temporary > 0 and bonus_data["temporary_invite_price"] > 0:
                                    invite_method += f"临时邀请({can_buy_temporary}个,{bonus_data['temporary_invite_price']}魔力/个)"
                                
                                if can_buy_permanent > 0 and bonus_data["permanent_invite_price"] > 0:
                                    if invite_method:
                                        invite_method += ","
                                    invite_method += f"永久邀请({can_buy_permanent}个,{bonus_data['permanent_invite_price']}魔力/个)"
                                
                                if invite_method and result["invite_status"]["reason"]:
                                    result["invite_status"]["reason"] += f"，魔力值({bonus_data['bonus']})可购买{invite_method}"
            except Exception as e:
                logger.warning(f"站点 {site_name} 解析魔力值商店失败: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"解析站点 {site_name} 邀请页面失败: {str(e)}")
            result["invite_status"]["reason"] = f"解析邀请页面失败: {str(e)}"
            return result
    
    def _parse_xiangdao_userdetails_page(self, site_name: str, site_url: str, html_content: str) -> Dict[str, Any]:
        """
        解析象岛站点用户详情页，获取邀请数量
        :param site_name: 站点名称
        :param site_url: 站点URL
        :param html_content: HTML内容
        :return: 邀请数量
        """
        result = {
            "permanent_count": 0,
            "temporary_count": 0
        }
        
        try:
            # 初始化BeautifulSoup对象
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找包含"邀请"的行
            invite_row = soup.select_one('td.rowhead:-soup-contains("邀请") + td.rowfollow')
            
            if invite_row:
                # 获取邀请文本
                invite_text = invite_row.get_text(strip=True)
                
                # 通过正则表达式提取邀请数量，格式为"X(Y)"，X为永久邀请数量，Y为临时邀请数量
                invite_match = re.search(r'(\d+)\((\d+)\)', invite_text)
                
                if invite_match:
                    permanent_count = invite_match.group(1)
                    temporary_count = invite_match.group(2)
                    
                    try:
                        result["permanent_count"] = int(permanent_count)
                        result["temporary_count"] = int(temporary_count)
                        
                        logger.info(f"站点 {site_name} 从用户详情页解析到邀请数量: 永久={result['permanent_count']}, 临时={result['temporary_count']}")
                    except (ValueError, TypeError):
                        logger.warning(f"站点 {site_name} 无法将邀请数量转换为整数: {permanent_count}({temporary_count})")
                else:
                    # 尝试使用其他格式解析，可能没有括号，直接查找数字
                    invite_nums = re.findall(r'\d+', invite_text)
                    if len(invite_nums) >= 1:
                        try:
                            result["permanent_count"] = int(invite_nums[0])
                            if len(invite_nums) >= 2:
                                result["temporary_count"] = int(invite_nums[1])
                            
                            logger.info(f"站点 {site_name} 从用户详情页解析到邀请数量(备用方法): 永久={result['permanent_count']}, 临时={result['temporary_count']}")
                        except (ValueError, TypeError):
                            logger.warning(f"站点 {site_name} 无法将邀请数量转换为整数(备用方法): {invite_nums}")
                    else:
                        logger.warning(f"站点 {site_name} 未找到邀请数量: {invite_text}")
            else:
                logger.warning(f"站点 {site_name} 未找到包含邀请信息的行")
        except Exception as e:
            logger.error(f"站点 {site_name} 解析用户详情页邀请数量失败: {str(e)}")
        
        return result
    
    def _check_xiangdao_invite_permission(self, site_name: str, html_content: str) -> Dict[str, Any]:
        """
        检查象岛站点邀请权限
        :param site_name: 站点名称
        :param html_content: HTML内容
        :return: 邀请权限
        """
        result = {
            "can_invite": False,
            "reason": ""
        }
        
        try:
            # 初始化BeautifulSoup对象
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 检查邀请按钮文本，判断邀请权限
            invite_button = soup.select_one('form[action*="invite.php"] input[type="submit"]')
            if invite_button:
                button_value = invite_button.get('value', '')
                
                # 如果按钮文本是"邀请其他人"，表示有邀请权限
                if button_value == "邀请其他人":
                    result["can_invite"] = True
                    result["reason"] = "可以邀请其他人"
                    logger.info(f"站点 {site_name} 可以邀请，按钮文本: {button_value}")
                else:
                    # 如果按钮文本是其他内容（如"邀请数量不足"），表示不能邀请，文本即为原因
                    result["can_invite"] = False
                    result["reason"] = button_value
                    logger.info(f"站点 {site_name} 不可邀请，原因: {button_value}")
            else:
                # 找不到按钮，可能是网页结构有问题
                result["can_invite"] = False
                result["reason"] = "无法找到邀请按钮，请检查站点是否已登录"
                logger.warning(f"站点 {site_name} 未找到邀请按钮")
        except Exception as e:
            logger.error(f"站点 {site_name} 检查邀请权限失败: {str(e)}")
            result["reason"] = f"检查邀请权限失败: {str(e)}"
        
        return result
    
    def _parse_xiangdao_invitee_page(self, site_name: str, site_url: str, html_content: str) -> Dict[str, Any]:
        """
        解析象岛站点后宫成员页面HTML内容
        :param site_name: 站点名称
        :param site_url: 站点URL
        :param html_content: HTML内容
        :return: 解析结果
        """
        result = {
            "invitees": []
        }
        
        # 初始化BeautifulSoup对象
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找后宫用户表格
        invitee_table = soup.select_one('table[border="1"]')
        if not invitee_table:
            logger.warning(f"站点 {site_name} 未找到后宫列表表格")
            return result
        
        # 获取表头
        header_row = invitee_table.select_one('tr')
        if not header_row:
            logger.warning(f"站点 {site_name} 未找到后宫列表表头")
            return result
        
        # 获取所有表头单元格
        header_cells = header_row.select('td.colhead, th.colhead, td, th')
        headers = [cell.get_text(strip=True).lower() for cell in header_cells]
        
        logger.info(f"站点 {site_name} 找到用户表格，表头: {headers}")
        
        # 找到所有数据行（跳过表头行）
        data_rows = invitee_table.select('tr.rowfollow')
        
        for row in data_rows:
            cells = row.select('td')
            if len(cells) < len(headers):
                continue
            
            invitee = {}
            username = ""
            is_banned = False
            
            # 逐列解析数据
            for idx, header in enumerate(headers):
                if idx >= len(cells):
                    break
                
                cell = cells[idx]
                cell_text = cell.get_text(strip=True)
                
                # 用户名列
                if idx == 0 or any(kw in header for kw in ['用户名']):
                    username_link = cell.select_one('a')
                    if username_link:
                        username = username_link.get_text(strip=True)
                        invitee["username"] = username
                        
                        # 获取用户个人页链接
                        href = username_link.get('href', '')
                        invitee["profile_url"] = urljoin(site_url, href) if href else ""
                    else:
                        username = cell_text
                        invitee["username"] = username
                
                # 邮箱列
                elif any(kw in header for kw in ['邮箱', 'email']):
                    invitee["email"] = cell_text
                
                # 启用状态列
                elif any(kw in header for kw in ['启用', 'enabled']):
                    status_text = cell_text.lower()
                    if status_text == 'no' or '否' in status_text:
                        invitee["enabled"] = "No"
                        is_banned = True
                    else:
                        invitee["enabled"] = "Yes"
                
                # 上传量列
                elif any(kw in header for kw in ['上传', 'uploaded']):
                    invitee["uploaded"] = cell_text
                
                # 下载量列
                elif any(kw in header for kw in ['下载', 'downloaded']):
                    invitee["downloaded"] = cell_text
                
                # 分享率列
                elif any(kw in header for kw in ['分享率', 'ratio']):
                    ratio_text = cell_text
                    
                    # 处理特殊分享率表示
                    if ratio_text.lower() in ['inf.', 'inf', '∞', 'infinite']:
                        invitee["ratio"] = "∞"
                        invitee["ratio_value"] = 1e20
                    elif ratio_text == '---' or not ratio_text:
                        invitee["ratio"] = "0"
                        invitee["ratio_value"] = 0
                    else:
                        invitee["ratio"] = ratio_text
                        
                        # 尝试解析为浮点数
                        try:
                            normalized_ratio = ratio_text.replace(',', '')
                            invitee["ratio_value"] = float(normalized_ratio)
                        except (ValueError, TypeError):
                            logger.warning(f"无法解析分享率: {ratio_text}")
                            invitee["ratio_value"] = 0
                
                # 做种数列
                elif any(kw in header for kw in ['做种数', 'seeding']):
                    invitee["seeding"] = cell_text
                
                # 做种体积列
                elif any(kw in header for kw in ['做种体积', 'seeding size']):
                    invitee["seeding_size"] = cell_text
                
                # 当前纯做种时魔列
                elif any(kw in header for kw in ['纯做种时魔', 'seed magic']):
                    invitee["seed_magic"] = cell_text
                
                # 后宫加成列
                elif any(kw in header for kw in ['后宫加成', 'bonus']):
                    invitee["seed_bonus"] = cell_text
                
                # 最后做种汇报时间列
                elif any(kw in header for kw in ['最后做种汇报时间', 'last seed']):
                    invitee["last_seed_report"] = cell_text
                
                # 状态列
                elif any(kw in header for kw in ['状态', 'status']):
                    invitee["status"] = cell_text
                    
                    # 根据状态判断是否禁用
                    status_lower = cell_text.lower()
                    if any(ban_word in status_lower for ban_word in ['banned', 'disabled', '禁止', '禁用', '封禁']):
                        is_banned = True
            
            # 检查行类和禁用标记
            row_classes = row.get('class', [])
            is_banned = is_banned or any(cls in ['rowbanned', 'banned', 'disabled'] 
                          for cls in row_classes)
            
            # 查找禁用图标
            disabled_img = row.select_one('img.disabled, img[alt="Disabled"]')
            if disabled_img:
                is_banned = True
            
            # 如果用户名不为空
            if username:
                # 设置启用状态（如果尚未设置）
                if "enabled" not in invitee:
                    invitee["enabled"] = "No" if is_banned else "Yes"
                
                # 设置状态（如果尚未设置）
                if "status" not in invitee:
                    invitee["status"] = "已禁用" if is_banned else "已确认"
                
                # 计算分享率健康状态
                if "ratio_value" in invitee:
                    # 检查是否是无数据情况（上传下载都是0）
                    uploaded = invitee.get("uploaded", "0")
                    downloaded = invitee.get("downloaded", "0")
                    is_no_data = False
                    
                    # 检查是否无数据
                    if isinstance(uploaded, str) and isinstance(downloaded, str):
                        # 转换为小写进行比较
                        uploaded_lower = uploaded.lower()
                        downloaded_lower = downloaded.lower()
                        # 检查所有可能的0值表示
                        zero_values = ['0', '', '0b', '0.00 kb', '0.00 b', '0.0 kb', '0kb', '0b', '0.00', '0.0']
                        is_no_data = any(uploaded_lower == val for val in zero_values) and \
                                   any(downloaded_lower == val for val in zero_values)
                    
                    # 设置数据状态
                    if is_no_data:
                        invitee["data_status"] = "无数据"
                    
                    # 设置分享率健康状态
                    if is_no_data:
                        invitee["ratio_health"] = "neutral"
                        invitee["ratio_label"] = ["无数据", "grey"]
                    elif invitee["ratio_value"] >= 1e20:
                        invitee["ratio_health"] = "excellent"
                        invitee["ratio_label"] = ["无限", "green"]
                    elif invitee["ratio_value"] >= 1.0:
                        invitee["ratio_health"] = "good"
                        invitee["ratio_label"] = ["良好", "green"]
                    elif invitee["ratio_value"] >= 0.5:
                        invitee["ratio_health"] = "warning"
                        invitee["ratio_label"] = ["较低", "orange"]
                    else:
                        invitee["ratio_health"] = "danger"
                        invitee["ratio_label"] = ["危险", "red"]
                else:
                    # 如果没有ratio_value，基于其它信息判断
                    if "ratio" in invitee and invitee["ratio"] == "∞":
                        invitee["ratio_health"] = "excellent"
                        invitee["ratio_label"] = ["无限", "green"]
                    else:
                        invitee["ratio_health"] = "unknown"
                        invitee["ratio_label"] = ["未知", "grey"]
                
                # 添加用户到结果中
                result["invitees"].append(invitee)
        
        logger.info(f"站点 {site_name} 解析到 {len(result['invitees'])} 个后宫成员")
        return result
    
    def _parse_xiangdao_bonus_shop(self, site_name: str, html_content: str) -> Dict[str, Any]:
        """
        解析象岛站点魔力值商店页面
        :param site_name: 站点名称
        :param html_content: HTML内容
        :return: 魔力值和邀请价格信息
        """
        result = {
            "bonus": 0,                  # 用户当前魔力值
            "permanent_invite_price": 0, # 永久邀请价格
            "temporary_invite_price": 0  # 临时邀请价格
        }
        
        # 初始化BeautifulSoup对象
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # 1. 查找当前魔力值 - 象岛特定格式
            bonus_text = soup.select_one('.text a[href="mybonus.php"]')
            if not bonus_text:
                # 尝试查找其他可能的魔力值显示位置
                bonus_text = soup.select_one('td.text')
            
            if bonus_text:
                bonus_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', bonus_text.get_text())
                if bonus_match:
                    bonus_str = bonus_match.group(1).replace(',', '')
                    try:
                        result["bonus"] = float(bonus_str)
                        logger.info(f"站点 {site_name} 魔力值: {result['bonus']}")
                    except ValueError:
                        pass
            
            # 2. 查找邀请价格 - 象岛使用表格显示
            # 查找包含"1个邀请名额"的行
            permanent_invite_row = None
            temporary_invite_row = None
            
            for row in soup.select('tr'):
                row_text = row.get_text().lower()
                if '邀请名额' in row_text and '临时' not in row_text:
                    permanent_invite_row = row
                elif '临时邀请名额' in row_text:
                    temporary_invite_row = row
            
            # 提取永久邀请价格
            if permanent_invite_row:
                price_cell = permanent_invite_row.select('td.rowfollow[align="center"]')[0]
                if price_cell:
                    price_text = price_cell.get_text().strip().replace(',', '')
                    try:
                        result["permanent_invite_price"] = float(price_text)
                        logger.info(f"站点 {site_name} 永久邀请价格: {result['permanent_invite_price']}")
                    except ValueError:
                        pass
            
            # 提取临时邀请价格
            if temporary_invite_row:
                price_cell = temporary_invite_row.select('td.rowfollow[align="center"]')[0]
                if price_cell:
                    price_text = price_cell.get_text().strip().replace(',', '')
                    try:
                        result["temporary_invite_price"] = float(price_text)
                        logger.info(f"站点 {site_name} 临时邀请价格: {result['temporary_invite_price']}")
                    except ValueError:
                        pass
            
            return result
            
        except Exception as e:
            logger.error(f"解析站点 {site_name} 魔力值商店失败: {str(e)}")
            return result

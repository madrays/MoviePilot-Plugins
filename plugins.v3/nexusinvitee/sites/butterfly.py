"""
蝶粉站点处理
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


class ButterflyHandler(_ISiteHandler):
    """
    蝶粉站点处理类
    """
    # 站点类型标识
    site_schema = "butterfly"
    
    @classmethod
    def match(cls, site_url: str) -> bool:
        """
        判断是否匹配蝶粉站点
        :param site_url: 站点URL
        :return: 是否匹配
        """
        # 蝶粉站点的特征 - 域名中包含butterfly或者站点名称为蝶粉
        butterfly_features = [
            "butterfly",  # 域名特征
            "discfan",    # 蝶粉官方域名
            "dmhy"        # 蝶粉可能的域名特征
        ]
        
        site_url_lower = site_url.lower()
        for feature in butterfly_features:
            if feature in site_url_lower:
                logger.info(f"匹配到蝶粉站点特征: {feature}")
                return True
        
        return False
    
    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        """
        解析蝶粉站点邀请页面
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
                "bonus": 0,  # 添加魔力值
                "permanent_invite_price": 0,  # 添加永久邀请价格
                "temporary_invite_price": 0   # 添加临时邀请价格
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
            
            # 获取邀请页面 - 从首页开始
            invite_url = urljoin(site_url, f"invite.php?id={user_id}")
            response = session.get(invite_url, timeout=(10, 30))
            response.raise_for_status()
            
            # 解析邀请页面
            invite_result = self._parse_butterfly_invite_page(site_name, site_url, response.text)
            
            # 获取魔力值商店页面，尝试解析邀请价格
            try:
                bonus_url = urljoin(site_url, "mybonus.php")
                bonus_response = session.get(bonus_url, timeout=(10, 30))
                if bonus_response.status_code == 200:
                    # 解析魔力值和邀请价格
                    bonus_data = self._parse_bonus_shop(site_name, bonus_response.text)
                    # 更新邀请状态
                    invite_result["invite_status"]["bonus"] = bonus_data["bonus"]
                    invite_result["invite_status"]["permanent_invite_price"] = bonus_data["permanent_invite_price"]
                    invite_result["invite_status"]["temporary_invite_price"] = bonus_data["temporary_invite_price"]
                    
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
                        if invite_result["invite_status"]["reason"] and not invite_result["invite_status"]["can_invite"]:
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
                                    invite_result["invite_status"]["reason"] += f"，但您的魔力值({bonus_data['bonus']})可购买{invite_method}"
                                    # 如果可以购买且没有现成邀请，也视为可邀请
                                    if invite_result["invite_status"]["permanent_count"] == 0 and invite_result["invite_status"]["temporary_count"] == 0:
                                        invite_result["invite_status"]["can_invite"] = True
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
                                
                                if invite_method and invite_result["invite_status"]["reason"]:
                                    invite_result["invite_status"]["reason"] += f"，魔力值({bonus_data['bonus']})可购买{invite_method}"
                    
            except Exception as e:
                logger.warning(f"站点 {site_name} 解析魔力值商店失败: {str(e)}")
            
            # 检查第一页后宫成员数量，如果少于50人，则不再翻页
            if len(invite_result["invitees"]) < 50:
                logger.info(f"站点 {site_name} 首页后宫成员数量少于50人({len(invite_result['invitees'])}人)，不再查找后续页面")
                # 如果成功解析到后宫成员，记录总数
                if invite_result["invitees"]:
                    logger.info(f"站点 {site_name} 共解析到 {len(invite_result['invitees'])} 个后宫成员")
                # 不要在这里返回结果，继续执行后面的发送邀请页面访问代码
            else:
                # 尝试获取更多页面的后宫成员
                current_page = 0  # 已获取了第一页，从第二页开始查找
                max_pages = 100  # 防止无限循环
                
                # 从首页中查找下一页链接
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 继续获取后续页面，直到没有更多数据或达到最大页数
                while current_page < max_pages:
                    # 查找下一页链接 - 蝶粉站点特有的繁体翻页标识："下一頁"
                    next_page_link = None
                    pagination_links = soup.select('a')
                    
                    for link in pagination_links:
                        link_text = link.get_text().strip()
                        if "下一頁" in link_text or "下一页" in link_text:
                            next_page_link = link.get('href')
                            break
                    
                    # 如果找不到下一页链接，结束翻页
                    if not next_page_link:
                        logger.info(f"站点 {site_name} 没有找到下一页链接，停止获取")
                        break
                    
                    # 构建下一页URL并请求
                    # 使用正确的URL模板
                    next_page_url = urljoin(site_url, f"invite.php?id={user_id}&menu=invitee&page={current_page+1}")
                    logger.info(f"站点 {site_name} 正在获取第 {current_page+2} 页后宫成员数据: {next_page_url}")
                    
                    try:
                        next_response = session.get(next_page_url, timeout=(10, 30))
                        next_response.raise_for_status()
                        
                        # 更新soup以便下次查找翻页链接
                        soup = BeautifulSoup(next_response.text, 'html.parser')
                        
                        # 解析下一页数据
                        next_page_result = self._parse_butterfly_invite_page(site_name, site_url, next_response.text, is_next_page=True)
                        
                        # 如果没有找到任何后宫成员，说明已到达最后一页
                        if not next_page_result["invitees"]:
                            logger.info(f"站点 {site_name} 第 {current_page+2} 页没有后宫成员数据，停止获取")
                            break
                        
                        # 如果当前页面后宫成员少于50人，默认认为没有下一页，避免错误进入下一页
                        if len(next_page_result["invitees"]) < 50:
                            logger.info(f"站点 {site_name} 第 {current_page+2} 页后宫成员数量少于50人({len(next_page_result['invitees'])}人)，默认没有下一页")
                            # 将当前页数据合并到结果中后退出循环
                            invite_result["invitees"].extend(next_page_result["invitees"])
                            logger.info(f"站点 {site_name} 第 {current_page+2} 页解析到 {len(next_page_result['invitees'])} 个后宫成员")
                            break
                        
                        # 将下一页的后宫成员添加到结果中
                        invite_result["invitees"].extend(next_page_result["invitees"])
                        logger.info(f"站点 {site_name} 第 {current_page+2} 页解析到 {len(next_page_result['invitees'])} 个后宫成员")
                        
                        # 继续下一页
                        current_page += 1
                        
                    except Exception as e:
                        logger.warning(f"站点 {site_name} 获取第 {current_page+2} 页数据失败: {str(e)}")
                        break
            
            # 访问发送邀请页面，这是判断权限的关键
            send_invite_url = urljoin(site_url, f"invite.php?id={user_id}&type=new")
            try:
                send_response = session.get(send_invite_url, timeout=(10, 30))
                send_response.raise_for_status()
                
                # 解析发送邀请页面
                send_page_result = self._parse_butterfly_invite_page(site_name, site_url, send_response.text, is_send_page=True)
                
                # 如果发送页面发现了权限问题，更新邀请状态
                if send_page_result["invite_status"]["reason"]:
                    # 特殊处理邀请数量不足的情况
                    if "邀請數量不足" in send_page_result["invite_status"]["reason"]:
                        invite_result["invite_status"]["can_invite"] = True
                        # 保留原始错误消息
                        invite_result["invite_status"]["reason"] = send_page_result["invite_status"]["reason"]
                    else:
                        # 其他限制情况，更新状态
                        invite_result["invite_status"]["can_invite"] = send_page_result["invite_status"]["can_invite"]
                        invite_result["invite_status"]["reason"] = send_page_result["invite_status"]["reason"]
                    
                    logger.debug(f"站点 {site_name} 从发送页面更新了邀请状态: {invite_result['invite_status']['reason']}")
                
            except Exception as e:
                logger.warning(f"站点 {site_name} 访问发送邀请页面失败: {str(e)}")
            
            # 如果成功解析到后宫成员，记录总数
            if invite_result["invitees"]:
                logger.debug(f"站点 {site_name} 共解析到 {len(invite_result['invitees'])} 个后宫成员")
            
            return invite_result
            
        except Exception as e:
            logger.error(f"解析站点 {site_name} 邀请页面失败: {str(e)}")
            result["invite_status"]["reason"] = f"解析邀请页面失败: {str(e)}"
            return result
    
    def _parse_butterfly_invite_page(self, site_name: str, site_url: str, html_content: str, is_next_page: bool = False, is_send_page: bool = False) -> Dict[str, Any]:
        """
        解析蝶粉站点邀请页面HTML内容
        :param site_name: 站点名称
        :param site_url: 站点URL
        :param html_content: HTML内容
        :param is_next_page: 是否是翻页内容，如果是则只提取后宫成员数据
        :param is_send_page: 是否是发送邀请页面
        :return: 解析结果
        """
        result = {
            "invite_status": {
                "can_invite": False,
                "reason": "",
                "permanent_count": 0,
                "temporary_count": 0
            },
            "invitees": []
        }
        
        # 初始化BeautifulSoup对象
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 检查是否有特殊标题，如"我的后宫"或"邀請系統"等
        special_title = False
        title_elem = soup.select_one('h1')
        if title_elem:
            title_text = title_elem.get_text().strip()
            if '后宫' in title_text or '後宮' in title_text or '邀請系統' in title_text or '邀请系统' in title_text:
                logger.info(f"站点 {site_name} 检测到特殊标题: {title_text}")
                special_title = True
        
        # 如果不是翻页内容，解析邀请状态
        if not is_next_page and not is_send_page:
            # 先检查info_block中的邀请信息
            info_block = soup.select_one('#info_block')
            if info_block:
                info_text = info_block.get_text()
                logger.debug(f"站点 {site_name} 获取到info_block信息")
                
                # 识别邀请数量 - 查找邀请链接并获取数量
                invite_link = info_block.select_one('a[href*="invite.php"]')
                if invite_link:
                    # 获取invite链接周围的文本
                    parent_text = invite_link.parent.get_text() if invite_link.parent else ""
                    logger.debug(f"站点 {site_name} 原始邀请文本: {parent_text}")
                    
                    # 更精确的邀请解析模式：处理两种情况
                    # 1. 只有永久邀请: "邀请 [发送]: 0"
                    # 2. 永久+临时邀请: "探视权 [发送]: 1(0)"
                    invite_pattern = re.compile(r'(?:邀请|探视权|invite|邀請|查看权|查看權).*?(?:\[.*?\]|发送|查看).*?:?\s*(\d+)(?:\s*\((\d+)\))?', re.IGNORECASE)
                    invite_match = invite_pattern.search(parent_text)
                    
                    if invite_match:
                        # 获取永久邀请数量
                        if invite_match.group(1):
                            result["invite_status"]["permanent_count"] = int(invite_match.group(1))
                        
                        # 如果有临时邀请数量
                        if len(invite_match.groups()) > 1 and invite_match.group(2):
                            result["invite_status"]["temporary_count"] = int(invite_match.group(2))
                        
                        logger.debug(f"站点 {site_name} 解析到邀请数量: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}")
                        
                        # 如果有邀请名额，初步判断为可邀请
                        if result["invite_status"]["permanent_count"] > 0 or result["invite_status"]["temporary_count"] > 0:
                            result["invite_status"]["can_invite"] = True
                            result["invite_status"]["reason"] = f"可用邀请数: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}"
                    else:
                        # 尝试直接查找邀请链接后面的文本
                        after_text = ""
                        next_sibling = invite_link.next_sibling
                        while next_sibling and not after_text.strip():
                            if isinstance(next_sibling, str):
                                after_text = next_sibling
                            next_sibling = next_sibling.next_sibling if hasattr(next_sibling, 'next_sibling') else None
                        
                        logger.debug(f"站点 {site_name} 后续文本: {after_text}")
                        
                        if after_text:
                            # 处理格式: ": 1(0)" 或 ": 1" 或 "1(0)" 或 "1"
                            after_pattern = re.compile(r'(?::)?\s*(\d+)(?:\s*\((\d+)\))?')
                            after_match = after_pattern.search(after_text)
                            
                            if after_match:
                                # 获取永久邀请数量
                                if after_match.group(1):
                                    result["invite_status"]["permanent_count"] = int(after_match.group(1))
                                
                                # 如果有临时邀请数量
                                if len(after_match.groups()) > 1 and after_match.group(2):
                                    result["invite_status"]["temporary_count"] = int(after_match.group(2))
                                
                                logger.debug(f"站点 {site_name} 从后续文本解析到邀请数量: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}")
                                
                                # 如果有邀请名额，初步判断为可邀请
                                if result["invite_status"]["permanent_count"] > 0 or result["invite_status"]["temporary_count"] > 0:
                                    result["invite_status"]["can_invite"] = True
                                    result["invite_status"]["reason"] = f"可用邀请数: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}"
            
            # 检查邀请权限
            form_disabled = soup.select_one('input[disabled][value*="貴賓 或以上等級才可以"]')
            if form_disabled:
                disabled_text = form_disabled.get('value', '')
                result["invite_status"]["can_invite"] = False
                result["invite_status"]["reason"] = disabled_text
                logger.debug(f"站点 {site_name} 邀请按钮被禁用: {disabled_text}")
            
            # 检查"对不起"消息 - 处理"邀请数量不足"等情况
            sorry_title = soup.find('h2', text=lambda t: t and ('對不起' in t or '对不起' in t or 'Sorry' in t))
            if sorry_title:
                # 查找包含具体原因的表格单元格
                text_td = None
                for parent in sorry_title.parents:
                    if parent.name == 'table':
                        text_td = parent.select_one('td.text')
                        if not text_td:
                            text_td = parent.select_one('td')
                        break
                
                if text_td:
                    error_text = text_td.get_text(strip=True)
                    logger.debug(f"站点 {site_name} 发现对不起消息: {error_text}")
                    
                    # 特殊处理：邀请数量不足 - 使用繁体字匹配
                    if '邀請數量不足' in error_text:
                        result["invite_status"]["can_invite"] = True
                        # 保留原始错误消息文本，不要翻译
                        result["invite_status"]["reason"] = error_text
                        logger.debug(f"站点 {site_name} 可以发送邀请，但当前邀请数量不足")
                    else:
                        # 其他限制情况
                        result["invite_status"]["can_invite"] = False
                        result["invite_status"]["reason"] = error_text
                        logger.debug(f"站点 {site_name} 不可发送邀请，原因: {error_text}")
                    
            # 检查是否是发送邀请页面 - 如果能找到takeinvite.php表单，说明可以发送邀请
            invite_form = soup.select_one('form[action*="takeinvite.php"]')
            if invite_form and not result["invite_status"]["reason"]:
                # 检查表单中是否有未禁用的提交按钮
                submit_btn = invite_form.select_one('input[type="submit"]:not([disabled])')
                if submit_btn:
                    result["invite_status"]["can_invite"] = True
                    if not result["invite_status"]["reason"]:
                        result["invite_status"]["reason"] = "可以发送邀请"
                    logger.debug(f"站点 {site_name} 可以发送邀请，确认有takeinvite表单")
        
        # 特殊处理发送邀请页面
        if is_send_page:
            # 直接检查是否有"对不起"消息
            sorry_blocks = []
            
            # 查找"对不起"标题 - 使用繁体字
            h2_sorry = soup.find('h2', text=lambda t: t and ('對不起' in t or 'Sorry' in t))
            if h2_sorry:
                sorry_blocks.append(h2_sorry)
            
            # 处理找到的对不起区块
            for block in sorry_blocks:
                # 查找相关联的表格单元格
                text_cell = None
                for parent in block.parents:
                    if parent.name == 'table':
                        text_cell = parent.select_one('td.text')
                        if not text_cell:
                            text_cell = parent.select_one('td')
                        break
                
                if text_cell:
                    error_msg = text_cell.get_text(strip=True)
                    logger.debug(f"站点 {site_name} 发送页面发现对不起消息: {error_msg}")
                    
                    # 特殊处理：邀请数量不足情况 - 使用繁体字匹配
                    if '邀請數量不足' in error_msg:
                        result["invite_status"]["can_invite"] = True
                        # 保留原始错误消息
                        result["invite_status"]["reason"] = error_msg
                        logger.debug(f"站点 {site_name} 可以发送邀请，但当前邀请数量不足")
                    else:
                        # 其他限制情况
                        result["invite_status"]["can_invite"] = False
                        result["invite_status"]["reason"] = error_msg
                        logger.debug(f"站点 {site_name} 不可发送邀请，原因: {error_msg}")
                    break
            
            # 如果没有对不起消息，检查是否有表单
            if not result["invite_status"]["reason"]:
                invite_form = soup.select_one('form[action*="takeinvite.php"]')
                if invite_form:
                    result["invite_status"]["can_invite"] = True
                    result["invite_status"]["reason"] = "可以发送邀请"
                    logger.debug(f"站点 {site_name} 发送页面可以发送邀请")
                else:
                    # 如果既没有对不起消息也没有表单，可能是其他限制
                    if not result["invite_status"]["reason"]:
                        result["invite_status"]["can_invite"] = False
                        result["invite_status"]["reason"] = "无法发送邀请，请查看页面了解原因"
                        logger.debug(f"站点 {site_name} 发送页面无法找到表单或错误消息")
        
        # 蝶粉站点特殊处理
        # 直接查找border="1"的表格，这通常是用户列表表格
        border_tables = soup.select('table[border="1"]')
        if border_tables:
            # 选取第一个border="1"表格
            table = border_tables[0]
            
            # 获取表头
            header_row = table.select_one('tr')
            if header_row:
                # 获取所有表头单元格
                header_cells = header_row.select('td.colhead, th.colhead, td, th')
                headers = [cell.get_text(strip=True).lower() for cell in header_cells]
                
                if is_next_page:
                    logger.debug(f"站点 {site_name} 翻页中找到用户表格，表头: {headers}")
                else:
                    logger.debug(f"站点 {site_name} 首页找到用户表格，表头: {headers}")
                
                # 找到所有数据行（跳过表头行）
                data_rows = table.select('tr.rowfollow')
                
                # 清空已有数据，避免重复
                result["invitees"] = []
                processed_usernames = set()  # 用于跟踪已处理的用户名，避免重复
                
                for row in data_rows:
                    cells = row.select('td')
                    if len(cells) < len(headers):
                        continue
                    
                    invitee = {}
                    username = ""
                    is_banned = False
                    
                    # 检查行类和禁用标记
                    row_classes = row.get('class', [])
                    if isinstance(row_classes, list) and any(cls in ['rowbanned', 'banned'] for cls in row_classes):
                        is_banned = True
                    
                    # 逐列解析数据
                    for idx, header in enumerate(headers):
                        if idx >= len(cells):
                            break
                        
                        cell = cells[idx]
                        cell_text = cell.get_text(strip=True)
                        
                        # 用户名列（通常是第一列）
                        if idx == 0 or any(kw in header for kw in ['用户名', '用戶名', 'username', 'user']):
                            username_link = cell.select_one('a')
                            disabled_img = cell.select_one('img.disabled, img[alt="Disabled"]')
                            
                            if disabled_img:
                                is_banned = True
                            
                            if username_link:
                                username = username_link.get_text(strip=True)
                                invitee["username"] = username
                                
                                # 处理可能在用户名中附带的Disabled文本
                                if "Disabled" in cell.get_text():
                                    is_banned = True
                                
                                # 获取用户个人页链接
                                href = username_link.get('href', '')
                                invitee["profile_url"] = urljoin(site_url, href) if href else ""
                            else:
                                username = cell_text
                                invitee["username"] = username
                        
                        # 邮箱列
                        elif any(kw in header for kw in ['郵箱', '邮箱', 'email', 'mail']):
                            invitee["email"] = cell_text
                        
                        # 启用状态列
                        elif any(kw in header for kw in ['啟用', '启用', 'enabled']):
                            status_text = cell_text.lower()
                            if status_text == 'no' or '禁' in status_text:
                                invitee["enabled"] = "No"
                                is_banned = True
                            else:
                                invitee["enabled"] = "Yes"
                        
                        # 上传量列
                        elif any(kw in header for kw in ['上傳', '上传', 'uploaded', 'upload']):
                            invitee["uploaded"] = cell_text
                        
                        # 下载量列
                        elif any(kw in header for kw in ['下載', '下载', 'downloaded', 'download']):
                            invitee["downloaded"] = cell_text
                        
                        # 分享率列 - 特别处理∞、Inf.等情况
                        elif any(kw in header for kw in ['分享率', '分享比率', 'ratio']):
                            ratio_text = cell_text
                            
                            # 处理特殊分享率表示 - 扩展无限分享率识别
                            if ratio_text.lower() in ['inf.', 'inf', '∞', 'infinite', '无限']:
                                invitee["ratio"] = "∞"
                                invitee["ratio_value"] = 1e20
                            elif ratio_text == '---' or not ratio_text:
                                invitee["ratio"] = "0"
                                invitee["ratio_value"] = 0
                            else:
                                # 获取font标签内的文本，如果存在
                                font_tag = cell.select_one('font')
                                if font_tag:
                                    ratio_text = font_tag.get_text(strip=True)
                                
                                invitee["ratio"] = ratio_text
                                
                                # 尝试解析为浮点数 - 正确处理千分位逗号
                                try:
                                    # 使用更好的方法完全移除千分位逗号
                                    normalized_ratio = ratio_text
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
                                    invitee["ratio_value"] = float(normalized_ratio)
                                except (ValueError, TypeError):
                                    logger.warning(f"无法解析分享率: {ratio_text}")
                                    invitee["ratio_value"] = 0
                        
                        # 做种数列
                        elif any(kw in header for kw in ['做種數', '做种数', 'seeding', 'seeds']):
                            invitee["seeding"] = cell_text
                        
                        # 做种体积列
                        elif any(kw in header for kw in ['做種體積', '做种体积', 'seeding size', 'seed size']):
                            invitee["seeding_size"] = cell_text
                        
                        # 当前纯做种时魔列
                        elif any(kw in header for kw in ['純做種時魔', '当前纯做种时魔', '纯做种时魔', 'seed magic']):
                            invitee["seed_magic"] = cell_text
                        
                        # 后宫加成列
                        elif any(kw in header for kw in ['後宮加成', '后宫加成', 'bonus']):
                            invitee["seed_bonus"] = cell_text
                        
                        # 最后做种汇报时间列
                        elif any(kw in header for kw in ['最後做種匯報時間', '最后做种汇报时间', '最后做种报告', 'last seed']):
                            invitee["last_seed_report"] = cell_text
                        
                        # 状态列
                        elif any(kw in header for kw in ['狀態', '状态', 'status']):
                            invitee["status"] = cell_text
                            
                            # 根据状态判断是否禁用
                            status_lower = cell_text.lower()
                            if any(ban_word in status_lower for ban_word in ['banned', 'disabled', '禁止', '禁用', '封禁']):
                                is_banned = True
                    
                    # 如果用户名不为空且未处理过
                    if username and username not in processed_usernames:
                        processed_usernames.add(username)
                        
                        # 设置启用状态（如果尚未设置）
                        if "enabled" not in invitee:
                            invitee["enabled"] = "No" if is_banned else "Yes"
                        
                        # 设置状态（如果尚未设置）
                        if "status" not in invitee:
                            invitee["status"] = "已禁用" if is_banned else "已確認"
                        
                        # 检查是否是无数据情况（上传下载都是0）
                        uploaded = invitee.get("uploaded", "0")
                        downloaded = invitee.get("downloaded", "0")
                        is_no_data = False
                        
                        # 字符串判断
                        if isinstance(uploaded, str) and isinstance(downloaded, str):
                            # 转换为小写进行比较
                            uploaded_lower = uploaded.lower()
                            downloaded_lower = downloaded.lower()
                            # 检查所有可能的0值表示
                            zero_values = ['0', '', '0b', '0.00 kb', '0.00 b', '0.0 kb', '0kb', '0b', '0.00', '0.0']
                            is_no_data = any(uploaded_lower == val for val in zero_values) and \
                                       any(downloaded_lower == val for val in zero_values)
                        # 数值判断
                        elif isinstance(uploaded, (int, float)) and isinstance(downloaded, (int, float)):
                            is_no_data = uploaded == 0 and downloaded == 0
                        
                        # 添加数据状态标记
                        if is_no_data:
                            invitee["data_status"] = "无数据"
                            logger.debug(f"用户 {invitee.get('username')} 被标记为无数据状态")
                        
                        # 计算分享率健康状态
                        if "ratio_value" in invitee:
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
                            # 处理没有ratio_value的情况
                            if is_no_data:
                                invitee["ratio_health"] = "neutral" 
                                invitee["ratio_label"] = ["无数据", "grey"]
                            elif "ratio" in invitee and invitee["ratio"] == "∞":
                                invitee["ratio_health"] = "excellent"
                                invitee["ratio_label"] = ["无限", "green"]
                            else:
                                invitee["ratio_health"] = "unknown"
                                invitee["ratio_label"] = ["未知", "grey"]
                        
                        # 将用户数据添加到结果中
                        if invitee.get("username"):
                            result["invitees"].append(invitee.copy())
                
                # 记录解析结果
                if result["invitees"]:
                    if is_next_page:
                        logger.debug(f"站点 {site_name} 从翻页中解析到 {len(result['invitees'])} 个后宫成员")
                    else:
                        logger.debug(f"站点 {site_name} 从首页解析到 {len(result['invitees'])} 个后宫成员")

        return result

    def _parse_bonus_shop(self, site_name: str, html_content: str) -> Dict[str, Any]:
        """
        解析魔力值商店页面
        :param site_name: 站点名称
        :param html_content: HTML内容
        :return: 魔力值和邀请价格信息
        """
        result = {
            "bonus": 0,                  # 用户当前魔力值
            "permanent_invite_price": 0, # 永久邀请价格
            "temporary_invite_price": 0  # 临时邀请价格
        }
        
        try:
            # 初始化BeautifulSoup对象
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 1. 查找当前魔力值
            # 查找包含魔力值的文本，常见格式如 "魔力值: 1,234" "积分/魔力值/欢乐值: 1,234" 等
            bonus_patterns = [
                r'魔力值\s*[:：]\s*([\d,\.]+)',
                r'积分\s*[:：]\s*([\d,\.]+)',
                r'欢乐值\s*[:：]\s*([\d,\.]+)',
                r'當前\s*[:：]?\s*([\d,\.]+)',
                r'目前\s*[:：]?\s*([\d,\.]+)',
                r'bonus\s*[:：]?\s*([\d,\.]+)',
                r'([\d,\.]+)\s*个魔力值'
            ]
            
            # 页面文本
            page_text = soup.get_text()
            
            # 尝试不同的正则表达式查找魔力值
            for pattern in bonus_patterns:
                bonus_match = re.search(pattern, page_text, re.IGNORECASE)
                if bonus_match:
                    bonus_str = bonus_match.group(1).replace(',', '')
                    try:
                        result["bonus"] = float(bonus_str)
                        logger.debug(f"站点 {site_name} 魔力值: {result['bonus']}")
                        break
                    except ValueError:
                        continue
            
            # 2. 查找邀请价格
            # 查找表格
            tables = soup.select('table')
            for table in tables:
                # 检查表头是否包含交换/价格等关键词
                headers = table.select('td.colhead, th.colhead, td, th')
                header_text = ' '.join([h.get_text().lower() for h in headers])
                
                if '魔力值' in header_text or '积分' in header_text or 'bonus' in header_text:
                    # 遍历表格行
                    rows = table.select('tr')
                    for row in rows:
                        cells = row.select('td')
                        if len(cells) < 3:
                            continue
                            
                        # 获取行文本
                        row_text = row.get_text().lower()
                        
                        # 检查是否包含邀请关键词
                        if '邀请名额' in row_text or '邀請名額' in row_text or '邀请' in row_text or 'invite' in row_text:
                            # 查找价格列(通常是第3列)
                            price_cell = None
                            
                            # 检查单元格数量
                            if len(cells) >= 3:
                                for i, cell in enumerate(cells):
                                    cell_text = cell.get_text().lower()
                                    if '价格' in cell_text or '魔力值' in cell_text or '积分' in cell_text or '售价' in cell_text:
                                        # 找到了价格列标题，下一列可能是价格
                                        if i+1 < len(cells):
                                            price_cell = cells[i+1]
                                            break
                                    elif any(price_word in cell_text for price_word in ['price', '价格', '售价']):
                                        price_cell = cell
                                        break
                            
                            # 如果没找到明确的价格列，就默认第3列
                            if not price_cell and len(cells) >= 3:
                                price_cell = cells[2]
                            
                            # 提取价格
                            if price_cell:
                                price_text = price_cell.get_text().strip()
                                try:
                                    # 尝试提取数字
                                    price_match = re.search(r'([\d,\.]+)', price_text)
                                    if price_match:
                                        price = float(price_match.group(1).replace(',', ''))
                                        
                                        # 判断是永久邀请还是临时邀请
                                        if '临时' in row_text or '臨時' in row_text or 'temporary' in row_text:
                                            result["temporary_invite_price"] = price
                                            logger.debug(f"站点 {site_name} 临时邀请价格: {price}")
                                        else:
                                            result["permanent_invite_price"] = price
                                            logger.debug(f"站点 {site_name} 永久邀请价格: {price}")
                                except ValueError:
                                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"解析站点 {site_name} 魔力值商店失败: {str(e)}")
            return result 

    def _get_health_from_ratio_value(self, ratio):
        """
        根据分享率数值获取健康状态和标签
        """
        # 分享率健康度判断
        if ratio >= 4.0:
            return "excellent", ["极好", "text-success"]
        elif ratio >= 2.0:
            return "good", ["良好", "text-success"]
        elif ratio >= 1.0:
            return "good", ["正常", "text-success"]
        elif ratio > 0:
            return "warning" if ratio >= 0.4 else "danger", ["较低", "text-warning"] if ratio >= 0.4 else ["危险", "text-error"]
        else:
            return "neutral", ["无数据", "text-grey"]

"""
蝶粉站点处理
"""
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.log import logger
from plugins.nexusinvitee.sites import _ISiteHandler


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
            
            # 获取邀请页面
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
            
            return invite_result
            
        except Exception as e:
            logger.error(f"解析站点 {site_name} 邀请页面失败: {str(e)}")
            result["invite_status"]["reason"] = f"解析邀请页面失败: {str(e)}"
            return result
    
    def _parse_butterfly_invite_page(self, site_name: str, site_url: str, html_content: str) -> Dict[str, Any]:
        """
        解析蝶粉站点邀请页面HTML内容
        :param site_name: 站点名称
        :param site_url: 站点URL
        :param html_content: HTML内容
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
        
        # 先检查info_block中的邀请信息
        info_block = soup.select_one('#info_block')
        if info_block:
            info_text = info_block.get_text()
            logger.info(f"站点 {site_name} 获取到info_block信息")
            
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
                    
                    logger.info(f"站点 {site_name} 解析到邀请数量: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}")
                    
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
                            
                            logger.info(f"站点 {site_name} 从后续文本解析到邀请数量: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}")
                            
                            # 如果有邀请名额，初步判断为可邀请
                            if result["invite_status"]["permanent_count"] > 0 or result["invite_status"]["temporary_count"] > 0:
                                result["invite_status"]["can_invite"] = True
                                result["invite_status"]["reason"] = f"可用邀请数: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}"
        
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
                
                logger.info(f"站点 {site_name} 找到用户表格，表头: {headers}")
                
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
                            
                            # 处理特殊分享率表示
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
                                
                                # 尝试解析为浮点数
                                try:
                                    # 替换逗号为点
                                    normalized_ratio = ratio_text.replace(',', '.')
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
                    logger.info(f"站点 {site_name} 从特殊格式表格解析到 {len(result['invitees'])} 个后宫成员")
        
        # 检查邀请权限
        form_disabled = soup.select_one('input[disabled][value*="貴賓 或以上等級才可以"]')
        if form_disabled:
            disabled_text = form_disabled.get('value', '')
            result["invite_status"]["can_invite"] = False
            result["invite_status"]["reason"] = disabled_text
            logger.info(f"站点 {site_name} 邀请按钮被禁用: {disabled_text}")

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
                        logger.info(f"站点 {site_name} 魔力值: {result['bonus']}")
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
                                            logger.info(f"站点 {site_name} 临时邀请价格: {price}")
                                        else:
                                            result["permanent_invite_price"] = price
                                            logger.info(f"站点 {site_name} 永久邀请价格: {price}")
                                except ValueError:
                                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"解析站点 {site_name} 魔力值商店失败: {str(e)}")
            return result 
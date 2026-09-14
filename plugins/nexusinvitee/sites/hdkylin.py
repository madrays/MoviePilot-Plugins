# plugins/nexusinvitee/sites/hdkylin.py
"""
麒麟(HDKylin)站点处理器
"""
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
import traceback

import requests
from bs4 import BeautifulSoup

from app.log import logger
from . import _ISiteHandler


class HdkylinHandler(_ISiteHandler):
    """
    麒麟(HDKylin)站点处理类
    """
    # 站点类型标识
    site_schema = "hdkylin" # 使用小写且唯一的标识符

    @classmethod
    def match(cls, site_url: str) -> bool:
        """
        判断是否匹配麒麟站点
        :param site_url: 站点URL
        :return: 是否匹配
        """
        # 仅通过域名精确匹配
        if "hdkyl.in" in site_url.lower():
            logger.info(f"匹配到麒麟站点: {site_url}")
            return True
        return False

    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        """
        解析麒麟站点邀请页面
        :param site_info: 站点信息
        :param session: 已配置好的请求会话
        :return: 解析结果字典
        """
        site_name = site_info.get("name", "")
        site_url = site_info.get("url", "")

        # 初始化默认结果
        result = {
            "invite_status": {
                "can_invite": False,
                "reason": "数据获取失败", # Default reason
                "permanent_count": 0,
                "temporary_count": 0,
                "bonus": 0,
                "permanent_invite_price": 0,
                "temporary_invite_price": 0
            },
            "invitees": []
        }
        
        user_id = None

        try:
            # 1. 获取用户ID (尝试从 invite_url 或 usercp.php 获取)
            # 优先尝试从已知的 invite_url 解析
            invite_page_url = "" # 初始化
            info_block_text = "" # 初始化
            invite_page_html = "" # 初始化
            
            try:
                # 尝试访问站点首页获取 info_block 来提取 user_id 和初始信息
                index_response = session.get(site_url, timeout=(10, 30))
                index_response.raise_for_status()
                index_soup = BeautifulSoup(index_response.text, 'html.parser')
                info_block = index_soup.select_one('#info_block')
                
                if info_block:
                    info_block_text = info_block.get_text()
                    # 从邀请链接提取用户ID
                    invite_link_tag = info_block.select_one('a[href*="invite.php?id="]')
                    if invite_link_tag and invite_link_tag.get('href'):
                       match_id = re.search(r'id=(\d+)', invite_link_tag['href'])
                       if match_id:
                           user_id = match_id.group(1)
                           logger.info(f"站点 {site_name} 从 info_block 提取到用户ID: {user_id}")
                           invite_page_url = urljoin(site_url, f"invite.php?id={user_id}")
                       else:
                            logger.warning(f"站点 {site_name} 在 info_block 邀请链接中未找到用户ID")
                else:
                    logger.warning(f"站点 {site_name} 在首页未找到 #info_block")

                # 如果无法从 info_block 获取 user_id，尝试通用方法
                if not user_id:
                    user_id = self._get_user_id(session, site_url)
                    if user_id:
                        logger.info(f"站点 {site_name} 通过通用方法获取到用户ID: {user_id}")
                        invite_page_url = urljoin(site_url, f"invite.php?id={user_id}")
                    else:
                         logger.error(f"站点 {site_name} 无法获取用户ID")
                         result["invite_status"]["reason"] = "无法获取用户ID，请检查Cookie或站点是否可访问"
                         return result

            except Exception as e:
                 logger.error(f"站点 {site_name} 获取用户ID过程中出错: {str(e)}")
                 result["invite_status"]["reason"] = f"获取用户信息失败: {str(e)}"
                 return result

            # 2. 访问并解析邀请页面 (`invite.php?id=...`)
            try:
                invite_response = session.get(invite_page_url, timeout=(10, 30))
                invite_response.raise_for_status()
                invite_page_html = invite_response.text
                invite_soup = BeautifulSoup(invite_page_html, 'html.parser')

                # 解析 info_block (如果首页没取到，这里再取一次)
                if not info_block_text:
                    info_block = invite_soup.select_one('#info_block')
                    if info_block:
                        info_block_text = info_block.get_text()
                    else:
                         logger.warning(f"站点 {site_name} 在邀请页面也未找到 #info_block")

                # --- 解析邀请数量 (从 info_block) ---
                if info_block_text:
                    invite_link_text = ""
                    # 直接在文本中查找包含"邀请"和数字括号的模式
                    invite_match_text = re.search(r'邀请\s*[:：]\s*(\d+)\s*\((\d+)\)', info_block_text)
                    if invite_match_text:
                        try:
                            result["invite_status"]["permanent_count"] = int(invite_match_text.group(1))
                            result["invite_status"]["temporary_count"] = int(invite_match_text.group(2))
                            logger.info(f"站点 {site_name} 从 info_block 解析到邀请数: 永久={result['invite_status']['permanent_count']}, 临时={result['invite_status']['temporary_count']}")
                        except (ValueError, TypeError) as e:
                             logger.warning(f"站点 {site_name} 解析邀请数量文本失败: {invite_match_text.group(0)}, Error: {e}")
                    else:
                        logger.warning(f"站点 {site_name} 在 info_block 未找到 '邀请 : X(Y)' 格式的文本")
                
                # --- 解析邀请权限和原因 (从邀请按钮) ---
                invite_nav = invite_soup.select_one('#invitenav')
                can_invite_flag = False
                invite_reason = "未知邀请状态" # Default

                if invite_nav:
                    invite_button = invite_nav.select_one('form[action*="invite.php"] input[type="submit"]')
                    if invite_button:
                        if invite_button.has_attr('disabled'):
                            can_invite_flag = False
                            invite_reason = invite_button.get('value', '邀请权限不足（未知原因）')
                            logger.info(f"站点 {site_name} 不可邀请，原因: {invite_reason}")
                        else:
                            can_invite_flag = True
                            invite_reason = "可以发送邀请" # 或者取按钮value? value可能是"邀请"
                            logger.info(f"站点 {site_name} 可以发送邀请 (按钮未禁用)")
                    else:
                        invite_reason = "无法找到邀请按钮"
                        logger.warning(f"站点 {site_name} {invite_reason}")
                else:
                     invite_reason = "无法找到邀请导航栏 (#invitenav)"
                     logger.warning(f"站点 {site_name} {invite_reason}")

                result["invite_status"]["can_invite"] = can_invite_flag
                result["invite_status"]["reason"] = invite_reason

                # --- 解析被邀请人列表 ---
                invitee_table = invite_soup.select_one('table[border="1"]') # 定位特定的表格
                if invitee_table:
                    # 检查是否包含 "没有被邀者"
                    no_invitee_text = invitee_table.find(text=lambda t: t and "没有被邀者" in t)
                    if no_invitee_text:
                        logger.info(f"站点 {site_name} 没有被邀请者记录")
                        result["invitees"] = []
                    else:
                        # TODO: 在这里添加解析被邀请人表格行的逻辑
                        # 因为提供的HTML没有被邀请人数据，暂时留空
                        # 需要根据实际有数据的HTML确定表头和列顺序
                        logger.warning(f"站点 {site_name} 检测到可能存在的被邀请人表格，但缺少解析逻辑（需要带数据的HTML）")
                        result["invitees"] = [] # 暂时返回空列表
                else:
                    logger.warning(f"站点 {site_name} 未找到被邀请人表格 (table[border=\"1\"])")

            except requests.exceptions.RequestException as req_err_invite:
                error_info = f"访问邀请页面网络错误: {str(req_err_invite)}"
                logger.error(f"站点 {site_name} 处理失败: {error_info}")
                result["invite_status"]["reason"] = error_info
                return result
            except Exception as invite_err:
                error_info = f"解析邀请页面时发生错误: {str(invite_err)}"
                logger.error(f"站点 {site_name} 处理失败: {error_info}")
                logger.error(traceback.format_exc())
                result["invite_status"]["reason"] = error_info
                # 继续尝试解析商店，但标记解析有问题
                pass # Continue to bonus parsing

            # 3. 访问并解析魔力值商店页面 (`mybonus.php`)
            try:
                bonus_url = urljoin(site_url, "mybonus.php")
                bonus_response = session.get(bonus_url, timeout=(10, 30))
                bonus_response.raise_for_status()
                bonus_soup = BeautifulSoup(bonus_response.text, 'html.parser')

                # --- 解析当前魔力值 ---
                # 更精确地定位包含魔力值的文本节点
                bonus_tag = bonus_soup.find(lambda tag: tag.name == "td" and "用你的魔力值" in tag.get_text() and "当前" in tag.get_text())

                if bonus_tag:
                    bonus_text = bonus_tag.get_text()
                    bonus_match = re.search(r'当前([\d,\.]+)', bonus_text)
                    if bonus_match:
                        bonus_str = bonus_match.group(1).replace(',', '')
                        try:
                            result["invite_status"]["bonus"] = float(bonus_str)
                            logger.info(f"站点 {site_name} 魔力值: {result['invite_status']['bonus']}")
                        except ValueError:
                            logger.warning(f"站点 {site_name} 无法解析魔力值: {bonus_match.group(1)}")
                    else:
                        logger.warning(f"站点 {site_name} 未在目标单元格找到 '当前X.X' 格式的魔力值文本: {bonus_text[:100]}...") # 记录部分文本
                else:
                    # Fallback: 尝试在整个页面查找
                    page_text = bonus_soup.get_text()
                    bonus_match_fallback = re.search(r'当前([\d,\.]+)', page_text)
                    if bonus_match_fallback:
                         bonus_str = bonus_match_fallback.group(1).replace(',', '')
                         try:
                             result["invite_status"]["bonus"] = float(bonus_str)
                             logger.info(f"站点 {site_name} 通过页面文本回退找到魔力值: {result['invite_status']['bonus']}")
                         except ValueError:
                             logger.warning(f"站点 {site_name} 无法解析页面文本中的魔力值: {bonus_match_fallback.group(1)}")
                    else:
                        logger.warning(f"站点 {site_name} 未找到包含'当前魔力值'信息的单元格或文本")


                # --- 解析邀请价格 ---
                # 定位包含商店项目的表格行，假设还是table[border="1"]
                shop_table = bonus_soup.select_one('table[border="1"]')
                if shop_table:
                    rows = shop_table.select('tr')
                    for row in rows:
                        cells = row.select('td')
                        # 确保行结构符合预期 (项目名/简介/价格/按钮)
                        if len(cells) >= 4:
                            item_text = cells[1].get_text() # 第2个单元格是简介
                            price_text = cells[2].get_text().strip().replace(',', '') # 第3个单元格是价格

                            # 查找临时邀请
                            if "临时邀请名额" in item_text:
                                try:
                                    price_match = re.search(r'([\d,\.]+)', price_text)
                                    if price_match:
                                        result["invite_status"]["temporary_invite_price"] = float(price_match.group(1))
                                        logger.info(f"站点 {site_name} 临时邀请价格: {result['invite_status']['temporary_invite_price']}")
                                    else:
                                        logger.warning(f"站点 {site_name} 临时邀请行未找到价格数字: {price_text}")
                                except ValueError:
                                    logger.warning(f"站点 {site_name} 无法解析临时邀请价格: {price_text}")

                            # 查找永久邀请 (假设描述中不含"临时")
                            elif "邀请名额" in item_text: # 匹配不含"临时"的邀请名额
                                try:
                                    price_match = re.search(r'([\d,\.]+)', price_text)
                                    if price_match:
                                        result["invite_status"]["permanent_invite_price"] = float(price_match.group(1))
                                        logger.info(f"站点 {site_name} 永久邀请价格: {result['invite_status']['permanent_invite_price']}")
                                    else:
                                        logger.warning(f"站点 {site_name} 永久邀请行未找到价格数字: {price_text}")
                                except ValueError:
                                    logger.warning(f"站点 {site_name} 无法解析永久邀请价格: {price_text}")
                else:
                    logger.warning(f"站点 {site_name} 未找到魔力值商店表格 (table[border=\"1\"])")

            except requests.exceptions.RequestException as req_err_bonus:
                 logger.warning(f"站点 {site_name} 访问魔力商店网络错误: {str(req_err_bonus)}")
                 # 不改变现有 reason，只记录警告
            except Exception as bonus_err:
                 logger.warning(f"站点 {site_name} 解析魔力商店时发生错误: {str(bonus_err)}")
                 # 不改变现有 reason，只记录警告


            # --- 补充 Reason (如果不可邀请但可购买) ---
            if not result["invite_status"]["can_invite"] and result["invite_status"]["reason"]:
                bonus = result["invite_status"]["bonus"]
                temp_price = result["invite_status"]["temporary_invite_price"]
                perm_price = result["invite_status"]["permanent_invite_price"]
                can_buy_temp = bonus > 0 and temp_price > 0 and bonus >= temp_price
                can_buy_perm = bonus > 0 and perm_price > 0 and bonus >= perm_price

                if can_buy_temp or can_buy_perm:
                    buy_info = []
                    if can_buy_temp:
                        buy_info.append(f"临时邀请({int(bonus / temp_price)}个, {temp_price}魔力/个)")
                    if can_buy_perm:
                         buy_info.append(f"永久邀请({int(bonus / perm_price)}个, {perm_price}魔力/个)")
                    if buy_info:
                        result["invite_status"]["reason"] += f"，但您的魔力值({bonus})可购买{'、'.join(buy_info)}"

            return result

        except Exception as final_err:
             # 最终捕获未预料的错误
            error_info = f"处理站点 {site_name} 时发生未知错误: {str(final_err)}"
            logger.error(error_info)
            logger.error(traceback.format_exc())
            result["invite_status"]["reason"] = error_info # 更新错误信息
            return result

    # 辅助方法：从页面解析邀请状态 (移植自NexusPhpHandler._parse_nexusphp_invite_page)
    def _parse_invite_status_from_page(self, site_name: str, html_content: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, 'html.parser')
        invite_status = {"can_invite": False, "reason": "", "permanent_count": 0, "temporary_count": 0}

        # 1. 检查 info_block (如果存在)
        info_block = soup.select_one('#info_block')
        if info_block:
            invite_link = info_block.select_one('a[href*="invite.php"]')
            if invite_link:
                parent_text = invite_link.parent.get_text() if invite_link.parent else ""
                # Corrected regex for invite counts
                invite_pattern = re.compile(r'(?:邀请|探视权|invite|邀請|查看权|查看權).*?:?\s*(\d+)(?:\s*\((\d+)\))?', re.IGNORECASE)
                invite_match = invite_pattern.search(parent_text)
                if invite_match:
                    if invite_match.group(1): invite_status["permanent_count"] = int(invite_match.group(1))
                    if len(invite_match.groups()) > 1 and invite_match.group(2): invite_status["temporary_count"] = int(invite_match.group(2))
                    if invite_status["permanent_count"] > 0 or invite_status["temporary_count"] > 0:
                        invite_status["can_invite"] = True # 初步判断
                        invite_status["reason"] = f"可用邀请数: 永久={invite_status['permanent_count']}, 临时={invite_status['temporary_count']}"
                else:
                    # 尝试解析链接后的文本
                    after_text = ""
                    next_sibling = invite_link.next_sibling
                    while next_sibling and not after_text.strip():
                        if isinstance(next_sibling, str): after_text = next_sibling
                        next_sibling = next_sibling.next_sibling if hasattr(next_sibling, 'next_sibling') else None
                    if after_text:
                        # Corrected regex for text after link
                        after_pattern = re.compile(r'(?::)?\s*(\d+)(?:\s*\((\d+)\))?')
                        after_match = after_pattern.search(after_text)
                        if after_match:
                            if after_match.group(1): invite_status["permanent_count"] = int(after_match.group(1))
                            if len(after_match.groups()) > 1 and after_match.group(2): invite_status["temporary_count"] = int(after_match.group(2))
                            if invite_status["permanent_count"] > 0 or invite_status["temporary_count"] > 0:
                                invite_status["can_invite"] = True # 初步判断
                                invite_status["reason"] = f"可用邀请数: 永久={invite_status['permanent_count']}, 临时={invite_status['temporary_count']}"

        # 2. 检查邀请表单和错误信息
        invite_form = soup.select('form[action*="takeinvite.php"], form[action*="invite.php"]') # 包含 takeinvite.php 或 invite.php
        can_invite_from_form = False
        reason_from_page = ""

        if invite_form:
            submit_btn = None
            for form in invite_form:
                # 查找未被禁用的提交按钮
                submit_btn = form.select_one('input[type="submit"]:not([disabled])')
                if submit_btn:
                    can_invite_from_form = True
                    reason_from_page = "存在可用邀请表单"
                    break # 找到一个即可

        if not can_invite_from_form:
            # 查找禁用的提交按钮获取原因
            disabled_submit = soup.select_one('form[action*="invite.php"] input[type="submit"][disabled]')
            if disabled_submit and disabled_submit.get('value'):
                reason_from_page = disabled_submit['value']
            else:
                # 查找常见的错误文本
                no_invite_text = soup.find(text=lambda t: t and ('没有剩余邀请名额' in t or '邀请数量不足' in t))
                if no_invite_text:
                    reason_from_page = "没有剩余邀请名额"
                else:
                    # 查找权限限制信息 (更通用的模式)
                    restriction_patterns = [
                        r"只有.*?才能发送邀请", r".*?及以上.*?才能发送邀请", r".*?才可以发送邀请",
                        r".*?或以上等级才可以发送邀请", r".*?或以上等级才可以.*?邀请", r"贵宾.*?及以上.*?",
                        r"当前账户上限数已到", r"发布员.*?或以上等级才可以发送邀请" # 添加麒麟站的特定原因
                    ]
                    page_text = soup.get_text()
                    for pattern in restriction_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            reason_from_page = match.group(0)
                            break

        # 综合判断最终状态
        if can_invite_from_form:
            invite_status["can_invite"] = True
            invite_status["reason"] = reason_from_page
        elif "数量不足" in reason_from_page or "名额不足" in reason_from_page:
            invite_status["can_invite"] = True # 数量不足也算可以发药
            invite_status["reason"] = reason_from_page
        elif reason_from_page: # 如果找到了明确的不可邀请原因
            invite_status["can_invite"] = False
            invite_status["reason"] = reason_from_page
        # 如果页面没表单也没错误，但info_block判断可邀请，则以info_block为准 (保持初步判断)
        elif invite_status["can_invite"]:
            pass
        else: # 未知状态
            invite_status["can_invite"] = False
            invite_status["reason"] = "无法发送邀请，请手动查看原因"

        return invite_status

    # 辅助方法：解析被邀请人表格 (移植自NexusPhpHandler._parse_nexusphp_invite_page)
    def _parse_invitee_table(self, site_name: str, html_content: str, site_url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        invitees = []
        # 麒麟站使用 table[border="1"] 作为主要用户表格
        invitee_tables = soup.select('table[border="1"]')

        if not invitee_tables:
            logger.warning(f"站点 {site_name} 未找到预期的被邀请人表格 (table[border=\"1\"])")
            # 尝试备用选择器 (如果将来结构变化)
            # invitee_tables = soup.select('table.main table.torrents')
            # if not invitee_tables:
            #    all_tables = soup.select('table')
            #    invitee_tables = [table for table in all_tables if len(table.select('tr')) > 2]
            # if not invitee_tables:
            #    return [] # 确实没找到
            return []

        for table in invitee_tables:
            header_row = table.select_one('tr')
            if not header_row: continue
            # 获取表头文本，转换为小写
            headers = [cell.get_text(strip=True).lower() for cell in header_row.select('td.colhead, th.colhead, td, th')]

            # 确认是否是用户表 (包含关键列头)
            if not any(keyword in ' '.join(headers) for keyword in ['用户名', '邮箱', 'email', '分享率', 'ratio', 'username', '会员', 'member', '用户']): continue
            logger.debug(f"站点 {site_name} 找到后宫用户表，表头: {headers}")

            rows = table.select('tr:not(:first-child)') # 跳过表头行
            for row in rows:
                cells = row.select('td')
                if not cells:
                    continue
                # 检查是否是"没有被邀者"的行
                if len(cells) == 1 and "没有被邀者" in cells[0].get_text():
                    logger.info(f"站点 {site_name} 明确提示没有被邀请者")
                    return [] # 返回空列表

                if len(cells) < max(3, len(headers) - 4): # 允许列数稍少于表头, 但至少有3列
                     logger.debug(f"站点 {site_name} 跳过无效行，单元格数量: {len(cells)}, 表头数量: {len(headers)}")
                     continue

                invitee = {}
                # 检查是否被禁用 (从样式判断)
                is_banned = 'rowbanned' in row.get('class', []) or 'banned' in row.get('class', []) or 'disabled' in row.get('class', [])
                # 检查是否有禁用图标
                if row.select_one('img.disabled, img[alt="Disabled"], img[src*="disabled"]'): is_banned = True

                # 遍历单元格，根据表头匹配数据
                for idx, cell in enumerate(cells):
                    if idx >= len(headers): break # 防止索引越界
                    header = headers[idx]
                    cell_text = cell.get_text(strip=True)

                    # 提取数据
                    if any(k in header for k in ['用户名', 'username', '会员', 'member', '用户']):
                        link = cell.select_one('a')
                        invitee["username"] = link.get_text(strip=True) if link else cell_text
                        if link and link.get('href'): invitee["profile_url"] = urljoin(site_url, link['href'])
                    elif any(k in header for k in ['邮箱', 'email']): invitee["email"] = cell_text
                    elif any(k in header for k in ['启用', '狀態', 'enabled']): invitee["enabled"] = "No" if cell_text.lower() == 'no' or is_banned else "Yes"
                    elif any(k in header for k in ['上传', 'uploaded', '上傳']): invitee["uploaded"] = cell_text
                    elif any(k in header for k in ['下载', 'downloaded', '下載']): invitee["downloaded"] = cell_text
                    elif any(k in header for k in ['分享率', 'ratio']): invitee["ratio"] = cell_text
                    elif any(k in header for k in ['做种数', 'seeding', '做種數']): invitee["seeding"] = cell_text
                    elif any(k in header for k in ['做种体积', 'size', '做種體積']): invitee["seeding_size"] = cell_text
                    elif any(k in header for k in ['做种时间', 'time', '做種時間']): invitee["seed_time"] = cell_text
                    elif any(k in header for k in ['做种时魔', 'magic', '做种积分', 'seed bonus', '单种魔力']): invitee["seed_magic"] = cell_text
                    elif any(k in header for k in ['后宫加成', 'bonus', '加成', 'invitee bonus']): invitee["seed_bonus"] = cell_text
                    elif any(k in header for k in ['最后做种汇报', 'report', '最後做種報告', 'last seen', '最后访问']):
                        invitee["last_seed_report"] = cell_text # 统一字段名
                    elif any(k in header for k in ['状态', 'status']): invitee["status"] = cell_text

                # 确保状态字段存在
                if "enabled" not in invitee: invitee["enabled"] = "No" if is_banned else "Yes"
                if "status" not in invitee: invitee["status"] = "已禁用" if invitee["enabled"] == "No" else "已确认"

                # --- 添加分享率健康度计算 --- (移植自NexusPhpHandler)
                ratio_value = 0
                ratio_health = "unknown"
                ratio_label = ["未知", "text-grey"]
                is_no_data_invitee = False

                # 检查是否无数据
                if "uploaded" in invitee and "downloaded" in invitee:
                    up = invitee["uploaded"]
                    down = invitee["downloaded"]
                    if isinstance(up, str) and isinstance(down, str):
                        is_no_data_invitee = (up=='0' or up=='' or up=='0.0' or up.lower()=='0b') and (down=='0' or down=='' or down=='0.0' or down.lower()=='0b')
                    elif isinstance(up, (int, float)) and isinstance(down, (int, float)):
                        is_no_data_invitee = up == 0 and down == 0

                if is_no_data_invitee:
                    ratio_health = "neutral"
                    ratio_label = ["无数据", "text-grey"]
                elif "ratio" in invitee:
                    ratio_str = invitee["ratio"]
                    if ratio_str == '∞' or ratio_str.lower() in ['inf.', 'inf', 'infinite', '无限']:
                        ratio_health = "excellent"
                        ratio_label = ["无限", "text-success"]
                        ratio_value = 1e20
                    else:
                        try:
                            # 标准化处理
                            normalized_ratio = ratio_str
                            while ',' in normalized_ratio:
                                comma_positions = [pos for pos, char in enumerate(normalized_ratio) if char == ',']
                                for pos in comma_positions:
                                    if (pos > 0 and pos < len(normalized_ratio) - 1 and
                                        normalized_ratio[pos-1].isdigit() and normalized_ratio[pos+1].isdigit()):
                                        normalized_ratio = normalized_ratio[:pos] + normalized_ratio[pos+1:]
                                        break
                                else: break
                            normalized_ratio = normalized_ratio.replace(',', '.')
                            ratio_value = float(normalized_ratio)

                            # 判断健康度
                            if ratio_value >= 1.0: ratio_health = "good"; ratio_label = ["良好", "text-success"]
                            elif ratio_value >= 0.5: ratio_health = "warning"; ratio_label = ["较低", "text-warning"]
                            else: ratio_health = "danger"; ratio_label = ["危险", "text-error"]
                        except (ValueError, TypeError):
                            ratio_health = "unknown"; ratio_label = ["无效", "text-grey"]

                invitee["ratio_value"] = ratio_value
                invitee["ratio_health"] = ratio_health
                invitee["ratio_label"] = ratio_label
                # --- 分享率健康度计算结束 ---

                if invitee.get("username"): # 确保至少解析到用户名
                    invitees.append(invitee)
            # 跳出外层循环，因为我们假定只有一个主要的用户表格
            break

        if invitees:
            logger.debug(f"站点 {site_name} 从表格解析到 {len(invitees)} 个后宫成员")
        # 仅在确实没有找到表格，或者表格内没有用户且没有"没有被邀者"提示时警告
        elif not invitee_tables or (not invitees and not any("没有被邀者" in t.get_text() for t in soup.select('table[border="1"] td'))):
            logger.warning(f"站点 {site_name} 未能从表格中解析到任何后宫成员")

        return invitees

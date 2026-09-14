"""
M-Team站点处理
"""
import time
from typing import Dict, Any, List
import requests
import re

try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger
from . import _ISiteHandler


class MTeamHandler(_ISiteHandler):
    """
    M-Team站点处理类 - 仅使用API方式
    """
    # 站点类型标识
    site_schema = "mteam"
    
    @classmethod
    def match(cls, site_url: str) -> bool:
        """
        判断是否匹配M-Team站点
        :param site_url: 站点URL
        :return: 是否匹配
        """
        # M-Team站点的特征
        mteam_features = [
            "m-team",
            "pt.m-team",
            "kp.m-team",
            "zp.m-team",
            "api.m-team.cc",
            "api.m-team.io"
        ]
        
        site_url_lower = site_url.lower()
        for feature in mteam_features:
            if feature in site_url_lower:
                logger.info(f"匹配到M-Team站点特征: {feature}")
                return True
        
        return False
    
    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        """
        使用API方式解析M-Team站点邀请数据
        :param site_info: 站点信息
        :param session: 已配置好的请求会话
        :return: 解析结果
        """
        site_name = site_info.get("name", "")
        site_url = site_info.get("url", "")
        api_key = site_info.get("apikey", "")
        authorization = site_info.get("token", "")  # 使用token字段作为Authorization
        
        # 记录站点配置信息（隐藏敏感内容）
        logger.info(f"站点 {site_name} 配置信息: URL={site_url}, API Key设置={bool(api_key)}, Token设置={bool(authorization)}")
        
        # 用户级别字典
        MTeam_sysRoleList = {
            "1": "User",
            "2": "Power User",
            "3": "Elite User",
            "4": "Crazy User",
            "5": "Insane User",
            "6": "Veteran User",
            "7": "Extreme User",
            "8": "Ultimate User",
            "9": "Nexus Master",
            "10": "VIP",
            "11": "Retiree",
            "12": "Uploader",
            "13": "Moderator",
            "14": "Administrator",
            "15": "Sysop",
            "16": "Staff",
            "17": "Offer memberStaff",
            "18": "Bet memberStaff",
        }
        
        result = {
            "invite_status": {
                "can_invite": False,
                "reason": "",
                "permanent_count": 0,
                "temporary_count": 0
            },
            "invitees": []
        }
        
        try:
            # 检查API认证信息
            if not api_key or not authorization:
                logger.error(f"站点 {site_name} API认证信息不完整")
                result["invite_status"]["reason"] = "API认证信息不完整，请在站点设置中配置API Key和Authorization"
                return result
            
            # 提取API域名
            api_domain = self._extract_api_domain(site_url)
            api_base_url = f"https://api.{api_domain}/api"
            logger.info(f"站点 {site_name} 使用API基础URL: {api_base_url}")
            
            # 配置API请求头 (根据最新参考调整，但恢复 Authorization)
            headers = {
                "Content-Type": "application/json",
                "User-Agent": site_info.get("ua", "Mozilla/5.0"),
                "Accept": "application/json, text/plain, */*",
                "Authorization": authorization, # 恢复 Authorization
                "x-api-key": api_key,
                # "ts": str(int(time.time())) # 保持移除 ts
            }
            
            # 重置会话并添加API认证头
            session.headers.clear()
            session.headers.update(headers)
            
            # 步骤1: 获取用户信息
            user_data = self._get_user_profile(api_base_url, session, site_name)
            if not user_data:
                result["invite_status"]["reason"] = "获取用户信息失败"
                return result
            
            # 提取用户ID、永久邀请和临时邀请数量
            user_id = user_data.get("id")
            if not user_id:
                result["invite_status"]["reason"] = "获取用户ID失败"
                return result
                
            # 直接从用户信息中获取邀请数量
            permanent_invites = int(user_data.get("invites", "0"))
            temporary_invites = int(user_data.get("limitInvites", "0"))
            
            # 获取用户等级
            user_role = user_data.get("role", "1")
            user_role_name = MTeam_sysRoleList.get(user_role, "未知等级")
            
            # 检查用户等级是否有邀请权限 (Elite User及以上)
            has_invite_permission = int(user_role) >= 3
            
            # 获取用户魔力值
            if user_data.get("memberCount") and isinstance(user_data["memberCount"], dict):
                user_bonus = float(user_data["memberCount"].get("bonus", "0"))
            else:
                user_bonus = 0
                
            # 计算可购买的临时邀请数量
            buyable_invites = int(user_bonus / 80000)
            
            logger.info(f"站点 {site_name} 用户ID: {user_id}, 永久邀请: {permanent_invites}, 临时邀请: {temporary_invites}, "
                       f"用户等级: {user_role_name}({user_role}), 魔力值: {user_bonus}, 可购买邀请: {buyable_invites}")
            
            # 更新邀请状态
            result["invite_status"].update({
                "permanent_count": permanent_invites,
                "temporary_count": temporary_invites,
                "can_invite": has_invite_permission and (permanent_invites > 0 or temporary_invites > 0 or buyable_invites > 0)
            })
            
            if not has_invite_permission:
                reason = f"当前用户等级不足，需要Elite User及以上才能发送邀请"
            elif permanent_invites > 0 or temporary_invites > 0:
                if buyable_invites > 0:
                    reason = f"用户等级({user_role_name})魔力值({user_bonus})可购买{buyable_invites}个临时邀请"
                else:
                    reason = f"用户等级({user_role_name})魔力值({user_bonus})"
            elif buyable_invites > 0:
                reason = f"无可用邀请名额，用户等级({user_role_name})魔力值({user_bonus})可购买{buyable_invites}个临时邀请"
            else:
                reason = f"没有可用的邀请名额，用户等级({user_role_name})魔力值({user_bonus})不足购买临时邀请(需80000魔力/个)"
            
            result["invite_status"]["reason"] = reason
            logger.info(f"站点 {site_name} 不可邀请原因: {reason}")
            
            # 步骤2: 获取被邀请人列表
            if user_id:
                invitees = self._get_invite_history(api_base_url, session, user_id, site_name)
                if invitees:
                    result["invitees"] = self._process_invitees(invitees)
                    logger.info(f"站点 {site_name} 获取到 {len(result['invitees'])} 个被邀请人")
            
            # 更新最后访问时间
            self._update_last_browse(api_base_url, session, site_name)
            
            return result
            
        except Exception as e:
            logger.error(f"解析站点 {site_name} 邀请页面失败: {str(e)}")
            result["invite_status"]["reason"] = f"解析邀请页面失败: {str(e)}"
            return result
            
    def _extract_api_domain(self, url: str) -> str:
        """
        从URL提取API域名
        :param url: 站点URL
        :return: API域名
        """
        if not url:
            return "m-team.cc"
            
        # 移除协议前缀和路径
        domain = url.lower()
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        
        # 直接使用API域名
        if domain in ["api.m-team.cc", "api.m-team.io"]:
            # 截取m-team.cc或m-team.io部分
            return domain.replace("api.", "")
            
        # 特殊处理m-team子域名
        if domain.startswith("www."):
            domain = domain[4:]
        elif any(domain.startswith(prefix) for prefix in ["pt.", "kp.", "zp."]):
            domain = domain[3:]
            
        # 如果域名包含m-team，提取主域名
        if "m-team.io" in domain:
            logger.info(f"使用m-team.io作为API域名")
            return "m-team.io"
        if "m-team.cc" in domain:
            logger.info(f"使用m-team.cc作为API域名")
            return "m-team.cc"
            
        # 默认返回m-team.cc
        logger.info(f"无法识别域名 {domain}，使用默认m-team.cc作为API域名")
        return "m-team.cc"
    
    def _get_user_profile(self, api_base_url: str, session: requests.Session, site_name: str) -> Dict[str, Any]:
        """
        获取用户信息
        :param api_base_url: API基础URL
        :param session: 请求会话
        :param site_name: 站点名称
        :return: 用户信息
        """
        try:
            profile_url = f"{api_base_url}/member/profile"
            logger.info(f"站点 {site_name} 获取用户信息: {profile_url}")
            
            # --- 修正：严格按照 SiteChain.__mteam_test 方式准备 Headers --- 
            # 获取原始 session 中的 UA 和 API Key
            original_ua = session.headers.get("User-Agent", "Mozilla/5.0")
            original_api_key = session.headers.get("x-api-key")

            if not original_api_key:
                 logger.error(f"无法从会话中获取 x-api-key")
                 return {}

            # 只构造必要的 Headers
            request_headers = {
                "User-Agent": original_ua,
                "Accept": "application/json, text/plain, */*",
                "x-api-key": original_api_key
            }
                         
            # 不再设置 Content-Type 和 Authorization
            logger.debug(f"为 /member/profile 设置 Headers: {request_headers}")
            # --- 修正结束 ---

            # 使用修正后的 headers 发送 POST 请求，不带 uid 参数，不显式设置 Content-Type
            # 注意：这里直接用 requests.post 而不是 session.post，避免 session 默认 headers 干扰
            response = requests.post(profile_url, headers=request_headers, timeout=(10, 30), proxies=session.proxies)
            
            if response.status_code != 200:
                logger.error(f"站点 {site_name} 获取用户信息失败，状态码: {response.status_code}")
                # 尝试解析错误信息
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", response.reason)
                    logger.error(f"API错误信息: {error_msg}")
                except Exception:
                    logger.error(f"无法解析API错误响应: {response.text[:200]}")
                return {}

            data = response.json()
            if data.get("code") != "0" or not data.get("data"):
                error_msg = data.get("message", "未知错误")
                logger.error(f"站点 {site_name} 获取用户信息API返回错误: {error_msg}")
                return {}
                
            return data.get("data", {})

        except Exception as e:
            logger.error(f"站点 {site_name} 获取用户信息异常: {str(e)}")
            return {}
    
    def _get_invite_history(self, api_base_url: str, session: requests.Session, user_id: str, site_name: str) -> List[Dict[str, Any]]:
        """
        获取邀请历史
        :param api_base_url: API基础URL
        :param session: 请求会话
        :param user_id: 用户ID
        :param site_name: 站点名称
        :return: 邀请历史
        """
        try:
            history_url = f"{api_base_url}/invite/getUserInviteHistory"
            params = {"uid": user_id}
            logger.info(f"站点 {site_name} 获取邀请历史: {history_url}?uid={user_id}")
            
            # --- 修正：为本次请求单独设置 Content-Type --- 
            request_headers = session.headers.copy() # 复制现有会话headers
            request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            logger.debug(f"为 getUserInviteHistory 设置 Content-Type: {request_headers['Content-Type']}")
            # --- 修正结束 ---

            # 使用POST方法，uid通过params加到URL，使用修正后的headers
            response = session.post(history_url, params=params, headers=request_headers, timeout=(10, 30))
            if response.status_code != 200:
                logger.error(f"站点 {site_name} 获取邀请历史失败，状态码: {response.status_code}")
                return []
                
            data = response.json()
            if data.get("code") != "0":
                error_msg = data.get("message", "未知错误")
                logger.error(f"站点 {site_name} 获取邀请历史API返回错误: {error_msg}")
                return []
                
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"站点 {site_name} 获取邀请历史异常: {str(e)}")
            return []
    
    def _process_invitees(self, invitees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理被邀请人信息
        :param invitees: 原始被邀请人列表
        :return: 处理后的被邀请人列表
        """
        result = []
        
        for invitee in invitees:
            if not isinstance(invitee, dict):
                    continue
                
            # 计算分享率
            uploaded = float(invitee.get("uploaded", 0))
            downloaded = float(invitee.get("downloaded", 0))
            ratio = "∞"
            
            if downloaded > 0:
                ratio = round(uploaded / downloaded, 3)
                ratio = f"{ratio:.3f}"
            
            # 获取状态
            status = invitee.get("status", "")
            if status == "CONFIRMED":
                status = "已确认"
            elif status == "PENDING":
                status = "待确认"
                    
                    # 创建用户记录
            user = {
                "username": invitee.get("username", ""),
                "email": invitee.get("email", ""),
                "uploaded": self._format_size(uploaded),
                "downloaded": self._format_size(downloaded),
                        "ratio": ratio,
                        "status": status,
                "enabled": "Yes" if status == "已确认" else "No",
                "uid": invitee.get("uid", ""),
                # 由于API返回数据中没有这些字段，设置为默认值
                        "seed_bonus": "0",
                        "seeding": "0",
                        "seeding_size": "0 B",
                        "seed_magic": "0",
                "last_seen": ""
            }
            result.append(user)
            
        return result
    
    def _update_last_browse(self, api_base_url: str, session: requests.Session, site_name: str) -> bool:
        """
        更新最后访问时间
        :param api_base_url: API基础URL
        :param session: 请求会话
        :param site_name: 站点名称
        :return: 是否成功
        """
        try:
            # 跳过更新最后访问时间，因为不影响主要功能
            logger.info(f"站点 {site_name} 跳过更新最后访问时间")
            return True
            
        except Exception as e:
            logger.warning(f"站点 {site_name} 更新最后访问时间异常: {str(e)}")
            # 即使更新失败，仍然返回True，因为这不影响主要功能
            return True

    def _format_size(self, size_bytes: float) -> str:
        """
        格式化文件大小
        :param size_bytes: 字节数
        :return: 格式化后的大小字符串
        """
        try:
            if not isinstance(size_bytes, (int, float)):
                return str(size_bytes)
                
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} PB"
        except Exception as e:
            logger.warning(f"格式化大小失败: {str(e)}")
            return "0 B"
    
    def _calculate_ratio_health(self, ratio_str, uploaded, downloaded):
        """
        计算分享率健康度
        """
        try:
            # 优先使用上传下载直接计算分享率（如果都是数值类型）
            if isinstance(uploaded, (int, float)) and isinstance(downloaded, (int, float)) and downloaded > 0:
                ratio = uploaded / downloaded
                # 使用计算结果生成适当的健康状态和标签
                return self._get_health_from_ratio_value(ratio)
                
            # 检查是否是无数据情况（上传下载都是0）
            is_no_data = False
            if isinstance(uploaded, str) and isinstance(downloaded, str):
                uploaded_zero = uploaded == '0' or uploaded == '' or uploaded == '0.0' or uploaded.lower() == '0b'
                downloaded_zero = downloaded == '0' or downloaded == '' or downloaded == '0.0' or downloaded.lower() == '0b'
                is_no_data = uploaded_zero and downloaded_zero
            elif isinstance(uploaded, (int, float)) and isinstance(downloaded, (int, float)):
                is_no_data = uploaded == 0 and downloaded == 0

            if is_no_data:
                return "neutral", ["无数据", "text-grey"]
                
            # 处理无限分享率情况 - 增强检测逻辑
            if not ratio_str:
                return "neutral", ["无效", "text-grey"]
                
            # 统一处理所有表示无限的情况，忽略大小写
            if ratio_str == '∞' or ratio_str.lower() in ['inf.', 'inf', 'infinite', '无限']:
                return "excellent", ["分享率无限", "text-success"]
                
            # 标准化分享率字符串 - 正确处理千分位逗号
            try:
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
                ratio = float(normalized_ratio)
                return self._get_health_from_ratio_value(ratio)
            except (ValueError, TypeError) as e:
                logger.error(f"分享率转换错误: {ratio_str}, 错误: {str(e)}")
                return "neutral", ["无效", "text-grey"]

        except (ValueError, TypeError) as e:
            logger.error(f"分享率计算错误: {str(e)}")
            return "neutral", ["无效", "text-grey"]
            
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

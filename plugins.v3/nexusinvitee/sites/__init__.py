"""
NexusPHP站点邀请系统解析器基类
"""
import re
from abc import ABCMeta, abstractmethod
from typing import Dict, Optional, Any

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger


class _ISiteHandler(metaclass=ABCMeta):
    """
    站点邀请系统处理的基类，所有站点处理类都需要继承此类
    """
    # 站点类型标识
    site_schema = ""
    
    @classmethod
    @abstractmethod
    def match(cls, site_url: str) -> bool:
        """
        判断是否匹配该站点处理类
        :param site_url: 站点URL
        :return: 是否匹配
        """
        pass
    
    @abstractmethod
    def parse_invite_page(self, site_info: Dict[str, Any], session: requests.Session) -> Dict[str, Any]:
        """
        解析站点邀请页面
        :param site_info: 站点信息
        :param session: 已配置好的请求会话
        :return: 解析结果
        """
        pass

    @staticmethod
    def _get_user_id(session: requests.Session, site_url: str) -> Optional[str]:
        """
        获取用户ID
        :param session: 请求会话
        :param site_url: 站点URL
        :return: 用户ID
        """
        try:
            # 访问个人信息页面
            usercp_url = urljoin(site_url, "usercp.php")
            response = session.get(usercp_url, timeout=(5, 15))
            response.raise_for_status()
            
            # 解析页面获取用户ID
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 方法1: 从个人信息链接获取
            user_link = soup.select_one('a[href*="userdetails.php"]')
            if user_link and 'href' in user_link.attrs:
                user_id_match = re.search(r'id=(\d+)', user_link['href'])
                if user_id_match:
                    return user_id_match.group(1)
            
            # 方法2: 从其他链接获取
            invite_link = soup.select_one('a[href*="invite.php"]')
            if invite_link and 'href' in invite_link.attrs:
                user_id_match = re.search(r'id=(\d+)', invite_link['href'])
                if user_id_match:
                    return user_id_match.group(1)
            
            return None
        except Exception as e:
            logger.error(f"获取用户ID失败: {str(e)}")
            return None

    @staticmethod
    def _convert_size_to_bytes(size_str: str) -> float:
        """
        将大小字符串转换为字节数
        :param size_str: 大小字符串
        :return: 字节数
        """
        if not size_str or size_str.strip() == '':
            logger.warning(f"空的大小字符串")
            return 0

        # 处理特殊情况
        if size_str.lower() == 'inf.' or size_str.lower() == 'inf' or size_str == '∞':
            logger.info(f"识别到无限大值: {size_str}")
            return 1e20  # 使用一个非常大的数值代替无穷大

        try:
            # 标准化字符串，替换逗号为点
            size_str = size_str.replace(',', '.')

            # 分离数字和单位
            # 正则表达式匹配数字部分和单位部分
            matches = re.match(
                r'([\d.]+)\s*([KMGTPEZY]?i?B)', size_str, re.IGNORECASE)

            if not matches:
                # 尝试匹配仅有数字的情况
                try:
                    return float(size_str)
                except ValueError:
                    logger.warning(f"无法解析大小字符串: {size_str}")
                    return 0

            size_num, unit = matches.groups()

            # 尝试转换数字
            try:
                size_value = float(size_num)
            except ValueError:
                logger.warning(f"无法转换大小值为浮点数: {size_num}")
                return 0

            # 单位转换
            unit = unit.upper()

            units = {
                'B': 1,
                'KB': 1024,
                'KIB': 1024,
                'MB': 1024 ** 2,
                'MIB': 1024 ** 2,
                'GB': 1024 ** 3,
                'GIB': 1024 ** 3,
                'TB': 1024 ** 4,
                'TIB': 1024 ** 4,
                'PB': 1024 ** 5,
                'PIB': 1024 ** 5,
                'EB': 1024 ** 6,
                'EIB': 1024 ** 6,
                'ZB': 1024 ** 7,
                'ZIB': 1024 ** 7,
                'YB': 1024 ** 8,
                'YIB': 1024 ** 8
            }

            # 处理简写单位
            if unit in ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
                unit = unit + 'B'

            if unit not in units:
                logger.warning(f"未知的大小单位: {unit}")
                return size_value  # 假设是字节

            return size_value * units[unit]

        except Exception as e:
            logger.warning(f"转换大小字符串到字节时出错 '{size_str}': {str(e)}")
            return 0

    @staticmethod
    def _calculate_ratio(uploaded: str, downloaded: str) -> str:
        """
        计算分享率
        :param uploaded: 上传量
        :param downloaded: 下载量
        :return: 分享率字符串
        """
        try:
            up_bytes = _ISiteHandler._convert_size_to_bytes(uploaded)
            down_bytes = _ISiteHandler._convert_size_to_bytes(downloaded)
            
            if down_bytes == 0:
                return "∞" if up_bytes > 0 else "0"
            
            ratio = up_bytes / down_bytes
            return f"{ratio:.3f}"
        except Exception as e:
            logger.error(f"计算分享率失败: {str(e)}")
            return "0" 
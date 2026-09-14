"""
数据管理模块
"""
import os
import json
import time
from typing import Dict, Any, List, Optional

try:
    from app.sdk.logging import logger
except ImportError:
    from app.log import logger


class DataManager:
    """
    数据管理类
    """
    
    def __init__(self, data_path: str):
        """
        初始化数据管理
        :param data_path: 数据目录路径
        """
        self.data_path = data_path
        self.data_file = os.path.join(data_path, "site_data.json")
    
    def load_data(self) -> Dict[str, Any]:
        """
        从文件加载数据
        :return: 数据字典
        """
        if not os.path.exists(self.data_file):
            return {}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取站点数据文件失败: {str(e)}")
            return {}
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        保存数据到文件
        :param data: 数据字典
        :return: 是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存站点数据到文件失败: {str(e)}")
            return False
    
    def update_site_data(self, site_name: str, site_data: Dict[str, Any]) -> bool:
        """
        更新指定站点的数据
        :param site_name: 站点名称
        :param site_data: 站点数据
        :return: 是否成功
        """
        all_data = self.load_data()
        
        # 更新站点数据并添加时间戳
        all_data[site_name] = {
            "data": site_data,
            "last_update": int(time.time())
        }
        
        return self.save_data(all_data)
    
    def get_site_data(self, site_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取站点数据
        :param site_name: 站点名称，如果为None则返回所有站点数据
        :return: 站点数据
        """
        all_data = self.load_data()
        
        if site_name:
            return all_data.get(site_name, {})
        return all_data
    
    def get_last_update_time(self) -> int:
        """
        获取最后更新时间
        :return: 时间戳
        """
        all_data = self.load_data()
        
        update_times = []
        for site_data in all_data.values():
            if "last_update" in site_data:
                update_times.append(site_data["last_update"])
        
        return max(update_times) if update_times else 0
        
    def clear_all_site_data(self) -> bool:
        """
        清空所有站点数据
        :return: 是否成功
        """
        try:
            if os.path.exists(self.data_file):
                # 直接清空为空字典
                return self.save_data({})
            return True
        except Exception as e:
            logger.error(f"清空站点数据失败: {str(e)}")
            return False 
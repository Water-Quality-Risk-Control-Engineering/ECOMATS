#!/usr/bin/env python3
"""
Name2CAS工具
将材料名称转换为CAS号
"""

import logging
from typing import Dict, Any
from tools.pubchem_tool import get_pubchem_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Name2CASTool:
    """Name2CAS工具类 - 将材料名称转换为CAS号"""
    
    def __init__(self):
        """初始化Name2CAS工具"""
        self.pubchem_tool = get_pubchem_tool()
    
    def convert_name_to_cas(self, compound_name: str) -> Dict[str, Any]:
        """
        将化学名称转换为CAS号
        
        Args:
            compound_name (str): 化学名称
            
        Returns:
            Dict[str, Any]: 包含CAS号和其他相关信息的字典
        """
        try:
            # 使用PubChem工具查询化合物信息
            result = self.pubchem_tool.get_compound_info_with_cas(compound_name)
            
            # 提取CAS号信息
            if "cas_number" in result:
                return {
                    "success": True,
                    "compound_name": compound_name,
                    "cas_number": result["cas_number"],
                    "molecular_formula": result.get("molecular_formula", ""),
                    "molecular_weight": result.get("molecular_weight", ""),
                    "synonyms": result.get("synonyms", [])
                }
            else:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": "未找到该化合物的CAS号信息",
                    "details": result.get("error", "未知错误")
                }
                
        except Exception as e:
            logger.error(f"转换化学名称到CAS号时出错: {e}")
            return {
                "success": False,
                "compound_name": compound_name,
                "error": f"转换失败: {str(e)}"
            }

# 全局实例
_name2cas_tool = None

def get_name2cas_tool() -> Name2CASTool:
    """
    获取Name2CAS工具实例
    
    Returns:
        Name2CASTool: Name2CAS工具实例
    """
    global _name2cas_tool
    if _name2cas_tool is None:
        _name2cas_tool = Name2CASTool()
    return _name2cas_tool
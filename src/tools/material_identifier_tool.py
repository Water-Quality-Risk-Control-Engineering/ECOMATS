#!/usr/bin/env python3
"""
材料标识符处理工具
统一处理金属材料和有机物的标识符（MP-ID和CAS号）
"""

import logging
from typing import Dict, Any, Optional
from src.tools.materials_project_tool import get_materials_project_tool
from src.tools.pubchem_tool import get_pubchem_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MaterialIdentifierTool:
    """材料标识符处理工具类 - 统一处理金属材料和有机物的标识符
    
    支持多种材料类型的标识符处理：
    1. 金属材料（获取Materials Project ID）
    2. 有机材料（获取CAS号）
    3. 复合材料（通过元素组成识别）
    """
    
    def __init__(self):
        """初始化材料标识符处理工具"""
        try:
            self.materials_project_tool = get_materials_project_tool()
        except Exception as e:
            logger.warning(f"Materials Project工具不可用: {e}")
            self.materials_project_tool = None
        self.pubchem_tool = get_pubchem_tool()
    
    def identify_material(self, query: str) -> Dict[str, Any]:
        """
        识别材料类型并获取相应的标识符
        
        Args:
            query (str): 材料查询字符串（可以是化学式、元素组合或材料名称）
            
        Returns:
            Dict[str, Any]: 包含材料类型和标识符信息的字典
        """
        try:
            result = {
                "query": query,
                "material_type": "unknown",
                "identifier": None,
                "identifier_type": None,
                "additional_info": {}
            }
            
            # 首先尝试判断材料类型
            material_type = self._determine_material_type(query)
            result["material_type"] = material_type
            
            # 根据材料类型使用相应的工具获取标识符
            if material_type == "metal":
                # 金属材料使用Materials Project获取MP-ID
                mp_result = self._get_mpid_for_metal(query)
                if mp_result and "material_id" in mp_result:
                    result["identifier"] = mp_result["material_id"]
                    result["identifier_type"] = "MP-ID"
                    result["additional_info"] = mp_result
            elif material_type == "organic":
                # 有机物使用PubChem获取CAS号
                cas_result = self._get_cas_for_organic(query)
                if cas_result and "CASNumbers" in cas_result:
                    cas_numbers = cas_result["CASNumbers"]
                    if cas_numbers:
                        result["identifier"] = cas_numbers[0]  # 使用第一个CAS号
                        result["identifier_type"] = "CAS"
                        result["additional_info"] = cas_result
            else:
                # 未知类型，尝试两种方法
                mp_result = self._get_mpid_for_metal(query)
                if mp_result and "material_id" in mp_result:
                    result["identifier"] = mp_result["material_id"]
                    result["identifier_type"] = "MP-ID"
                    result["additional_info"] = mp_result
                    result["material_type"] = "metal"
                else:
                    cas_result = self._get_cas_for_organic(query)
                    if cas_result and "CASNumbers" in cas_result:
                        cas_numbers = cas_result["CASNumbers"]
                        if cas_numbers:
                            result["identifier"] = cas_numbers[0]  # 使用第一个CAS号
                            result["identifier_type"] = "CAS"
                            result["additional_info"] = cas_result
                            result["material_type"] = "organic"
            
            return result
                
        except Exception as e:
            logger.error(f"识别材料标识符时出错: {e}")
            return {
                "success": False,
                "query": query,
                "error": f"识别失败: {str(e)}"
            }
    
    def _determine_material_type(self, query: str) -> str:
        """
        判断材料类型（金属、有机物或其他）
        
        Args:
            query (str): 查询字符串
            
        Returns:
            str: 材料类型 ("metal", "organic", "unknown")
        """
        # 简单的材料类型判断逻辑
        # 基于元素组成判断
        elements = self._extract_elements(query)
        
        # 常见金属元素
        metal_elements = ['Li', 'Be', 'Na', 'Mg', 'Al', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 
                         'Ga', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Cs', 'Ba',
                         'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
                         'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',
                         'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr']
        
        # 常见非金属元素（通常构成有机物）
        non_metal_elements = ['H', 'C', 'N', 'O', 'F', 'P', 'S', 'Cl', 'Br', 'I']
        
        # 判断是否包含金属元素
        has_metal = any(element in metal_elements for element in elements)
        
        # 判断是否主要由非金属元素组成（可能是有机物）
        non_metal_count = sum(1 for element in elements if element in non_metal_elements)
        total_elements = len(elements)
        
        # 如果包含金属元素，认为是金属材料
        if has_metal:
            return "metal"
        
        # 如果主要由非金属元素组成，认为是有机物
        if total_elements > 0 and non_metal_count / total_elements >= 0.5:
            return "organic"
        
        # 默认返回未知
        return "unknown"
    
    def _extract_elements(self, query: str) -> list:
        """
        从查询字符串中提取元素符号
        
        Args:
            query (str): 查询字符串
            
        Returns:
            list: 元素符号列表
        """
        import re
        # 匹配常见的元素符号（1-2个字母，首字母大写）
        elements = re.findall(r'[A-Z][a-z]?', query)
        # 过滤掉可能不是元素的字符串
        valid_elements = []
        # 常见元素列表（简化版）
        common_elements = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
                          'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
                          'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
                          'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
                          'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn']
        
        for element in elements:
            if element in common_elements:
                valid_elements.append(element)
        
        return list(set(valid_elements))  # 去重
    
    def _get_mpid_for_metal(self, query: str) -> Optional[Dict[str, Any]]:
        """
        为金属材料获取MP-ID
        
        Args:
            query (str): 查询字符串
            
        Returns:
            Optional[Dict[str, Any]]: Materials Project数据或None
        """
        if not self.materials_project_tool:
            return None
            
        try:
            # 尝试按化学式搜索
            result = self.materials_project_tool.search_materials(formula=query, limit=1)
            if "error" not in result and "data" in result and result["data"]:
                return result["data"][0]
                
            # 如果按化学式搜索失败，尝试按元素搜索
            elements = self._extract_elements(query)
            if elements:
                result = self.materials_project_tool.search_materials(elements=elements[:2], limit=1)
                if "error" not in result and "data" in result and result["data"]:
                    return result["data"][0]
                    
            # 如果仍然没有找到，返回None而不是生成虚假数据
            return None
        except Exception as e:
            logger.warning(f"获取金属材料MP-ID时出错: {e}")
            return None
    
    def _get_cas_for_organic(self, query: str) -> Optional[Dict[str, Any]]:
        """
        为有机物获取CAS号
        
        Args:
            query (str): 查询字符串
            
        Returns:
            Optional[Dict[str, Any]]: PubChem数据（包含CAS号）或None
        """
        try:
            # 使用PubChem工具获取包含CAS号的化合物信息
            result = self.pubchem_tool.get_compound_info_with_cas(query)
            if "error" not in result and "Compound" in result:
                return result["Compound"]
            return None
        except Exception as e:
            logger.warning(f"获取有机物CAS号时出错: {e}")
            return None

# 全局实例
_material_identifier_tool = None

def get_material_identifier_tool() -> MaterialIdentifierTool:
    """
    获取材料标识符处理工具实例
    
    Returns:
        MaterialIdentifierTool: 材料标识符处理工具实例
    """
    global _material_identifier_tool
    if _material_identifier_tool is None:
        _material_identifier_tool = MaterialIdentifierTool()
    return _material_identifier_tool
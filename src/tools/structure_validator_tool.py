#!/usr/bin/env python3
"""
结构验证工具
验证材料结构是否真实存在
"""

import logging
from typing import Dict, Any
from src.tools.materials_project_tool import get_materials_project_tool
from src.tools.pubchem_tool import get_pubchem_tool
from src.tools.material_identifier_tool import get_material_identifier_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class StructureValidatorTool:
    """结构验证工具类 - 验证材料结构是否真实存在
    
    支持多种材料类型的结构验证：
    1. 金属材料（使用Materials Project数据库）
    2. 有机材料（使用PubChem数据库）
    3. 复合材料（通过元素组成验证）
    """
    
    def __init__(self):
        """初始化结构验证工具"""
        try:
            self.materials_project_tool = get_materials_project_tool()
        except Exception as e:
            logger.warning(f"Materials Project工具不可用: {e}")
            self.materials_project_tool = None
        self.pubchem_tool = get_pubchem_tool()
        self.identifier_tool = get_material_identifier_tool()
    
    def validate_structure_exists(self, material_formula: str) -> Dict[str, Any]:
        """
        验证材料结构是否真实存在
        
        Args:
            material_formula (str): 材料化学式
            
        Returns:
            Dict[str, Any]: 验证结果字典
        """
        try:
            result = {
                "query": material_formula,
                "valid": False,
                "type": "unknown",
                "data": None,
                "source": None,
                "reason": None,
                "validation_confidence": "low"  # 添加验证置信度字段
            }
            
            # 首先识别材料类型
            if self.identifier_tool:
                identification = self.identifier_tool.identify_material(material_formula)
                material_type = identification.get("material_type", "unknown")
                result["type"] = material_type
                
                # 检查材料是否已验证
                validation_status = identification.get("validation_status", "not_found")
                is_verified = identification.get("is_verified", False)
                if validation_status == "validated" and is_verified:
                    # 如果材料已通过标识符工具验证，设置高置信度
                    result["validation_confidence"] = "high"
                    result["reason"] = f"材料类型已通过标识符工具验证为{material_type}"
                    # 添加标识符信息
                    result["identifier"] = identification.get("identifier")
                    result["identifier_type"] = identification.get("identifier_type")
                elif validation_status == "not_found":
                    result["reason"] = f"标识符工具未能找到匹配的{material_type}材料"
                else:
                    result["reason"] = f"标识符工具验证失败: {identification.get('error', '未知错误')}"
            else:
                # 如果标识符工具不可用，使用简单判断
                material_type = self._simple_determine_material_type(material_formula)
                result["type"] = material_type
                result["reason"] = "标识符工具不可用，使用简单判断"
            
            # 根据材料类型使用相应的验证方法
            if material_type == "metal":
                # 金属材料验证
                validation_result = self._validate_metal_structure(material_formula)
                result.update(validation_result)
                # 更新验证置信度
                if validation_result["valid"]:
                    result["validation_confidence"] = "high"
                else:
                    result["validation_confidence"] = "low"
            elif material_type == "organic":
                # 有机材料验证
                validation_result = self._validate_organic_structure(material_formula)
                result.update(validation_result)
                # 更新验证置信度
                if validation_result["valid"]:
                    result["validation_confidence"] = "high"
                else:
                    result["validation_confidence"] = "low"
            else:
                # 未知类型，尝试两种方法
                metal_result = self._validate_metal_structure(material_formula)
                if metal_result["valid"]:
                    result.update(metal_result)
                    result["validation_confidence"] = "high"
                else:
                    organic_result = self._validate_organic_structure(material_formula)
                    result.update(organic_result)
                    if organic_result["valid"]:
                        result["validation_confidence"] = "high"
                    else:
                        result["validation_confidence"] = "low"
            
            # 添加强制验证要求
            if not result["valid"]:
                result["mandatory_action_required"] = True
                result["action_description"] = "材料结构未通过验证，需要重新设计或提供更多实验数据支持"
            else:
                result["mandatory_action_required"] = False
                
            return result
                
        except Exception as e:
            logger.error(f"验证材料结构时出错: {e}")
            return {
                "query": material_formula,
                "valid": False,
                "type": "unknown",
                "data": None,
                "source": None,
                "reason": f"验证过程中出错: {str(e)}",
                "validation_confidence": "low",
                "mandatory_action_required": True,
                "action_description": f"验证过程中出现错误: {str(e)}，需要人工检查"
            }
    
    def _validate_metal_structure(self, formula: str) -> Dict[str, Any]:
        """
        验证金属材料结构
        
        Args:
            formula (str): 化学式
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        if not self.materials_project_tool:
            return {
                "valid": False,
                "type": "metal",
                "data": None,
                "source": None,
                "reason": "Materials Project工具不可用"
            }
            
        try:
            # 尝试按化学式搜索
            search_result = self.materials_project_tool.search_materials(formula=formula, limit=1)
            if "error" not in search_result and "data" in search_result and search_result["data"]:
                material = search_result["data"][0]
                # 验证material_id在Materials Project数据库中是否存在
                material_id = material.get("material_id", "")
                if material_id and self.materials_project_tool.verify_material_id_exists(material_id):
                    return {
                        "valid": True,
                        "type": "metal",
                        "data": material,
                        "source": "Materials Project",
                        "reason": "在Materials Project中找到匹配的材料结构"
                    }
                else:
                    logger.warning(f"发现无效的材料ID: {material_id}")
                
            # 如果按化学式搜索失败，尝试按元素搜索
            elements = self._extract_elements(formula)
            if elements:
                element_result = self.materials_project_tool.search_materials(elements=elements[:2], limit=1)
                if "error" not in element_result and "data" in element_result and element_result["data"]:
                    material = element_result["data"][0]
                    # 验证material_id在Materials Project数据库中是否存在
                    material_id = material.get("material_id", "")
                    if material_id and self.materials_project_tool.verify_material_id_exists(material_id):
                        return {
                            "valid": True,
                            "type": "metal",
                            "data": material,
                            "source": "Materials Project",
                            "reason": "在Materials Project中找到包含相同元素的材料结构"
                        }
                    else:
                        logger.warning(f"发现无效的材料ID: {material_id}")
            
            return {
                "valid": False,
                "type": "metal",
                "data": None,
                "source": None,
                "reason": f"Materials Project中未找到化学式为{formula}的材料或找到的材料ID无效"
            }
        except Exception as e:
            logger.warning(f"验证金属材料结构时出错: {e}")
            return {
                "valid": False,
                "type": "metal",
                "data": None,
                "source": None,
                "reason": f"验证金属材料时出错: {str(e)}"
            }
    
    def _validate_organic_structure(self, formula: str) -> Dict[str, Any]:
        """
        验证有机材料结构
        
        Args:
            formula (str): 化学式或化合物名称
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 使用PubChem工具搜索化合物
            compound_info = self.pubchem_tool.search_compound(formula)
            if "error" not in compound_info:
                return {
                    "valid": True,
                    "type": "organic",
                    "data": compound_info,
                    "source": "PubChem",
                    "reason": "在PubChem中找到匹配的化合物结构"
                }
            else:
                return {
                    "valid": False,
                    "type": "organic",
                    "data": None,
                    "source": None,
                    "reason": f"PubChem中未找到化学式为{formula}的化合物"
                }
        except Exception as e:
            logger.warning(f"验证有机化合物结构时出错: {e}")
            return {
                "valid": False,
                "type": "organic",
                "data": None,
                "source": None,
                "reason": f"验证有机化合物时出错: {str(e)}"
            }
    
    def _simple_determine_material_type(self, query: str) -> str:
        """
        简单判断材料类型（当标识符工具不可用时）
        
        Args:
            query (str): 查询字符串
            
        Returns:
            str: 材料类型 ("metal", "organic", "unknown")
        """
        # 提取元素符号
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

# 全局实例
_structure_validator_tool = None

def get_structure_validator_tool() -> StructureValidatorTool:
    """
    获取结构验证工具实例
    
    Returns:
        StructureValidatorTool: 结构验证工具实例
    """
    global _structure_validator_tool
    if _structure_validator_tool is None:
        _structure_validator_tool = StructureValidatorTool()
    return _structure_validator_tool
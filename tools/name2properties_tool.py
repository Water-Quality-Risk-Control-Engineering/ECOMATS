#!/usr/bin/env python3
"""
Name2Properties工具
根据材料名称查询理化性质
"""

import logging
from typing import Dict, Any, List
from tools.pubchem_tool import get_pubchem_tool
from tools.materials_project_tool import get_materials_project_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Name2PropertiesTool:
    """Name2Properties工具类 - 根据材料名称查询理化性质"""
    
    def __init__(self):
        """初始化Name2Properties工具"""
        self.pubchem_tool = get_pubchem_tool()
        try:
            self.materials_project_tool = get_materials_project_tool()
        except Exception as e:
            logger.warning(f"Materials Project工具不可用: {e}")
            self.materials_project_tool = None
    
    def get_properties_by_name(self, material_name: str) -> Dict[str, Any]:
        """
        根据材料名称查询理化性质
        
        Args:
            material_name (str): 材料名称
            
        Returns:
            Dict[str, Any]: 包含理化性质的字典
        """
        try:
            # 首先尝试从PubChem获取信息
            pubchem_result = self.pubchem_tool.get_basic_properties_by_name(material_name)
            
            result = {
                "material_name": material_name,
                "sources": []
            }
            
            # 处理PubChem结果
            if "error" not in pubchem_result:
                result["sources"].append("PubChem")
                result.update({
                    "molecular_formula": pubchem_result.get("molecular_formula", ""),
                    "molecular_weight": pubchem_result.get("molecular_weight", ""),
                    "iupac_name": pubchem_result.get("iupac_name", ""),
                    "synonyms": pubchem_result.get("synonyms", []),
                    "pubchem_cid": pubchem_result.get("cid", "")
                })
            
            # 如果Materials Project可用，也尝试查询
            if self.materials_project_tool:
                try:
                    # 尝试将材料名称作为化学式搜索
                    mp_result = self.materials_project_tool.search_materials(formula=material_name)
                    if mp_result and "materials" in mp_result and len(mp_result["materials"]) > 0:
                        material = mp_result["materials"][0]  # 取第一个结果
                        result["sources"].append("Materials Project")
                        result.update({
                            "material_id": material.get("material_id", ""),
                            "formula": material.get("formula", ""),
                            "crystal_system": material.get("symmetry", {}).get("crystal_system", ""),
                            "band_gap": material.get("band_gap", ""),
                            "formation_energy": material.get("formation_energy_per_atom", ""),
                            "density": material.get("density", ""),
                            "volume": material.get("volume", "")
                        })
                except Exception as e:
                    logger.warning(f"从Materials Project查询时出错: {e}")
            
            # 如果没有找到任何信息，返回错误
            if len(result["sources"]) == 0:
                return {
                    "success": False,
                    "material_name": material_name,
                    "error": "未找到该材料的理化性质信息"
                }
            
            result["success"] = True
            return result
                
        except Exception as e:
            logger.error(f"查询材料理化性质时出错: {e}")
            return {
                "success": False,
                "material_name": material_name,
                "error": f"查询失败: {str(e)}"
            }

# 全局实例
_name2properties_tool = None

def get_name2properties_tool() -> Name2PropertiesTool:
    """
    获取Name2Properties工具实例
    
    Returns:
        Name2PropertiesTool: Name2Properties工具实例
    """
    global _name2properties_tool
    if _name2properties_tool is None:
        _name2properties_tool = Name2PropertiesTool()
    return _name2properties_tool
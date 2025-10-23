#!/usr/bin/env python3
"""
Formula2Properties工具
根据化学式预测性质
"""

import logging
from typing import Dict, Any, List
from src.tools.pubchem_tool import get_pubchem_tool
from src.tools.materials_project_tool import get_materials_project_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Formula2PropertiesTool:
    """Formula2Properties工具类 - 根据化学式预测性质"""
    
    def __init__(self):
        """初始化Formula2Properties工具"""
        self.pubchem_tool = get_pubchem_tool()
        try:
            self.materials_project_tool = get_materials_project_tool()
        except Exception as e:
            logger.warning(f"Materials Project工具不可用: {e}")
            self.materials_project_tool = None
    
    def get_properties_by_formula(self, formula: str) -> Dict[str, Any]:
        """
        根据化学式预测性质
        
        Args:
            formula (str): 化学式
            
        Returns:
            Dict[str, Any]: 包含预测性质的字典
        """
        try:
            result = {
                "formula": formula,
                "sources": []
            }
            
            # 首先尝试从PubChem获取信息
            pubchem_result = self.pubchem_tool.search_compound(formula, search_type="formula")
            
            if "error" not in pubchem_result and "compounds" in pubchem_result:
                result["sources"].append("PubChem")
                compounds = pubchem_result["compounds"]
                if len(compounds) > 0:
                    # 取第一个化合物的信息
                    first_compound = compounds[0]
                    result.update({
                        "molecular_weight": first_compound.get("molecular_weight", ""),
                        "synonyms": first_compound.get("synonyms", []),
                        "cid": first_compound.get("cid", "")
                    })
            
            # 如果Materials Project可用，也尝试查询
            if self.materials_project_tool:
                try:
                    mp_result = self.materials_project_tool.search_materials(formula=formula)
                    if mp_result and "materials" in mp_result and len(mp_result["materials"]) > 0:
                        result["sources"].append("Materials Project")
                        # 取第一个材料的信息
                        material = mp_result["materials"][0]
                        result.update({
                            "material_id": material.get("material_id", ""),
                            "full_formula": material.get("formula", ""),
                            "crystal_system": material.get("symmetry", {}).get("crystal_system", ""),
                            "band_gap": material.get("band_gap", ""),
                            "formation_energy": material.get("formation_energy_per_atom", ""),
                            "energy_above_hull": material.get("energy_above_hull", ""),
                            "density": material.get("density", ""),
                            "volume": material.get("volume", ""),
                            "nsites": material.get("nsites", ""),
                            "elements": material.get("elements", []),
                            "nelements": material.get("nelements", "")
                        })
                except Exception as e:
                    logger.warning(f"从Materials Project查询时出错: {e}")
            
            # 如果没有找到任何信息，返回错误
            if len(result["sources"]) == 0:
                return {
                    "success": False,
                    "formula": formula,
                    "error": "未找到该化学式的性质信息"
                }
            
            result["success"] = True
            return result
                
        except Exception as e:
            logger.error(f"根据化学式预测性质时出错: {e}")
            return {
                "success": False,
                "formula": formula,
                "error": f"预测失败: {str(e)}"
            }

# 全局实例
_formula2properties_tool = None

def get_formula2properties_tool() -> Formula2PropertiesTool:
    """
    获取Formula2Properties工具实例
    
    Returns:
        Formula2PropertiesTool: Formula2Properties工具实例
    """
    global _formula2properties_tool
    if _formula2properties_tool is None:
        _formula2properties_tool = Formula2PropertiesTool()
    return _formula2properties_tool
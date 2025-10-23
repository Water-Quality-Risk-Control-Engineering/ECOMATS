#!/usr/bin/env python3
"""
MaterialSearch工具
检索相似材料的性能数据
"""

import logging
from typing import Dict, Any, List
from src.tools.materials_project_tool import get_materials_project_tool
from src.tools.pubchem_tool import get_pubchem_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MaterialSearchTool:
    """MaterialSearch工具类 - 检索相似材料的性能数据"""
    
    def __init__(self):
        """初始化MaterialSearch工具"""
        try:
            self.materials_project_tool = get_materials_project_tool()
        except Exception as e:
            logger.warning(f"Materials Project工具不可用: {e}")
            self.materials_project_tool = None
        self.pubchem_tool = get_pubchem_tool()
    
    def search_similar_materials(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        检索相似材料的性能数据
        
        Args:
            query (str): 查询内容（可以是化学式、元素组合或材料名称）
            limit (int): 返回结果数量限制
            
        Returns:
            Dict[str, Any]: 包含相似材料性能数据的字典
        """
        try:
            results = {
                "query": query,
                "sources": [],
                "materials": []
            }
            
            # 首先尝试从Materials Project搜索
            if self.materials_project_tool:
                try:
                    # 尝试多种搜索方式
                    mp_results = []
                    
                    # 方式1: 按化学式搜索
                    formula_result = self.materials_project_tool.search_materials(formula=query, limit=limit)
                    if formula_result and "materials" in formula_result:
                        mp_results.extend(formula_result["materials"])
                    
                    # 方式2: 如果查询包含元素，按元素搜索
                    if any(char.isalpha() for char in query):
                        elements = self._extract_elements(query)
                        if elements:
                            element_result = self.materials_project_tool.search_materials(elements=elements, limit=limit)
                            if element_result and "materials" in element_result:
                                mp_results.extend(element_result["materials"])
                    
                    # 整理Materials Project结果
                    if mp_results:
                        results["sources"].append("Materials Project")
                        for material in mp_results[:limit]:
                            results["materials"].append({
                                "source": "Materials Project",
                                "material_id": material.get("material_id", ""),
                                "formula": material.get("formula", ""),
                                "formation_energy": material.get("formation_energy_per_atom", ""),
                                "energy_above_hull": material.get("energy_above_hull", ""),
                                "band_gap": material.get("band_gap", ""),
                                "density": material.get("density", ""),
                                "volume": material.get("volume", ""),
                                "crystal_system": material.get("symmetry", {}).get("crystal_system", ""),
                                "elements": material.get("elements", [])
                            })
                except Exception as e:
                    logger.warning(f"从Materials Project搜索时出错: {e}")
            
            # 如果Materials Project没有结果或不可用，尝试从PubChem搜索
            if len(results["materials"]) == 0:
                try:
                    pubchem_result = self.pubchem_tool.search_compound(query)
                    if "error" not in pubchem_result and "compounds" in pubchem_result:
                        results["sources"].append("PubChem")
                        compounds = pubchem_result["compounds"][:limit]
                        for compound in compounds:
                            results["materials"].append({
                                "source": "PubChem",
                                "name": compound.get("name", ""),
                                "cid": compound.get("cid", ""),
                                "molecular_formula": compound.get("molecular_formula", ""),
                                "molecular_weight": compound.get("molecular_weight", ""),
                                "synonyms": compound.get("synonyms", [])
                            })
                except Exception as e:
                    logger.warning(f"从PubChem搜索时出错: {e}")
            
            # 设置成功标志
            results["success"] = len(results["materials"]) > 0
            results["count"] = len(results["materials"])
            
            if not results["success"]:
                results["error"] = "未找到相似材料的性能数据"
            
            return results
                
        except Exception as e:
            logger.error(f"检索相似材料时出错: {e}")
            return {
                "success": False,
                "query": query,
                "error": f"检索失败: {str(e)}"
            }
    
    def _extract_elements(self, query: str) -> List[str]:
        """
        从查询字符串中提取元素符号
        
        Args:
            query (str): 查询字符串
            
        Returns:
            List[str]: 元素符号列表
        """
        # 简单的元素提取逻辑
        import re
        # 匹配常见的元素符号（1-2个字母，首字母大写）
        elements = re.findall(r'[A-Z][a-z]?', query)
        # 过滤掉可能不是元素的字符串
        valid_elements = []
        # 常见元素列表（简化版）
        common_elements = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
                          'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
                          'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe']
        
        for element in elements:
            if element in common_elements:
                valid_elements.append(element)
        
        return list(set(valid_elements))  # 去重

# 全局实例
_material_search_tool = None

def get_material_search_tool() -> MaterialSearchTool:
    """
    获取MaterialSearch工具实例
    
    Returns:
        MaterialSearchTool: MaterialSearch工具实例
    """
    global _material_search_tool
    if _material_search_tool is None:
        _material_search_tool = MaterialSearchTool()
    return _material_search_tool
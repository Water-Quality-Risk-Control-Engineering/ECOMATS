#!/usr/bin/env python3
"""
MaterialSearch工具
检索相似材料的性能数据
"""

import logging
from typing import Dict, Any, List
from src.tools.materials_project_tool import get_materials_project_tool
from src.tools.pubchem_tool import get_pubchem_tool
from src.tools.material_identifier_tool import get_material_identifier_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MaterialSearchTool:
    """MaterialSearch工具类 - 检索相似材料的性能数据"""
    
    def __init__(self, pubchem_api_key: str = None, materials_project_api_key: str = None):
        """初始化MaterialSearch工具"""
        try:
            self.materials_project_tool = get_materials_project_tool(materials_project_api_key)
        except Exception as e:
            logger.warning(f"Materials Project工具不可用: {e}")
            self.materials_project_tool = None
        self.pubchem_tool = get_pubchem_tool(pubchem_api_key)
        self.material_identifier_tool = get_material_identifier_tool()
    
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
                "materials": [],
                "success": False,
                "count": 0,
                "material_type": "unknown"
            }
            
            # 首先识别材料类型
            if self.material_identifier_tool:
                identification = self.material_identifier_tool.identify_material(query)
                if "material_type" in identification:
                    results["material_type"] = identification["material_type"]
            
            # 根据材料类型使用相应的搜索策略
            if results["material_type"] == "metal":
                # 金属材料优先使用Materials Project
                self._search_metal_materials(results, query, limit)
            elif results["material_type"] == "organic":
                # 有机物优先使用PubChem
                self._search_organic_compounds(results, query, limit)
            else:
                # 未知类型，尝试两种方法
                # 首先尝试从Materials Project搜索
                self._search_metal_materials(results, query, limit)
                # 如果Materials Project没有足够结果，尝试PubChem
                if len(results["materials"]) < limit:
                    self._search_organic_compounds(results, query, limit)
            
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
    
    def _search_metal_materials(self, results: Dict, query: str, limit: int):
        """
        搜索金属材料
        
        Args:
            results (Dict): 结果字典
            query (str): 查询内容
            limit (int): 返回结果数量限制
        """
        if not self.materials_project_tool:
            return
            
        try:
            # 尝试按化学式搜索
            formula_result = self.materials_project_tool.search_materials(formula=query, limit=min(limit, 20))
            if "error" not in formula_result and "data" in formula_result:
                if "Materials Project" not in results["sources"]:
                    results["sources"].append("Materials Project")
                materials_data = formula_result["data"][:limit]
                for material in materials_data:
                    # 检查是否已存在相同材料
                    existing_materials = [m for m in results["materials"] if m["source"] == "Materials Project" and m["formula"] == material.get("formula", "N/A")]
                    if not existing_materials:
                        results["materials"].append({
                            "source": "Materials Project",
                            "material_id": material.get("material_id", "N/A"),
                            "formula": material.get("formula", "N/A"),
                            "formation_energy": material.get("formation_energy_per_atom", "N/A"),
                            "energy_above_hull": material.get("energy_above_hull", "N/A"),
                            "band_gap": material.get("band_gap", "N/A"),
                            "density": material.get("density", "N/A"),
                            "volume": material.get("volume", "N/A"),
                            "crystal_system": material.get("crystal_system", "N/A"),
                            "elements": []  # 可以进一步完善
                        })
        except Exception as e:
            logger.warning(f"从Materials Project搜索金属材料时出错: {e}")
        
        # 如果按化学式搜索没有足够结果，尝试按元素搜索
        if len([m for m in results["materials"] if m["source"] == "Materials Project"]) < limit:
            try:
                if any(char.isalpha() for char in query):
                    elements = self._extract_elements(query)
                    if elements:
                        # 限制元素数量以避免过多结果
                        elements = elements[:2]  # 最多使用2个元素以提高性能
                        element_result = self.materials_project_tool.search_materials(
                            elements=elements, 
                            limit=min(limit, 10)
                        )
                        if "error" not in element_result and "data" in element_result:
                            if "Materials Project" not in results["sources"]:
                                results["sources"].append("Materials Project")
                            existing_formulas = [m["formula"] for m in results["materials"] if m["source"] == "Materials Project"]
                            materials_data = element_result["data"]
                            for material in materials_data:
                                # 避免重复添加相同材料
                                if material.get("formula", "") not in existing_formulas and len([m for m in results["materials"] if m["source"] == "Materials Project"]) < limit:
                                    results["materials"].append({
                                        "source": "Materials Project",
                                        "material_id": material.get("material_id", "N/A"),
                                        "formula": material.get("formula", "N/A"),
                                        "formation_energy": material.get("formation_energy_per_atom", "N/A"),
                                        "energy_above_hull": material.get("energy_above_hull", "N/A"),
                                        "band_gap": material.get("band_gap", "N/A"),
                                        "density": material.get("density", "N/A"),
                                        "volume": material.get("volume", "N/A"),
                                        "crystal_system": material.get("crystal_system", "N/A"),
                                        "elements": []
                                    })
            except Exception as e:
                logger.warning(f"从Materials Project按元素搜索金属材料时出错: {e}")
    
    def _search_organic_compounds(self, results: Dict, query: str, limit: int):
        """
        搜索有机化合物
        
        Args:
            results (Dict): 结果字典
            query (str): 查询内容
            limit (int): 返回结果数量限制
        """
        if not self.pubchem_tool:
            return
            
        try:
            # 使用PubChem搜索化合物
            compound_info = self.pubchem_tool.get_compound_info(query)
            if "error" not in compound_info and "Compound" in compound_info:
                if "PubChem" not in results["sources"]:
                    results["sources"].append("PubChem")
                
                compound = compound_info["Compound"]
                # 检查是否已存在相同化合物
                existing_compounds = [m for m in results["materials"] if m["source"] == "PubChem"]
                if not existing_compounds and len([m for m in results["materials"] if m["source"] == "PubChem"]) < limit:
                    results["materials"].append({
                        "source": "PubChem",
                        "compound_id": compound.get("CID", "N/A"),
                        "name": compound.get("IUPACName", "N/A"),
                        "formula": compound.get("MolecularFormula", "N/A"),
                        "molecular_weight": compound.get("MolecularWeight", "N/A"),
                        "canonical_smiles": compound.get("canonical_smiles", "N/A"),
                        "isomeric_smiles": compound.get("isomeric_smiles", "N/A"),
                        "inchi": compound.get("inchi", "N/A"),
                        "inchi_key": compound.get("inchi_key", "N/A")
                    })
        except Exception as e:
            logger.warning(f"从PubChem搜索有机化合物时出错: {e}")
    
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
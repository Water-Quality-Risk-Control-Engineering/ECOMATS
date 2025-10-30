#!/usr/bin/env python3
"""
材料搜索工具
用于搜索具有特定属性的材料
"""

import json
import logging
from typing import Dict, Any, Optional, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.materials_project_tool import get_materials_project_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MaterialSearchInput(BaseModel):
    """材料搜索工具输入参数"""
    query: str = Field(..., description="搜索查询，可以是材料类型、化学式或元素组合")
    limit: int = Field(default=10, description="返回结果数量限制")

class MaterialSearchTool(BaseTool):
    """材料搜索工具"""
    
    name: str = "Material Search Tool"
    description: str = (
        "搜索具有特定属性的材料。"
        "可以按材料类型、化学式或元素组合进行搜索。"
    )
    args_schema: type[BaseModel] = MaterialSearchInput
    
    def _run(self, query: str, limit: int = 10) -> str:
        """
        搜索材料
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            JSON格式的搜索结果
        """
        try:
            # 获取Materials Project工具实例
            mp_tool = get_materials_project_tool()
            
            # 解析查询，尝试识别是否为化学式或元素
            materials = []
            
            # 首先尝试按化学式搜索
            formula_result = mp_tool.search_materials(formula=query, limit=limit)
            
            if "error" not in formula_result and formula_result.get("data"):
                materials.extend(formula_result["data"])
            
            # 如果按化学式搜索没有结果，尝试按元素搜索
            if not materials:
                # 尝试将查询解析为元素列表
                elements = self._parse_elements(query)
                if elements:
                    element_result = mp_tool.search_materials(elements=elements, limit=limit)
                    if "error" not in element_result and element_result.get("data"):
                        materials.extend(element_result["data"])
            
            # 如果仍然没有结果，尝试使用元素组合搜索
            if not materials:
                # 尝试用"-"连接的元素组合搜索
                if "-" in query:
                    element_list = [elem.strip() for elem in query.split("-") if elem.strip()]
                    if element_list:
                        combo_result = mp_tool.search_materials(elements=element_list, limit=limit)
                        if "error" not in combo_result and combo_result.get("data"):
                            materials.extend(combo_result["data"])
            
            # 如果还是没有结果，返回空结果
            if not materials:
                return json.dumps({
                    "query": query,
                    "results": [],
                    "message": f"未找到与 '{query}' 匹配的材料"
                }, ensure_ascii=False, indent=2)
            
            # 限制结果数量
            materials = materials[:limit]
            
            # 格式化结果
            formatted_results = []
            for material in materials:
                formatted_material = {
                    "material_id": material.get("material_id", "N/A"),
                    "formula": material.get("formula", "N/A"),
                    "chemsys": material.get("chemsys", "N/A"),
                    "volume": material.get("volume", "N/A"),
                    "density": material.get("density", "N/A"),
                    "nsites": material.get("nsites", "N/A")
                }
                formatted_results.append(formatted_material)
            
            return json.dumps({
                "query": query,
                "results": formatted_results
            }, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"搜索材料 '{query}' 时出错: {e}")
            return json.dumps({"error": f"搜索材料 '{query}' 时出错: {str(e)}"}, ensure_ascii=False)
    
    def _parse_elements(self, query: str) -> Optional[List[str]]:
        """
        解析查询中的元素
        
        Args:
            query: 查询字符串
            
        Returns:
            元素列表或None
        """
        # 简单的元素解析逻辑
        # 这里可以扩展为更复杂的化学式解析
        elements = []
        
        # 移除数字和特殊字符，只保留字母
        import re
        element_chars = re.findall(r'[A-Z][a-z]?', query)
        
        # 过滤出有效的元素符号（这里只是简单示例）
        # 在实际应用中，应该有一个完整的元素符号列表进行验证
        valid_elements = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
                         "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
                         "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe"]
        
        for element in element_chars:
            if element in valid_elements:
                elements.append(element)
        
        return elements if elements else None

# 创建工具实例
material_search_tool = MaterialSearchTool()

def get_material_search_tool():
    """获取材料搜索工具实例"""
    return material_search_tool
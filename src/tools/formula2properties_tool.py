#!/usr/bin/env python3
"""
化学式到性质查询工具
通过材料的化学式查询其关键物理化学性质
"""

import json
import logging
from typing import Dict, Any, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.materials_project_tool import get_materials_project_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Formula2PropertiesInput(BaseModel):
    """化学式到性质查询工具输入参数"""
    formula: str = Field(..., description="化学式")

class Formula2PropertiesTool(BaseTool):
    """化学式到性质查询工具"""
    
    name: str = "Formula to Properties Query Tool"
    description: str = (
        "通过材料的化学式查询其关键物理化学性质。"
        "输入化学式，返回材料的关键性质信息。"
    )
    args_schema: type[BaseModel] = Formula2PropertiesInput
    
    def _run(self, formula: str) -> str:
        """
        通过化学式查询材料性质
        
        Args:
            formula: 化学式
            
        Returns:
            JSON格式的材料性质信息
        """
        try:
            # 获取Materials Project工具实例
            mp_tool = get_materials_project_tool()
            
            # 搜索材料
            search_result = mp_tool.search_materials(formula=formula, limit=5)
            
            if "error" in search_result:
                return json.dumps({"error": search_result["error"]}, ensure_ascii=False)
            
            if not search_result.get("data"):
                return json.dumps({"error": f"未找到化学式为 {formula} 的材料"}, ensure_ascii=False)
            
            # 获取第一个材料的详细信息
            first_material = search_result["data"][0]
            material_id = first_material.get("material_id")
            
            if not material_id or material_id == "N/A":
                return json.dumps({"error": f"未找到化学式为 {formula} 的有效材料ID"}, ensure_ascii=False)
            
            # 获取材料详细信息
            detail_result = mp_tool.get_material_by_id(material_id)
            
            if "error" in detail_result:
                return json.dumps({"error": detail_result["error"]}, ensure_ascii=False)
            
            # 提取关键性质信息
            properties = {
                "formula": detail_result.get("formula", formula),
                "material_id": detail_result.get("material_id", "N/A"),
                "chemsys": detail_result.get("chemsys", "N/A"),
                "volume": detail_result.get("volume", "N/A"),
                "density": detail_result.get("density", "N/A"),
                "nsites": detail_result.get("nsites", "N/A"),
                "crystal_system": detail_result.get("crystal_system", "N/A")
            }
            
            return json.dumps(properties, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"查询化学式 {formula} 的性质时出错: {e}")
            return json.dumps({"error": f"查询化学式 {formula} 的性质时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例
formula2properties_tool = Formula2PropertiesTool()

def get_formula2properties_tool():
    """获取化学式到性质查询工具实例"""
    return formula2properties_tool
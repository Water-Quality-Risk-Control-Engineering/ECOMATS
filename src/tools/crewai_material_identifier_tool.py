import json
from typing import Dict, Any
from crewai.tools import BaseTool
from src.tools.material_identifier_tool import get_material_identifier_tool

class CrewAIMaterialIdentifierTool(BaseTool):
    """CrewAI工具包装器，用于材料标识符处理"""
    
    name: str = "Material Identifier Tool"
    description: str = (
        "统一处理金属材料和有机物的标识符（MP-ID和CAS号）。"
        "能够识别材料类型并获取相应的唯一标识符。"
        "当需要确定材料的唯一标识符时使用此工具。"
    )
    
    def _run(self, query: str) -> str:
        """
        执行材料标识符识别
        
        Args:
            query: 材料查询字符串（可以是化学式、元素组合或材料名称）
            
        Returns:
            JSON格式的识别结果
        """
        try:
            # 获取工具实例
            tool = get_material_identifier_tool()
            
            # 执行材料识别
            result = tool.identify_material(query)
            
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行材料识别时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
material_identifier_tool = CrewAIMaterialIdentifierTool()
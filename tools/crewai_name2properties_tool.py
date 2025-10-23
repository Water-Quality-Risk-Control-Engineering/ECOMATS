import json
from typing import Optional
from crewai.tools import BaseTool
from tools.name2properties_tool import get_name2properties_tool

class CrewAIName2PropertiesTool(BaseTool):
    """CrewAI工具包装器，用于根据材料名称查询理化性质"""
    
    name: str = "Name to Properties Lookup"
    description: str = (
        "根据化学物质或材料名称查询其理化性质。"
        "可以获取分子式、分子量、晶体结构等信息。"
        "当需要了解材料的基本物理化学特性时使用此工具。"
    )
    
    def _run(self, material_name: str) -> str:
        """
        执行材料名称到理化性质的查询
        
        Args:
            material_name: 材料名称
            
        Returns:
            JSON格式的查询结果
        """
        try:
            # 获取工具实例
            tool = get_name2properties_tool()
            
            # 执行查询
            result = tool.get_properties_by_name(material_name)
            
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行查询时出错: {str(e)}"}, ensure_ascii=False)
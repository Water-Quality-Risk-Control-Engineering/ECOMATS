import json
from typing import Optional
from crewai.tools import BaseTool
from src.tools.name2properties_tool import get_name2properties_tool

class CrewAIName2PropertiesTool(BaseTool):
    """CrewAI工具包装器，用于根据材料名称查询理化性质 / CrewAI tool wrapper for querying physicochemical properties by material name"""
    
    name: str = "Name to Properties Lookup"
    description: str = (
        "根据化学物质或材料名称查询其理化性质。/ Query the physicochemical properties of chemical substances or materials by name. "
        "可以获取分子式、分子量、晶体结构等信息。/ Can obtain information such as molecular formula, molecular weight, crystal structure, etc. "
        "当需要了解材料的基本物理化学特性时使用此工具。/ Use this tool when you need to understand the basic physicochemical characteristics of materials."
    )
    
    def _run(self, material_name: str) -> str:
        """
        执行材料名称到理化性质的查询 / Execute query from material name to physicochemical properties
        
        Args:
            material_name: 材料名称 / Material name
            
        Returns:
            JSON格式的查询结果 / Query result in JSON format
        """
        try:
            # 获取工具实例 / Get tool instance
            tool = get_name2properties_tool()
            
            # 执行查询 / Execute query
            result = tool.get_properties_by_name(material_name)
            
            # 返回JSON格式的结果 / Return result in JSON format
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行查询时出错: {str(e)} / Error executing query: {str(e)}"}, ensure_ascii=False)
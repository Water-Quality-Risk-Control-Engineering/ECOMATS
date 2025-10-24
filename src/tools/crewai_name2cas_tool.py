import json
from typing import Optional
from crewai.tools import BaseTool
from src.tools.name2cas_tool import get_name2cas_tool

class CrewAIName2CASTool(BaseTool):
    """CrewAI工具包装器，用于将材料名称转换为CAS号 / CrewAI tool wrapper for converting material names to CAS numbers"""
    
    name: str = "Name to CAS Number Converter"
    description: str = (
        "将化学物质名称转换为CAS登记号。/ Convert chemical substance names to CAS registry numbers. "
        "当需要获取化合物的唯一标识符时使用此工具。/ Use this tool when you need to obtain the unique identifier of a compound. "
        "输入参数为化学物质的名称。/ The input parameter is the name of the chemical substance."
    )
    
    def _run(self, compound_name: str) -> str:
        """
        执行名称到CAS号的转换 / Execute name to CAS number conversion
        
        Args:
            compound_name: 化学物质名称 / Chemical substance name
            
        Returns:
            JSON格式的转换结果 / Conversion result in JSON format
        """
        try:
            # 获取工具实例 / Get tool instance
            tool = get_name2cas_tool()
            
            # 执行转换 / Execute conversion
            result = tool.convert_name_to_cas(compound_name)
            
            # 返回JSON格式的结果 / Return result in JSON format
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行转换时出错: {str(e)} / Error executing conversion: {str(e)}"}, ensure_ascii=False)
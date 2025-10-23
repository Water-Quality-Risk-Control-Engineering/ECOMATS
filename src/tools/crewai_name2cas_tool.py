import json
from typing import Optional
from crewai.tools import BaseTool
from src.tools.name2cas_tool import get_name2cas_tool

class CrewAIName2CASTool(BaseTool):
    """CrewAI工具包装器，用于将材料名称转换为CAS号"""
    
    name: str = "Name to CAS Number Converter"
    description: str = (
        "将化学物质名称转换为CAS登记号。"
        "当需要获取化合物的唯一标识符时使用此工具。"
        "输入参数为化学物质的名称。"
    )
    
    def _run(self, compound_name: str) -> str:
        """
        执行名称到CAS号的转换
        
        Args:
            compound_name: 化学物质名称
            
        Returns:
            JSON格式的转换结果
        """
        try:
            # 获取工具实例
            tool = get_name2cas_tool()
            
            # 执行转换
            result = tool.convert_name_to_cas(compound_name)
            
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行转换时出错: {str(e)}"}, ensure_ascii=False)
import json
from typing import Optional
from crewai.tools import BaseTool
from src.tools.pubchem_tool import get_pubchem_tool

class CrewAIPubChemTool(BaseTool):
    """CrewAI工具包装器，用于PubChem数据库查询"""
    
    name: str = "PubChem Database Query"
    description: str = (
        "查询PubChem化学数据库以获取化合物信息。"
        "支持通过化学名称或分子式搜索化合物，并获取CAS号、分子量、SMILES等信息。"
        "当需要验证化学信息或获取化合物详细数据时使用此工具。"
    )
    
    def _run(
        self,
        query: str,
        search_type: str = "auto",
        get_cas: bool = True
    ) -> str:
        """
        执行PubChem数据库查询
        
        Args:
            query: 查询内容（化学名称或分子式）
            search_type: 查询类型 ("auto", "name", "formula")
            get_cas: 是否获取CAS号信息
            
        Returns:
            JSON格式的查询结果
        """
        try:
            # 获取工具实例
            tool = get_pubchem_tool()
            
            # 根据参数执行相应功能
            if get_cas:
                result = tool.get_compound_info_with_cas(query)
            else:
                if search_type == "auto" and get_cas:
                    result = tool.get_compound_info_with_cas(query)
                else:
                    result = tool.search_compound(query, search_type)
                
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行查询时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
pubchem_tool = CrewAIPubChemTool()
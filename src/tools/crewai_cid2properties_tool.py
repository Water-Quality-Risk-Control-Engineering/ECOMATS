import json
from typing import Optional
from crewai.tools import BaseTool
from src.tools.cid2properties_tool import get_cid2properties_tool

class CrewAICID2PropertiesTool(BaseTool):
    """CrewAI工具包装器，用于根据PubChem CID查询性质"""
    
    name: str = "CID to Properties Lookup"
    description: str = (
        "根据PubChem化合物ID (CID) 查询化合物的详细性质。"
        "可以获取分子结构、物理化学性质、生物活性等信息。"
        "当需要通过已知的CID获取化合物详细信息时使用此工具。"
    )
    
    def _run(self, cid: str) -> str:
        """
        执行CID到化合物性质的查询
        
        Args:
            cid: PubChem化合物ID
            
        Returns:
            JSON格式的查询结果
        """
        try:
            # 获取工具实例
            tool = get_cid2properties_tool()
            
            # 执行查询
            result = tool.get_properties_by_cid(cid)
            
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行查询时出错: {str(e)}"}, ensure_ascii=False)
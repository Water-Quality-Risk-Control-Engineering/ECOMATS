import json
from typing import Optional
from crewai.tools import BaseTool
from tools.material_search_tool import get_material_search_tool

class CrewAIMaterialSearchTool(BaseTool):
    """CrewAI工具包装器，用于检索相似材料的性能数据"""
    
    name: str = "Material Similarity Search"
    description: str = (
        "检索与给定材料相似的其他材料及其性能数据。"
        "可以基于化学式、元素组成或材料名称搜索相似材料。"
        "当需要参考类似材料的性能数据来评估新材料时使用此工具。"
    )
    
    def _run(self, query: str, limit: int = 10) -> str:
        """
        执行相似材料搜索
        
        Args:
            query: 查询内容（化学式、元素组合或材料名称）
            limit: 返回结果数量限制
            
        Returns:
            JSON格式的搜索结果
        """
        try:
            # 获取工具实例
            tool = get_material_search_tool()
            
            # 执行搜索
            result = tool.search_similar_materials(query, limit)
            
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行搜索时出错: {str(e)}"}, ensure_ascii=False)
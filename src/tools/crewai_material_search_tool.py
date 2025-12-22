import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.material_search_tool import get_material_search_tool

class MaterialSearchToolInput(BaseModel):
    """Material Search Tool Input Model"""
    query: str = Field(description="Query content (formula, elements or material name)")
    limit: int = Field(default=10, description="Result limit")

class CrewAIMaterialSearchTool(BaseTool):
    """CrewAI tool wrapper for retrieving similar material performance data"""
    
    name: str = "Material Similarity Search"
    description: str = (
        "Retrieve similar materials and their performance data. "
        "Search by formula, element composition or material name. "
        "Use when you need reference data from similar materials to evaluate new ones."
    )
    args_schema: type[BaseModel] = MaterialSearchToolInput
    
    def _run(self, query: str, limit: int = 10) -> str:
        """
        Execute similar material search.
        
        Args:
            query: Query content (formula, elements or material name)
            limit: Result limit
            
        Returns:
            JSON formatted search result
        """
        try:
            tool = get_material_search_tool()
            result_json = tool._run(query, limit)
            return result_json
        except Exception as e:
            return json.dumps({"error": f"Search error: {str(e)}"}, ensure_ascii=False)

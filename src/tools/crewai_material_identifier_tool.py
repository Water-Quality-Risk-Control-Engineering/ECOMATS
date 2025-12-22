import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.material_identifier_tool import get_material_identifier_tool
from src.utils.context_store import ContextStore

class MaterialIdentifierToolInput(BaseModel):
    """Material Identifier Tool Input Model"""
    query: str = Field(description="Material query string (formula, elements or name)")

class CrewAIMaterialIdentifierTool(BaseTool):
    """CrewAI tool wrapper for material identifier processing"""
    
    name: str = "Material Identifier Tool"
    description: str = (
        "Process metal materials (MP-ID) and organic compounds (CAS number) identifiers. "
        "Identify material type and get corresponding unique identifier. "
        "Use when you need to determine the unique identifier of a material. "
        "This tool supports global caching."
    )
    args_schema: type[BaseModel] = MaterialIdentifierToolInput
    
    def _run(self, query: str) -> str:
        """
        Execute material identifier recognition with ContextStore caching.
        
        Args:
            query: Material query string (formula, elements or name)
            
        Returns:
            JSON formatted identification result
        """
        try:
            # Check global context cache first
            cache_key = f"material_identifier:{query}"
            cached = ContextStore.get(cache_key)
            if cached is not None:
                return json.dumps(cached, ensure_ascii=False, indent=2)
            
            tool = get_material_identifier_tool()
            result = tool.identify_material(query)
            
            # Write to global cache
            ContextStore.set(cache_key, result)
            ContextStore.set("material_identifier", result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Identification error: {str(e)}"}, ensure_ascii=False)

# Create tool instance for agent use
material_identifier_tool = CrewAIMaterialIdentifierTool()
import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.name2properties_tool import get_name2properties_tool

class Name2PropertiesToolInput(BaseModel):
    """Name2Properties Tool Input Model"""
    material_name: str = Field(description="Material name")

class CrewAIName2PropertiesTool(BaseTool):
    """CrewAI tool wrapper for querying physicochemical properties by material name"""
    
    name: str = "Name to Properties Lookup"
    description: str = (
        "Query physicochemical properties of chemical substances or materials by name. "
        "Get molecular formula, molecular weight, crystal structure etc. "
        "Use when you need to understand basic physicochemical characteristics of materials."
    )
    args_schema: type[BaseModel] = Name2PropertiesToolInput
    
    def _run(self, material_name: str) -> str:
        """
        Execute material name to physicochemical properties query.
        
        Args:
            material_name: Material name
            
        Returns:
            JSON formatted query result
        """
        try:
            tool = get_name2properties_tool()
            result = json.loads(tool._run(material_name))
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Query error: {str(e)}"}, ensure_ascii=False)

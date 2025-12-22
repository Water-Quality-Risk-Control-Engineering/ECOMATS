import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.structure_validator_tool import get_structure_validator_tool
from src.utils.context_store import ContextStore

class StructureValidatorToolInput(BaseModel):
    """Structure Validator Tool Input Model"""
    material_formula: str = Field(description="Material chemical formula")

class CrewAIStructureValidatorTool(BaseTool):
    """CrewAI tool wrapper for material structure validation"""
    
    name: str = "Material Structure Validator"
    description: str = (
        "Validate whether material structure exists in reality. "
        "Support metal materials (Materials Project) and organic compounds (PubChem) validation. "
        "Use when you need to confirm if designed material structure exists. "
        "This tool supports global caching."
    )
    args_schema: type[BaseModel] = StructureValidatorToolInput
    
    def _run(
        self,
        material_formula: str
    ) -> str:
        """
        Execute material structure validation with ContextStore caching.
        
        Args:
            material_formula: Material chemical formula
            
        Returns:
            JSON formatted validation result
        """
        try:
            # Check global context cache first
            cache_key = f"structure_validator:{material_formula}"
            cached = ContextStore.get(cache_key)
            if cached is not None:
                return json.dumps(cached, ensure_ascii=False, indent=2)
            
            tool = get_structure_validator_tool()
            result = tool.validate_structure_exists(material_formula)
            
            # Write to global cache
            ContextStore.set(cache_key, result)
            ContextStore.set("structure_validator", result)
                
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Validation error: {str(e)}"}, ensure_ascii=False)

# Create tool instance for agent use
structure_validator_tool = CrewAIStructureValidatorTool()
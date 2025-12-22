import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.formula2properties_tool import get_formula2properties_tool

class Formula2PropertiesToolInput(BaseModel):
    """Formula2Properties Tool Input Model"""
    formula: str = Field(description="Chemical molecular formula")

class CrewAIFormula2PropertiesTool(BaseTool):
    """CrewAI tool wrapper for predicting properties by chemical formula"""
    
    name: str = "Formula to Properties Predictor"
    description: str = (
        "Predict physicochemical properties of compounds by molecular formula. "
        "Can predict molecular weight, crystal structure, band gap etc. "
        "Use when you need to understand possible material properties based on formula."
    )
    args_schema: type[BaseModel] = Formula2PropertiesToolInput
    
    def _run(self, formula: str) -> str:
        """
        Execute formula to properties prediction.
        
        Args:
            formula: Chemical molecular formula
            
        Returns:
            JSON formatted prediction result
        """
        try:
            tool = get_formula2properties_tool()
            result = json.loads(tool._run(formula))
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Prediction error: {str(e)}"}, ensure_ascii=False)

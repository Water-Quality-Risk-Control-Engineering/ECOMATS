import json
from typing import Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.data_validator_tool import get_data_validator_tool

class DataValidatorToolInput(BaseModel):
    """Data Validator Tool Input Model"""
    data: Dict[str, Any] = Field(description="Data dictionary to validate")
    validation_type: str = Field(default="full", description="Validation type ('full', 'cid', 'cas', 'formula', 'h_statements', 'molecular_weight', 'material_id')")

class CrewAIDataValidatorTool(BaseTool):
    """CrewAI tool wrapper for validating chemical and material data"""
    
    name: str = "Data Validator"
    description: str = (
        "Validate authenticity and validity of chemical and material data. "
        "Can validate CID, CAS number, formula, molecular weight, hazard statements etc. "
        "Use when you need to verify if generated chemical data is authentic and valid."
    )
    args_schema: type[BaseModel] = DataValidatorToolInput
    
    def _run(
        self,
        data: Dict[str, Any],
        validation_type: str = "full"
    ) -> str:
        """
        Execute data validation.
        
        Args:
            data: Data dictionary to validate
            validation_type: Validation type ("full", "cid", "cas", "formula", "h_statements", "molecular_weight", "material_id")
            
        Returns:
            JSON formatted validation result
        """
        try:
            tool = get_data_validator_tool()
            
            # Execute based on validation type
            if validation_type == "cid":
                if "pubchem_cid" in data:
                    result = tool.validate_cid(data["pubchem_cid"])
                else:
                    result = {"error": "pubchem_cid field not found in data"}
            elif validation_type == "cas":
                if "cas_number" in data:
                    result = tool.validate_cas_number(data["cas_number"])
                else:
                    result = {"error": "cas_number field not found in data"}
            elif validation_type == "formula":
                if "molecular_formula" in data:
                    result = tool.validate_molecular_formula(data["molecular_formula"])
                else:
                    result = {"error": "molecular_formula field not found in data"}
            elif validation_type == "h_statements":
                if "hazard_statements" in data:
                    result = tool.validate_h_statements(data["hazard_statements"])
                else:
                    result = {"error": "hazard_statements field not found in data"}
            elif validation_type == "molecular_weight":
                if "molecular_weight" in data:
                    result = tool.validate_molecular_weight(data["molecular_weight"])
                else:
                    result = {"error": "molecular_weight field not found in data"}
            elif validation_type == "material_id":
                if "material_id" in data:
                    result = tool.validate_material_id(data["material_id"])
                else:
                    result = {"error": "material_id field not found in data"}
            else:  # full validation
                result = tool.validate_chemical_data(data)
                
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Validation error: {str(e)}"}, ensure_ascii=False)

# Create tool instance for agent use
data_validator_tool = CrewAIDataValidatorTool()
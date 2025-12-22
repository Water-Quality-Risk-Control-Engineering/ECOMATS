#!/usr/bin/env python3
"""
Assessment Tool Executor.
Provides unified tool invocation logic to ensure all assessment agents use the same tool invocation process.
"""

import logging
from typing import Dict, Any
from src.utils.tool_call_spec import ToolCallSpec
from src.utils.context_store import ContextStore

# Delayed import to avoid circular import
def get_material_identifier_tool():
    from src.tools.material_identifier_tool import get_material_identifier_tool as _get_material_identifier_tool
    return _get_material_identifier_tool()

def get_structure_validator_tool():
    from src.tools.structure_validator_tool import get_structure_validator_tool as _get_structure_validator_tool
    return _get_structure_validator_tool()

def get_materials_project_tool():
    from src.tools.materials_project_tool import get_materials_project_tool as _get_materials_project_tool
    return _get_materials_project_tool()

def get_pubchem_tool():
    from src.tools.pubchem_tool import get_pubchem_tool as _get_pubchem_tool
    return _get_pubchem_tool()

def get_pnec_tool():
    from src.tools.pnec_tool import get_pnec_tool as _get_pnec_tool
    return _get_pnec_tool()

def get_data_validator_tool():
    from src.tools.data_validator_tool import get_data_validator_tool as _get_data_validator_tool
    return _get_data_validator_tool()

def get_material_search_tool():
    from src.tools.material_search_tool import get_material_search_tool as _get_material_search_tool
    return _get_material_search_tool()

 

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentToolExecutor:
    """Assessment Tool Executor Class - Provides unified tool invocation logic."""
    
    def __init__(self):
        """Initialize assessment tool executor."""
        self.material_identifier_tool = get_material_identifier_tool()
        self.structure_validator_tool = get_structure_validator_tool()
        self.materials_project_tool = get_materials_project_tool()
        self.pubchem_tool = get_pubchem_tool()
        self.pnec_tool = get_pnec_tool()
        self.data_validator_tool = get_data_validator_tool()
        self.material_search_tool = get_material_search_tool()
    
    def execute_mandatory_tool_calls(self, material_formula: str) -> Dict[str, Any]:
        """
        Execute mandatory tool invocation sequence for assessment agents.
        
        Args:
            material_formula (str): Material chemical formula
            
        Returns:
            Dict[str, Any]: Results of all tool invocations
        """
        results = {
            "material_identifier": None,
            "structure_validator": None,
            "materials_project": None,
            "pubchem": None,
            "pnec": None,
            "data_validator": None,
            "material_search": None,
            "errors": []
        }
        
        try:
            # 1. Material identifier tool invocation
            results["material_identifier"] = self.material_identifier_tool.identify_material(material_formula)
            
            # 2. Structure validator tool invocation
            results["structure_validator"] = self.structure_validator_tool.validate_structure_exists(material_formula)
            
            # 3. Invoke appropriate database tool based on material type (only when validation passes)
            material_type = results["material_identifier"].get("material_type", "unknown")
            if results["material_identifier"].get("is_verified"):
                if material_type == "metal":
                    results["materials_project"] = self.materials_project_tool.search_materials(
                        formula=material_formula,
                        limit=5,
                        fields=["material_id", "formula_pretty"]
                    )
                elif material_type == "organic":
                    results["pubchem"] = self.pubchem_tool.search_compound(material_formula)
            
            # 4. Invoke PNEC tool (environmental risk assessment): only attempt when validated or valid name parsed
            try:
                if results["material_identifier"].get("is_verified"):
                    results["pnec"] = self.pnec_tool.get_pnec_by_name(material_formula)
                else:
                    results["pnec"] = {"warning": "Material not validated, skipping PNEC query"}
            except Exception:
                results["pnec"] = {"error": "PNEC query failed"}
            
            # 5. Invoke data validator tool
            # Create a data dictionary containing material information for validation
            material_data = {
                "molecular_formula": material_formula,
                "material_name": material_formula
            }
            results["data_validator"] = self.data_validator_tool.validate_chemical_data(material_data)
            
            # 6. Invoke material search tool: this tool is BaseTool, use its _run interface
            try:
                results["material_search"] = self.material_search_tool._run(material_formula, limit=10)
            except Exception:
                results["material_search"] = {"error": "Material search tool invocation failed"}
            
            # Write to global context for reuse to avoid duplicate queries
            try:
                ContextStore.set("material_identifier", results.get("material_identifier"))
                if results.get("materials_project"):
                    ContextStore.set("materials_project_search", results.get("materials_project"))
                if results.get("structure_validator"):
                    ContextStore.set("structure_validator", results.get("structure_validator"))
                if results.get("material_search"):
                    ContextStore.set("material_search", results.get("material_search"))
            except Exception:
                pass
            
        except Exception as e:
            results["errors"].append(f"Error occurred during tool invocation: {str(e)}")
            logger.error(f"Assessment tool invocation failed: {e}")
        
        return results
    
    def validate_tool_results(self, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all tool invocation results.
        
        Args:
            tool_results (Dict[str, Any]): Tool invocation results
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation_result = {
            "all_valid": True,
            "validation_details": {},
            "errors": []
        }
        
        # Validate material identifier results
        if tool_results.get("material_identifier"):
            is_valid = ToolCallSpec.validate_material_identifier_result(tool_results["material_identifier"])
            validation_result["validation_details"]["material_identifier"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("Material identifier validation failed")
        
        # Validate structure validator results
        if tool_results.get("structure_validator"):
            is_valid = ToolCallSpec.validate_structure_validator_result(tool_results["structure_validator"])
            validation_result["validation_details"]["structure_validator"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("Structure validation failed")
        
        # Validate Materials Project results
        if tool_results.get("materials_project"):
            is_valid = ToolCallSpec.validate_materials_project_result(tool_results["materials_project"])
            validation_result["validation_details"]["materials_project"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("Materials Project data validation failed")
        
        # Validate PubChem results
        if tool_results.get("pubchem"):
            is_valid = ToolCallSpec.validate_pubchem_result(tool_results["pubchem"])
            validation_result["validation_details"]["pubchem"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("PubChem data validation failed")
        
        return validation_result

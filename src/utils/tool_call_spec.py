#!/usr/bin/env python3
"""
Tool Call Specification Module.
Defines tool call specifications and validation logic for each Agent.
"""

import logging
from typing import Dict, Any, List

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

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ToolCallSpec:
    """Tool Call Specification Class."""
    
    @staticmethod
    def validate_material_identifier_result(result: Dict[str, Any]) -> bool:
        """
        Validate material identifier tool result.
        
        Args:
            result (Dict[str, Any]): Result returned by material identifier tool
            
        Returns:
            bool: Whether validation passed
        """
        if not isinstance(result, dict):
            return False
            
        # Check required fields
        required_fields = ["query", "material_type", "identifier", "identifier_type", "validation_status", "is_verified"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"Material identifier result missing required field: {field}")
                return False
        
        # Check validation status
        if result.get("is_verified", False) is not True:
            logger.warning(f"Material identifier validation failed: {result.get('query', 'Unknown')}")
            return False
            
        return True
    
    @staticmethod
    def validate_structure_validator_result(result: Dict[str, Any]) -> bool:
        """
        Validate structure validator tool result.
        
        Args:
            result (Dict[str, Any]): Result returned by structure validator tool
            
        Returns:
            bool: Whether validation passed
        """
        if not isinstance(result, dict):
            return False
            
        # Check required fields
        required_fields = ["query", "valid", "type", "source", "reason", "validation_confidence"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"Structure validation result missing required field: {field}")
                return False
        
        # Check validation result
        if result.get("valid", False) is not True:
            logger.warning(f"Material structure validation failed: {result.get('query', 'Unknown')}")
            return False
            
        # Check confidence level
        if result.get("validation_confidence", "low") != "high":
            logger.warning(f"Material structure validation confidence insufficient: {result.get('query', 'Unknown')}")
            return False
            
        return True
    
    @staticmethod
    def validate_materials_project_result(result: Dict[str, Any]) -> bool:
        """
        Validate Materials Project tool result.
        
        Args:
            result (Dict[str, Any]): Result returned by Materials Project tool
            
        Returns:
            bool: Whether validation passed
        """
        if not isinstance(result, dict):
            return False
            
        # Check if there are errors
        if "error" in result:
            logger.warning(f"Materials Project tool returned error: {result['error']}")
            return False
            
        # Check data field
        if "data" not in result:
            logger.warning("Materials Project result missing data field")
            return False
            
        # Check if data is empty
        if not result["data"]:
            logger.warning("Materials Project returned empty data")
            return False
            
        return True
    
    @staticmethod
    def validate_pubchem_result(result: Dict[str, Any]) -> bool:
        """
        Validate PubChem tool result.
        
        Args:
            result (Dict[str, Any]): Result returned by PubChem tool
            
        Returns:
            bool: Whether validation passed
        """
        if not isinstance(result, dict):
            return False
            
        # Check if there are errors
        if "error" in result:
            logger.warning(f"PubChem tool returned error: {result['error']}")
            return False
            
        # Check PropertyTable field
        if "PropertyTable" not in result:
            logger.warning("PubChem result missing PropertyTable field")
            return False
            
        # Check Properties field
        if "Properties" not in result["PropertyTable"]:
            logger.warning("PubChem result missing Properties field")
            return False
            
        # Check if Properties is empty
        if not result["PropertyTable"]["Properties"]:
            logger.warning("PubChem returned empty Properties data")
            return False
            
        return True

class MaterialDesignerToolSpec(ToolCallSpec):
    """Material Designer Expert Tool Call Specification."""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        Get list of tools required by material designer expert.
        
        Returns:
            List[str]: List of tool names
        """
        return [
            "Materials Project Tool",
            "PubChem Tool",
            "Material Identifier Tool",
            "Structure Validator Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        Validate tool calls by material designer expert.
        
        Args:
            material_formula (str): Material chemical formula
            
        Returns:
            Dict[str, Any]: Validation result
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # Prioritize reading from global context, call tool if missing
            try:
                from src.utils.context_store import ContextStore
                cached_identifier = ContextStore.get("material_identifier")
                cached_validator = ContextStore.get("structure_validator")
                cached_mp = ContextStore.get("materials_project_search")
            except Exception:
                cached_identifier = None
                cached_validator = None
                cached_mp = None

            # Call material identifier tool (or reuse cache)
            identifier_tool = get_material_identifier_tool()
            identifier_result = cached_identifier or identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # Validate material identifier result
            if not ToolCallSpec.validate_material_identifier_result(identifier_result):
                result["validation_passed"] = False
                result["errors"].append("Material identifier validation failed")
            
            # Call structure validator tool (or reuse cache)
            validator_tool = get_structure_validator_tool()
            validator_result = cached_validator or validator_tool.validate_structure_exists(material_formula)
            result["tool_calls"]["structure_validator"] = validator_result
            
            # Validate structure validator result
            if not ToolCallSpec.validate_structure_validator_result(validator_result):
                result["validation_passed"] = False
                result["errors"].append("Structure validation failed")
            
            # Call appropriate database tool based on material type
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                mp_tool = get_materials_project_tool()
                if cached_mp and isinstance(cached_mp, dict) and cached_mp.get("data"):
                    mp_result = cached_mp
                else:
                    # Prioritize reusing structure validation results to avoid duplicate queries
                    validator_data = result["tool_calls"].get("structure_validator", {})
                    if isinstance(validator_data, dict) and validator_data.get("valid") and validator_data.get("source") == "Materials Project" and validator_data.get("data"):
                        mp_result = {
                            "data": [validator_data["data"]],
                            "meta": {"total_count": 1, "limit": 1}
                        }
                    else:
                        # Secondly, reuse material_id from identifier for detail query
                        add_info = identifier_result.get("additional_info") or {}
                        material_id = add_info.get("material_id")
                        if material_id and mp_tool.validate_material_id(material_id):
                            detail = mp_tool.get_material_by_id(material_id)
                            mp_result = {"data": [detail] if "error" not in detail else [], "meta": {"total_count": 1, "limit": 1}}
                        else:
                            mp_result = mp_tool.search_materials(formula=material_formula, limit=5, fields=["material_id", "formula_pretty"])
                result["tool_calls"]["materials_project"] = mp_result
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project data validation failed")
            elif material_type == "organic":
                # Call PubChem tool
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # Validate PubChem result
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem data validation failed")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"Error occurred during tool invocation: {str(e)}")
            logger.error(f"Material designer expert tool call validation failed: {e}")
        
        return result

class AssessmentExpertToolSpec(ToolCallSpec):
    """Assessment Expert Tool Call Specification."""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        Get list of tools required by assessment expert.
        
        Returns:
            List[str]: List of tool names
        """
        return [
            "Materials Project Tool",
            "PubChem Tool",
            "Material Identifier Tool",
            "Structure Validator Tool",
            "PNEC Tool",
            "Data Validator Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        Validate tool calls by assessment expert.
        
        Args:
            material_formula (str): Material chemical formula
            
        Returns:
            Dict[str, Any]: Validation result
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # Prioritize reusing context
            try:
                from src.utils.context_store import ContextStore
                cached_identifier = ContextStore.get("material_identifier")
                cached_validator = ContextStore.get("structure_validator")
                cached_mp = ContextStore.get("materials_project_search")
            except Exception:
                cached_identifier = None
                cached_validator = None
                cached_mp = None

            identifier_tool = get_material_identifier_tool()
            identifier_result = cached_identifier or identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # Validate material identifier result
            if not ToolCallSpec.validate_material_identifier_result(identifier_result):
                result["validation_passed"] = False
                result["errors"].append("Material identifier validation failed")
            
            validator_tool = get_structure_validator_tool()
            validator_result = cached_validator or validator_tool.validate_structure_exists(material_formula)
            result["tool_calls"]["structure_validator"] = validator_result
            
            # Validate structure validator result
            if not ToolCallSpec.validate_structure_validator_result(validator_result):
                result["validation_passed"] = False
                result["errors"].append("Structure validation failed")
            
            # Call appropriate database tool based on material type
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                mp_tool = get_materials_project_tool()
                if cached_mp and isinstance(cached_mp, dict) and cached_mp.get("data"):
                    mp_result = cached_mp
                else:
                    validator_data = result["tool_calls"].get("structure_validator", {})
                    if isinstance(validator_data, dict) and validator_data.get("valid") and validator_data.get("source") == "Materials Project" and validator_data.get("data"):
                        mp_result = {
                            "data": [validator_data["data"]],
                            "meta": {"total_count": 1, "limit": 1}
                        }
                    else:
                        add_info = identifier_result.get("additional_info") or {}
                        material_id = add_info.get("material_id")
                        if material_id and mp_tool.validate_material_id(material_id):
                            detail = mp_tool.get_material_by_id(material_id)
                            mp_result = {"data": [detail] if "error" not in detail else [], "meta": {"total_count": 1, "limit": 1}}
                        else:
                            mp_result = mp_tool.search_materials(formula=material_formula, limit=5, fields=["material_id", "formula_pretty"])
                result["tool_calls"]["materials_project"] = mp_result
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project data validation failed")
            elif material_type == "organic":
                # Call PubChem tool
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # Validate PubChem result
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem data validation failed")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"Error occurred during tool invocation: {str(e)}")
            logger.error(f"Assessment expert tool call validation failed: {e}")
        
        return result

class FinalValidatorToolSpec(ToolCallSpec):
    """Final Validator Expert Tool Call Specification."""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        Get list of tools required by final validator expert.
        
        Returns:
            List[str]: List of tool names
        """
        return [
            "Materials Project Tool",
            "PubChem Tool",
            "Material Identifier Tool",
            "Structure Validator Tool",
            "PNEC Tool",
            "Data Validator Tool",
            "Name2Properties Tool",
            "CID2Properties Tool",
            "Formula2Properties Tool",
            "Material Search Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        Validate tool calls by final validator expert.
        
        Args:
            material_formula (str): Material chemical formula
            
        Returns:
            Dict[str, Any]: Validation result
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # Call material identifier tool
            identifier_tool = get_material_identifier_tool()
            identifier_result = identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # Validate material identifier result
            if not ToolCallSpec.validate_material_identifier_result(identifier_result):
                result["validation_passed"] = False
                result["errors"].append("Material identifier validation failed")
            
            # Call structure validator tool
            validator_tool = get_structure_validator_tool()
            validator_result = validator_tool.validate_structure_exists(material_formula)
            result["tool_calls"]["structure_validator"] = validator_result
            
            # Validate structure validator result
            if not ToolCallSpec.validate_structure_validator_result(validator_result):
                result["validation_passed"] = False
                result["errors"].append("Structure validation failed")
            
            # Call appropriate database tool based on material type
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                mp_tool = get_materials_project_tool()
                validator_data = result["tool_calls"].get("structure_validator", {})
                if isinstance(validator_data, dict) and validator_data.get("valid") and validator_data.get("source") == "Materials Project" and validator_data.get("data"):
                    mp_result = {
                        "data": [validator_data["data"]],
                        "meta": {"total_count": 1, "limit": 1}
                    }
                else:
                    add_info = identifier_result.get("additional_info") or {}
                    material_id = add_info.get("material_id")
                    if material_id and mp_tool.validate_material_id(material_id):
                        detail = mp_tool.get_material_by_id(material_id)
                        mp_result = {"data": [detail] if "error" not in detail else [], "meta": {"total_count": 1, "limit": 1}}
                    else:
                        mp_result = mp_tool.search_materials(formula=material_formula, limit=5, fields=["material_id", "formula_pretty"])
                result["tool_calls"]["materials_project"] = mp_result
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project data validation failed")
            elif material_type == "organic":
                # Call PubChem tool
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # Validate PubChem result
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem data validation failed")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"Error occurred during tool invocation: {str(e)}")
            logger.error(f"Final validator expert tool call validation failed: {e}")
        
        return result

class MechanismExpertToolSpec(ToolCallSpec):
    """Mechanism Analysis Expert Tool Call Specification."""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        Get list of tools required by mechanism analysis expert.
        
        Returns:
            List[str]: List of tool names
        """
        return [
            "Materials Project Tool",
            "PubChem Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        Validate tool calls by mechanism analysis expert.
        
        Args:
            material_formula (str): Material chemical formula
            
        Returns:
            Dict[str, Any]: Validation result
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # Prioritize reusing context
            try:
                from src.utils.context_store import ContextStore
                cached_identifier = ContextStore.get("material_identifier")
                cached_mp = ContextStore.get("materials_project_search")
            except Exception:
                cached_identifier = None
                cached_mp = None

            identifier_tool = get_material_identifier_tool()
            identifier_result = cached_identifier or identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # Call appropriate database tool based on material type
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                mp_tool = get_materials_project_tool()
                if cached_mp and isinstance(cached_mp, dict) and cached_mp.get("data"):
                    mp_result = cached_mp
                else:
                    validator_data = result["tool_calls"].get("material_identifier", {})
                    add_info = validator_data.get("additional_info") if isinstance(validator_data, dict) else {}
                    material_id = (add_info or {}).get("material_id")
                    if material_id and mp_tool.validate_material_id(material_id):
                        detail = mp_tool.get_material_by_id(material_id)
                        mp_result = {"data": [detail] if "error" not in detail else [], "meta": {"total_count": 1, "limit": 1}}
                    else:
                        mp_result = mp_tool.search_materials(formula=material_formula, limit=5, fields=["material_id", "formula_pretty"])
                result["tool_calls"]["materials_project"] = mp_result
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project data validation failed")
            elif material_type == "organic":
                # Call PubChem tool
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # Validate PubChem result
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem data validation failed")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"Error occurred during tool invocation: {str(e)}")
            logger.error(f"Mechanism analysis expert tool call validation failed: {e}")
        
        return result

class SynthesisExpertToolSpec(ToolCallSpec):
    """Synthesis Guidance Expert Tool Call Specification."""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        Get list of tools required by synthesis guidance expert.
        
        Returns:
            List[str]: List of tool names
        """
        return [
            "PubChem Tool",
            "Materials Project Tool",
            "Material Search Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(chemical_reagents: List[str]) -> Dict[str, Any]:
        """
        Validate tool calls by synthesis guidance expert.
        
        Args:
            chemical_reagents (List[str]): List of chemical reagents
            
        Returns:
            Dict[str, Any]: Validation result
        """
        result = {
            "chemical_reagents": chemical_reagents,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # Call PubChem tool for each chemical reagent
            pubchem_results = []
            for reagent in chemical_reagents:
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(reagent)
                pubchem_results.append({
                    "reagent": reagent,
                    "result": pubchem_result
                })
                
                # Validate PubChem result
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append(f"PubChem data validation failed for reagent {reagent}")
            
            result["tool_calls"]["pubchem"] = pubchem_results
            
            # If there is material information, also call Materials Project tool
            # Simplified handling here, actual application may require more complex logic
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"Error occurred during tool invocation: {str(e)}")
            logger.error(f"Synthesis guidance expert tool call validation failed: {e}")
        
        return result

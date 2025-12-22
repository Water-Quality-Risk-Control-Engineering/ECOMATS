#!/usr/bin/env python3
"""
Structure Validator Tool.
Validate if material structure actually exists.
"""

import logging
from typing import Dict, Any
from src.tools.materials_project_tool import get_materials_project_tool
from src.tools.pubchem_tool import get_pubchem_tool
from src.tools.material_identifier_tool import get_material_identifier_tool

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class StructureValidatorTool:
    """Structure Validator Tool - Validate if material structure actually exists.
    
    Supports structure validation for multiple material types:
    1. Metal materials (using Materials Project database)
    2. Organic materials (using PubChem database)
    3. Composite materials (validation by element composition)
    """
    
    def __init__(self):
        """Initialize structure validator tool."""
        try:
            self.materials_project_tool = get_materials_project_tool()
        except Exception as e:
            logger.warning(f"Materials Project tool not available: {e}")
            self.materials_project_tool = None
        self.pubchem_tool = get_pubchem_tool()
        self.identifier_tool = get_material_identifier_tool()
    
    def validate_structure_exists(self, material_formula: str) -> Dict[str, Any]:
        """
        Validate if material structure actually exists.
        
        Args:
            material_formula (str): Material chemical formula
            
        Returns:
            Dict[str, Any]: Validation result dictionary
        """
        try:
            result = {
                "query": material_formula,
                "valid": False,
                "type": "unknown",
                "data": None,
                "source": None,
                "reason": None,
                "validation_confidence": "low"  # Add validation confidence field
            }
            
            # First identify material type
            if self.identifier_tool:
                identification = self.identifier_tool.identify_material(material_formula)
                material_type = identification.get("material_type", "unknown")
                result["type"] = material_type
                
                # Check if material is verified
                validation_status = identification.get("validation_status", "not_found")
                is_verified = identification.get("is_verified", False)
                if validation_status == "validated" and is_verified:
                    # If material is verified by identifier tool, set high confidence
                    result["validation_confidence"] = "high"
                    result["reason"] = f"Material type verified as {material_type} by identifier tool"
                    # Add identifier info
                    result["identifier"] = identification.get("identifier")
                    result["identifier_type"] = identification.get("identifier_type")
                elif validation_status == "not_found":
                    result["reason"] = f"Identifier tool could not find matching {material_type} material"
                else:
                    result["reason"] = f"Identifier tool verification failed: {identification.get('error', 'unknown error')}"
            else:
                # If identifier tool not available, use simple judgment
                material_type = self._simple_determine_material_type(material_formula)
                result["type"] = material_type
                result["reason"] = "Identifier tool not available, using simple judgment"
            
            # Use appropriate validation method based on material type
            if material_type == "metal":
                # Metal material validation
                validation_result = self._validate_metal_structure(material_formula)
                result.update(validation_result)
                # Update validation confidence
                if validation_result["valid"]:
                    result["validation_confidence"] = "high"
                else:
                    result["validation_confidence"] = "low"
            elif material_type == "organic":
                # Organic material validation
                validation_result = self._validate_organic_structure(material_formula)
                result.update(validation_result)
                # Update validation confidence
                if validation_result["valid"]:
                    result["validation_confidence"] = "high"
                else:
                    result["validation_confidence"] = "low"
            else:
                # Unknown type, try both methods
                metal_result = self._validate_metal_structure(material_formula)
                if metal_result["valid"]:
                    result.update(metal_result)
                    result["validation_confidence"] = "high"
                else:
                    organic_result = self._validate_organic_structure(material_formula)
                    result.update(organic_result)
                    if organic_result["valid"]:
                        result["validation_confidence"] = "high"
                    else:
                        result["validation_confidence"] = "low"
            
            # Add mandatory verification requirement
            if not result["valid"]:
                result["mandatory_action_required"] = True
                result["action_description"] = "Material structure failed validation, needs redesign or more experimental data support"
            else:
                result["mandatory_action_required"] = False
                
            return result
                
        except Exception as e:
            logger.error(f"Error validating material structure: {e}")
            return {
                "query": material_formula,
                "valid": False,
                "type": "unknown",
                "data": None,
                "source": None,
                "reason": f"Error during validation: {str(e)}",
                "validation_confidence": "low",
                "mandatory_action_required": True,
                "action_description": f"Error occurred during validation: {str(e)}, manual check required"
            }
    
    def _validate_metal_structure(self, formula: str) -> Dict[str, Any]:
        """
        Validate metal material structure.
        
        Args:
            formula (str): Chemical formula
            
        Returns:
            Dict[str, Any]: Validation result
        """
        if not self.materials_project_tool:
            return {
                "valid": False,
                "type": "metal",
                "data": None,
                "source": None,
                "reason": "Materials Project tool not available"
            }
            
        try:
            # Try search by formula
            search_result = self.materials_project_tool.search_materials(formula=formula, limit=1)
            if "error" not in search_result and "data" in search_result and search_result["data"]:
                material = search_result["data"][0]
                return {
                    "valid": True,
                    "type": "metal",
                    "data": material,
                    "source": "Materials Project",
                    "reason": "Found matching material structure in Materials Project"
                }
                
            # If search by formula fails, try search by elements
            elements = self._extract_elements(formula)
            if elements:
                element_result = self.materials_project_tool.search_materials(elements=elements[:2], limit=1)
                if "error" not in element_result and "data" in element_result and element_result["data"]:
                    material = element_result["data"][0]
                    return {
                        "valid": True,
                        "type": "metal",
                        "data": material,
                        "source": "Materials Project",
                        "reason": "Found material structure with same elements in Materials Project"
                    }
            
            return {
                "valid": False,
                "type": "metal",
                "data": None,
                "source": None,
                "reason": f"No material with formula {formula} found in Materials Project or found material ID is invalid"
            }
        except Exception as e:
            logger.warning(f"Error validating metal material structure: {e}")
            return {
                "valid": False,
                "type": "metal",
                "data": None,
                "source": None,
                "reason": f"Error validating metal material: {str(e)}"
            }
    
    def _validate_organic_structure(self, formula: str) -> Dict[str, Any]:
        """
        Validate organic material structure.
        
        Args:
            formula (str): Chemical formula or compound name
            
        Returns:
            Dict[str, Any]: Validation result
        """
        try:
            # Use PubChem tool to search compound
            compound_info = self.pubchem_tool.search_compound(formula)
            if "error" not in compound_info:
                return {
                    "valid": True,
                    "type": "organic",
                    "data": compound_info,
                    "source": "PubChem",
                    "reason": "Found matching compound structure in PubChem"
                }
            else:
                return {
                    "valid": False,
                    "type": "organic",
                    "data": None,
                    "source": None,
                    "reason": f"No compound with formula {formula} found in PubChem"
                }
        except Exception as e:
            logger.warning(f"Error validating organic compound structure: {e}")
            return {
                "valid": False,
                "type": "organic",
                "data": None,
                "source": None,
                "reason": f"Error validating organic compound: {str(e)}"
            }
    
    def _simple_determine_material_type(self, query: str) -> str:
        """
        Simple material type determination (when identifier tool is unavailable).
        
        Args:
            query (str): Query string
            
        Returns:
            str: Material type ("metal", "organic", "unknown")
        """
        # Extract element symbols
        elements = self._extract_elements(query)
        
        # Common metal elements
        metal_elements = ['Li', 'Be', 'Na', 'Mg', 'Al', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 
                         'Ga', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Cs', 'Ba',
                         'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
                         'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',
                         'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr']
        
        # Common non-metal elements (typically form organic compounds)
        non_metal_elements = ['H', 'C', 'N', 'O', 'F', 'P', 'S', 'Cl', 'Br', 'I']
        
        # Check if contains metal elements
        has_metal = any(element in metal_elements for element in elements)
        
        # Check if mainly composed of non-metal elements (likely organic)
        non_metal_count = sum(1 for element in elements if element in non_metal_elements)
        total_elements = len(elements)
        
        # If contains metal elements, consider as metal material
        if has_metal:
            return "metal"
        
        # If mainly composed of non-metal elements, consider as organic
        if total_elements > 0 and non_metal_count / total_elements >= 0.5:
            return "organic"
        
        # Default return unknown
        return "unknown"
    
    def _extract_elements(self, query: str) -> list:
        """
        Extract element symbols from query string.
        
        Args:
            query (str): Query string
            
        Returns:
            list: List of element symbols
        """
        import re
        # Match common element symbols (1-2 letters, first uppercase)
        elements = re.findall(r'[A-Z][a-z]?', query)
        # Filter out strings that may not be elements
        valid_elements = []
        # Common elements list (simplified)
        common_elements = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
                          'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
                          'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
                          'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
                          'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn']
        
        for element in elements:
            if element in common_elements:
                valid_elements.append(element)
        
        return list(set(valid_elements))  # Deduplicate

# Global instance
_structure_validator_tool = None

def get_structure_validator_tool() -> StructureValidatorTool:
    """
    Get structure validator tool instance.
    
    Returns:
        StructureValidatorTool: Structure validator tool instance
    """
    global _structure_validator_tool
    if _structure_validator_tool is None:
        _structure_validator_tool = StructureValidatorTool()
    return _structure_validator_tool

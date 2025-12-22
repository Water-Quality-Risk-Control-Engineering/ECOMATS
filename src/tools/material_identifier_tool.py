#!/usr/bin/env python3
"""
Material Identifier Processing Tool.
Unified handling of metal materials and organic compound identifiers (MP-ID and CAS numbers).
"""

import logging
from typing import Dict, Any, Optional
from src.tools.materials_project_tool import get_materials_project_tool
from src.tools.pubchem_tool import get_pubchem_tool

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MaterialIdentifierTool:
    """Material Identifier Processing Tool - Unified handling of metal and organic material identifiers.
    
    Supports identifier processing for multiple material types:
    1. Metal materials (get Materials Project ID)
    2. Organic materials (get CAS number)
    3. Composite materials (identify by element composition)
    """
    
    def __init__(self):
        """Initialize material identifier processing tool."""
        try:
            self.materials_project_tool = get_materials_project_tool()
        except Exception as e:
            logger.warning(f"Materials Project tool not available: {e}")
            self.materials_project_tool = None
        self.pubchem_tool = get_pubchem_tool()
    
    def identify_material(self, query: str) -> Dict[str, Any]:
        """
        Identify material type and get corresponding identifier.
        
        Args:
            query (str): Material query string (formula, element combination, or material name)
            
        Returns:
            Dict[str, Any]: Dictionary containing material type and identifier information
        """
        try:
            result = {
                "query": query,
                "material_type": "unknown",
                "identifier": None,
                "identifier_type": None,
                "additional_info": {},
                "validation_status": "not_found",  # Add validation status field
                "is_verified": False  # Add verification flag field
            }
            
            # First try to determine material type
            material_type = self._determine_material_type(query)
            result["material_type"] = material_type
            
            # Get identifier using appropriate tool based on material type
            if material_type == "metal":
                # Use Materials Project to get MP-ID for metal materials
                mp_result = self._get_mpid_for_metal(query)
                if mp_result and "material_id" in mp_result:
                    result["identifier"] = mp_result["material_id"]
                    result["identifier_type"] = "MP-ID"
                    result["additional_info"] = mp_result
                    result["validation_status"] = "validated"  # Set validation status
                    result["is_verified"] = True  # Set verification flag
                else:
                    result["validation_status"] = "not_found"
                    result["is_verified"] = False
                    logger.info(f"Could not find material in Materials Project: {query}")
            elif material_type == "organic":
                # Use PubChem to get CAS number for organic materials
                cas_result = self._get_cas_for_organic(query)
                if cas_result and "CASNumbers" in cas_result:
                    cas_numbers = cas_result["CASNumbers"]
                    if cas_numbers:
                        result["identifier"] = cas_numbers[0]  # Use first CAS number
                        result["identifier_type"] = "CAS"
                        result["additional_info"] = cas_result
                        result["validation_status"] = "validated"  # Set validation status
                        result["is_verified"] = True  # Set verification flag
                    else:
                        result["validation_status"] = "not_found"
                        result["is_verified"] = False
                        logger.info(f"Could not find CAS number in PubChem: {query}")
                else:
                    result["validation_status"] = "not_found"
                    result["is_verified"] = False
                    logger.info(f"Could not find compound info in PubChem: {query}")
            else:
                # Unknown type, try both methods
                mp_result = self._get_mpid_for_metal(query)
                if mp_result and "material_id" in mp_result:
                    result["identifier"] = mp_result["material_id"]
                    result["identifier_type"] = "MP-ID"
                    result["additional_info"] = mp_result
                    result["material_type"] = "metal"
                    result["validation_status"] = "validated"  # Set validation status
                    result["is_verified"] = True  # Set verification flag
                else:
                    cas_result = self._get_cas_for_organic(query)
                    if cas_result and "CASNumbers" in cas_result:
                        cas_numbers = cas_result["CASNumbers"]
                        if cas_numbers:
                            result["identifier"] = cas_numbers[0]  # Use first CAS number
                            result["identifier_type"] = "CAS"
                            result["additional_info"] = cas_result
                            result["material_type"] = "organic"
                            result["validation_status"] = "validated"  # Set validation status
                            result["is_verified"] = True  # Set verification flag
                        else:
                            result["validation_status"] = "not_found"
                            result["is_verified"] = False
                            logger.info(f"Could not find CAS number in PubChem: {query}")
                    else:
                        result["validation_status"] = "not_found"
                        result["is_verified"] = False
                        logger.info(f"Could not find material in any database: {query}")
            
            # Add additional validation info
            if not result["is_verified"]:
                result["warning"] = f"Warning: Could not verify identifier for material '{query}'. Do not use unverified database identifiers."
            
            return result
                
        except Exception as e:
            logger.error(f"Error identifying material identifier: {e}")
            return {
                "success": False,
                "query": query,
                "error": f"Identification failed: {str(e)}",
                "validation_status": "error",  # Add validation status
                "is_verified": False,  # Add verification flag
                "warning": f"Warning: Error occurred while verifying identifier for material '{query}'. Do not use unverified database identifiers."
            }
    
    def _determine_material_type(self, query: str) -> str:
        """
        Determine material type (metal, organic, or other).
        
        Args:
            query (str): Query string
            
        Returns:
            str: Material type ("metal", "organic", "unknown")
        """
        # Simple material type determination logic
        # Based on element composition
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
    
    def _get_mpid_for_metal(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get MP-ID for metal material.
        
        Args:
            query (str): Query string
            
        Returns:
            Optional[Dict[str, Any]]: Materials Project data or None
        """
        if not self.materials_project_tool:
            return None
            
        try:
            # Try search by formula
            result = self.materials_project_tool.search_materials(
                formula=query,
                limit=5,
                fields=["material_id", "formula_pretty", "chemsys"]
            )
            if "error" not in result and "data" in result and result["data"]:
                # Check if returned material is related to query
                for material in result["data"]:
                    material_formula = material.get("formula", "")
                    material_id = material.get("material_id", "")
                    
                    # Verify material_id exists in Materials Project database
                    if material_id and self.materials_project_tool.verify_material_id_exists(material_id):
                        # Check if formula is strictly related to query
                        if self._is_formula_strictly_related(query, material_formula):
                            logger.info(f"Found related material: {material_formula} (ID: {material_id})")
                            return material
                        else:
                            logger.warning(f"Found material but formula mismatch: query '{query}' vs '{material_formula}'")
                    else:
                        logger.warning(f"Found invalid material ID: {material_id}")
                
            # If search by formula fails, try search by elements
            elements = self._extract_elements(query)
            if elements:
                result = self.materials_project_tool.search_materials(
                    elements=elements[:3],
                    limit=5,
                    fields=["material_id", "formula_pretty", "chemsys"]
                )
                if "error" not in result and "data" in result and result["data"]:
                    # Check if returned material contains elements from query
                    for material in result["data"]:
                        material_elements = material.get("chemsys", "").split("-")
                        material_id = material.get("material_id", "")
                        
                        # Verify material_id exists in Materials Project database
                        if material_id and self.materials_project_tool.verify_material_id_exists(material_id):
                            # Check if elements strictly match
                            if self._are_elements_strictly_related(elements, material_elements):
                                logger.info(f"Found material with related elements: {material.get('formula', '')} (ID: {material_id})")
                                return material
                            else:
                                logger.warning(f"Found material but elements mismatch: query '{elements}' vs '{material_elements}'")
                        else:
                            logger.warning(f"Found invalid material ID: {material_id}")
                    
            # If still not found, return None instead of generating fake data
            # Add explicit log indicating no matching material found
            logger.info(f"No matching material found in Materials Project for {query}")
            return None
        except Exception as e:
            logger.warning(f"Error getting MP-ID for metal material: {e}")
            # Even on exception, return None instead of generating fake data
            return None
    
    def _is_formula_strictly_related(self, query: str, formula: str) -> bool:
        """
        Strictly check if query and formula are related.
        
        Args:
            query (str): Query string
            formula (str): Chemical formula
            
        Returns:
            bool: Whether related
        """
        # Extract elements from query
        query_elements = set(self._extract_elements(query))
        formula_elements = set(self._extract_elements(formula))
        
        # For complex queries like (FeTCPP)Co(Melm), need special handling
        # If query contains complex organic ligands, check if main metal elements match
        main_metal_elements = ['Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Mn', 'Cr', 'V', 'Ti']
        query_metals = [e for e in query_elements if e in main_metal_elements]
        formula_metals = [e for e in formula_elements if e in main_metal_elements]
        
        # If both query and formula contain same main metal elements, consider related
        if query_metals and formula_metals and set(query_metals) == set(formula_metals):
            return True
            
        # Check if there are enough common elements (at least 50% match)
        if len(query_elements) > 0:
            common_elements = query_elements.intersection(formula_elements)
            return len(common_elements) / len(query_elements) >= 0.5
            
        return False
    
    def _are_elements_strictly_related(self, query_elements: list, material_elements: list) -> bool:
        """
        Strictly check if query elements and material elements are related.
        
        Args:
            query_elements (list): Query element list
            material_elements (list): Material element list
            
        Returns:
            bool: Whether related
        """
        query_set = set(query_elements)
        material_set = set(material_elements)
        
        # Check if there are enough common elements (at least 50% match)
        if len(query_set) > 0:
            common_elements = query_set.intersection(material_set)
            return len(common_elements) / len(query_set) >= 0.5
            
        return False
    
    def _is_formula_related(self, query: str, formula: str) -> bool:
        """
        Check if query and formula are related.
        
        Args:
            query (str): Query string
            formula (str): Chemical formula
            
        Returns:
            bool: Whether related
        """
        # Extract elements from query
        query_elements = set(self._extract_elements(query))
        formula_elements = set(self._extract_elements(formula))
        
        # Check if there are common elements
        return len(query_elements.intersection(formula_elements)) > 0
    
    def _are_elements_related(self, query_elements: list, material_elements: list) -> bool:
        """
        Check if query elements and material elements are related.
        
        Args:
            query_elements (list): Query element list
            material_elements (list): Material element list
            
        Returns:
            bool: Whether related
        """
        query_set = set(query_elements)
        material_set = set(material_elements)
        
        # Check if there are common elements
        return len(query_set.intersection(material_set)) > 0
    
    def _get_cas_for_organic(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get CAS number for organic material.
        
        Args:
            query (str): Query string
            
        Returns:
            Optional[Dict[str, Any]]: PubChem data (containing CAS number) or None
        """
        try:
            # Use PubChem tool to get compound info with CAS number
            result = self.pubchem_tool.get_compound_info_with_cas(query)
            if "error" not in result and "Compound" in result:
                return result["Compound"]
            return None
        except Exception as e:
            logger.warning(f"Error getting CAS number for organic material: {e}")
            return None

# Global instance
_material_identifier_tool = None

def get_material_identifier_tool() -> MaterialIdentifierTool:
    """
    Get material identifier processing tool instance.
    
    Returns:
        MaterialIdentifierTool: Material identifier processing tool instance
    """
    global _material_identifier_tool
    if _material_identifier_tool is None:
        _material_identifier_tool = MaterialIdentifierTool()
    return _material_identifier_tool

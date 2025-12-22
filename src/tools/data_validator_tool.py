#!/usr/bin/env python3
"""
Data Validator Tool.
Used to validate the authenticity and validity of chemical and material data.
"""

import logging
import re
import time
from typing import Dict, Any, List, Union

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class DataValidatorTool:
    """Data Validator Tool Class."""
    
    def __init__(self):
        """Initialize data validator tool."""
        # Define valid chemical element symbols
        self.valid_elements = [
            'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
            'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
            'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
            'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
            'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'
        ]
        
        # Define valid GHS hazard statement codes
        self.valid_h_statements = [
            "H200", "H201", "H202", "H203", "H204", "H205", "H220", "H221", "H222", "H223", "H224", "H225", "H226", 
            "H228", "H240", "H241", "H242", "H250", "H251", "H252", "H260", "H261", "H270", "H271", "H272", "H280", 
            "H281", "H290", "H300", "H301", "H302", "H303", "H304", "H305", "H310", "H311", "H312", "H313", "H314", 
            "H315", "H316", "H317", "H318", "H319", "H320", "H330", "H331", "H332", "H333", "H334", "H335", "H336", 
            "H340", "H341", "H350", "H351", "H360", "H361", "H362", "H370", "H371", "H372", "H373", "H400", "H401", 
            "H402", "H410", "H411", "H412", "H413", "H420"
        ]
    
    def validate_cid(self, cid: Any) -> Dict[str, Any]:
        """
        Validate if PubChem CID is valid.
        
        Args:
            cid: Compound ID
            
        Returns:
            Validation result dictionary
        """
        try:
            # CID should be a positive integer
            if cid is None or cid == "" or cid == "N/A" or cid == "null":
                return {
                    "valid": False,
                    "reason": "CID is empty or invalid",
                    "value": cid
                }
            cid_int = int(cid)
            if cid_int <= 0:
                return {
                    "valid": False,
                    "reason": "CID must be a positive integer",
                    "value": cid
                }
            return {
                "valid": True,
                "reason": "CID is valid",
                "value": cid_int
            }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "reason": "CID is not a valid number",
                "value": cid
            }
    
    def validate_material_id(self, material_id: Any) -> Dict[str, Any]:
        """
        Validate if Materials Project material ID is valid.
        
        Args:
            material_id: Material ID
            
        Returns:
            Validation result dictionary
        """
        try:
            # Material ID should be a string starting with "mp-"
            if material_id is None or material_id == "" or material_id == "N/A" or material_id == "null":
                return {
                    "valid": False,
                    "reason": "Material ID is empty or invalid",
                    "value": material_id
                }
            material_id_str = str(material_id)
            if not material_id_str.startswith("mp-") or len(material_id_str) <= 3:
                return {
                    "valid": False,
                    "reason": "Material ID format is incorrect, should start with 'mp-'",
                    "value": material_id
                }
            return {
                "valid": True,
                "reason": "Material ID is valid",
                "value": material_id_str
            }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "reason": "Material ID is not a valid string",
                "value": material_id
            }
    
    def validate_cas_number(self, cas_number: str) -> Dict[str, Any]:
        """
        Validate if CAS number format is correct.
        
        Args:
            cas_number: CAS number
            
        Returns:
            Validation result dictionary
        """
        if not cas_number or cas_number == "N/A" or cas_number == "null":
            return {
                "valid": False,
                "reason": "CAS number is empty or invalid",
                "value": cas_number
            }
        
        # CAS number format: XXXXX-XX-X
        cas_pattern = r'^\d{2,7}-\d{2}-\d$'
        if re.match(cas_pattern, cas_number):
            return {
                "valid": True,
                "reason": "CAS number format is correct",
                "value": cas_number
            }
        else:
            return {
                "valid": False,
                "reason": "CAS number format is incorrect, should be XXXXX-XX-X format",
                "value": cas_number
            }
    
    def validate_molecular_formula(self, formula: str) -> Dict[str, Any]:
        """
        Validate if molecular formula is valid.
        
        Args:
            formula: Molecular formula
            
        Returns:
            Validation result dictionary
        """
        if not formula or formula == "N/A" or formula == "null":
            return {
                "valid": False,
                "reason": "Molecular formula is empty or invalid",
                "value": formula
            }
        
        # Simple molecular formula validation (supports parentheses)
        formula_pattern = r'^([A-Z][a-z]?[0-9]*)+([A-Z][a-z]?[0-9]*)*$|^([A-Z][a-z]?[0-9]*)*\([A-Z][a-z]?[0-9]*\)[0-9]*([A-Z][a-z]?[0-9]*)*$'
        if re.match(formula_pattern, formula):
            # Extract element symbols and validate they are valid
            elements = re.findall(r'[A-Z][a-z]?', formula)
            invalid_elements = [e for e in elements if e not in self.valid_elements]
            if not invalid_elements:
                return {
                    "valid": True,
                    "reason": "Molecular formula format is correct and elements are valid",
                    "value": formula
                }
            else:
                return {
                    "valid": False,
                    "reason": f"Molecular formula contains invalid elements: {', '.join(invalid_elements)}",
                    "value": formula
                }
        else:
            return {
                "valid": False,
                "reason": "Molecular formula format is incorrect",
                "value": formula
            }
    
    def validate_h_statements(self, h_statements: List[str]) -> Dict[str, Any]:
        """
        Validate if GHS hazard statement codes are valid.
        
        Args:
            h_statements: List of hazard statement codes
            
        Returns:
            Validation result dictionary
        """
        if not h_statements:
            return {
                "valid": True,
                "reason": "Hazard statement list is empty",
                "value": h_statements
            }
        
        invalid_statements = [h for h in h_statements if h not in self.valid_h_statements]
        if not invalid_statements:
            return {
                "valid": True,
                "reason": "All hazard statement codes are valid",
                "value": h_statements
            }
        else:
            return {
                "valid": False,
                "reason": f"Contains invalid hazard statement codes: {', '.join(invalid_statements)}",
                "value": h_statements,
                "invalid_statements": invalid_statements
            }
    
    def validate_molecular_weight(self, molecular_weight: Union[str, float]) -> Dict[str, Any]:
        """
        Validate if molecular weight is valid.
        
        Args:
            molecular_weight: Molecular weight
            
        Returns:
            Validation result dictionary
        """
        if molecular_weight == "N/A" or molecular_weight == "null" or molecular_weight is None:
            # Molecular weight can be empty
            return {
                "valid": True,
                "reason": "Molecular weight is empty (acceptable)",
                "value": molecular_weight
            }
        
        try:
            mw = float(molecular_weight)
            if mw <= 0:
                return {
                    "valid": False,
                    "reason": "Molecular weight must be positive",
                    "value": molecular_weight
                }
            elif mw > 100000:  # 100,000 Da, a reasonable upper limit
                return {
                    "valid": False,
                    "reason": "Molecular weight is too large, may be incorrect",
                    "value": molecular_weight
                }
            else:
                return {
                    "valid": True,
                    "reason": "Molecular weight is valid",
                    "value": mw
                }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "reason": "Molecular weight is not a valid number",
                "value": molecular_weight
            }
    
    def validate_chemical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the completeness and validity of chemical data.
        
        Args:
            data: Chemical data dictionary
            
        Returns:
            Validation result dictionary
        """
        validation_results = {}
        overall_valid = True
        
        # Validate CID (if exists)
        if "pubchem_cid" in data:
            cid_result = self.validate_cid(data["pubchem_cid"])
            validation_results["cid"] = cid_result
            if not cid_result["valid"]:
                overall_valid = False
        
        # Validate CAS number (if exists)
        if "cas_number" in data:
            cas_result = self.validate_cas_number(data["cas_number"])
            validation_results["cas_number"] = cas_result
            if not cas_result["valid"]:
                overall_valid = False
        
        # Validate molecular formula (if exists)
        if "molecular_formula" in data:
            formula_result = self.validate_molecular_formula(data["molecular_formula"])
            validation_results["molecular_formula"] = formula_result
            if not formula_result["valid"]:
                overall_valid = False
        
        # Validate molecular weight (if exists)
        if "molecular_weight" in data:
            mw_result = self.validate_molecular_weight(data["molecular_weight"])
            validation_results["molecular_weight"] = mw_result
            if not mw_result["valid"]:
                overall_valid = False
        
        # Validate hazard statements (if exists)
        if "hazard_statements" in data and isinstance(data["hazard_statements"], list):
            h_result = self.validate_h_statements(data["hazard_statements"])
            validation_results["hazard_statements"] = h_result
            if not h_result["valid"]:
                overall_valid = False
        
        # Validate material ID (if exists)
        if "material_id" in data:
            material_id_result = self.validate_material_id(data["material_id"])
            validation_results["material_id"] = material_id_result
            if not material_id_result["valid"]:
                overall_valid = False
        
        return {
            "valid": overall_valid,
            "validation_results": validation_results,
            "timestamp": time.time(),
            "data": data
        }

# Global instance
_data_validator_tool = None

def get_data_validator_tool() -> DataValidatorTool:
    """
    Get data validator tool instance.
    
    Returns:
        DataValidatorTool: Data validator tool instance
    """
    global _data_validator_tool
    if _data_validator_tool is None:
        _data_validator_tool = DataValidatorTool()
    return _data_validator_tool

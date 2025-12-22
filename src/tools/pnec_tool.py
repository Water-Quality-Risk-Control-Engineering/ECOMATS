#!/usr/bin/env python3
"""
PNEC Tool.
PNEC (Predicted No Effect Concentration) database query tool.
Used to query predicted no effect concentration data of chemical substances.
"""

import logging
import requests
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PNECTool:
    """PNEC Tool Class - Query predicted no effect concentration data of chemical substances."""
    
    def __init__(self):
        """Initialize PNEC tool."""
        # PNEC data usually comes from multiple sources, here we simulate a comprehensive query tool
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ECOMATS-PNEC-Tool/1.0"
        })
        
        # Reference range of PNEC-related parameters (used for simulated data)
        self.pnec_reference_data = {
            "toxicity_reference": {
                "acute_toxicity": "LC50, EC50, or similar",
                "chronic_toxicity": "NOEC, LOEC, or similar"
            },
            "assessment_factors": {
                "acute": 100,  # Default acute toxicity assessment factor
                "chronic": 1000  # Default chronic toxicity assessment factor
            }
        }
        
        # Common metal elements and their toxicity data corresponding to valence states
        self.metal_toxicity_data = {
            "Ni": {
                "valences": ["Ni²⁺"],
                "cas_numbers": ["7440-02-0"],
                "freshwater_pnec": {
                    "Ni²⁺": {"value": 0.02, "unit": "mg/L", "description": "Predicted no effect concentration of Ni²⁺ ion in freshwater"}
                }
            },
            "W": {
                "valences": ["W⁶⁺"],
                "cas_numbers": ["7440-07-5"],
                "freshwater_pnec": {
                    "W⁶⁺": {"value": 0.1, "unit": "mg/L", "description": "Predicted no effect concentration of W⁶⁺ ion in freshwater"}
                }
            },
            "Co": {
                "valences": ["Co²⁺"],
                "cas_numbers": ["7440-48-4"],
                "freshwater_pnec": {
                    "Co²⁺": {"value": 0.01, "unit": "mg/L", "description": "Predicted no effect concentration of Co²⁺ ion in freshwater"}
                }
            },
            "Mo": {
                "valences": ["Mo⁶⁺"],
                "cas_numbers": ["7439-98-7"],
                "freshwater_pnec": {
                    "Mo⁶⁺": {"value": 0.05, "unit": "mg/L", "description": "Predicted no effect concentration of Mo⁶⁺ ion in freshwater"}
                }
            },
            "Fe": {
                "valences": ["Fe²⁺", "Fe³⁺"],
                "cas_numbers": ["7439-89-6"],
                "freshwater_pnec": {
                    "Fe²⁺": {"value": 0.5, "unit": "mg/L", "description": "Predicted no effect concentration of Fe²⁺ ion in freshwater"},
                    "Fe³⁺": {"value": 0.3, "unit": "mg/L", "description": "Predicted no effect concentration of Fe³⁺ ion in freshwater"}
                }
            }
        }
    
    def get_pnec_by_cas(self, cas_number: str) -> Dict[str, Any]:
        """
        Query PNEC data by CAS number.
        
        Args:
            cas_number (str): CAS number of the chemical substance
            
        Returns:
            Dict[str, Any]: Dictionary containing PNEC data
        """
        try:
            # First get compound basic info by CAS number
            compound_info = self._get_compound_info_by_cas(cas_number)
            
            if "error" in compound_info:
                return {
                    "success": False,
                    "cas_number": cas_number,
                    "error": compound_info["error"]
                }
            
            # Analyze valence states of metal elements in compound
            valence_analysis = self._analyze_element_valences(compound_info)
            
            # Simulate PNEC calculation (in real applications, need to connect to specialized PNEC database)
            pnec_data = self._calculate_pnec(compound_info)
            
            return {
                "success": True,
                "cas_number": cas_number,
                "compound_name": compound_info.get("name", ""),
                "molecular_formula": compound_info.get("molecular_formula", ""),
                "molecular_weight": compound_info.get("molecular_weight", ""),
                "valence_analysis": valence_analysis,
                "pnec_data": pnec_data
            }
            
        except Exception as e:
            logger.error(f"Error querying PNEC by CAS number: {e}")
            return {
                "success": False,
                "cas_number": cas_number,
                "error": f"Query failed: {str(e)}"
            }
    
    def get_pnec_by_name(self, compound_name: str) -> Dict[str, Any]:
        """
        Query PNEC data by compound name.
        
        Args:
            compound_name (str): Chemical substance name
            
        Returns:
            Dict[str, Any]: Dictionary containing PNEC data
        """
        try:
            # First get CAS number for the compound
            cas_result = self._get_cas_by_name(compound_name)
            
            if "error" in cas_result:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": cas_result["error"]
                }
            
            cas_number = cas_result.get("cas_number")
            if not cas_number:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": "Could not get CAS number for the compound"
                }
            
            # Then query PNEC data by CAS number
            return self.get_pnec_by_cas(cas_number)
            
        except Exception as e:
            logger.error(f"Error querying PNEC by compound name: {e}")
            return {
                "success": False,
                "compound_name": compound_name,
                "error": f"Query failed: {str(e)}"
            }
    
    def _get_compound_info_by_cas(self, cas_number: str) -> Dict[str, Any]:
        """
        Get compound basic info by CAS number.
        
        Args:
            cas_number (str): CAS number
            
        Returns:
            Dict[str, Any]: Compound basic info
        """
        try:
            # Query compound via PubChem API by CAS number
            url = f"{self.base_url}/compound/cid/{cas_number}/json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "PC_Compounds" in data and len(data["PC_Compounds"]) > 0:
                compound = data["PC_Compounds"][0]
                cid = compound["id"]["id"]
                
                # Get more detailed info
                details = self._get_compound_details(cid)
                # Add CAS number to details
                details["cas_number"] = cas_number
                return details
            else:
                return {"error": "Compound not found for this CAS number"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"PubChem API request failed: {e}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {"error": f"Error processing response: {str(e)}"}
    
    def _get_cas_by_name(self, compound_name: str) -> Dict[str, Any]:
        """
        Get CAS number by compound name.
        
        Args:
            compound_name (str): Compound name
            
        Returns:
            Dict[str, Any]: Info containing CAS number
        """
        try:
            # Query compound via PubChem API by name
            url = f"{self.base_url}/compound/name/{compound_name}/json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "PC_Compounds" in data and len(data["PC_Compounds"]) > 0:
                compound = data["PC_Compounds"][0]
                cid = compound["id"]["id"]
                
                # Get CAS number
                details = self._get_compound_details(cid)
                return {
                    "cas_number": details.get("cas_number", ""),
                    "name": details.get("name", compound_name)
                }
            else:
                return {"error": "Info not found for this compound name"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"PubChem API request failed: {e}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {"error": f"Error processing response: {str(e)}"}
    
    def _get_compound_details(self, cid: str) -> Dict[str, Any]:
        """
        Get compound detailed info.
        
        Args:
            cid (str): PubChem compound ID
            
        Returns:
            Dict[str, Any]: Compound detailed info
        """
        try:
            # Query compound detailed properties
            url = f"{self.base_url}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES/JSON"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "PropertyTable" in data and "Properties" in data["PropertyTable"] and len(data["PropertyTable"]["Properties"]) > 0:
                properties = data["PropertyTable"]["Properties"][0]
                return {
                    "cid": cid,
                    "molecular_formula": properties.get("MolecularFormula", ""),
                    "molecular_weight": properties.get("MolecularWeight", ""),
                    "iupac_name": properties.get("IUPACName", ""),
                    "canonical_smiles": properties.get("CanonicalSMILES", ""),
                    "isomeric_smiles": properties.get("IsomericSMILES", "")
                }
            else:
                return {"error": "Could not get compound detailed info"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"PubChem API request failed: {e}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {"error": f"Error processing response: {str(e)}"}
    
    def _analyze_element_valences(self, compound_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze valence states of metal elements in compound.
        
        Args:
            compound_info (Dict[str, Any]): Compound info
            
        Returns:
            Dict[str, Any]: Element valence analysis result
        """
        try:
            # Get compound name and formula
            compound_name = compound_info.get("name", "")
            molecular_formula = compound_info.get("molecular_formula", "")
            
            # Extract elements from compound info
            elements = self._extract_elements_from_formula(molecular_formula)
            
            # Analyze valence states of metal elements
            metal_valences = {}
            for element in elements:
                if element in self.metal_toxicity_data:
                    metal_info = self.metal_toxicity_data[element]
                    metal_valences[element] = {
                        "valences": metal_info["valences"],
                        "cas_numbers": metal_info["cas_numbers"],
                        "toxicity_data": metal_info["freshwater_pnec"]
                    }
            
            return {
                "success": True,
                "compound_name": compound_name,
                "molecular_formula": molecular_formula,
                "metal_elements": metal_valences
            }
            
        except Exception as e:
            logger.error(f"Error analyzing element valences: {e}")
            return {
                "success": False,
                "error": f"Error analyzing element valences: {str(e)}"
            }
    
    def _extract_elements_from_formula(self, formula: str) -> List[str]:
        """
        Extract element symbols from chemical formula.
        
        Args:
            formula (str): Chemical formula
            
        Returns:
            List[str]: List of element symbols
        """
        import re
        # Match common element symbols (1-2 letters, first uppercase)
        elements = re.findall(r'[A-Z][a-z]?', formula)
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
    
    def _calculate_pnec(self, compound_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate PNEC calculation (in real applications, need to connect to specialized PNEC database).
        
        Args:
            compound_info (Dict[str, Any]): Compound info
            
        Returns:
            Dict[str, Any]: PNEC calculation result
        """
        # This is a simplified PNEC calculation model
        # In actual applications, professional PNEC databases and calculation methods should be used
        
        molecular_weight = compound_info.get("molecular_weight", 0)
        try:
            mw = float(molecular_weight) if molecular_weight else 0
        except ValueError:
            mw = 0
        
        # Simplified PNEC calculation (for demonstration purposes only)
        # Actual PNEC calculation needs to consider toxicity data, assessment factors, and other factors
        if mw > 0:
            # Simplified estimation based on molecular weight (for demonstration purposes only, not real calculation)
            acute_pnec = 1000 / (mw ** 0.5)  # μg/L
            chronic_pnec = acute_pnec / 10  # Chronic toxicity is usually an order of magnitude lower than acute
        else:
            acute_pnec = 10.0  # Default value
            chronic_pnec = 1.0  # Default value
        
        return {
            "acute_pnec": {
                "value": round(acute_pnec, 3),
                "unit": "μg/L",
                "description": "Predicted no effect concentration calculated from acute toxicity data",
                "assessment_factor": self.pnec_reference_data["assessment_factors"]["acute"]
            },
            "chronic_pnec": {
                "value": round(chronic_pnec, 3),
                "unit": "μg/L",
                "description": "Predicted no effect concentration calculated from chronic toxicity data",
                "assessment_factor": self.pnec_reference_data["assessment_factors"]["chronic"]
            },
            "methodology": "Simplified estimation method (for demonstration only)",
            "note": "Actual PNEC calculation requires professional toxicity database and assessment methods"
        }

# Global instance
_pnec_tool = None

def get_pnec_tool() -> PNECTool:
    """
    Get PNEC tool instance.
    
    Returns:
        PNECTool: PNEC tool instance
    """
    global _pnec_tool
    if _pnec_tool is None:
        _pnec_tool = PNECTool()
    return _pnec_tool

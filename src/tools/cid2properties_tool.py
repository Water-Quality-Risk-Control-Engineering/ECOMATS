#!/usr/bin/env python3
"""
CID2Properties Tool.
Query compound properties by PubChem CID.
"""

import logging
from typing import Dict, Any
from src.tools.pubchem_tool import get_pubchem_tool

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class CID2PropertiesTool:
    """CID2Properties Tool Class - Query compound properties by PubChem CID."""
    
    def __init__(self):
        """Initialize CID2Properties tool."""
        self.pubchem_tool = get_pubchem_tool()
    
    def get_properties_by_cid(self, cid: str) -> Dict[str, Any]:
        """
        Query compound properties by PubChem CID.
        
        Args:
            cid (str): PubChem compound ID
            
        Returns:
            Dict[str, Any]: Dictionary containing compound properties
        """
        try:
            # Use PubChem tool to query compound information by CID
            result = self.pubchem_tool.get_properties_by_cid(int(cid))
            
            # If query successful, organize return result
            if "error" not in result:
                # Extract property data
                if "PropertyTable" in result and "Properties" in result["PropertyTable"]:
                    properties = result["PropertyTable"]["Properties"][0]
                    return {
                        "success": True,
                        "cid": cid,
                        "molecular_formula": properties.get("MolecularFormula", "N/A"),
                        "molecular_weight": properties.get("MolecularWeight", "N/A"),
                        "iupac_name": properties.get("IUPACName", "N/A"),
                        "canonical_smiles": properties.get("CanonicalSMILES", "N/A"),
                        "isomeric_smiles": properties.get("IsomericSMILES", "N/A"),
                        "inchi": properties.get("InChI", "N/A"),
                        "inchi_key": properties.get("InChIKey", "N/A")
                    }
                else:
                    return {
                        "success": False,
                        "cid": cid,
                        "error": "Unable to parse return data"
                    }
            else:
                return {
                    "success": False,
                    "cid": cid,
                    "error": result.get("error", "Query failed")
                }
                
        except Exception as e:
            logger.error(f"Error querying compound properties by CID: {e}")
            return {
                "success": False,
                "cid": cid,
                "error": f"Query failed: {str(e)}"
            }

# Global instance
_cid2properties_tool = None

def get_cid2properties_tool() -> CID2PropertiesTool:
    """
    Get CID2Properties tool instance.
    
    Returns:
        CID2PropertiesTool: CID2Properties tool instance
    """
    global _cid2properties_tool
    if _cid2properties_tool is None:
        _cid2properties_tool = CID2PropertiesTool()
    return _cid2properties_tool

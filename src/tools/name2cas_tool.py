#!/usr/bin/env python3
"""
Compound Name to CAS Number Tool.
Convert compound names to CAS numbers via PubChem API.
"""

import logging
import requests
import time
import random
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class NameToCASTool:
    """Compound Name to CAS Number Tool Class."""
    
    def __init__(self):
        """Initialize NameToCAS tool."""
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ECOMATS-NameToCAS-Tool/1.0"
        })
    
    def _make_request(self, endpoint: str, timeout: int = 30, max_retries: int = 3) -> Dict[str, Any]:
        """
        Send API request with retry mechanism.
        
        Args:
            endpoint: API endpoint
            timeout: Timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            API response data
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(endpoint, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:  # Not the last attempt
                    # Exponential backoff
                    delay = (2 ** attempt) + (random.randint(0, 1000) / 1000)  # 1-2s random delay
                    logger.info(f"Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
                else:
                    logger.error(f"API request finally failed: {e}")
                    return {"error": str(e)}
    
    def convert_name_to_cas(self, compound_name: str) -> Dict[str, Any]:
        """
        Convert chemical name to CAS number.
        
        Args:
            compound_name (str): Chemical name
            
        Returns:
            Dict[str, Any]: Dictionary containing CAS number and other related information
        """
        try:
            # Query compound information using PubChem API
            endpoint = f"{self.base_url}/compound/name/{compound_name}/cids/JSON"
            result = self._make_request(endpoint)
            
            # Extract CAS number information
            if "IdentifierList" in result and "CID" in result["IdentifierList"]:
                cids = result["IdentifierList"]["CID"]
                if isinstance(cids, list):
                    cid = cids[0]
                else:
                    cid = cids
                
                # Get detailed information, including CAS number
                endpoint = f"{self.base_url}/compound/cid/{cid}/property/CAS,IUPACName,Formula,MolecularWeight,Synonyms/JSON"
                details = self._make_request(endpoint)
                
                if "PropertyTable" in details and "Properties" in details["PropertyTable"]:
                    properties = details["PropertyTable"]["Properties"][0]
                    # Extract CAS number from Synonyms
                    synonyms = properties.get("Synonyms", [])
                    cas_numbers = [syn for syn in synonyms if self._is_cas_number(syn)]
                    cas_number = cas_numbers[0] if cas_numbers else "N/A"
                    
                    return {
                        "success": True,
                        "compound_name": compound_name,
                        "cid": cid,
                        "cas_number": cas_number,
                        "iupac_name": properties.get("IUPACName", ""),
                        "molecular_formula": properties.get("MolecularFormula", ""),
                        "molecular_weight": properties.get("MolecularWeight", ""),
                        "synonyms": synonyms
                    }
                else:
                    return {
                        "success": False,
                        "compound_name": compound_name,
                        "error": "Detailed information of the compound not found",
                        "details": details.get("error", "Unknown error")
                    }
            else:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": "CAS number information of the compound not found",
                    "details": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error converting chemical name to CAS number: {e}")
            return {
                "success": False,
                "compound_name": compound_name,
                "error": f"Conversion failed: {str(e)}"
            }
    
    def _is_cas_number(self, text: str) -> bool:
        """
        Determine if text is in CAS number format.
        
        Args:
            text: Text to check
            
        Returns:
            Whether it is in CAS number format
        """
        import re
        # CAS number format: XXXXX-XX-X
        cas_pattern = r'^\d{2,7}-\d{2}-\d$'
        return bool(re.match(cas_pattern, text))

# Global instance
_name2cas_tool = None

def get_name2cas_tool() -> NameToCASTool:
    """
    Get Name2CAS tool instance.
    
    Returns:
        Name2CASTool: Name2CAS tool instance
    """
    global _name2cas_tool
    if _name2cas_tool is None:
        _name2cas_tool = NameToCASTool()
    return _name2cas_tool
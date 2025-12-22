import requests
import logging
import time
import random
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PubChemTool:
    """PubChem database query tool.
    
    Supports querying and validation for various organic materials:
    1. Pure organic compounds
    2. Bio-based materials
    3. Carbon-based materials (partial)
    4. Other materials containing organic components
    """
    
    def __init__(self, api_key: str = None):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.api_key = api_key or os.getenv('PUBCHEM_API_KEY')
        # Set request headers
        self.headers = {
            "User-Agent": "ECOMATS-PubChem-Tool/1.0"
        }
        # Add API key to request headers if available
        if self.api_key:
            self.headers["X-PubChem-API-Key"] = self.api_key
        
        # Request rate control
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Reduced to 1 second for faster response
    
    def _make_request(self, endpoint: str, timeout: int = 10, max_retries: int = 2) -> Dict[str, Any]:
        """
        Send API request with retry mechanism.
        
        Args:
            endpoint: API endpoint
            timeout: Timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            API response data
        """
        # Request rate control
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/{endpoint}"
                logger.debug(f"Requesting PubChem API: {url}")
                
                # Update last request time
                self.last_request_time = time.time()
                
                response = requests.get(url, headers=self.headers, timeout=timeout)
                
                # Check if it's a 503 error (server busy)
                if response.status_code == 503:
                    retry_after = int(response.headers.get('Retry-After', 30))
                    logger.warning(f"PubChem server is busy, will retry after {retry_after} seconds")
                    if attempt < max_retries - 1:
                        logger.info(f"Waiting {retry_after} seconds before retry")
                        time.sleep(retry_after)
                        continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"PubChem API request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    delay = 2
                    logger.info(f"Waiting {delay} seconds before retry")
                    time.sleep(delay)
                else:
                    logger.error(f"PubChem API request finally timed out")
                    return {"error": f"API request timeout: Please check network connection"}
            except requests.exceptions.RequestException as e:
                logger.warning(f"PubChem API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:  # Not the last attempt
                    # Exponential backoff with random delay
                    delay = (2 ** attempt) + (random.randint(0, 1000) / 1000)  # 1-3s random delay
                    logger.info(f"Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
                else:
                    logger.error(f"PubChem API request finally failed: {e}")
                    return {"error": f"API request failed: {str(e)}"}
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return {"error": f"Error processing response: {str(e)}"}
    
    def get_basic_properties_by_name(self, compound_name: str) -> Dict[str, Any]:
        """
        Query basic information by compound name.
        
        Args:
            compound_name: Compound name
            
        Returns:
            Compound basic information
        """
        endpoint = f"compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def get_synonyms_with_cas(self, compound_name: str) -> Dict[str, Any]:
        """
        Get compound synonyms (including CAS numbers).
        
        Args:
            compound_name: Compound name
            
        Returns:
            List of compound synonyms (including CAS numbers)
        """
        endpoint = f"compound/name/{compound_name}/synonyms/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def get_properties_by_cid(self, cid: int) -> Dict[str, Any]:
        """
        Get detailed information by CID.
        
        Args:
            cid: PubChem compound ID
            
        Returns:
            Compound detailed information
        """
        endpoint = f"compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def search_by_molecular_formula(self, formula: str) -> Dict[str, Any]:
        """
        Search compound by molecular formula.
        
        Args:
            formula: Chemical molecular formula
            
        Returns:
            Compound information
        """
        endpoint = f"compound/fastformula/{formula}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def search_by_inchikey(self, inchikey: str) -> Dict[str, Any]:
        """
        Search compound by InChIKey.
        
        Args:
            inchikey: InChIKey identifier
            
        Returns:
            Compound information
        """
        endpoint = f"compound/inchikey/{inchikey}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def search_compound(self, query: str, search_type: str = "auto") -> Dict[str, Any]:
        """
        Intelligent compound search (automatically determine search type).
        
        Args:
            query: Query content (compound name, molecular formula, or InChIKey)
            search_type: Search type ("auto", "name", "formula", "inchikey")
            
        Returns:
            Compound information
        """
        if search_type == "auto":
            # Check if it's InChIKey format (usually 27 characters with hyphens)
            if len(query) == 27 and query.count('-') >= 2:
                # Likely InChIKey, use inchikey endpoint
                return self.search_by_inchikey(query)
            # Check if it's molecular formula format (contains element symbols and numbers)
            elif self._is_molecular_formula(query):
                # Likely molecular formula, use fastformula endpoint
                return self.search_by_molecular_formula(query)
            else:
                # Likely compound name, use name endpoint
                return self.get_basic_properties_by_name(query)
        elif search_type == "name":
            return self.get_basic_properties_by_name(query)
        elif search_type == "formula":
            return self.search_by_molecular_formula(query)
        elif search_type == "inchikey":
            return self.search_by_inchikey(query)
        else:
            return {"error": f"Unsupported search type: {search_type}"}
    
    def _is_molecular_formula(self, query: str) -> bool:
        """
        Determine if query string is likely a molecular formula.
        
        Args:
            query: Query string
            
        Returns:
            Whether it is likely a molecular formula
        """
        import re
        # Molecular formulas typically consist of element symbols and numbers, may contain parentheses
        # Element symbols start with uppercase letter, may be followed by lowercase
        # Examples: H2O, C6H6, C12H22O11, Ca(OH)2, NaCl
        # More accurate regex pattern supporting various formats
        formula_pattern = r'^([A-Z][a-z]?[0-9]*)+([A-Z][a-z]?[0-9]*)*$|^([A-Z][a-z]?[0-9]*)*\([A-Z][a-z]?[0-9]*\)[0-9]*([A-Z][a-z]?[0-9]*)*$'
        return bool(re.match(formula_pattern, query))
    
    def get_compound_info(self, query: str) -> Dict[str, Any]:
        """
        Get complete compound information.
        
        Args:
            query: Compound name, CID, molecular formula, or InChIKey
            
        Returns:
            Complete compound information
        """
        try:
            # Use intelligent search to get basic information
            basic_info = self.search_compound(query)
            
            if "error" in basic_info:
                return basic_info
                
            try:
                # Extract CID
                if "PropertyTable" in basic_info and "Properties" in basic_info["PropertyTable"]:
                    properties = basic_info["PropertyTable"]["Properties"]
                    if properties and len(properties) > 0:
                        cid = properties[0].get("CID")
                        if cid:
                            # Get detailed information
                            endpoint = f"compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES,InChI,InChIKey,MolecularFormula,MolecularWeight,IUPACName,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
                            details = self._make_request(endpoint, max_retries=3)
                            
                            if "PropertyTable" in details and "Properties" in details["PropertyTable"]:
                                detail_props = details["PropertyTable"]["Properties"][0]
                                
                                # Get SMILES representation and validate
                                canonical_smiles = detail_props.get("CanonicalSMILES", "N/A")
                                isomeric_smiles = detail_props.get("IsomericSMILES", "N/A")
                                
                                # Validate SMILES (simple check)
                                if canonical_smiles != "N/A" and self._is_valid_smiles(canonical_smiles):
                                    canonical_smiles_value = canonical_smiles
                                else:
                                    canonical_smiles_value = "N/A"
                                    
                                if isomeric_smiles != "N/A" and self._is_valid_smiles(isomeric_smiles):
                                    isomeric_smiles_value = isomeric_smiles
                                else:
                                    isomeric_smiles_value = "N/A"
                                
                                # Merge information
                                result = properties[0].copy()
                                result.update({
                                    "canonical_smiles": canonical_smiles_value,
                                    "isomeric_smiles": isomeric_smiles_value,
                                    "inchi": detail_props.get("InChI", "N/A"),
                                    "inchi_key": detail_props.get("InChIKey", "N/A"),
                                    "molecular_formula": detail_props.get("MolecularFormula", "N/A"),
                                    "molecular_weight": detail_props.get("MolecularWeight", "N/A"),
                                    "iupac_name": detail_props.get("IUPACName", "N/A"),
                                    "xlogp": detail_props.get("XLogP", "N/A"),
                                    "hydrogen_bond_donor_count": detail_props.get("HBondDonorCount", "N/A"),
                                    "hydrogen_bond_acceptor_count": detail_props.get("HBondAcceptorCount", "N/A"),
                                    "rotatable_bond_count": detail_props.get("RotatableBondCount", "N/A"),
                                    "tpsa": detail_props.get("TPSA", "N/A"),  # Topological polar surface area
                                    "complexity": detail_props.get("Complexity", "N/A")
                                })
                                return {"Compound": result}
                            else:
                                return {"error": "Failed to get compound detailed information"}
                        else:
                            return {"error": "Failed to extract compound CID"}
                    else:
                        return {"error": "Compound property information not found"}
                else:
                    return basic_info
                    
            except Exception as e:
                logger.error(f"Error getting compound detailed information: {e}")
                return {"error": f"Error getting compound detailed information: {str(e)}"}
                
        except Exception as e:
            logger.error(f"Error getting complete compound information: {e}")
            return {"error": f"Error getting complete compound information: {str(e)}"}
    
    def _is_valid_smiles(self, smiles: str) -> bool:
        """
        Simple validation of SMILES string.
        
        Args:
            smiles: SMILES string
            
        Returns:
            Whether it is valid
        """
        # Simple check: ensure it's not an obviously invalid value
        invalid_patterns = ["#", "N/A", "None", "", "null", "NULL"]
        if any(pattern in smiles for pattern in invalid_patterns):
            return False
            
        # Ensure it contains at least one letter
        if not any(c.isalpha() for c in smiles):
            return False
            
        # Check if it contains valid chemical element symbols
        # Check if it contains at least one common chemical element symbol
        common_elements = ['C', 'H', 'O', 'N', 'P', 'S', 'F', 'Cl', 'Br', 'I', 'B', 'Si']
        if not any(element in smiles for element in common_elements):
            return False
            
        return True
    
    def validate_cid(self, cid: Any) -> bool:
        """
        Validate if CID is valid.
        
        Args:
            cid: Compound ID
            
        Returns:
            Whether CID is valid
        """
        try:
            # CID should be a positive integer
            if cid is None or cid == "" or cid == "N/A":
                return False
            cid_int = int(cid)
            return cid_int > 0
        except (ValueError, TypeError):
            return False
    
    def get_validated_compound_info(self, query: str) -> Dict[str, Any]:
        """
        Get validated compound information.
        
        Args:
            query: Query content
            
        Returns:
            Validated compound information
        """
        try:
            # Get compound information
            compound_info = self.get_compound_info(query)
            
            # Check for errors
            if "error" in compound_info:
                return compound_info
            
            # Validate CID
            if "Compound" in compound_info:
                compound = compound_info["Compound"]
                cid = compound.get("CID")
                if not self.validate_cid(cid):
                    return {
                        "success": False,
                        "query": query,
                        "error": f"Invalid CID: {cid}"
                    }
                
                # Validate molecular weight
                molecular_weight = compound.get("MolecularWeight")
                if molecular_weight == "N/A" or molecular_weight is None:
                    # This is acceptable, some compounds may not have molecular weight info
                    pass
                else:
                    try:
                        mw = float(molecular_weight)
                        if mw <= 0:
                            return {
                                "success": False,
                                "query": query,
                                "error": f"Invalid molecular weight: {molecular_weight}"
                            }
                    except (ValueError, TypeError):
                        # Molecular weight is not a number, this could be a problem
                        pass
                
                # Add validation marker
                compound_info["validated"] = True
                compound_info["validation_time"] = time.time()
            
            return compound_info
            
        except Exception as e:
            logger.error(f"Error validating compound information: {e}")
            return {
                "success": False,
                "query": query,
                "error": f"Validation failed: {str(e)}"
            }
    
    def get_compound_info_with_cas(self, query: str) -> Dict[str, Any]:
        """
        Get complete compound information (including CAS numbers).
        
        Args:
            query: Compound name or molecular formula
            
        Returns:
            Complete compound information
        """
        # First get basic information
        basic_info = self.search_compound(query)
        
        if "error" in basic_info:
            return basic_info
            
        try:
                        # Extract CID
            if "PropertyTable" in basic_info and "Properties" in basic_info["PropertyTable"]:
                properties = basic_info["PropertyTable"]["Properties"]
                if properties and len(properties) > 0:
                    cid = properties[0].get("CID")
                    if cid:
                        # Get synonyms (including CAS numbers)
                        synonyms_data = self.get_synonyms_with_cas(query)
                        cas_numbers = []
                        
                        if "InformationList" in synonyms_data and "Information" in synonyms_data["InformationList"]:
                            info_list = synonyms_data["InformationList"]["Information"]
                            if info_list and len(info_list) > 0:
                                synonyms = info_list[0].get("Synonym", [])
                                # Filter out CAS numbers (format: XXXXX-XX-X)
                                cas_numbers = [syn for syn in synonyms if self._is_cas_number(syn)]
                        
                        # Merge information
                        result = properties[0].copy()
                        result["CASNumbers"] = cas_numbers
                        return {"Compound": result}
                        
            return basic_info
            
        except Exception as e:
            logger.error(f"Error getting complete compound information: {e}")
            return {"error": f"Error getting complete compound information: {str(e)}"}
    
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

# Create global instance
pubchem_tool = None

def get_pubchem_tool(api_key: str = None) -> PubChemTool:
    """
    Get PubChem tool instance.
    
    Args:
        api_key (str, optional): PubChem API key
        
    Returns:
        PubChemTool: Tool instance
    """
    global pubchem_tool
    if pubchem_tool is None:
        pubchem_tool = PubChemTool(api_key)
    return pubchem_tool
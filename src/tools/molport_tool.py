import requests
import logging
import time
import random
import os
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MolPortTool:
    """MolPort database query tool.
    
    Supported features:
    1. Search compounds by SMILES (exact, similarity, substructure, etc.)
    2. Get detailed information by MolPort ID
    3. Get supplier, inventory and price information
    4. Assess compound commercial availability
    """
    
    # Search type constants
    SEARCH_TYPE_EXACT = 3
    SEARCH_TYPE_SIMILARITY = 4
    SEARCH_TYPE_SUBSTRUCTURE = 1
    SEARCH_TYPE_SUPERSTRUCTURE = 2
    SEARCH_TYPE_PERFECT = 5
    SEARCH_TYPE_EXACT_FRAGMENT = 6
    
    def __init__(self, api_key: str = None):
        """
        Initialize MolPort tool.
        
        Args:
            api_key: MolPort API key, reads from environment variable if not provided
        """
        self.base_url = "https://api.molport.com/api"
        self.api_key = api_key or os.getenv('MOLPORT_API_KEY', '')
        self.session = requests.Session()
        
        # Set request headers
        self.session.headers.update({
            "User-Agent": "ECOMATS-MolPort-Tool/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Request rate control
        self.last_request_time = 0
        self.min_request_interval = 1.0  # MolPort API has relaxed rate limits
    
    def _make_get_request(self, endpoint: str, params: Dict = None, timeout: int = 30, max_retries: int = 3) -> Dict[str, Any]:
        """
        Send GET request with retry mechanism.
        
        Args:
            endpoint: API endpoint
            params: URL parameters
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
                logger.debug(f"Requesting MolPort API (GET): {url}")
                
                # Update last request time
                self.last_request_time = time.time()
                
                response = self.session.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"MolPort API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + (random.randint(0, 1000) / 1000)
                    logger.info(f"Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
                else:
                    logger.error(f"MolPort API request finally failed: {e}")
                    return {"error": f"API request failed: {str(e)}"}
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return {"error": f"Error processing response: {str(e)}"}
        
        return {"error": "Request failed"}
    
    def _make_post_request(self, endpoint: str, data: Dict = None, timeout: int = 60, max_retries: int = 3) -> Dict[str, Any]:
        """
        Send POST request with retry mechanism.
        
        Args:
            endpoint: API endpoint
            data: Request body data
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
                logger.debug(f"Requesting MolPort API (POST): {url}")
                
                # Update last request time
                self.last_request_time = time.time()
                
                response = self.session.post(url, json=data, timeout=timeout)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"MolPort API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + (random.randint(0, 1000) / 1000)
                    logger.info(f"Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
                else:
                    logger.error(f"MolPort API request finally failed: {e}")
                    return {"error": f"API request failed: {str(e)}"}
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return {"error": f"Error processing response: {str(e)}"}
        
        return {"error": "Request failed"}
    
    def load_molecule_by_id(self, molecule_id: str) -> Dict[str, Any]:
        """
        Load molecule details by MolPort ID.
        
        Args:
            molecule_id: MolPort molecule ID (e.g., "2325020" or "Molport-002-325-020")
            
        Returns:
            Molecule details including SMILES, suppliers, prices, inventory, etc.
        """
        if not self.api_key:
            return {"error": "MOLPORT_API_KEY not configured, please set it in .env file"}
        
        # Remove possible "Molport-" prefix, keep only numbers
        if isinstance(molecule_id, str) and molecule_id.startswith("Molport-"):
            molecule_id = molecule_id.replace("Molport-", "").replace("-", "")
        
        endpoint = "molecule/load"
        params = {
            "molecule": molecule_id,
            "apikey": self.api_key
        }
        
        return self._make_get_request(endpoint, params=params)
    
    def search_by_smiles(
        self, 
        smiles: str, 
        search_type: int = None,
        similarity_index: float = 0.9,
        max_results: int = 100,
        max_search_time: int = 60000
    ) -> Dict[str, Any]:
        """
        Search by SMILES structure.
        
        Args:
            smiles: SMILES string
            search_type: Search type (1-6), defaults to 4 (similarity search)
            similarity_index: Similarity threshold (0-1), only for similarity search
            max_results: Maximum number of results (max 10000)
            max_search_time: Maximum search time in milliseconds
            
        Returns:
            Search result list containing matched molecule IDs, SMILES and similarity indices
        """
        if not self.api_key:
            return {"error": "MOLPORT_API_KEY not configured, please set it in .env file"}
        
        if search_type is None:
            search_type = self.SEARCH_TYPE_SIMILARITY
        
        # Validate parameters
        if max_results > 10000:
            max_results = 10000
        if similarity_index < 0 or similarity_index > 1:
            similarity_index = 0.9
        
        endpoint = "chemical-search/search"
        data = {
            "API Key": self.api_key,
            "Structure": smiles,
            "Search Type": search_type,
            "Maximum Result Count": max_results,
            "Maximum Search Time": max_search_time,
            "Chemical Similarity Index": similarity_index
        }
        
        return self._make_post_request(endpoint, data=data)
    
    def get_availability_info(self, molecule_id: str) -> Dict[str, Any]:
        """
        Get commercial availability info (simplified version).
        
        Args:
            molecule_id: MolPort molecule ID
            
        Returns:
            Dict containing availability, supplier count, price range, etc.
        """
        molecule_data = self.load_molecule_by_id(molecule_id)
        
        if "error" in molecule_data:
            return molecule_data
        
        try:
            data = molecule_data.get("Data", {}).get("Molecule", {})
            
            # Extract key availability information
            availability_info = {
                "molport_id": data.get("Molport Id", ""),
                "status": data.get("Status", ""),
                "type": data.get("Type", ""),
                "largest_stock": data.get("Largest Stock", ""),
                "largest_stock_measure": data.get("Largest Stock Measure", ""),
                "smiles": data.get("SMILES", ""),
                "iupac": data.get("IUPAC", ""),
                "formula": data.get("Formula", ""),
                "molecular_weight": data.get("Molecular Weight", ""),
                "supplier_count": 0,
                "min_price": None,
                "max_price": None,
                "currency": None
            }
            
            # Count suppliers and price information
            catalogues = data.get("Catalogues", {})
            all_suppliers = []
            
            for category in ["Screening Block Suppliers", "Building Block Suppliers", "Virtual Suppliers"]:
                suppliers = catalogues.get(category, [])
                all_suppliers.extend(suppliers)
            
            availability_info["supplier_count"] = len(all_suppliers)
            
            # Collect price information
            prices = []
            for supplier in all_suppliers:
                for catalogue in supplier.get("Catalogues", []):
                    for packing in catalogue.get("Available Packings", []):
                        price = packing.get("Price")
                        currency = packing.get("Currency")
                        if price is not None:
                            prices.append({
                                "price": price,
                                "currency": currency,
                                "amount": packing.get("Amount", ""),
                                "measure": packing.get("Measure", "")
                            })
            
            if prices:
                # Assume all prices use the same currency (usually USD)
                availability_info["currency"] = prices[0]["currency"]
                price_values = [p["price"] for p in prices]
                availability_info["min_price"] = min(price_values)
                availability_info["max_price"] = max(price_values)
                availability_info["price_details"] = prices[:5]  # Keep only first 5 price entries
            
            return availability_info
            
        except Exception as e:
            logger.error(f"Error parsing availability info: {e}")
            return {"error": f"Failed to parse data: {str(e)}"}
    
    def check_compound_availability(self, smiles: str, similarity_threshold: float = 0.95) -> Dict[str, Any]:
        """
        Check compound commercial availability by SMILES.
        
        Args:
            smiles: SMILES string
            similarity_threshold: Similarity threshold for determining "available"
            
        Returns:
            Availability assessment result
        """
        # First perform exact search
        exact_result = self.search_by_smiles(smiles, search_type=self.SEARCH_TYPE_EXACT, max_results=10)
        
        if "error" in exact_result:
            return exact_result
        
        result_data = exact_result.get("Data", {})
        molecules = result_data.get("Molecules", [])
        
        assessment = {
            "query_smiles": smiles,
            "exact_match_found": len(molecules) > 0,
            "match_count": len(molecules),
            "availability_status": "unknown",
            "best_match": None
        }
        
        if molecules:
            # Has exact match
            assessment["availability_status"] = "available"
            best_match = molecules[0]
            assessment["best_match"] = {
                "molport_id": best_match.get("Molport Id", ""),
                "smiles": best_match.get("SMILES", ""),
                "canonical_smiles": best_match.get("Canonical SMILES", ""),
                "verified_amount": best_match.get("Verified Amount", 0),
                "unverified_amount": best_match.get("Unverified Amount", 0)
            }
        else:
            # Try similarity search
            similar_result = self.search_by_smiles(
                smiles, 
                search_type=self.SEARCH_TYPE_SIMILARITY,
                similarity_index=similarity_threshold,
                max_results=10
            )
            
            if "error" not in similar_result:
                similar_molecules = similar_result.get("Data", {}).get("Molecules", [])
                if similar_molecules:
                    assessment["availability_status"] = "similar_available"
                    assessment["match_count"] = len(similar_molecules)
                    best_match = similar_molecules[0]
                    assessment["best_match"] = {
                        "molport_id": best_match.get("Molport Id", ""),
                        "smiles": best_match.get("SMILES", ""),
                        "canonical_smiles": best_match.get("Canonical SMILES", ""),
                        "similarity_index": best_match.get("Similarity Index", 0),
                        "verified_amount": best_match.get("Verified Amount", 0),
                        "unverified_amount": best_match.get("Unverified Amount", 0)
                    }
                else:
                    assessment["availability_status"] = "not_available"
        
        return assessment


# Singleton pattern
_molport_tool_instance = None

def get_molport_tool(api_key: str = None) -> MolPortTool:
    """
    Get MolPort tool singleton.
    
    Args:
        api_key: MolPort API key (optional)
        
    Returns:
        MolPortTool instance
    """
    global _molport_tool_instance
    if _molport_tool_instance is None:
        _molport_tool_instance = MolPortTool(api_key=api_key)
    return _molport_tool_instance

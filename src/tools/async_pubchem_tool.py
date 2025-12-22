"""
Async PubChem Tool - Supports CrewAI 1.7.0 async execution.
"""
import httpx
import logging
import asyncio
import time
import os
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class AsyncPubChemTool:
    """Async PubChem database query tool.
    
    Advantages over sync version:
    - Supports concurrent query of multiple compounds
    - Non-blocking event loop
    - Fully compatible with CrewAI 1.7.0 async API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.api_key = api_key or os.getenv('PUBCHEM_API_KEY')
        
        # Request headers
        self.headers = {
            "User-Agent": "ECOMATS-PubChem-Tool/2.0-Async"
        }
        if self.api_key:
            self.headers["X-PubChem-API-Key"] = self.api_key
        
        # Concurrency control: max 3 simultaneous requests
        self.semaphore = asyncio.Semaphore(3)
        
        # Rate limiting
        self.min_request_interval = 0.3  # Async version can be faster
        self.last_request_time = 0
        
    async def _rate_limit(self):
        """Async rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    async def _make_request(
        self, 
        endpoint: str, 
        timeout: int = 15, 
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Async API request with concurrency control and retry."""
        async with self.semaphore:  # Limit concurrency
            await self._rate_limit()
            
            for attempt in range(max_retries):
                try:
                    url = f"{self.base_url}/{endpoint}"
                    logger.debug(f"Async requesting PubChem API: {url}")
                    
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.get(url, headers=self.headers)
                        
                        # Handle 503 error
                        if response.status_code == 503:
                            retry_after = int(response.headers.get('Retry-After', 10))
                            if attempt < max_retries - 1:
                                logger.warning(f"Server busy, retrying after {retry_after} seconds")
                                await asyncio.sleep(retry_after)
                                continue
                        
                        response.raise_for_status()
                        return response.json()
                        
                except httpx.TimeoutException:
                    logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        return {"error": "API request timeout"}
                        
                except httpx.HTTPStatusError as e:
                    logger.warning(f"HTTP error {e.response.status_code}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        return {"error": f"HTTP error: {e.response.status_code}"}
                        
                except Exception as e:
                    logger.error(f"Request failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        return {"error": f"Request failed: {str(e)}"}
            
            return {"error": "Max retries exceeded"}
    
    async def get_basic_properties_by_name(self, compound_name: str) -> Dict[str, Any]:
        """Async query basic information."""
        endpoint = f"compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    async def get_properties_by_cid(self, cid: int) -> Dict[str, Any]:
        """Async get CID detailed information."""
        endpoint = f"compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    async def search_by_molecular_formula(self, formula: str) -> Dict[str, Any]:
        """Async search by molecular formula."""
        endpoint = f"compound/fastformula/{formula}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    async def search_by_inchikey(self, inchikey: str) -> Dict[str, Any]:
        """Async search by InChIKey."""
        endpoint = f"compound/inchikey/{inchikey}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    def _is_molecular_formula(self, query: str) -> bool:
        """Determine if query is a molecular formula."""
        import re
        formula_pattern = r'^([A-Z][a-z]?[0-9]*)+([A-Z][a-z]?[0-9]*)*$|^([A-Z][a-z]?[0-9]*)*\([A-Z][a-z]?[0-9]*\)[0-9]*([A-Z][a-z]?[0-9]*)*$'
        return bool(re.match(formula_pattern, query))
    
    async def search_compound(
        self, 
        query: str, 
        search_type: str = "auto"
    ) -> Dict[str, Any]:
        """Intelligent async search."""
        if search_type == "auto":
            if len(query) == 27 and query.count('-') >= 2:
                return await self.search_by_inchikey(query)
            elif self._is_molecular_formula(query):
                return await self.search_by_molecular_formula(query)
            else:
                return await self.get_basic_properties_by_name(query)
        elif search_type == "name":
            return await self.get_basic_properties_by_name(query)
        elif search_type == "formula":
            return await self.search_by_molecular_formula(query)
        elif search_type == "inchikey":
            return await self.search_by_inchikey(query)
        else:
            return {"error": f"Unsupported search type: {search_type}"}
    
    async def get_compound_info(self, query: str) -> Dict[str, Any]:
        """Async get complete compound information."""
        try:
            basic_info = await self.search_compound(query)
            
            if "error" in basic_info:
                return basic_info
            
            if "PropertyTable" in basic_info and "Properties" in basic_info["PropertyTable"]:
                properties = basic_info["PropertyTable"]["Properties"]
                if properties and len(properties) > 0:
                    cid = properties[0].get("CID")
                    if cid:
                        # Async get detailed information
                        details = await self.get_properties_by_cid(cid)
                        
                        if "PropertyTable" in details and "Properties" in details["PropertyTable"]:
                            detail_props = details["PropertyTable"]["Properties"][0]
                            
                            result = properties[0].copy()
                            result.update({
                                "canonical_smiles": detail_props.get("CanonicalSMILES", "N/A"),
                                "isomeric_smiles": detail_props.get("IsomericSMILES", "N/A"),
                                "inchi": detail_props.get("InChI", "N/A"),
                                "inchi_key": detail_props.get("InChIKey", "N/A"),
                                "molecular_formula": detail_props.get("MolecularFormula", "N/A"),
                                "molecular_weight": detail_props.get("MolecularWeight", "N/A"),
                                "iupac_name": detail_props.get("IUPACName", "N/A"),
                                "xlogp": detail_props.get("XLogP", "N/A"),
                                "hydrogen_bond_donor_count": detail_props.get("HBondDonorCount", "N/A"),
                                "hydrogen_bond_acceptor_count": detail_props.get("HBondAcceptorCount", "N/A"),
                                "rotatable_bond_count": detail_props.get("RotatableBondCount", "N/A"),
                                "tpsa": detail_props.get("TPSA", "N/A"),
                                "complexity": detail_props.get("Complexity", "N/A")
                            })
                            return {"Compound": result}
            
            return basic_info
            
        except Exception as e:
            logger.error(f"Failed to get compound info: {e}")
            return {"error": f"Failed to get compound info: {str(e)}"}
    
    async def batch_search(self, queries: list[str]) -> list[Dict[str, Any]]:
        """Batch async search - Key for performance improvement!
        
        Args:
            queries: List of compound queries
            
        Returns:
            List of compound information
            
        Example:
            queries = ["benzene", "toluene", "xylene"]
            results = await tool.batch_search(queries)
            # Concurrent execution, 3x+ faster than sync
        """
        tasks = [self.get_compound_info(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "query": queries[i],
                    "error": f"Query failed: {str(result)}"
                })
            else:
                processed_results.append(result)
        
        return processed_results


# Global instance
_async_pubchem_tool: Optional[AsyncPubChemTool] = None


def get_async_pubchem_tool(api_key: Optional[str] = None) -> AsyncPubChemTool:
    """Get async PubChem tool singleton."""
    global _async_pubchem_tool
    if _async_pubchem_tool is None:
        _async_pubchem_tool = AsyncPubChemTool(api_key)
    return _async_pubchem_tool


# CrewAI tool wrapper
async def async_pubchem_search(compound_name: str) -> str:
    """CrewAI async tool function.
    
    Usage:
        from crewai import Tool
        
        pubchem_tool = Tool(
            name="PubChem Async Search",
            func=async_pubchem_search,  # Pass async function directly
            description="Async query PubChem compound information"
        )
    """
    tool = get_async_pubchem_tool()
    result = await tool.get_compound_info(compound_name)
    
    if "error" in result:
        return f"Query failed: {result['error']}"
    
    if "Compound" in result:
        compound = result["Compound"]
        return f"""Compound Information:
- CID: {compound.get('CID', 'N/A')}
- Molecular Formula: {compound.get('molecular_formula', 'N/A')}
- Molecular Weight: {compound.get('molecular_weight', 'N/A')}
- IUPAC Name: {compound.get('iupac_name', 'N/A')}
- SMILES: {compound.get('canonical_smiles', 'N/A')}
- InChIKey: {compound.get('inchi_key', 'N/A')}
"""
    
    return "Compound information not found"

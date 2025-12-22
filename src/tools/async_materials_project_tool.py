"""
Async Materials Project Tool - Supports CrewAI 1.7.0.

Note: mp-api itself doesn't support async, here we use asyncio.to_thread for non-blocking calls.
"""
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    MP_API_AVAILABLE = False
    logger.warning("mp-api not installed")


class AsyncMaterialsProjectTool:
    """Async Materials Project Tool.
    
    Although mp-api doesn't support async, we use ThreadPoolExecutor for non-blocking.
    Advantage: Does not block event loop in CrewAI async Crew.
    """
    
    def __init__(self, api_key: Optional[str] = None, max_workers: int = 3):
        if not MP_API_AVAILABLE:
            raise ImportError("Please install: pip install mp-api")
        
        self.api_key = api_key or os.getenv('MATERIALS_PROJECT_API_KEY')
        if not self.api_key:
            raise ValueError("MATERIALS_PROJECT_API_KEY not set")
        
        # Use thread pool for non-blocking
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.mpr = MPRester(self.api_key)
        
        # Simple cache
        self._cache = {}
        self._cache_ttl = 600
    
    async def search_materials(
        self,
        formula: Optional[str] = None,
        elements: Optional[List[str]] = None,
        limit: int = 10,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Async search materials."""
        
        # Execute sync operation in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._sync_search,
            formula,
            elements,
            limit,
            fields
        )
        return result
    
    def _sync_search(
        self,
        formula: Optional[str],
        elements: Optional[List[str]],
        limit: int,
        fields: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Sync search (executed in thread pool)."""
        try:
            kwargs = {}
            if formula:
                kwargs["formula"] = formula
            if elements:
                kwargs["elements"] = elements
            
            default_fields = ["material_id", "formula_pretty", "nsites"]
            fields = fields or default_fields
            
            docs = self.mpr.materials.search(
                **kwargs,
                num_chunks=1,
                chunk_size=min(limit, 50),
                fields=fields
            )
            
            if len(docs) > limit:
                docs = docs[:limit]
            
            materials_data = []
            for doc in docs:
                material_dict = {
                    "material_id": str(getattr(doc, "material_id", "N/A")),
                    "formula": getattr(doc, "formula_pretty", "N/A"),
                }
                
                # Add extra fields
                if "nsites" in fields:
                    material_dict["nsites"] = getattr(doc, "nsites", "N/A")
                if "volume" in fields:
                    material_dict["volume"] = getattr(doc, "volume", "N/A")
                if "density" in fields:
                    material_dict["density"] = getattr(doc, "density", "N/A")
                
                materials_data.append(material_dict)
            
            return {
                "data": materials_data,
                "meta": {
                    "total_count": len(materials_data),
                    "limit": limit
                }
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e)}
    
    async def get_material_by_id(self, material_id: str) -> Dict[str, Any]:
        """Async get material details."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._sync_get_by_id,
            material_id
        )
        return result
    
    def _sync_get_by_id(self, material_id: str) -> Dict[str, Any]:
        """Sync get material (executed in thread pool)."""
        try:
            doc = self.mpr.materials.get_data_by_id(material_id)
            
            if not doc:
                return {"error": f"Material not found: {material_id}"}
            
            return {
                "material_id": str(getattr(doc, "material_id", "N/A")),
                "formula": getattr(doc, "formula_pretty", "N/A"),
                "nsites": getattr(doc, "nsites", "N/A"),
                "volume": getattr(doc, "volume", "N/A"),
                "density": getattr(doc, "density", "N/A"),
            }
            
        except Exception as e:
            logger.error(f"Failed to get material: {e}")
            return {"error": str(e)}
    
    async def batch_search(
        self,
        queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Batch async search.
        
        Args:
            queries: [{"formula": "Fe2O3"}, {"elements": ["Cu", "O"]}, ...]
        
        Returns:
            List of all search results
        """
        tasks = []
        for query in queries:
            task = self.search_materials(
                formula=query.get("formula"),
                elements=query.get("elements"),
                limit=query.get("limit", 10)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "query": queries[i],
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# Global singleton
_async_mp_tool: Optional[AsyncMaterialsProjectTool] = None


def get_async_mp_tool(api_key: Optional[str] = None) -> AsyncMaterialsProjectTool:
    """Get async MP tool singleton."""
    global _async_mp_tool
    if _async_mp_tool is None:
        _async_mp_tool = AsyncMaterialsProjectTool(api_key)
    return _async_mp_tool


# CrewAI tool function
async def async_mp_search(formula: str) -> str:
    """CrewAI async search materials."""
    tool = get_async_mp_tool()
    result = await tool.search_materials(formula=formula, limit=5)
    
    if "error" in result:
        return f"Search failed: {result['error']}"
    
    if "data" in result and result["data"]:
        materials = result["data"]
        output = f"Found {len(materials)} materials:\n"
        for mat in materials[:5]:
            output += f"- {mat['material_id']}: {mat['formula']}\n"
        return output
    
    return "No materials found"

import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.molport_tool import get_molport_tool
from src.utils.context_store import ContextStore

class MolPortAvailabilityInput(BaseModel):
    """MolPort Availability Query Input"""
    smiles: str = Field(description="Compound SMILES string")
    similarity_threshold: float = Field(default=0.95, description="Similarity threshold (0-1), default 0.95")

class MolPortSearchInput(BaseModel):
    """MolPort Structure Search Input"""
    smiles: str = Field(description="Compound SMILES string")
    search_type: int = Field(default=4, description="Search type: 1=substructure, 2=superstructure, 3=exact, 4=similarity(default), 5=perfect, 6=exact fragment")
    similarity_index: float = Field(default=0.9, description="Similarity threshold (0-1), default 0.9")
    max_results: int = Field(default=100, description="Max results, default 100 (max 10000)")

class MolPortMoleculeInfoInput(BaseModel):
    """MolPort Molecule Info Query Input"""
    molecule_id: str = Field(description="MolPort molecule ID (e.g. '2325020' or 'Molport-002-325-020')")


class CrewAIMolPortAvailabilityTool(BaseTool):
    """CrewAI tool: Check compound commercial availability"""
    
    name: str = "MolPort Compound Availability Checker"
    description: str = (
        "Check commercial availability of compounds. "
        "Query if compounds can be purchased from suppliers via SMILES string. "
        "Returns availability status, matched compound ID, stock level etc. "
        "Use for assessing material economic feasibility and precursor availability."
    )
    args_schema: type[BaseModel] = MolPortAvailabilityInput

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 3600  # 1 hour cache
    
    def _run(self, smiles: str, similarity_threshold: float = 0.95) -> str:
        """
        Check compound commercial availability.
        
        Args:
            smiles: Compound SMILES string
            similarity_threshold: Similarity threshold (0-1)
            
        Returns:
            JSON formatted availability assessment result
        """
        try:
            # Check context store
            cache_key = f"molport_availability:{smiles}:{similarity_threshold}"
            cached_ctx = ContextStore.get(cache_key)
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            
            # Check memory cache
            import time as _t
            now = _t.time()
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)
            
            # Execute query
            tool = get_molport_tool()
            result = tool.check_compound_availability(smiles, similarity_threshold)
            
            # Save to cache
            ContextStore.set(cache_key, result)
            self._cache[cache_key] = (now, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Query error: {str(e)}"}, ensure_ascii=False)


class CrewAIMolPortSearchTool(BaseTool):
    """CrewAI tool: MolPort chemical structure search"""
    
    name: str = "MolPort Chemical Structure Search"
    description: str = (
        "Search chemical structures in MolPort database. "
        "Supports exact match, similarity search, substructure search etc. "
        "Search similar compounds via SMILES string, get MolPort ID and similarity index. "
        "Use for finding similar purchasable compounds or verifying material design feasibility."
    )
    args_schema: type[BaseModel] = MolPortSearchInput

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 3600
    
    def _run(
        self, 
        smiles: str,
        search_type: int = 4,
        similarity_index: float = 0.9,
        max_results: int = 100
    ) -> str:
        """
        Execute chemical structure search.
        
        Args:
            smiles: Compound SMILES string
            search_type: Search type (1-6)
            similarity_index: Similarity threshold (0-1)
            max_results: Maximum results to return
            
        Returns:
            JSON formatted search results
        """
        try:
            # Check context store
            cache_key = f"molport_search:{search_type}:{smiles}:{similarity_index}:{max_results}"
            cached_ctx = ContextStore.get(cache_key)
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            
            # Check memory cache
            import time as _t
            now = _t.time()
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)
            
            # Execute query
            tool = get_molport_tool()
            result = tool.search_by_smiles(
                smiles,
                search_type=search_type,
                similarity_index=similarity_index,
                max_results=max_results
            )
            
            # Save to cache
            ContextStore.set(cache_key, result)
            self._cache[cache_key] = (now, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Search error: {str(e)}"}, ensure_ascii=False)


class CrewAIMolPortMoleculeInfoTool(BaseTool):
    """CrewAI tool: Get MolPort molecule details"""
    
    name: str = "MolPort Molecule Info Loader"
    description: str = (
        "Get detailed compound info via MolPort ID, including SMILES, IUPAC name, formula, "
        "molecular weight, supplier info, stock, price, delivery time etc. "
        "Use for assessing specific compound commercial availability and cost."
    )
    args_schema: type[BaseModel] = MolPortMoleculeInfoInput

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 3600
    
    def _run(self, molecule_id: str) -> str:
        """
        Get molecule detailed information.
        
        Args:
            molecule_id: MolPort molecule ID
            
        Returns:
            JSON formatted molecule details
        """
        try:
            # Check context store
            cache_key = f"molport_molecule:{molecule_id}"
            cached_ctx = ContextStore.get(cache_key)
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            
            # Check memory cache
            import time as _t
            now = _t.time()
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)
            
            # Execute query
            tool = get_molport_tool()
            result = tool.get_availability_info(molecule_id)
            
            # Save to cache
            ContextStore.set(cache_key, result)
            self._cache[cache_key] = (now, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Info retrieval error: {str(e)}"}, ensure_ascii=False)


# Create tool instances for agent use
molport_availability_tool = CrewAIMolPortAvailabilityTool()
molport_search_tool = CrewAIMolPortSearchTool()
molport_molecule_info_tool = CrewAIMolPortMoleculeInfoTool()

import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.pubchem_tool import get_pubchem_tool
from src.utils.context_store import ContextStore

class PubChemToolInput(BaseModel):
    """PubChem Tool Input Model"""
    query: str = Field(description="Query content (chemical name, formula or InChIKey)")
    search_type: str = Field(default="auto", description="Query type ('auto', 'name', 'formula', 'inchikey')")
    get_cas: bool = Field(default=True, description="Whether to get CAS number")
    get_full_info: bool = Field(default=False, description="Whether to get full compound info")

class CrewAIPubChemTool(BaseTool):
    """CrewAI tool wrapper for PubChem database query"""
    
    name: str = "PubChem Database Query"
    description: str = (
        "Query PubChem chemical database to get compound information. "
        "Search compounds by name, formula or InChIKey. "
        "Get CAS number, molecular weight, SMILES, InChI and other properties. "
        "Use when you need to verify chemical info or get compound details."
    )
    args_schema: type[BaseModel] = PubChemToolInput

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 600
    
    def _run(
        self,
        query: str,
        search_type: str = "auto",
        get_cas: bool = True,
        get_full_info: bool = False
    ) -> str:
        """
        Execute PubChem database query.
        
        Args:
            query: Query content (chemical name, formula or InChIKey)
            search_type: Query type ("auto", "name", "formula", "inchikey")
            get_cas: Whether to get CAS number
            get_full_info: Whether to get full compound info
            
        Returns:
            JSON formatted query result
        """
        try:
            key = (query, search_type, bool(get_cas), bool(get_full_info))
            import time as _t
            now = _t.time()
            if get_full_info:
                cached_ctx = ContextStore.get(f"pubchem_full:{query}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            elif get_cas:
                cached_ctx = ContextStore.get(f"pubchem_cas:{query}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            else:
                cached_ctx = ContextStore.get(f"pubchem_search:{search_type}:{query}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)

            cached = self._cache.get(key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)

            tool = get_pubchem_tool()
            if get_full_info:
                result = tool.get_compound_info(query)
                ContextStore.set(f"pubchem_full:{query}", result)
            elif get_cas:
                result = tool.get_compound_info_with_cas(query)
                ContextStore.set(f"pubchem_cas:{query}", result)
            else:
                result = tool.search_compound(query, search_type)
                ContextStore.set(f"pubchem_search:{search_type}:{query}", result)

            self._cache[key] = (now, result)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Query error: {str(e)}"}, ensure_ascii=False)

# Create tool instance for agent use
pubchem_tool = CrewAIPubChemTool()
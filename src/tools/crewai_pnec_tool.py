import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.pnec_tool import get_pnec_tool
from src.utils.context_store import ContextStore

class PNECToolInput(BaseModel):
    """PNEC Tool Input Model"""
    query: str = Field(description="Query content (CAS number or compound name)")
    query_type: str = Field(default="name", description="Query type ('name' or 'cas')")

class CrewAIPNECTool(BaseTool):
    """CrewAI tool wrapper for PNEC data query"""
    
    name: str = "PNEC Database Query"
    description: str = (
        "Query Predicted No Effect Concentration (PNEC) data for environmental risk assessment. "
        "Query PNEC values by CAS number or compound name. "
        "Use when you need to assess environmental safety of chemicals."
    )
    args_schema: type[BaseModel] = PNECToolInput
    
    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 600
    
    def _run(self, query: str, query_type: str = "name") -> str:
        """
        Execute PNEC data query.
        
        Args:
            query: Query content (CAS number or compound name)
            query_type: Query type ("name" or "cas")
            
        Returns:
            JSON formatted query result
        """
        try:
            key = (query_type.lower(), query)
            import time as _t
            now = _t.time()

            # Try global context first
            if query_type.lower() == "cas":
                cached_ctx = ContextStore.get(f"pnec:cas:{query}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            else:
                cached_ctx = ContextStore.get(f"pnec:name:{query}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)

            # Try local TTL cache
            cached = self._cache.get(key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)

            tool = get_pnec_tool()
            
            # Execute based on query type
            if query_type.lower() == "cas":
                result = tool.get_pnec_by_cas(query)
                ContextStore.set(f"pnec:cas:{query}", result)
            else:
                result = tool.get_pnec_by_name(query)
                ContextStore.set(f"pnec:name:{query}", result)
            
            # Write to local cache and return
            self._cache[key] = (now, result)
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Query error: {str(e)}"}, ensure_ascii=False)
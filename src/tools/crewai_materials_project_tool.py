import json
from typing import Optional, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.materials_project_tool import get_materials_project_tool
from src.utils.context_store import ContextStore

class MaterialsProjectToolInput(BaseModel):
    """Materials Project Tool Input Model"""
    action: str = Field(default="search", description="Action to perform ('search', 'get_material')")
    material_id: Optional[str] = Field(default=None, description="Material ID (for get_material action)")
    formula: Optional[str] = Field(default=None, description="Chemical formula (for search)")
    elements: Optional[List[str]] = Field(default=None, description="Elements that must be included (for search)")
    exclude_elements: Optional[List[str]] = Field(default=None, description="Elements to exclude (for search)")
    crystal_system: Optional[str] = Field(default=None, description="Crystal system (for search)")
    limit: int = Field(default=100, description="Result limit (for search)")
    skip: int = Field(default=0, description="Results to skip (for search)")
    fields: Optional[List[str]] = Field(default=None, description="Data fields to include")

class CrewAIMaterialsProjectTool(BaseTool):
    """CrewAI tool wrapper for Materials Project API"""
    
    name: str = "Materials Project Database Access"
    description: str = (
        "Access Materials Project database to search materials and get properties. "
        "Search by formula, elements, crystal structure or properties. "
        "Usage: action='search', formula='C3N4'"
    )
    args_schema: type[BaseModel] = MaterialsProjectToolInput

    def __init__(self):
        super().__init__()
        self._cache: dict = {}
        self._ttl_seconds = 600

    def _sanitize_fields(self, fields: Optional[List[str]], action: str) -> Optional[List[str]]:
        if not fields:
            return None
        allowed_search = {"material_id", "formula_pretty", "chemsys", "volume", "density", "nsites"}
        allowed_detail = allowed_search | {"symmetry"}
        if action == "search":
            return [f for f in fields if f in allowed_search]
        return [f for f in fields if f in allowed_detail]
    
    def _run(
        self,
        action: str = "search",
        material_id: Optional[str] = None,
        formula: Optional[str] = None,
        elements: Optional[List[str]] = None,
        exclude_elements: Optional[List[str]] = None,
        crystal_system: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
        fields: Optional[List[str]] = None
    ) -> str:
        """
        Execute Materials Project API operation.
        
        Args:
            action: Action to perform ("search", "get_material", etc.)
            material_id: Material ID (for get_material action)
            formula: Chemical formula (for search)
            elements: Elements that must be included (for search)
            exclude_elements: Elements to exclude (for search)
            crystal_system: Crystal system (for search)
            limit: Result limit (for search)
            skip: Results to skip (for search)
            fields: Data fields to include
            
        Returns:
            JSON formatted API response
        """
        try:
            tool = get_materials_project_tool()
            key = (
                action,
                material_id or "",
                formula or "",
                tuple(elements) if elements else (),
                tuple(exclude_elements) if exclude_elements else (),
                crystal_system or "",
                int(limit or 0),
                int(skip or 0),
                tuple(fields) if fields else ()
            )
            import time as _t
            now = _t.time()
            if action == "search":
                cached_ctx = ContextStore.get("materials_project_search")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
                if formula:
                    cached_ctx = ContextStore.get(f"materials_project_search:{formula}")
                    if cached_ctx is not None:
                        return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            elif action == "get_material" and material_id:
                cached_ctx = ContextStore.get(f"materials_project_get:{material_id}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            cached = self._cache.get(key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)

            # Execute operation based on action type
            if action == "search":
                fields = self._sanitize_fields(fields, action)
                # Limit element combination query to avoid large data pulls
                if elements and (limit is None or limit > 10):
                    limit = 10
                result = tool.search_materials(
                    formula=formula,
                    elements=elements,
                    exclude_elements=exclude_elements,
                    crystal_system=crystal_system,
                    limit=min(limit or 100, 10),
                    skip=skip,
                    fields=fields
                )
            elif action == "get_material":
                if not material_id:
                    return json.dumps({"error": "material_id required for get_material action"})
                fields = self._sanitize_fields(fields, action)
                result = tool.get_material_by_id(material_id)
                ContextStore.set(f"materials_project_get:{material_id}", result)
            elif action == "get_structure":
                if not material_id:
                    return json.dumps({"error": "material_id required for get_structure action"})
                return json.dumps({"error": "Feature not implemented"}, ensure_ascii=False)
            elif action == "get_electronic":
                if not material_id:
                    return json.dumps({"error": "material_id required for get_electronic action"})
                return json.dumps({"error": "Feature not implemented"}, ensure_ascii=False)
            elif action == "get_thermo":
                if not material_id:
                    return json.dumps({"error": "material_id required for get_thermo action"})
                return json.dumps({"error": "Feature not implemented"}, ensure_ascii=False)
            elif action == "get_elastic":
                if not material_id:
                    return json.dumps({"error": "material_id required for get_elastic action"})
                return json.dumps({"error": "Feature not implemented"}, ensure_ascii=False)
            elif action == "get_summary":
                return json.dumps({"error": "Feature not implemented"}, ensure_ascii=False)
            else:
                return json.dumps({"error": f"Unsupported action: {action}"})
                
            # Cache and return
            self._cache[key] = (now, result)
            if action == "search":
                ContextStore.set("materials_project_search", result)
                if formula:
                    ContextStore.set(f"materials_project_search:{formula}", result)
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Operation error: {str(e)}"}, ensure_ascii=False)

# Create tool instance for agent use
materials_project_tool = CrewAIMaterialsProjectTool()

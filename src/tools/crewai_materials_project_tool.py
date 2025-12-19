import json
from typing import Optional, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.materials_project_tool import get_materials_project_tool
from src.utils.context_store import ContextStore

class MaterialsProjectToolInput(BaseModel):
    """Materials Project工具输入参数模型 / Materials Project Tool Input Model"""
    action: str = Field(default="search", description="要执行的操作 / Action to perform ('search', 'get_material')")
    material_id: Optional[str] = Field(default=None, description="材料ID / Material ID (for get_material action)")
    formula: Optional[str] = Field(default=None, description="化学式 / Chemical formula (for search)")
    elements: Optional[List[str]] = Field(default=None, description="必须包含的元素列表 / Elements that must be included (for search)")
    exclude_elements: Optional[List[str]] = Field(default=None, description="必须排除的元素列表 / Elements to exclude (for search)")
    crystal_system: Optional[str] = Field(default=None, description="晶体系统 / Crystal system (for search)")
    limit: int = Field(default=100, description="返回结果数量限制 / Result limit (for search)")
    skip: int = Field(default=0, description="跳过的结果数量 / Results to skip (for search)")
    fields: Optional[List[str]] = Field(default=None, description="要包含的数据字段列表 / Data fields to include")

class CrewAIMaterialsProjectTool(BaseTool):
    """CrewAI工具包装器，用于Materials Project API / CrewAI tool wrapper for Materials Project API"""
    
    name: str = "Materials Project Database Access"
    description: str = (
        "访问Materials Project材料科学数据库以搜索材料、获取材料属性等。/ "
        "Access Materials Project database to search materials and get material properties. "
        "可以搜索具有特定化学式、元素组成、晶体结构或物理性质的材料。/ "
        "Search materials with specific formula, elements, crystal structure or properties. "
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
        执行Materials Project API操作
        
        Args:
            action: 要执行的操作 ("search", "get_material", "get_structure", "get_electronic", "get_thermo", "get_elastic", "get_summary")，默认为"search"
            material_id: 材料ID（用于获取特定材料信息的操作）
            formula: 化学式（用于搜索）
            elements: 必须包含的元素列表（用于搜索）
            exclude_elements: 必须排除的元素列表（用于搜索）
            crystal_system: 晶体系统（用于搜索）
            limit: 返回结果数量限制（用于搜索）
            skip: 跳过的结果数量（用于搜索）
            fields: 要包含的数据字段列表（用于获取材料详情，注意：必须是API支持的字段）
            
        Returns:
            JSON格式的API响应结果
        """
        try:
            # 获取工具实例
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

            # 根据操作类型执行相应功能
            if action == "search":
                fields = self._sanitize_fields(fields, action)
                # 限制元素组合查询的limit，避免大范围拉取
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
                    return json.dumps({"error": "获取材料详情需要提供material_id"})
                fields = self._sanitize_fields(fields, action)
                result = tool.get_material_by_id(material_id)
                ContextStore.set(f"materials_project_get:{material_id}", result)
            elif action == "get_structure":
                if not material_id:
                    return json.dumps({"error": "获取晶体结构需要提供material_id"})
                return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
            elif action == "get_electronic":
                if not material_id:
                    return json.dumps({"error": "获取电子性质需要提供material_id"})
                return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
            elif action == "get_thermo":
                if not material_id:
                    return json.dumps({"error": "获取热力学性质需要提供material_id"})
                return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
            elif action == "get_elastic":
                if not material_id:
                    return json.dumps({"error": "获取弹性性质需要提供material_id"})
                return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
            elif action == "get_summary":
                return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
            else:
                return json.dumps({"error": f"不支持的操作: {action}"})
                
            # 缓存并返回
            self._cache[key] = (now, result)
            if action == "search":
                ContextStore.set("materials_project_search", result)
                if formula:
                    ContextStore.set(f"materials_project_search:{formula}", result)
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行操作时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
materials_project_tool = CrewAIMaterialsProjectTool()

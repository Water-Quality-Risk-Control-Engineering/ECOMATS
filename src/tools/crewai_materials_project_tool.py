import json
from typing import Optional, List, Dict, Any
from crewai.tools import BaseTool
from src.tools.materials_project_tool import get_materials_project_tool

class CrewAIMaterialsProjectTool(BaseTool):
    """CrewAI工具包装器，用于Materials Project API"""
    
    name: str = "Materials Project Database Access"
    description: str = (
        "访问Materials Project材料科学数据库以搜索材料、获取材料属性等。"
        "可以搜索具有特定化学式、元素组成、晶体结构或物理性质的材料。"
    )
    
    def _run(
        self,
        action: str,
        material_id: Optional[str] = None,
        formula: Optional[str] = None,
        elements: Optional[List[str]] = None,
        exclude_elements: Optional[List[str]] = None,
        crystal_system: Optional[str] = None,
        band_gap_min: Optional[float] = None,
        band_gap_max: Optional[float] = None,
        is_stable: Optional[bool] = None,
        limit: int = 100,
        skip: int = 0,
        fields: Optional[List[str]] = None
    ) -> str:
        """
        执行Materials Project API操作
        
        Args:
            action: 要执行的操作 ("search", "get_material", "get_structure", "get_electronic", "get_thermo", "get_elastic", "get_summary")
            material_id: 材料ID（用于获取特定材料信息的操作）
            formula: 化学式（用于搜索）
            elements: 必须包含的元素列表（用于搜索）
            exclude_elements: 必须排除的元素列表（用于搜索）
            crystal_system: 晶体系统（用于搜索）
            band_gap_min: 最小带隙（用于搜索）
            band_gap_max: 最大带隙（用于搜索）
            is_stable: 是否稳定（用于搜索）
            limit: 返回结果数量限制（用于搜索）
            skip: 跳过的结果数量（用于搜索）
            fields: 要包含的数据字段列表（用于获取材料详情）
            
        Returns:
            JSON格式的API响应结果
        """
        try:
            # 获取工具实例
            tool = get_materials_project_tool()
            
            # 根据操作类型执行相应功能
            if action == "search":
                result = tool.search_materials(
                    formula=formula,
                    elements=elements,
                    exclude_elements=exclude_elements,
                    crystal_system=crystal_system,
                    band_gap_min=band_gap_min,
                    band_gap_max=band_gap_max,
                    is_stable=is_stable,
                    limit=limit,
                    skip=skip
                )
            elif action == "get_material":
                if not material_id:
                    return json.dumps({"error": "获取材料详情需要提供material_id"})
                result = tool.get_material_by_id(material_id)
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
                
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行操作时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
materials_project_tool = CrewAIMaterialsProjectTool()
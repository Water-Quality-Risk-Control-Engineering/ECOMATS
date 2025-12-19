import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.material_identifier_tool import get_material_identifier_tool
from src.utils.context_store import ContextStore

class MaterialIdentifierToolInput(BaseModel):
    """材料标识符工具输入参数模型 / Material Identifier Tool Input Model"""
    query: str = Field(description="材料查询字符串 / Material query string (formula, elements or name)")

class CrewAIMaterialIdentifierTool(BaseTool):
    """CrewAI工具包装器，用于材料标识符处理 / CrewAI tool wrapper for material identifier processing"""
    
    name: str = "Material Identifier Tool"
    description: str = (
        "统一处理金属材料和有机物的标识符（MP-ID和CAS号）。/ "
        "Process metal materials (MP-ID) and organic compounds (CAS number) identifiers. "
        "能够识别材料类型并获取相应的唯一标识符。/ "
        "Identify material type and get corresponding unique identifier. "
        "当需要确定材料的唯一标识符时使用此工具。/ "
        "Use when you need to determine the unique identifier of a material. "
        "✨ 此工具支持全局缓存。/ This tool supports global caching."
    )
    args_schema: type[BaseModel] = MaterialIdentifierToolInput
    
    def _run(self, query: str) -> str:
        """
        执行材料标识符识别，支持 ContextStore 缓存
        
        Args:
            query: 材料查询字符串（可以是化学式、元素组合或材料名称）
            
        Returns:
            JSON格式的识别结果
        """
        try:
            # 先从全局上下文查询缓存 / Check global context cache first
            cache_key = f"material_identifier:{query}"
            cached = ContextStore.get(cache_key)
            if cached is not None:
                # 返回缓存结果 / Return cached result
                return json.dumps(cached, ensure_ascii=False, indent=2)
            
            # 获取工具实例 / Get tool instance
            tool = get_material_identifier_tool()
            
            # 执行材料识别 / Execute material identification
            result = tool.identify_material(query)
            
            # 写入全局缓存 / Write to global cache
            ContextStore.set(cache_key, result)
            
            # 也写入通用键以供其他 Agent 复用 / Also write to generic key for other Agents
            ContextStore.set("material_identifier", result)
            
            # 返回JSON格式的结果 / Return JSON result
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行材料识别时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
material_identifier_tool = CrewAIMaterialIdentifierTool()
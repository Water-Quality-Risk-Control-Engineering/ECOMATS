import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.structure_validator_tool import get_structure_validator_tool
from src.utils.context_store import ContextStore

class StructureValidatorToolInput(BaseModel):
    """结构验证工具输入参数模型 / Structure Validator Tool Input Model"""
    material_formula: str = Field(description="材料化学式 / Material chemical formula")

class CrewAIStructureValidatorTool(BaseTool):
    """CrewAI工具包装器，用于材料结构验证 / CrewAI tool wrapper for material structure validation"""
    
    name: str = "Material Structure Validator"
    description: str = (
        "验证材料结构是否真实存在。/ "
        "Validate whether material structure exists in reality. "
        "支持金属材料（使用Materials Project数据库）和有机化合物（使用PubChem数据库）的结构验证。/ "
        "Support metal materials (Materials Project) and organic compounds (PubChem) validation. "
        "当需要确认设计的材料结构在现实中是否存在时使用此工具。/ "
        "Use when you need to confirm if designed material structure exists. "
        "✨ 此工具支持全局缓存。/ This tool supports global caching."
    )
    args_schema: type[BaseModel] = StructureValidatorToolInput
    
    def _run(
        self,
        material_formula: str
    ) -> str:
        """
        执行材料结构验证，支持 ContextStore 缓存
        
        Args:
            material_formula: 材料化学式
            
        Returns:
            JSON格式的验证结果
        """
        try:
            # 先从全局上下文查询缓存 / Check global context cache first
            cache_key = f"structure_validator:{material_formula}"
            cached = ContextStore.get(cache_key)
            if cached is not None:
                # 返回缓存结果 / Return cached result
                return json.dumps(cached, ensure_ascii=False, indent=2)
            
            # 获取工具实例 / Get tool instance
            tool = get_structure_validator_tool()
            
            # 执行验证 / Execute validation
            result = tool.validate_structure_exists(material_formula)
            
            # 写入全局缓存 / Write to global cache
            ContextStore.set(cache_key, result)
            
            # 也写入通用键以供其他 Agent 复用 / Also write to generic key for other Agents
            ContextStore.set("structure_validator", result)
                
            # 返回JSON格式的结果 / Return JSON result
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行验证时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
structure_validator_tool = CrewAIStructureValidatorTool()
import json
from typing import Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.structure_validator_tool import get_structure_validator_tool

class StructureValidatorToolInput(BaseModel):
    """结构验证工具输入参数模型"""
    material_formula: str = Field(description="材料化学式")

class CrewAIStructureValidatorTool(BaseTool):
    """CrewAI工具包装器，用于材料结构验证"""
    
    name: str = "Material Structure Validator"
    description: str = (
        "验证材料结构是否真实存在。"
        "支持金属材料（使用Materials Project数据库）和有机化合物（使用PubChem数据库）的结构验证。"
        "当需要确认设计的材料结构在现实中是否存在时使用此工具。"
    )
    args_schema: type[BaseModel] = StructureValidatorToolInput
    
    def _run(
        self,
        material_formula: str
    ) -> str:
        """
        执行材料结构验证
        
        Args:
            material_formula: 材料化学式
            
        Returns:
            JSON格式的验证结果
        """
        try:
            # 获取工具实例
            tool = get_structure_validator_tool()
            
            # 执行验证
            result = tool.validate_structure_exists(material_formula)
                
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行验证时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
structure_validator_tool = CrewAIStructureValidatorTool()
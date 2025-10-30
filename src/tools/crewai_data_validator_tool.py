import json
from typing import Optional, List, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.data_validator_tool import get_data_validator_tool

class DataValidatorToolInput(BaseModel):
    """Data Validator工具输入参数模型"""
    data: Dict[str, Any] = Field(description="要验证的数据字典")
    validation_type: str = Field(default="full", description="验证类型 ('full', 'cid', 'cas', 'formula', 'h_statements', 'molecular_weight', 'material_id')")

class CrewAIDataValidatorTool(BaseTool):
    """CrewAI工具包装器，用于验证化学品和材料数据"""
    
    name: str = "Data Validator"
    description: str = (
        "验证化学品和材料数据的真实性与有效性。"
        "可以验证CID、CAS号、分子式、分子量、危险声明等信息。"
        "当需要验证生成的化学品数据是否真实有效时使用此工具。"
    )
    args_schema: type[BaseModel] = DataValidatorToolInput
    
    def _run(
        self,
        data: Dict[str, Any],
        validation_type: str = "full"
    ) -> str:
        """
        执行数据验证
        
        Args:
            data: 要验证的数据字典
            validation_type: 验证类型 ("full", "cid", "cas", "formula", "h_statements", "molecular_weight", "material_id")
            
        Returns:
            JSON格式的验证结果
        """
        try:
            # 获取工具实例
            tool = get_data_validator_tool()
            
            # 根据验证类型执行相应验证
            if validation_type == "cid":
                if "pubchem_cid" in data:
                    result = tool.validate_cid(data["pubchem_cid"])
                else:
                    result = {"error": "数据中未找到pubchem_cid字段"}
            elif validation_type == "cas":
                if "cas_number" in data:
                    result = tool.validate_cas_number(data["cas_number"])
                else:
                    result = {"error": "数据中未找到cas_number字段"}
            elif validation_type == "formula":
                if "molecular_formula" in data:
                    result = tool.validate_molecular_formula(data["molecular_formula"])
                else:
                    result = {"error": "数据中未找到molecular_formula字段"}
            elif validation_type == "h_statements":
                if "hazard_statements" in data:
                    result = tool.validate_h_statements(data["hazard_statements"])
                else:
                    result = {"error": "数据中未找到hazard_statements字段"}
            elif validation_type == "molecular_weight":
                if "molecular_weight" in data:
                    result = tool.validate_molecular_weight(data["molecular_weight"])
                else:
                    result = {"error": "数据中未找到molecular_weight字段"}
            elif validation_type == "material_id":
                if "material_id" in data:
                    result = tool.validate_material_id(data["material_id"])
                else:
                    result = {"error": "数据中未找到material_id字段"}
            else:  # full validation
                result = tool.validate_chemical_data(data)
                
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行验证时出错: {str(e)}"}, ensure_ascii=False)

# 创建工具实例供智能体使用
data_validator_tool = CrewAIDataValidatorTool()
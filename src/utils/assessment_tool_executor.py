#!/usr/bin/env python3
"""
评估工具执行器
提供统一的工具调用逻辑，确保所有评估代理使用相同的工具调用流程
"""

import logging
from typing import Dict, Any, List, Optional

# 延迟导入以避免循环导入
def get_material_identifier_tool():
    from src.tools.material_identifier_tool import get_material_identifier_tool as _get_material_identifier_tool
    return _get_material_identifier_tool()

def get_structure_validator_tool():
    from src.tools.structure_validator_tool import get_structure_validator_tool as _get_structure_validator_tool
    return _get_structure_validator_tool()

def get_materials_project_tool():
    from src.tools.materials_project_tool import get_materials_project_tool as _get_materials_project_tool
    return _get_materials_project_tool()

def get_pubchem_tool():
    from src.tools.pubchem_tool import get_pubchem_tool as _get_pubchem_tool
    return _get_pubchem_tool()

def get_pnec_tool():
    from src.tools.pnec_tool import get_pnec_tool as _get_pnec_tool
    return _get_pnec_tool()

def get_data_validator_tool():
    from src.tools.data_validator_tool import get_data_validator_tool as _get_data_validator_tool
    return _get_data_validator_tool()

def get_material_search_tool():
    from src.tools.material_search_tool import get_material_search_tool as _get_material_search_tool
    return _get_material_search_tool()

from src.utils.tool_call_spec import ToolCallSpec

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentToolExecutor:
    """评估工具执行器类 - 提供统一的工具调用逻辑"""
    
    def __init__(self):
        """初始化评估工具执行器"""
        self.material_identifier_tool = get_material_identifier_tool()
        self.structure_validator_tool = get_structure_validator_tool()
        self.materials_project_tool = get_materials_project_tool()
        self.pubchem_tool = get_pubchem_tool()
        self.pnec_tool = get_pnec_tool()
        self.data_validator_tool = get_data_validator_tool()
        self.material_search_tool = get_material_search_tool()
    
    def execute_mandatory_tool_calls(self, material_formula: str) -> Dict[str, Any]:
        """
        执行评估代理的强制工具调用序列
        
        Args:
            material_formula (str): 材料化学式
            
        Returns:
            Dict[str, Any]: 所有工具调用的结果
        """
        results = {
            "material_identifier": None,
            "structure_validator": None,
            "materials_project": None,
            "pubchem": None,
            "pnec": None,
            "data_validator": None,
            "material_search": None,
            "errors": []
        }
        
        try:
            # 1. 材料标识符工具调用
            results["material_identifier"] = self.material_identifier_tool.identify_material(material_formula)
            
            # 2. 结构验证工具调用
            results["structure_validator"] = self.structure_validator_tool.validate_structure_exists(material_formula)
            
            # 3. 根据材料类型调用相应的数据库工具
            material_type = results["material_identifier"].get("material_type", "unknown")
            if material_type == "metal":
                results["materials_project"] = self.materials_project_tool.search_materials(formula=material_formula, limit=5)
            elif material_type == "organic":
                results["pubchem"] = self.pubchem_tool.search_compound(material_formula)
            
            # 4. 调用PNEC工具（环境风险评估）
            # 根据材料类型调用相应的PNEC查询方法
            if material_type == "organic":
                results["pnec"] = self.pnec_tool.get_pnec_by_name(material_formula)
            else:
                # 对于金属材料，我们可能需要提取元素符号来查询
                # 这里简化处理，直接使用名称查询
                results["pnec"] = self.pnec_tool.get_pnec_by_name(material_formula)
            
            # 5. 调用数据验证工具
            # 创建一个包含材料信息的数据字典用于验证
            material_data = {
                "molecular_formula": material_formula,
                "material_name": material_formula
            }
            results["data_validator"] = self.data_validator_tool.validate_chemical_data(material_data)
            
            # 6. 调用材料搜索工具
            results["material_search"] = self.material_search_tool.search_similar_materials(material_formula)
            
        except Exception as e:
            results["errors"].append(f"工具调用过程中出现错误: {str(e)}")
            logger.error(f"评估工具调用失败: {e}")
        
        return results
    
    def validate_tool_results(self, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证所有工具调用结果
        
        Args:
            tool_results (Dict[str, Any]): 工具调用结果
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        validation_result = {
            "all_valid": True,
            "validation_details": {},
            "errors": []
        }
        
        # 验证材料标识符结果
        if tool_results.get("material_identifier"):
            is_valid = ToolCallSpec.validate_material_identifier_result(tool_results["material_identifier"])
            validation_result["validation_details"]["material_identifier"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("材料标识符验证失败")
        
        # 验证结构验证结果
        if tool_results.get("structure_validator"):
            is_valid = ToolCallSpec.validate_structure_validator_result(tool_results["structure_validator"])
            validation_result["validation_details"]["structure_validator"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("结构验证失败")
        
        # 验证Materials Project结果
        if tool_results.get("materials_project"):
            is_valid = ToolCallSpec.validate_materials_project_result(tool_results["materials_project"])
            validation_result["validation_details"]["materials_project"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("Materials Project数据验证失败")
        
        # 验证PubChem结果
        if tool_results.get("pubchem"):
            is_valid = ToolCallSpec.validate_pubchem_result(tool_results["pubchem"])
            validation_result["validation_details"]["pubchem"] = is_valid
            if not is_valid:
                validation_result["all_valid"] = False
                validation_result["errors"].append("PubChem数据验证失败")
        
        return validation_result
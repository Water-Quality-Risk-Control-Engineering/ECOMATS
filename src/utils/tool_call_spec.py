#!/usr/bin/env python3
"""
工具调用规范模块
定义各Agent的工具调用规范和验证逻辑
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

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ToolCallSpec:
    """工具调用规范类"""
    
    @staticmethod
    def validate_material_identifier_result(result: Dict[str, Any]) -> bool:
        """
        验证材料标识符工具结果
        
        Args:
            result (Dict[str, Any]): 材料标识符工具返回的结果
            
        Returns:
            bool: 验证是否通过
        """
        if not isinstance(result, dict):
            return False
            
        # 检查必需字段
        required_fields = ["query", "material_type", "identifier", "identifier_type", "validation_status", "is_verified"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"材料标识符结果缺少必需字段: {field}")
                return False
        
        # 检查验证状态
        if result.get("is_verified", False) is not True:
            logger.warning(f"材料标识符未通过验证: {result.get('query', 'Unknown')}")
            return False
            
        return True
    
    @staticmethod
    def validate_structure_validator_result(result: Dict[str, Any]) -> bool:
        """
        验证结构验证工具结果
        
        Args:
            result (Dict[str, Any]): 结构验证工具返回的结果
            
        Returns:
            bool: 验证是否通过
        """
        if not isinstance(result, dict):
            return False
            
        # 检查必需字段
        required_fields = ["query", "valid", "type", "source", "reason", "validation_confidence"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"结构验证结果缺少必需字段: {field}")
                return False
        
        # 检查验证结果
        if result.get("valid", False) is not True:
            logger.warning(f"材料结构验证失败: {result.get('query', 'Unknown')}")
            return False
            
        # 检查置信度
        if result.get("validation_confidence", "low") != "high":
            logger.warning(f"材料结构验证置信度不足: {result.get('query', 'Unknown')}")
            return False
            
        return True
    
    @staticmethod
    def validate_materials_project_result(result: Dict[str, Any]) -> bool:
        """
        验证Materials Project工具结果
        
        Args:
            result (Dict[str, Any]): Materials Project工具返回的结果
            
        Returns:
            bool: 验证是否通过
        """
        if not isinstance(result, dict):
            return False
            
        # 检查是否有错误
        if "error" in result:
            logger.warning(f"Materials Project工具返回错误: {result['error']}")
            return False
            
        # 检查数据字段
        if "data" not in result:
            logger.warning("Materials Project结果缺少data字段")
            return False
            
        # 检查数据是否为空
        if not result["data"]:
            logger.warning("Materials Project返回空数据")
            return False
            
        return True
    
    @staticmethod
    def validate_pubchem_result(result: Dict[str, Any]) -> bool:
        """
        验证PubChem工具结果
        
        Args:
            result (Dict[str, Any]): PubChem工具返回的结果
            
        Returns:
            bool: 验证是否通过
        """
        if not isinstance(result, dict):
            return False
            
        # 检查是否有错误
        if "error" in result:
            logger.warning(f"PubChem工具返回错误: {result['error']}")
            return False
            
        # 检查PropertyTable字段
        if "PropertyTable" not in result:
            logger.warning("PubChem结果缺少PropertyTable字段")
            return False
            
        # 检查Properties字段
        if "Properties" not in result["PropertyTable"]:
            logger.warning("PubChem结果缺少Properties字段")
            return False
            
        # 检查Properties是否为空
        if not result["PropertyTable"]["Properties"]:
            logger.warning("PubChem返回空Properties数据")
            return False
            
        return True

class MaterialDesignerToolSpec(ToolCallSpec):
    """材料设计专家工具调用规范"""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        获取材料设计专家必需的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return [
            "Materials Project Tool",
            "PubChem Tool",
            "Material Identifier Tool",
            "Structure Validator Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        验证材料设计专家的工具调用
        
        Args:
            material_formula (str): 材料化学式
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # 调用材料标识符工具
            identifier_tool = get_material_identifier_tool()
            identifier_result = identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # 验证材料标识符结果
            if not ToolCallSpec.validate_material_identifier_result(identifier_result):
                result["validation_passed"] = False
                result["errors"].append("材料标识符验证失败")
            
            # 调用结构验证工具
            validator_tool = get_structure_validator_tool()
            validator_result = validator_tool.validate_structure_exists(material_formula)
            result["tool_calls"]["structure_validator"] = validator_result
            
            # 验证结构验证结果
            if not ToolCallSpec.validate_structure_validator_result(validator_result):
                result["validation_passed"] = False
                result["errors"].append("结构验证失败")
            
            # 根据材料类型调用相应的数据库工具
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                # 调用Materials Project工具
                mp_tool = get_materials_project_tool()
                mp_result = mp_tool.search_materials(formula=material_formula, limit=5)
                result["tool_calls"]["materials_project"] = mp_result
                
                # 验证Materials Project结果
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project数据验证失败")
            elif material_type == "organic":
                # 调用PubChem工具
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # 验证PubChem结果
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem数据验证失败")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"工具调用过程中出现错误: {str(e)}")
            logger.error(f"材料设计专家工具调用验证失败: {e}")
        
        return result

class AssessmentExpertToolSpec(ToolCallSpec):
    """评估专家工具调用规范"""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        获取评估专家必需的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return [
            "Materials Project Tool",
            "PubChem Tool",
            "Material Identifier Tool",
            "Structure Validator Tool",
            "PNEC Tool",
            "Data Validator Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        验证评估专家的工具调用
        
        Args:
            material_formula (str): 材料化学式
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # 调用材料标识符工具
            identifier_tool = get_material_identifier_tool()
            identifier_result = identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # 验证材料标识符结果
            if not ToolCallSpec.validate_material_identifier_result(identifier_result):
                result["validation_passed"] = False
                result["errors"].append("材料标识符验证失败")
            
            # 调用结构验证工具
            validator_tool = get_structure_validator_tool()
            validator_result = validator_tool.validate_structure_exists(material_formula)
            result["tool_calls"]["structure_validator"] = validator_result
            
            # 验证结构验证结果
            if not ToolCallSpec.validate_structure_validator_result(validator_result):
                result["validation_passed"] = False
                result["errors"].append("结构验证失败")
            
            # 根据材料类型调用相应的数据库工具
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                # 调用Materials Project工具
                mp_tool = get_materials_project_tool()
                mp_result = mp_tool.search_materials(formula=material_formula, limit=5)
                result["tool_calls"]["materials_project"] = mp_result
                
                # 验证Materials Project结果
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project数据验证失败")
            elif material_type == "organic":
                # 调用PubChem工具
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # 验证PubChem结果
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem数据验证失败")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"工具调用过程中出现错误: {str(e)}")
            logger.error(f"评估专家工具调用验证失败: {e}")
        
        return result

class FinalValidatorToolSpec(ToolCallSpec):
    """最终验证专家工具调用规范"""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        获取最终验证专家必需的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return [
            "Materials Project Tool",
            "PubChem Tool",
            "Material Identifier Tool",
            "Structure Validator Tool",
            "PNEC Tool",
            "Data Validator Tool",
            "Name2Properties Tool",
            "CID2Properties Tool",
            "Formula2Properties Tool",
            "Material Search Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        验证最终验证专家的工具调用
        
        Args:
            material_formula (str): 材料化学式
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # 调用材料标识符工具
            identifier_tool = get_material_identifier_tool()
            identifier_result = identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # 验证材料标识符结果
            if not ToolCallSpec.validate_material_identifier_result(identifier_result):
                result["validation_passed"] = False
                result["errors"].append("材料标识符验证失败")
            
            # 调用结构验证工具
            validator_tool = get_structure_validator_tool()
            validator_result = validator_tool.validate_structure_exists(material_formula)
            result["tool_calls"]["structure_validator"] = validator_result
            
            # 验证结构验证结果
            if not ToolCallSpec.validate_structure_validator_result(validator_result):
                result["validation_passed"] = False
                result["errors"].append("结构验证失败")
            
            # 根据材料类型调用相应的数据库工具
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                # 调用Materials Project工具
                mp_tool = get_materials_project_tool()
                mp_result = mp_tool.search_materials(formula=material_formula, limit=5)
                result["tool_calls"]["materials_project"] = mp_result
                
                # 验证Materials Project结果
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project数据验证失败")
            elif material_type == "organic":
                # 调用PubChem工具
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # 验证PubChem结果
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem数据验证失败")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"工具调用过程中出现错误: {str(e)}")
            logger.error(f"最终验证专家工具调用验证失败: {e}")
        
        return result

class MechanismExpertToolSpec(ToolCallSpec):
    """机理分析专家工具调用规范"""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        获取机理分析专家必需的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return [
            "Materials Project Tool",
            "PubChem Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(material_formula: str) -> Dict[str, Any]:
        """
        验证机理分析专家的工具调用
        
        Args:
            material_formula (str): 材料化学式
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "material_formula": material_formula,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # 调用材料标识符工具获取材料类型
            identifier_tool = get_material_identifier_tool()
            identifier_result = identifier_tool.identify_material(material_formula)
            result["tool_calls"]["material_identifier"] = identifier_result
            
            # 根据材料类型调用相应的数据库工具
            material_type = identifier_result.get("material_type", "unknown")
            if material_type == "metal":
                # 调用Materials Project工具
                mp_tool = get_materials_project_tool()
                mp_result = mp_tool.search_materials(formula=material_formula, limit=5)
                result["tool_calls"]["materials_project"] = mp_result
                
                # 验证Materials Project结果
                if not ToolCallSpec.validate_materials_project_result(mp_result):
                    result["validation_passed"] = False
                    result["errors"].append("Materials Project数据验证失败")
            elif material_type == "organic":
                # 调用PubChem工具
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(material_formula)
                result["tool_calls"]["pubchem"] = pubchem_result
                
                # 验证PubChem结果
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append("PubChem数据验证失败")
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"工具调用过程中出现错误: {str(e)}")
            logger.error(f"机理分析专家工具调用验证失败: {e}")
        
        return result

class SynthesisExpertToolSpec(ToolCallSpec):
    """合成指导专家工具调用规范"""
    
    @staticmethod
    def get_required_tools() -> List[str]:
        """
        获取合成指导专家必需的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return [
            "PubChem Tool",
            "Materials Project Tool",
            "Material Search Tool"
        ]
    
    @staticmethod
    def validate_tool_usage(chemical_reagents: List[str]) -> Dict[str, Any]:
        """
        验证合成指导专家的工具调用
        
        Args:
            chemical_reagents (List[str]): 化学试剂列表
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "chemical_reagents": chemical_reagents,
            "validation_passed": True,
            "errors": [],
            "tool_calls": {}
        }
        
        try:
            # 为每个化学试剂调用PubChem工具
            pubchem_results = []
            for reagent in chemical_reagents:
                pubchem_tool = get_pubchem_tool()
                pubchem_result = pubchem_tool.search_compound(reagent)
                pubchem_results.append({
                    "reagent": reagent,
                    "result": pubchem_result
                })
                
                # 验证PubChem结果
                if not ToolCallSpec.validate_pubchem_result(pubchem_result):
                    result["validation_passed"] = False
                    result["errors"].append(f"试剂 {reagent} 的PubChem数据验证失败")
            
            result["tool_calls"]["pubchem"] = pubchem_results
            
            # 如果有材料信息，也调用Materials Project工具
            # 这里简化处理，实际应用中可能需要更复杂的逻辑
            
        except Exception as e:
            result["validation_passed"] = False
            result["errors"].append(f"工具调用过程中出现错误: {str(e)}")
            logger.error(f"合成指导专家工具调用验证失败: {e}")
        
        return result
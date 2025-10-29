#!/usr/bin/env python3
"""
数据验证工具 / Data Validator Tool
用于验证化学品和材料数据的真实性与有效性
"""

import logging
import re
import time
from typing import Dict, Any, List, Union

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class DataValidatorTool:
    """数据验证工具类 / Data Validator Tool Class"""
    
    def __init__(self):
        """初始化数据验证工具 / Initialize data validator tool"""
        # 定义有效的化学元素符号
        self.valid_elements = [
            'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
            'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
            'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
            'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
            'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'
        ]
        
        # 定义有效的GHS危险声明代码
        self.valid_h_statements = [
            "H200", "H201", "H202", "H203", "H204", "H205", "H220", "H221", "H222", "H223", "H224", "H225", "H226", 
            "H228", "H240", "H241", "H242", "H250", "H251", "H252", "H260", "H261", "H270", "H271", "H272", "H280", 
            "H281", "H290", "H300", "H301", "H302", "H303", "H304", "H305", "H310", "H311", "H312", "H313", "H314", 
            "H315", "H316", "H317", "H318", "H319", "H320", "H330", "H331", "H332", "H333", "H334", "H335", "H336", 
            "H340", "H341", "H350", "H351", "H360", "H361", "H362", "H370", "H371", "H372", "H373", "H400", "H401", 
            "H402", "H410", "H411", "H412", "H413", "H420"
        ]
    
    def validate_cid(self, cid: Any) -> Dict[str, Any]:
        """
        验证PubChem CID是否有效
        
        Args:
            cid: 化合物ID
            
        Returns:
            验证结果字典
        """
        try:
            # CID应该是正整数
            if cid is None or cid == "" or cid == "N/A" or cid == "null":
                return {
                    "valid": False,
                    "reason": "CID为空或无效值",
                    "value": cid
                }
            cid_int = int(cid)
            if cid_int <= 0:
                return {
                    "valid": False,
                    "reason": "CID必须是正整数",
                    "value": cid
                }
            return {
                "valid": True,
                "reason": "CID有效",
                "value": cid_int
            }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "reason": "CID不是有效数字",
                "value": cid
            }
    
    def validate_material_id(self, material_id: Any) -> Dict[str, Any]:
        """
        验证Materials Project材料ID是否有效
        
        Args:
            material_id: 材料ID
            
        Returns:
            验证结果字典
        """
        try:
            # 材料ID应该是以"mp-"开头的字符串
            if material_id is None or material_id == "" or material_id == "N/A" or material_id == "null":
                return {
                    "valid": False,
                    "reason": "材料ID为空或无效值",
                    "value": material_id
                }
            material_id_str = str(material_id)
            if not material_id_str.startswith("mp-") or len(material_id_str) <= 3:
                return {
                    "valid": False,
                    "reason": "材料ID格式不正确，应以'mp-'开头",
                    "value": material_id
                }
            return {
                "valid": True,
                "reason": "材料ID有效",
                "value": material_id_str
            }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "reason": "材料ID不是有效字符串",
                "value": material_id
            }
    
    def validate_cas_number(self, cas_number: str) -> Dict[str, Any]:
        """
        验证CAS号格式是否正确
        
        Args:
            cas_number: CAS号
            
        Returns:
            验证结果字典
        """
        if not cas_number or cas_number == "N/A" or cas_number == "null":
            return {
                "valid": False,
                "reason": "CAS号为空或无效值",
                "value": cas_number
            }
        
        # CAS号格式：XXXXX-XX-X
        cas_pattern = r'^\d{2,7}-\d{2}-\d$'
        if re.match(cas_pattern, cas_number):
            return {
                "valid": True,
                "reason": "CAS号格式正确",
                "value": cas_number
            }
        else:
            return {
                "valid": False,
                "reason": "CAS号格式不正确，应为XXXXX-XX-X格式",
                "value": cas_number
            }
    
    def validate_molecular_formula(self, formula: str) -> Dict[str, Any]:
        """
        验证分子式是否有效
        
        Args:
            formula: 分子式
            
        Returns:
            验证结果字典
        """
        if not formula or formula == "N/A" or formula == "null":
            return {
                "valid": False,
                "reason": "分子式为空或无效值",
                "value": formula
            }
        
        # 简单的分子式验证（支持括号）
        formula_pattern = r'^([A-Z][a-z]?[0-9]*)+([A-Z][a-z]?[0-9]*)*$|^([A-Z][a-z]?[0-9]*)*\([A-Z][a-z]?[0-9]*\)[0-9]*([A-Z][a-z]?[0-9]*)*$'
        if re.match(formula_pattern, formula):
            # 提取元素符号并验证它们是否有效
            elements = re.findall(r'[A-Z][a-z]?', formula)
            invalid_elements = [e for e in elements if e not in self.valid_elements]
            if not invalid_elements:
                return {
                    "valid": True,
                    "reason": "分子式格式正确且元素有效",
                    "value": formula
                }
            else:
                return {
                    "valid": False,
                    "reason": f"分子式包含无效元素: {', '.join(invalid_elements)}",
                    "value": formula
                }
        else:
            return {
                "valid": False,
                "reason": "分子式格式不正确",
                "value": formula
            }
    
    def validate_h_statements(self, h_statements: List[str]) -> Dict[str, Any]:
        """
        验证GHS危险声明代码是否有效
        
        Args:
            h_statements: 危险声明代码列表
            
        Returns:
            验证结果字典
        """
        if not h_statements:
            return {
                "valid": True,
                "reason": "危险声明列表为空",
                "value": h_statements
            }
        
        invalid_statements = [h for h in h_statements if h not in self.valid_h_statements]
        if not invalid_statements:
            return {
                "valid": True,
                "reason": "所有危险声明代码都有效",
                "value": h_statements
            }
        else:
            return {
                "valid": False,
                "reason": f"包含无效的危险声明代码: {', '.join(invalid_statements)}",
                "value": h_statements,
                "invalid_statements": invalid_statements
            }
    
    def validate_molecular_weight(self, molecular_weight: Union[str, float]) -> Dict[str, Any]:
        """
        验证分子量是否有效
        
        Args:
            molecular_weight: 分子量
            
        Returns:
            验证结果字典
        """
        if molecular_weight == "N/A" or molecular_weight == "null" or molecular_weight is None:
            # 分子量可以为空
            return {
                "valid": True,
                "reason": "分子量为空（可接受）",
                "value": molecular_weight
            }
        
        try:
            mw = float(molecular_weight)
            if mw <= 0:
                return {
                    "valid": False,
                    "reason": "分子量必须是正数",
                    "value": molecular_weight
                }
            elif mw > 100000:  # 100,000 Da，一个合理的上限
                return {
                    "valid": False,
                    "reason": "分子量过大，可能不正确",
                    "value": molecular_weight
                }
            else:
                return {
                    "valid": True,
                    "reason": "分子量有效",
                    "value": mw
                }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "reason": "分子量不是有效数字",
                "value": molecular_weight
            }
    
    def validate_chemical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证化学品数据的完整性和有效性
        
        Args:
            data: 化学品数据字典
            
        Returns:
            验证结果字典
        """
        validation_results = {}
        overall_valid = True
        
        # 验证CID（如果存在）
        if "pubchem_cid" in data:
            cid_result = self.validate_cid(data["pubchem_cid"])
            validation_results["cid"] = cid_result
            if not cid_result["valid"]:
                overall_valid = False
        
        # 验证CAS号（如果存在）
        if "cas_number" in data:
            cas_result = self.validate_cas_number(data["cas_number"])
            validation_results["cas_number"] = cas_result
            if not cas_result["valid"]:
                overall_valid = False
        
        # 验证分子式（如果存在）
        if "molecular_formula" in data:
            formula_result = self.validate_molecular_formula(data["molecular_formula"])
            validation_results["molecular_formula"] = formula_result
            if not formula_result["valid"]:
                overall_valid = False
        
        # 验证分子量（如果存在）
        if "molecular_weight" in data:
            mw_result = self.validate_molecular_weight(data["molecular_weight"])
            validation_results["molecular_weight"] = mw_result
            if not mw_result["valid"]:
                overall_valid = False
        
        # 验证危险声明（如果存在）
        if "hazard_statements" in data and isinstance(data["hazard_statements"], list):
            h_result = self.validate_h_statements(data["hazard_statements"])
            validation_results["hazard_statements"] = h_result
            if not h_result["valid"]:
                overall_valid = False
        
        # 验证材料ID（如果存在）
        if "material_id" in data:
            material_id_result = self.validate_material_id(data["material_id"])
            validation_results["material_id"] = material_id_result
            if not material_id_result["valid"]:
                overall_valid = False
        
        return {
            "valid": overall_valid,
            "validation_results": validation_results,
            "timestamp": time.time(),
            "data": data
        }

# 全局实例
_data_validator_tool = None

def get_data_validator_tool() -> DataValidatorTool:
    """
    获取数据验证工具实例
    
    Returns:
        DataValidatorTool: 数据验证工具实例
    """
    global _data_validator_tool
    if _data_validator_tool is None:
        _data_validator_tool = DataValidatorTool()
    return _data_validator_tool
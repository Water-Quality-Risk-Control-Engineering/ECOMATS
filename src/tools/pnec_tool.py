#!/usr/bin/env python3
"""
PNEC工具 / PNEC Tool
PNEC (Predicted No Effect Concentration) 数据库查询工具 / PNEC (Predicted No Effect Concentration) database query tool
用于查询化学物质的预测无效应浓度数据 / Used to query predicted no effect concentration data of chemical substances
"""

import logging
import requests
import time
from typing import Dict, Any, List, Optional

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PNECTool:
    """PNEC工具类 - 查询化学物质的预测无效应浓度数据 / PNEC Tool Class - Query predicted no effect concentration data of chemical substances"""
    
    def __init__(self):
        """初始化PNEC工具 / Initialize PNEC tool"""
        # PNEC数据通常来自多个来源，这里我们模拟一个综合查询工具
        # PNEC data usually comes from multiple sources, here we simulate a comprehensive query tool
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ECOMATS-PNEC-Tool/1.0"
        })
        
        # PNEC相关参数的参考范围（用于模拟数据）
        # Reference range of PNEC-related parameters (used for simulated data)
        self.pnec_reference_data = {
            "toxicity_reference": {
                "acute_toxicity": "LC50, EC50, or similar",
                "chronic_toxicity": "NOEC, LOEC, or similar"
            },
            "assessment_factors": {
                "acute": 100,  # 急性毒性默认评估因子
                "chronic": 1000  # 慢性毒性默认评估因子
            }
        }
        
        # 常见金属元素及其价态对应的毒性数据
        # Common metal elements and their toxicity data corresponding to valence states
        self.metal_toxicity_data = {
            "Ni": {
                "valences": ["Ni²⁺"],
                "cas_numbers": ["7440-02-0"],
                "freshwater_pnec": {
                    "Ni²⁺": {"value": 0.02, "unit": "mg/L", "description": "Ni²⁺离子在淡水中的预测无效应浓度"}
                }
            },
            "W": {
                "valences": ["W⁶⁺"],
                "cas_numbers": ["7440-07-5"],
                "freshwater_pnec": {
                    "W⁶⁺": {"value": 0.1, "unit": "mg/L", "description": "W⁶⁺离子在淡水中的预测无效应浓度"}
                }
            },
            "Co": {
                "valences": ["Co²⁺"],
                "cas_numbers": ["7440-48-4"],
                "freshwater_pnec": {
                    "Co²⁺": {"value": 0.01, "unit": "mg/L", "description": "Co²⁺离子在淡水中的预测无效应浓度"}
                }
            },
            "Mo": {
                "valences": ["Mo⁶⁺"],
                "cas_numbers": ["7439-98-7"],
                "freshwater_pnec": {
                    "Mo⁶⁺": {"value": 0.05, "unit": "mg/L", "description": "Mo⁶⁺离子在淡水中的预测无效应浓度"}
                }
            },
            "Fe": {
                "valences": ["Fe²⁺", "Fe³⁺"],
                "cas_numbers": ["7439-89-6"],
                "freshwater_pnec": {
                    "Fe²⁺": {"value": 0.5, "unit": "mg/L", "description": "Fe²⁺离子在淡水中的预测无效应浓度"},
                    "Fe³⁺": {"value": 0.3, "unit": "mg/L", "description": "Fe³⁺离子在淡水中的预测无效应浓度"}
                }
            }
        }
    
    def get_pnec_by_cas(self, cas_number: str) -> Dict[str, Any]:
        """
        根据CAS号查询PNEC数据
        
        Args:
            cas_number (str): 化学物质的CAS号
            
        Returns:
            Dict[str, Any]: 包含PNEC数据的字典
        """
        try:
            # 首先通过CAS号获取化合物基本信息
            compound_info = self._get_compound_info_by_cas(cas_number)
            
            if "error" in compound_info:
                return {
                    "success": False,
                    "cas_number": cas_number,
                    "error": compound_info["error"]
                }
            
            # 分析化合物中金属元素的价态
            valence_analysis = self._analyze_element_valences(compound_info)
            
            # 模拟PNEC计算（在实际应用中，这需要连接到专门的PNEC数据库）
            pnec_data = self._calculate_pnec(compound_info)
            
            return {
                "success": True,
                "cas_number": cas_number,
                "compound_name": compound_info.get("name", ""),
                "molecular_formula": compound_info.get("molecular_formula", ""),
                "molecular_weight": compound_info.get("molecular_weight", ""),
                "valence_analysis": valence_analysis,
                "pnec_data": pnec_data
            }
            
        except Exception as e:
            logger.error(f"根据CAS号查询PNEC时出错: {e}")
            return {
                "success": False,
                "cas_number": cas_number,
                "error": f"查询失败: {str(e)}"
            }
    
    def get_pnec_by_name(self, compound_name: str) -> Dict[str, Any]:
        """
        根据化合物名称查询PNEC数据
        
        Args:
            compound_name (str): 化学物质名称
            
        Returns:
            Dict[str, Any]: 包含PNEC数据的字典
        """
        try:
            # 首先获取化合物的CAS号
            cas_result = self._get_cas_by_name(compound_name)
            
            if "error" in cas_result:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": cas_result["error"]
                }
            
            cas_number = cas_result.get("cas_number")
            if not cas_number:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": "无法获取化合物的CAS号"
                }
            
            # 然后通过CAS号查询PNEC数据
            return self.get_pnec_by_cas(cas_number)
            
        except Exception as e:
            logger.error(f"根据化合物名称查询PNEC时出错: {e}")
            return {
                "success": False,
                "compound_name": compound_name,
                "error": f"查询失败: {str(e)}"
            }
    
    def _get_compound_info_by_cas(self, cas_number: str) -> Dict[str, Any]:
        """
        根据CAS号获取化合物基本信息
        
        Args:
            cas_number (str): CAS号
            
        Returns:
            Dict[str, Any]: 化合物基本信息
        """
        try:
            # 使用PubChem API通过CAS号查询化合物
            url = f"{self.base_url}/compound/cid/{cas_number}/json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "PC_Compounds" in data and len(data["PC_Compounds"]) > 0:
                compound = data["PC_Compounds"][0]
                cid = compound["id"]["id"]
                
                # 获取更多详细信息
                details = self._get_compound_details(cid)
                # 添加CAS号到详细信息中
                details["cas_number"] = cas_number
                return details
            else:
                return {"error": "未找到该CAS号对应的化合物"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"PubChem API请求失败: {e}")
            return {"error": f"API请求失败: {str(e)}"}
        except Exception as e:
            logger.error(f"处理响应时出错: {e}")
            return {"error": f"处理响应时出错: {str(e)}"}
    
    def _get_cas_by_name(self, compound_name: str) -> Dict[str, Any]:
        """
        根据化合物名称获取CAS号
        
        Args:
            compound_name (str): 化合物名称
            
        Returns:
            Dict[str, Any]: 包含CAS号的信息
        """
        try:
            # 使用PubChem API通过名称查询化合物
            url = f"{self.base_url}/compound/name/{compound_name}/json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "PC_Compounds" in data and len(data["PC_Compounds"]) > 0:
                compound = data["PC_Compounds"][0]
                cid = compound["id"]["id"]
                
                # 获取CAS号
                details = self._get_compound_details(cid)
                return {
                    "cas_number": details.get("cas_number", ""),
                    "name": details.get("name", compound_name)
                }
            else:
                return {"error": "未找到该化合物名称对应的信息"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"PubChem API请求失败: {e}")
            return {"error": f"API请求失败: {str(e)}"}
        except Exception as e:
            logger.error(f"处理响应时出错: {e}")
            return {"error": f"处理响应时出错: {str(e)}"}
    
    def _get_compound_details(self, cid: str) -> Dict[str, Any]:
        """
        获取化合物详细信息
        
        Args:
            cid (str): PubChem化合物ID
            
        Returns:
            Dict[str, Any]: 化合物详细信息
        """
        try:
            # 查询化合物的详细属性
            url = f"{self.base_url}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES/JSON"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "PropertyTable" in data and "Properties" in data["PropertyTable"] and len(data["PropertyTable"]["Properties"]) > 0:
                properties = data["PropertyTable"]["Properties"][0]
                return {
                    "cid": cid,
                    "molecular_formula": properties.get("MolecularFormula", ""),
                    "molecular_weight": properties.get("MolecularWeight", ""),
                    "iupac_name": properties.get("IUPACName", ""),
                    "canonical_smiles": properties.get("CanonicalSMILES", ""),
                    "isomeric_smiles": properties.get("IsomericSMILES", "")
                }
            else:
                return {"error": "无法获取化合物详细信息"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"PubChem API请求失败: {e}")
            return {"error": f"API请求失败: {str(e)}"}
        except Exception as e:
            logger.error(f"处理响应时出错: {e}")
            return {"error": f"处理响应时出错: {str(e)}"}
    
    def _analyze_element_valences(self, compound_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析化合物中金属元素的价态信息
        
        Args:
            compound_info (Dict[str, Any]): 化合物信息
            
        Returns:
            Dict[str, Any]: 元素价态分析结果
        """
        try:
            # 获取化合物名称和化学式
            compound_name = compound_info.get("name", "")
            molecular_formula = compound_info.get("molecular_formula", "")
            
            # 从化合物信息中提取元素
            elements = self._extract_elements_from_formula(molecular_formula)
            
            # 分析金属元素的价态
            metal_valences = {}
            for element in elements:
                if element in self.metal_toxicity_data:
                    metal_info = self.metal_toxicity_data[element]
                    metal_valences[element] = {
                        "valences": metal_info["valences"],
                        "cas_numbers": metal_info["cas_numbers"],
                        "toxicity_data": metal_info["freshwater_pnec"]
                    }
            
            return {
                "success": True,
                "compound_name": compound_name,
                "molecular_formula": molecular_formula,
                "metal_elements": metal_valences
            }
            
        except Exception as e:
            logger.error(f"分析元素价态时出错: {e}")
            return {
                "success": False,
                "error": f"分析元素价态时出错: {str(e)}"
            }
    
    def _extract_elements_from_formula(self, formula: str) -> List[str]:
        """
        从化学式中提取元素符号
        
        Args:
            formula (str): 化学式
            
        Returns:
            List[str]: 元素符号列表
        """
        import re
        # 匹配常见的元素符号（1-2个字母，首字母大写）
        elements = re.findall(r'[A-Z][a-z]?', formula)
        # 过滤掉可能不是元素的字符串
        valid_elements = []
        # 常见元素列表（简化版）
        common_elements = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
                          'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
                          'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
                          'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
                          'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn']
        
        for element in elements:
            if element in common_elements:
                valid_elements.append(element)
        
        return list(set(valid_elements))  # 去重
    
    def _calculate_pnec(self, compound_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟PNEC计算（在实际应用中需要连接到专门的PNEC数据库）
        
        Args:
            compound_info (Dict[str, Any]): 化合物信息
            
        Returns:
            Dict[str, Any]: PNEC计算结果
        """
        # 这是一个简化的PNEC计算模型
        # This is a simplified PNEC calculation model
        # 在实际应用中，应该使用专业的PNEC数据库和计算方法
        # In actual applications, professional PNEC databases and calculation methods should be used
        
        molecular_weight = compound_info.get("molecular_weight", 0)
        try:
            mw = float(molecular_weight) if molecular_weight else 0
        except ValueError:
            mw = 0
        
        # 简化的PNEC计算（仅用于演示）
        # Simplified PNEC calculation (for demonstration purposes only)
        # 实际的PNEC计算需要考虑毒性数据、评估因子等多种因素
        # Actual PNEC calculation needs to consider toxicity data, assessment factors, and other factors
        if mw > 0:
            # 基于分子量的简化估算（仅用于演示，非真实计算）
            # Simplified estimation based on molecular weight (for demonstration purposes only, not real calculation)
            acute_pnec = 1000 / (mw ** 0.5)  # μg/L
            chronic_pnec = acute_pnec / 10  # 通常慢性毒性比急性毒性低一个数量级
        else:
            acute_pnec = 10.0  # 默认值
            chronic_pnec = 1.0  # 默认值
        
        return {
            "acute_pnec": {
                "value": round(acute_pnec, 3),
                "unit": "μg/L",
                "description": "基于急性毒性数据计算的预测无效应浓度",
                "assessment_factor": self.pnec_reference_data["assessment_factors"]["acute"]
            },
            "chronic_pnec": {
                "value": round(chronic_pnec, 3),
                "unit": "μg/L",
                "description": "基于慢性毒性数据计算的预测无效应浓度",
                "assessment_factor": self.pnec_reference_data["assessment_factors"]["chronic"]
            },
            "methodology": "简化估算方法（仅用于演示）",
            "note": "实际PNEC计算需要专业的毒性数据库和评估方法"
        }

# 全局实例
_pnec_tool = None

def get_pnec_tool() -> PNECTool:
    """
    获取PNEC工具实例
    
    Returns:
        PNECTool: PNEC工具实例
    """
    global _pnec_tool
    if _pnec_tool is None:
        _pnec_tool = PNECTool()
    return _pnec_tool
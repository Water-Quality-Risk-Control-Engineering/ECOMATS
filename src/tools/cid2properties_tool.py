#!/usr/bin/env python3
"""
CID2Properties工具
根据PubChem CID查询性质
"""

import logging
from typing import Dict, Any
from src.tools.pubchem_tool import get_pubchem_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class CID2PropertiesTool:
    """CID2Properties工具类 - 根据PubChem CID查询性质"""
    
    def __init__(self):
        """初始化CID2Properties工具"""
        self.pubchem_tool = get_pubchem_tool()
    
    def get_properties_by_cid(self, cid: str) -> Dict[str, Any]:
        """
        根据PubChem CID查询化合物性质
        
        Args:
            cid (str): PubChem化合物ID
            
        Returns:
            Dict[str, Any]: 包含化合物性质的字典
        """
        try:
            # 使用PubChem工具通过CID查询化合物信息
            result = self.pubchem_tool.get_properties_by_cid(int(cid))
            
            # 如果查询成功，整理返回结果
            if "error" not in result:
                # 提取属性数据
                if "PropertyTable" in result and "Properties" in result["PropertyTable"]:
                    properties = result["PropertyTable"]["Properties"][0]
                    return {
                        "success": True,
                        "cid": cid,
                        "molecular_formula": properties.get("MolecularFormula", "N/A"),
                        "molecular_weight": properties.get("MolecularWeight", "N/A"),
                        "iupac_name": properties.get("IUPACName", "N/A"),
                        "canonical_smiles": properties.get("CanonicalSMILES", "N/A"),
                        "isomeric_smiles": properties.get("IsomericSMILES", "N/A"),
                        "inchi": properties.get("InChI", "N/A"),
                        "inchi_key": properties.get("InChIKey", "N/A")
                    }
                else:
                    return {
                        "success": False,
                        "cid": cid,
                        "error": "无法解析返回数据"
                    }
            else:
                return {
                    "success": False,
                    "cid": cid,
                    "error": result.get("error", "查询失败")
                }
                
        except Exception as e:
            logger.error(f"根据CID查询化合物性质时出错: {e}")
            return {
                "success": False,
                "cid": cid,
                "error": f"查询失败: {str(e)}"
            }

# 全局实例
_cid2properties_tool = None

def get_cid2properties_tool() -> CID2PropertiesTool:
    """
    获取CID2Properties工具实例
    
    Returns:
        CID2PropertiesTool: CID2Properties工具实例
    """
    global _cid2properties_tool
    if _cid2properties_tool is None:
        _cid2properties_tool = CID2PropertiesTool()
    return _cid2properties_tool
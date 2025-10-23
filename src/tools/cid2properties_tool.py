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
            result = self.pubchem_tool.get_compound_info(cid)
            
            # 如果查询成功，整理返回结果
            if "error" not in result:
                return {
                    "success": True,
                    "cid": cid,
                    "molecular_formula": result.get("molecular_formula", ""),
                    "molecular_weight": result.get("molecular_weight", ""),
                    "iupac_name": result.get("iupac_name", ""),
                    "synonyms": result.get("synonyms", []),
                    "canonical_smiles": result.get("canonical_smiles", ""),
                    "isomeric_smiles": result.get("isomeric_smiles", ""),
                    "inchi": result.get("inchi", ""),
                    "inchi_key": result.get("inchi_key", ""),
                    "xlogp": result.get("xlogp", ""),
                    "hydrogen_bond_donor_count": result.get("hydrogen_bond_donor_count", ""),
                    "hydrogen_bond_acceptor_count": result.get("hydrogen_bond_acceptor_count", ""),
                    "rotatable_bond_count": result.get("rotatable_bond_count", ""),
                    "tpsa": result.get("tpsa", ""),  # 极性表面积
                    "complexity": result.get("complexity", "")
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
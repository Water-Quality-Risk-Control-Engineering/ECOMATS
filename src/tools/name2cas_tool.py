#!/usr/bin/env python3
"""
化合物名称转CAS号工具 / Compound Name to CAS Number Tool
通过PubChem API将化合物名称转换为CAS号 / Convert compound names to CAS numbers via PubChem API
"""

import logging
import requests
import time
from typing import Dict, Any, Optional

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class NameToCASTool:
    """化合物名称转CAS号工具类 / Compound Name to CAS Number Tool Class"""
    
    def __init__(self):
        """初始化NameToCAS工具 / Initialize NameToCAS tool"""
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ECOMATS-NameToCAS-Tool/1.0"
        })
    
    def _make_request(self, endpoint: str, timeout: int = 30) -> Dict[str, Any]:
        """
        发送API请求 / Send API request
        
        Args:
            endpoint: API端点 / API endpoint
            timeout: 超时时间（秒） / Timeout (seconds)
            
        Returns:
            API响应数据 / API response data
        """
        try:
            response = self.session.get(endpoint, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            return {"error": str(e)}
    
    def convert_name_to_cas(self, compound_name: str) -> Dict[str, Any]:
        """
        将化学名称转换为CAS号
        
        Args:
            compound_name (str): 化学名称
            
        Returns:
            Dict[str, Any]: 包含CAS号和其他相关信息的字典
        """
        try:
            # 使用PubChem API查询化合物信息
            endpoint = f"{self.base_url}/compound/name/{compound_name}/cids/JSON"
            result = self._make_request(endpoint)
            
            # 提取CAS号信息
            if "IdentifierList" in result and "CID" in result["IdentifierList"]:
                cids = result["IdentifierList"]["CID"]
                if isinstance(cids, list):
                    cid = cids[0]
                else:
                    cid = cids
                
                # 获取详细信息
                endpoint = f"{self.base_url}/compound/cid/{cid}/property/CAS,Formula,MolecularWeight,Synonyms/JSON"
                details = self._make_request(endpoint)
                
                if "PropertyTable" in details and "Properties" in details["PropertyTable"]:
                    properties = details["PropertyTable"]["Properties"][0]
                    return {
                        "success": True,
                        "compound_name": compound_name,
                        "cas_number": properties.get("CID", ""),
                        "molecular_formula": properties.get("MolecularFormula", ""),
                        "molecular_weight": properties.get("MolecularWeight", ""),
                        "synonyms": properties.get("Synonyms", [])
                    }
                else:
                    return {
                        "success": False,
                        "compound_name": compound_name,
                        "error": "未找到该化合物的详细信息",
                        "details": details.get("error", "未知错误")
                    }
            else:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": "未找到该化合物的CAS号信息",
                    "details": result.get("error", "未知错误")
                }
                
        except Exception as e:
            logger.error(f"转换化学名称到CAS号时出错: {e}")
            return {
                "success": False,
                "compound_name": compound_name,
                "error": f"转换失败: {str(e)}"
            }

# 全局实例
_name2cas_tool = None

def get_name2cas_tool() -> NameToCASTool:
    """
    获取Name2CAS工具实例
    
    Returns:
        Name2CASTool: Name2CAS工具实例
    """
    global _name2cas_tool
    if _name2cas_tool is None:
        _name2cas_tool = NameToCASTool()
    return _name2cas_tool
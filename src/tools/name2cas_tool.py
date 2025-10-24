#!/usr/bin/env python3
"""
化合物名称转CAS号工具 / Compound Name to CAS Number Tool
通过PubChem API将化合物名称转换为CAS号 / Convert compound names to CAS numbers via PubChem API
"""

import logging
import requests
import time
import random
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
    
    def _make_request(self, endpoint: str, timeout: int = 30, max_retries: int = 3) -> Dict[str, Any]:
        """
        发送API请求，带重试机制 / Send API request with retry mechanism
        
        Args:
            endpoint: API端点 / API endpoint
            timeout: 超时时间（秒） / Timeout (seconds)
            max_retries: 最大重试次数 / Maximum retry attempts
            
        Returns:
            API响应数据 / API response data
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(endpoint, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"API请求失败 (尝试 {attempt + 1}/{max_retries}): {e} / API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:  # 不是最后一次尝试
                    # 指数退避延迟
                    delay = (2 ** attempt) + (random.randint(0, 1000) / 1000)  # 1-2秒随机延迟
                    logger.info(f"等待 {delay:.2f} 秒后重试 / Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
                else:
                    logger.error(f"API请求最终失败: {e} / API request finally failed: {e}")
                    return {"error": str(e)}
    
    def convert_name_to_cas(self, compound_name: str) -> Dict[str, Any]:
        """
        将化学名称转换为CAS号 / Convert chemical name to CAS number
        
        Args:
            compound_name (str): 化学名称 / Chemical name
            
        Returns:
            Dict[str, Any]: 包含CAS号和其他相关信息的字典 / Dictionary containing CAS number and other related information
        """
        try:
            # 使用PubChem API查询化合物信息 / Query compound information using PubChem API
            endpoint = f"{self.base_url}/compound/name/{compound_name}/cids/JSON"
            result = self._make_request(endpoint)
            
            # 提取CAS号信息 / Extract CAS number information
            if "IdentifierList" in result and "CID" in result["IdentifierList"]:
                cids = result["IdentifierList"]["CID"]
                if isinstance(cids, list):
                    cid = cids[0]
                else:
                    cid = cids
                
                # 获取详细信息，包括CAS号 / Get detailed information, including CAS number
                endpoint = f"{self.base_url}/compound/cid/{cid}/property/CAS,IUPACName,Formula,MolecularWeight,Synonyms/JSON"
                details = self._make_request(endpoint)
                
                if "PropertyTable" in details and "Properties" in details["PropertyTable"]:
                    properties = details["PropertyTable"]["Properties"][0]
                    # 从Synonyms中提取CAS号 / Extract CAS number from Synonyms
                    synonyms = properties.get("Synonyms", [])
                    cas_numbers = [syn for syn in synonyms if self._is_cas_number(syn)]
                    cas_number = cas_numbers[0] if cas_numbers else "N/A"
                    
                    return {
                        "success": True,
                        "compound_name": compound_name,
                        "cid": cid,
                        "cas_number": cas_number,
                        "iupac_name": properties.get("IUPACName", ""),
                        "molecular_formula": properties.get("MolecularFormula", ""),
                        "molecular_weight": properties.get("MolecularWeight", ""),
                        "synonyms": synonyms
                    }
                else:
                    return {
                        "success": False,
                        "compound_name": compound_name,
                        "error": "未找到该化合物的详细信息 / Detailed information of the compound not found",
                        "details": details.get("error", "未知错误 / Unknown error")
                    }
            else:
                return {
                    "success": False,
                    "compound_name": compound_name,
                    "error": "未找到该化合物的CAS号信息 / CAS number information of the compound not found",
                    "details": result.get("error", "未知错误 / Unknown error")
                }
                
        except Exception as e:
            logger.error(f"转换化学名称到CAS号时出错: {e} / Error converting chemical name to CAS number: {e}")
            return {
                "success": False,
                "compound_name": compound_name,
                "error": f"转换失败: {str(e)} / Conversion failed: {str(e)}"
            }
    
    def _is_cas_number(self, text: str) -> bool:
        """
        判断文本是否为CAS号格式 / Determine if text is in CAS number format
        
        Args:
            text: 待判断文本 / Text to be judged
            
        Returns:
            是否为CAS号格式 / Whether it is in CAS number format
        """
        import re
        # CAS号格式：XXXXX-XX-X / CAS number format: XXXXX-XX-X
        cas_pattern = r'^\d{2,7}-\d{2}-\d$'
        return bool(re.match(cas_pattern, text))

# 全局实例 / Global instance
_name2cas_tool = None

def get_name2cas_tool() -> NameToCASTool:
    """
    获取Name2CAS工具实例 / Get Name2CAS tool instance
    
    Returns:
        Name2CASTool: Name2CAS工具实例 / Name2CAS tool instance
    """
    global _name2cas_tool
    if _name2cas_tool is None:
        _name2cas_tool = NameToCASTool()
    return _name2cas_tool
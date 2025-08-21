import requests
import logging
import time
from typing import Dict, List, Optional, Any

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PubChemTool:
    """PubChem数据库查询工具"""
    
    def __init__(self):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.session = requests.Session()
        # 设置请求头
        self.session.headers.update({
            "User-Agent": "ECOMATS-PubChem-Tool/1.0"
        })
    
    def _make_request(self, endpoint: str, timeout: int = 30) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            endpoint: API端点
            timeout: 超时时间（秒）
            
        Returns:
            API响应数据
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            logger.debug(f"请求PubChem API: {url}")
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PubChem API请求失败: {e}")
            return {"error": f"API请求失败: {str(e)}"}
        except Exception as e:
            logger.error(f"处理响应时出错: {e}")
            return {"error": f"处理响应时出错: {str(e)}"}
    
    def get_basic_properties_by_name(self, compound_name: str) -> Dict[str, Any]:
        """
        通过化学名称查询基础信息
        
        Args:
            compound_name: 化合物名称
            
        Returns:
            化合物基础信息
        """
        endpoint = f"compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON"
        return self._make_request(endpoint)
    
    def get_synonyms_with_cas(self, compound_name: str) -> Dict[str, Any]:
        """
        获取化合物同义词（包含CAS号）
        
        Args:
            compound_name: 化合物名称
            
        Returns:
            化合物同义词列表（包含CAS号）
        """
        endpoint = f"compound/name/{compound_name}/synonyms/JSON"
        return self._make_request(endpoint)
    
    def get_properties_by_cid(self, cid: int) -> Dict[str, Any]:
        """
        通过CID获取详细信息
        
        Args:
            cid: PubChem化合物ID
            
        Returns:
            化合物详细信息
        """
        endpoint = f"compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON"
        return self._make_request(endpoint)
    
    def search_by_molecular_formula(self, formula: str) -> Dict[str, Any]:
        """
        通过分子式搜索化合物
        
        Args:
            formula: 化学分子式
            
        Returns:
            化合物信息
        """
        endpoint = f"compound/fastformula/{formula}/property/MolecularWeight,IUPACName,CanonicalSMILES/JSON"
        return self._make_request(endpoint)
    
    def search_compound(self, query: str, search_type: str = "auto") -> Dict[str, Any]:
        """
        智能搜索化合物（自动判断查询类型）
        
        Args:
            query: 查询内容（化学名称或分子式）
            search_type: 查询类型 ("auto", "name", "formula")
            
        Returns:
            化合物信息
        """
        if search_type == "auto":
            # 简单判断：如果包含字母和数字的组合，可能是分子式
            if any(c.isalpha() for c in query) and any(c.isdigit() for c in query):
                # 可能是分子式，使用fastformula端点
                return self.search_by_molecular_formula(query)
            else:
                # 可能是化学名称，使用name端点
                return self.get_basic_properties_by_name(query)
        elif search_type == "name":
            return self.get_basic_properties_by_name(query)
        elif search_type == "formula":
            return self.search_by_molecular_formula(query)
        else:
            return {"error": f"不支持的搜索类型: {search_type}"}
    
    def get_compound_info_with_cas(self, query: str) -> Dict[str, Any]:
        """
        获取化合物完整信息（包括CAS号）
        
        Args:
            query: 化合物名称或分子式
            
        Returns:
            化合物完整信息
        """
        # 首先获取基本信息
        basic_info = self.search_compound(query)
        
        if "error" in basic_info:
            return basic_info
            
        try:
            # 提取CID
            if "PropertyTable" in basic_info and "Properties" in basic_info["PropertyTable"]:
                properties = basic_info["PropertyTable"]["Properties"]
                if properties and len(properties) > 0:
                    cid = properties[0].get("CID")
                    if cid:
                        # 获取同义词（包含CAS号）
                        synonyms_data = self.get_synonyms_with_cas(query)
                        cas_numbers = []
                        
                        if "InformationList" in synonyms_data and "Information" in synonyms_data["InformationList"]:
                            info_list = synonyms_data["InformationList"]["Information"]
                            if info_list and len(info_list) > 0:
                                synonyms = info_list[0].get("Synonym", [])
                                # 筛选出CAS号（格式：XXXXX-XX-X）
                                cas_numbers = [syn for syn in synonyms if self._is_cas_number(syn)]
                        
                        # 合并信息
                        result = properties[0].copy()
                        result["CASNumbers"] = cas_numbers
                        return {"Compound": result}
                        
            return basic_info
            
        except Exception as e:
            logger.error(f"获取完整化合物信息时出错: {e}")
            return {"error": f"获取完整化合物信息时出错: {str(e)}"}
    
    def _is_cas_number(self, text: str) -> bool:
        """
        判断文本是否为CAS号格式
        
        Args:
            text: 待判断文本
            
        Returns:
            是否为CAS号格式
        """
        import re
        # CAS号格式：XXXXX-XX-X
        cas_pattern = r'^\d{2,7}-\d{2}-\d$'
        return bool(re.match(cas_pattern, text))

# 创建全局实例
pubchem_tool = None

def get_pubchem_tool() -> PubChemTool:
    """
    获取PubChem工具实例
    
    Returns:
        PubChemTool: 工具实例
    """
    global pubchem_tool
    if pubchem_tool is None:
        pubchem_tool = PubChemTool()
    return pubchem_tool
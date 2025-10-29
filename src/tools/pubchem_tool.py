import requests
import logging
import time
import random
import os
from typing import Dict, Any

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PubChemTool:
    """PubChem数据库查询工具 / PubChem database query tool
    
    支持多种有机材料的查询和验证：
    1. 纯有机化合物
    2. 生物基材料
    3. 碳基材料（部分）
    4. 其他含有机成分的材料
    """
    
    def __init__(self, api_key: str = None):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.api_key = api_key or os.getenv('PUBCHEM_API_KEY')
        self.session = requests.Session()
        # 设置请求头 / Set request headers
        headers = {
            "User-Agent": "ECOMATS-PubChem-Tool/1.0"
        }
        # 如果有API密钥，添加到请求头 / Add API key to request headers if available
        if self.api_key:
            headers["X-PubChem-API-Key"] = self.api_key
        self.session.headers.update(headers)
        
        # 请求频率控制 / Request rate control
        self.last_request_time = 0
        self.min_request_interval = 0.3  # 最小请求间隔0.3秒 / Minimum request interval 0.3 seconds
    
    def _make_request(self, endpoint: str, timeout: int = 30, max_retries: int = 5) -> Dict[str, Any]:
        """
        发送API请求，带重试机制 / Send API request with retry mechanism
        
        Args:
            endpoint: API端点 / API endpoint
            timeout: 超时时间（秒） / Timeout (seconds)
            max_retries: 最大重试次数 / Maximum retry attempts
            
        Returns:
            API响应数据 / API response data
        """
        # 请求频率控制 / Request rate control
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/{endpoint}"
                logger.debug(f"请求PubChem API: {url}")
                
                # 更新最后请求时间 / Update last request time
                self.last_request_time = time.time()
                
                response = self.session.get(url, timeout=timeout)
                
                # 检查是否是503错误（服务器繁忙） / Check if it's a 503 error (server busy)
                if response.status_code == 503:
                    retry_after = int(response.headers.get('Retry-After', 30))
                    logger.warning(f"PubChem服务器繁忙，将在 {retry_after} 秒后重试 / PubChem server is busy, will retry after {retry_after} seconds")
                    if attempt < max_retries - 1:
                        logger.info(f"等待 {retry_after} 秒后重试 / Waiting {retry_after} seconds before retry")
                        time.sleep(retry_after)
                        continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"PubChem API请求失败 (尝试 {attempt + 1}/{max_retries}): {e} / PubChem API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:  # 不是最后一次尝试
                    # 指数退避延迟，增加基础延迟时间
                    delay = (3 ** attempt) + (random.randint(0, 2000) / 1000)  # 1-5秒随机延迟
                    logger.info(f"等待 {delay:.2f} 秒后重试 / Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
                else:
                    logger.error(f"PubChem API请求最终失败: {e} / PubChem API request finally failed: {e}")
                    return {"error": f"API请求失败: {str(e)}"}
            except Exception as e:
                logger.error(f"处理响应时出错: {e}")
                return {"error": f"处理响应时出错: {str(e)}"}
    
    def get_basic_properties_by_name(self, compound_name: str) -> Dict[str, Any]:
        """
        通过化学名称查询基础信息 / Query basic information by compound name
        
        Args:
            compound_name: 化合物名称 / Compound name
            
        Returns:
            化合物基础信息 / Compound basic information
        """
        endpoint = f"compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def get_synonyms_with_cas(self, compound_name: str) -> Dict[str, Any]:
        """
        获取化合物同义词（包含CAS号） / Get compound synonyms (including CAS numbers)
        
        Args:
            compound_name: 化合物名称 / Compound name
            
        Returns:
            化合物同义词列表（包含CAS号） / List of compound synonyms (including CAS numbers)
        """
        endpoint = f"compound/name/{compound_name}/synonyms/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def get_properties_by_cid(self, cid: int) -> Dict[str, Any]:
        """
        通过CID获取详细信息 / Get detailed information by CID
        
        Args:
            cid: PubChem化合物ID / PubChem compound ID
            
        Returns:
            化合物详细信息 / Compound detailed information
        """
        endpoint = f"compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def search_by_molecular_formula(self, formula: str) -> Dict[str, Any]:
        """
        通过分子式搜索化合物 / Search compound by molecular formula
        
        Args:
            formula: 化学分子式 / Chemical molecular formula
            
        Returns:
            化合物信息 / Compound information
        """
        endpoint = f"compound/fastformula/{formula}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def search_by_inchikey(self, inchikey: str) -> Dict[str, Any]:
        """
        通过InChIKey搜索化合物 / Search compound by InChIKey
        
        Args:
            inchikey: InChIKey标识符 / InChIKey identifier
            
        Returns:
            化合物信息 / Compound information
        """
        endpoint = f"compound/inchikey/{inchikey}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return self._make_request(endpoint, max_retries=3)
    
    def search_compound(self, query: str, search_type: str = "auto") -> Dict[str, Any]:
        """
        智能搜索化合物（自动判断查询类型） / Intelligent search compound (automatically determine search type)
        
        Args:
            query: 查询内容（化学名称、分子式或InChIKey） / Query content (compound name, molecular formula, or InChIKey)
            search_type: 查询类型 ("auto", "name", "formula", "inchikey") / Search type ("auto", "name", "formula", "inchikey")
            
        Returns:
            化合物信息 / Compound information
        """
        if search_type == "auto":
            # 检查是否为InChIKey格式 (通常为27个字符，包含连字符)
            if len(query) == 27 and query.count('-') >= 2:
                # 可能是InChIKey，使用inchikey端点
                return self.search_by_inchikey(query)
            # 检查是否为分子式格式 (包含元素符号和数字)
            elif self._is_molecular_formula(query):
                # 可能是分子式，使用fastformula端点
                return self.search_by_molecular_formula(query)
            else:
                # 可能是化学名称，使用name端点
                return self.get_basic_properties_by_name(query)
        elif search_type == "name":
            return self.get_basic_properties_by_name(query)
        elif search_type == "formula":
            return self.search_by_molecular_formula(query)
        elif search_type == "inchikey":
            return self.search_by_inchikey(query)
        else:
            return {"error": f"不支持的搜索类型: {search_type}"}
    
    def _is_molecular_formula(self, query: str) -> bool:
        """
        判断查询字符串是否可能是分子式 / Determine if query string is likely a molecular formula
        
        Args:
            query: 查询字符串 / Query string
            
        Returns:
            是否可能是分子式 / Whether it is likely a molecular formula
        """
        import re
        # 分子式通常由元素符号和数字组成，可能包含括号
        # 元素符号以大写字母开头，可能跟着小写字母
        # 例如: H2O, C6H6, C12H22O11, Ca(OH)2, NaCl
        # 更准确的正则表达式，支持多种格式
        formula_pattern = r'^([A-Z][a-z]?[0-9]*)+([A-Z][a-z]?[0-9]*)*$|^([A-Z][a-z]?[0-9]*)*\([A-Z][a-z]?[0-9]*\)[0-9]*([A-Z][a-z]?[0-9]*)*$'
        return bool(re.match(formula_pattern, query))
    
    def get_compound_info(self, query: str) -> Dict[str, Any]:
        """
        获取化合物完整信息 / Get complete compound information
        
        Args:
            query: 化合物名称、CID、分子式或InChIKey / Compound name, CID, molecular formula, or InChIKey
            
        Returns:
            化合物完整信息 / Complete compound information
        """
        try:
            # 使用智能搜索获取基本信息 / Use intelligent search to get basic information
            basic_info = self.search_compound(query)
            
            if "error" in basic_info:
                return basic_info
                
            try:
                # 提取CID / Extract CID
                if "PropertyTable" in basic_info and "Properties" in basic_info["PropertyTable"]:
                    properties = basic_info["PropertyTable"]["Properties"]
                    if properties and len(properties) > 0:
                        cid = properties[0].get("CID")
                        if cid:
                            # 获取详细信息 / Get detailed information
                            endpoint = f"compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES,InChI,InChIKey,MolecularFormula,MolecularWeight,IUPACName,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
                            details = self._make_request(endpoint, max_retries=3)
                            
                            if "PropertyTable" in details and "Properties" in details["PropertyTable"]:
                                detail_props = details["PropertyTable"]["Properties"][0]
                                
                                # 获取SMILES表示并验证有效性
                                canonical_smiles = detail_props.get("CanonicalSMILES", "N/A")
                                isomeric_smiles = detail_props.get("IsomericSMILES", "N/A")
                                
                                # 验证SMILES有效性（简单检查）
                                if canonical_smiles != "N/A" and self._is_valid_smiles(canonical_smiles):
                                    canonical_smiles_value = canonical_smiles
                                else:
                                    canonical_smiles_value = "N/A"
                                    
                                if isomeric_smiles != "N/A" and self._is_valid_smiles(isomeric_smiles):
                                    isomeric_smiles_value = isomeric_smiles
                                else:
                                    isomeric_smiles_value = "N/A"
                                
                                # 合并信息 / Merge information
                                result = properties[0].copy()
                                result.update({
                                    "canonical_smiles": canonical_smiles_value,
                                    "isomeric_smiles": isomeric_smiles_value,
                                    "inchi": detail_props.get("InChI", "N/A"),
                                    "inchi_key": detail_props.get("InChIKey", "N/A"),
                                    "molecular_formula": detail_props.get("MolecularFormula", "N/A"),
                                    "molecular_weight": detail_props.get("MolecularWeight", "N/A"),
                                    "iupac_name": detail_props.get("IUPACName", "N/A"),
                                    "xlogp": detail_props.get("XLogP", "N/A"),
                                    "hydrogen_bond_donor_count": detail_props.get("HBondDonorCount", "N/A"),
                                    "hydrogen_bond_acceptor_count": detail_props.get("HBondAcceptorCount", "N/A"),
                                    "rotatable_bond_count": detail_props.get("RotatableBondCount", "N/A"),
                                    "tpsa": detail_props.get("TPSA", "N/A"),  # 极性表面积
                                    "complexity": detail_props.get("Complexity", "N/A")
                                })
                                return {"Compound": result}
                            else:
                                return {"error": "无法获取化合物详细信息"}
                        else:
                            return {"error": "无法提取化合物CID"}
                    else:
                        return {"error": "未找到化合物属性信息"}
                else:
                    return basic_info
                    
            except Exception as e:
                logger.error(f"获取化合物详细信息时出错: {e}")
                return {"error": f"获取化合物详细信息时出错: {str(e)}"}
                
        except Exception as e:
            logger.error(f"获取完整化合物信息时出错: {e}")
            return {"error": f"获取完整化合物信息时出错: {str(e)}"}
    
    def _is_valid_smiles(self, smiles: str) -> bool:
        """
        简单验证SMILES字符串是否有效 / Simple validation of SMILES string
        
        Args:
            smiles: SMILES字符串 / SMILES string
            
        Returns:
            是否有效 / Whether it is valid
        """
        # 简单检查：确保不是明显的无效值
        invalid_patterns = ["#", "N/A", "None", "", "null", "NULL"]
        if any(pattern in smiles for pattern in invalid_patterns):
            return False
            
        # 确保包含至少一个字母
        if not any(c.isalpha() for c in smiles):
            return False
            
        # 检查是否包含有效的化学元素符号
        import re
        # 检查是否包含至少一个常见的化学元素符号
        common_elements = ['C', 'H', 'O', 'N', 'P', 'S', 'F', 'Cl', 'Br', 'I', 'B', 'Si']
        if not any(element in smiles for element in common_elements):
            return False
            
        return True
    
    def validate_cid(self, cid: Any) -> bool:
        """
        验证CID是否有效 / Validate if CID is valid
        
        Args:
            cid: 化合物ID / Compound ID
            
        Returns:
            CID是否有效 / Whether CID is valid
        """
        try:
            # CID应该是正整数
            if cid is None or cid == "" or cid == "N/A":
                return False
            cid_int = int(cid)
            return cid_int > 0
        except (ValueError, TypeError):
            return False
    
    def get_validated_compound_info(self, query: str) -> Dict[str, Any]:
        """
        获取经过验证的化合物信息 / Get validated compound information
        
        Args:
            query: 查询内容 / Query content
            
        Returns:
            经过验证的化合物信息 / Validated compound information
        """
        try:
            # 获取化合物信息
            compound_info = self.get_compound_info(query)
            
            # 检查是否有错误
            if "error" in compound_info:
                return compound_info
            
            # 验证CID
            if "Compound" in compound_info:
                compound = compound_info["Compound"]
                cid = compound.get("CID")
                if not self.validate_cid(cid):
                    return {
                        "success": False,
                        "query": query,
                        "error": f"无效的CID: {cid}"
                    }
                
                # 验证分子量
                molecular_weight = compound.get("MolecularWeight")
                if molecular_weight == "N/A" or molecular_weight is None:
                    # 这是可以接受的，某些化合物可能没有分子量信息
                    pass
                else:
                    try:
                        mw = float(molecular_weight)
                        if mw <= 0:
                            return {
                                "success": False,
                                "query": query,
                                "error": f"无效的分子量: {molecular_weight}"
                            }
                    except (ValueError, TypeError):
                        # 分子量不是数字，这可能是一个问题
                        pass
                
                # 添加验证标记
                compound_info["validated"] = True
                compound_info["validation_time"] = time.time()
            
            return compound_info
            
        except Exception as e:
            logger.error(f"验证化合物信息时出错: {e}")
            return {
                "success": False,
                "query": query,
                "error": f"验证失败: {str(e)}"
            }
    
    def get_compound_info_with_cas(self, query: str) -> Dict[str, Any]:
        """
        获取化合物完整信息（包括CAS号） / Get complete compound information (including CAS numbers)
        
        Args:
            query: 化合物名称或分子式 / Compound name or molecular formula
            
        Returns:
            化合物完整信息 / Complete compound information
        """
        # 首先获取基本信息 / First get basic information
        basic_info = self.search_compound(query)
        
        if "error" in basic_info:
            return basic_info
            
        try:
            # 提取CID / Extract CID
            if "PropertyTable" in basic_info and "Properties" in basic_info["PropertyTable"]:
                properties = basic_info["PropertyTable"]["Properties"]
                if properties and len(properties) > 0:
                    cid = properties[0].get("CID")
                    if cid:
                        # 获取同义词（包含CAS号） / Get synonyms (including CAS numbers)
                        synonyms_data = self.get_synonyms_with_cas(query)
                        cas_numbers = []
                        
                        if "InformationList" in synonyms_data and "Information" in synonyms_data["InformationList"]:
                            info_list = synonyms_data["InformationList"]["Information"]
                            if info_list and len(info_list) > 0:
                                synonyms = info_list[0].get("Synonym", [])
                                # 筛选出CAS号（格式：XXXXX-XX-X） / Filter out CAS numbers (format: XXXXX-XX-X)
                                cas_numbers = [syn for syn in synonyms if self._is_cas_number(syn)]
                        
                        # 合并信息 / Merge information
                        result = properties[0].copy()
                        result["CASNumbers"] = cas_numbers
                        return {"Compound": result}
                        
            return basic_info
            
        except Exception as e:
            logger.error(f"获取完整化合物信息时出错: {e}")
            return {"error": f"获取完整化合物信息时出错: {str(e)}"}
    
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

# 创建全局实例 / Create global instance
pubchem_tool = None

def get_pubchem_tool(api_key: str = None) -> PubChemTool:
    """
    获取PubChem工具实例 / Get PubChem tool instance
    
    Args:
        api_key (str, optional): PubChem API密钥 / PubChem API key
        
    Returns:
        PubChemTool: 工具实例 / Tool instance
    """
    global pubchem_tool
    if pubchem_tool is None:
        pubchem_tool = PubChemTool(api_key)
    return pubchem_tool
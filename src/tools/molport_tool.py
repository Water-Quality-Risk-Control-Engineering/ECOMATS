import requests
import logging
import time
import random
import os
from typing import Dict, Any, List, Optional

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MolPortTool:
    """MolPort数据库查询工具 / MolPort database query tool
    
    支持功能：
    1. 通过SMILES搜索化合物（精确、相似性、子结构等）
    2. 通过MolPort ID获取详细信息
    3. 获取供应商、库存和价格信息
    4. 评估化合物的商业可获得性
    """
    
    # 搜索类型常量 / Search type constants
    SEARCH_TYPE_EXACT = 3
    SEARCH_TYPE_SIMILARITY = 4
    SEARCH_TYPE_SUBSTRUCTURE = 1
    SEARCH_TYPE_SUPERSTRUCTURE = 2
    SEARCH_TYPE_PERFECT = 5
    SEARCH_TYPE_EXACT_FRAGMENT = 6
    
    def __init__(self, api_key: str = None):
        """
        初始化MolPort工具 / Initialize MolPort tool
        
        Args:
            api_key: MolPort API密钥，如果不提供则从环境变量读取 / MolPort API key
        """
        self.base_url = "https://api.molport.com/api"
        self.api_key = api_key or os.getenv('MOLPORT_API_KEY', '')
        self.session = requests.Session()
        
        # 设置请求头 / Set request headers
        self.session.headers.update({
            "User-Agent": "ECOMATS-MolPort-Tool/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # 请求频率控制 / Request rate control
        self.last_request_time = 0
        self.min_request_interval = 1.0  # MolPort API限制较宽松
    
    def _make_get_request(self, endpoint: str, params: Dict = None, timeout: int = 30, max_retries: int = 3) -> Dict[str, Any]:
        """
        发送GET请求，带重试机制 / Send GET request with retry mechanism
        
        Args:
            endpoint: API端点 / API endpoint
            params: URL参数 / URL parameters
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
                logger.debug(f"请求MolPort API (GET): {url}")
                
                # 更新最后请求时间 / Update last request time
                self.last_request_time = time.time()
                
                response = self.session.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"MolPort API请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + (random.randint(0, 1000) / 1000)
                    logger.info(f"等待 {delay:.2f} 秒后重试")
                    time.sleep(delay)
                else:
                    logger.error(f"MolPort API请求最终失败: {e}")
                    return {"error": f"API请求失败: {str(e)}"}
            except Exception as e:
                logger.error(f"处理响应时出错: {e}")
                return {"error": f"处理响应时出错: {str(e)}"}
        
        return {"error": "请求失败"}
    
    def _make_post_request(self, endpoint: str, data: Dict = None, timeout: int = 60, max_retries: int = 3) -> Dict[str, Any]:
        """
        发送POST请求，带重试机制 / Send POST request with retry mechanism
        
        Args:
            endpoint: API端点 / API endpoint
            data: 请求体数据 / Request body data
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
                logger.debug(f"请求MolPort API (POST): {url}")
                
                # 更新最后请求时间 / Update last request time
                self.last_request_time = time.time()
                
                response = self.session.post(url, json=data, timeout=timeout)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"MolPort API请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + (random.randint(0, 1000) / 1000)
                    logger.info(f"等待 {delay:.2f} 秒后重试")
                    time.sleep(delay)
                else:
                    logger.error(f"MolPort API请求最终失败: {e}")
                    return {"error": f"API请求失败: {str(e)}"}
            except Exception as e:
                logger.error(f"处理响应时出错: {e}")
                return {"error": f"处理响应时出错: {str(e)}"}
        
        return {"error": "请求失败"}
    
    def load_molecule_by_id(self, molecule_id: str) -> Dict[str, Any]:
        """
        通过MolPort ID加载分子详细信息 / Load molecule details by MolPort ID
        
        Args:
            molecule_id: MolPort分子ID（如 "2325020" 或 "Molport-002-325-020"）
            
        Returns:
            分子详细信息，包括SMILES、供应商、价格、库存等
        """
        if not self.api_key:
            return {"error": "未配置MOLPORT_API_KEY，请在.env文件中设置"}
        
        # 移除可能的"Molport-"前缀，只保留数字
        if isinstance(molecule_id, str) and molecule_id.startswith("Molport-"):
            molecule_id = molecule_id.replace("Molport-", "").replace("-", "")
        
        endpoint = "molecule/load"
        params = {
            "molecule": molecule_id,
            "apikey": self.api_key
        }
        
        return self._make_get_request(endpoint, params=params)
    
    def search_by_smiles(
        self, 
        smiles: str, 
        search_type: int = None,
        similarity_index: float = 0.9,
        max_results: int = 100,
        max_search_time: int = 60000
    ) -> Dict[str, Any]:
        """
        通过SMILES进行化学结构搜索 / Search by SMILES structure
        
        Args:
            smiles: SMILES字符串 / SMILES string
            search_type: 搜索类型（1-6），默认为4（相似性搜索）
            similarity_index: 相似度阈值（0-1），仅用于相似性搜索
            max_results: 最大返回结果数（最大10000）
            max_search_time: 最大搜索时间（毫秒）
            
        Returns:
            搜索结果列表，包含匹配的分子ID、SMILES和相似度指数
        """
        if not self.api_key:
            return {"error": "未配置MOLPORT_API_KEY，请在.env文件中设置"}
        
        if search_type is None:
            search_type = self.SEARCH_TYPE_SIMILARITY
        
        # 验证参数 / Validate parameters
        if max_results > 10000:
            max_results = 10000
        if similarity_index < 0 or similarity_index > 1:
            similarity_index = 0.9
        
        endpoint = "chemical-search/search"
        data = {
            "API Key": self.api_key,
            "Structure": smiles,
            "Search Type": search_type,
            "Maximum Result Count": max_results,
            "Maximum Search Time": max_search_time,
            "Chemical Similarity Index": similarity_index
        }
        
        return self._make_post_request(endpoint, data=data)
    
    def get_availability_info(self, molecule_id: str) -> Dict[str, Any]:
        """
        获取化合物的商业可获得性信息（简化版）/ Get commercial availability info
        
        Args:
            molecule_id: MolPort分子ID
            
        Returns:
            包含可获得性、供应商数量、价格范围等信息的字典
        """
        molecule_data = self.load_molecule_by_id(molecule_id)
        
        if "error" in molecule_data:
            return molecule_data
        
        try:
            data = molecule_data.get("Data", {}).get("Molecule", {})
            
            # 提取关键可获得性信息
            availability_info = {
                "molport_id": data.get("Molport Id", ""),
                "status": data.get("Status", ""),
                "type": data.get("Type", ""),
                "largest_stock": data.get("Largest Stock", ""),
                "largest_stock_measure": data.get("Largest Stock Measure", ""),
                "smiles": data.get("SMILES", ""),
                "iupac": data.get("IUPAC", ""),
                "formula": data.get("Formula", ""),
                "molecular_weight": data.get("Molecular Weight", ""),
                "supplier_count": 0,
                "min_price": None,
                "max_price": None,
                "currency": None
            }
            
            # 统计供应商和价格信息
            catalogues = data.get("Catalogues", {})
            all_suppliers = []
            
            for category in ["Screening Block Suppliers", "Building Block Suppliers", "Virtual Suppliers"]:
                suppliers = catalogues.get(category, [])
                all_suppliers.extend(suppliers)
            
            availability_info["supplier_count"] = len(all_suppliers)
            
            # 收集价格信息
            prices = []
            for supplier in all_suppliers:
                for catalogue in supplier.get("Catalogues", []):
                    for packing in catalogue.get("Available Packings", []):
                        price = packing.get("Price")
                        currency = packing.get("Currency")
                        if price is not None:
                            prices.append({
                                "price": price,
                                "currency": currency,
                                "amount": packing.get("Amount", ""),
                                "measure": packing.get("Measure", "")
                            })
            
            if prices:
                # 假设所有价格使用同一货币（通常是USD）
                availability_info["currency"] = prices[0]["currency"]
                price_values = [p["price"] for p in prices]
                availability_info["min_price"] = min(price_values)
                availability_info["max_price"] = max(price_values)
                availability_info["price_details"] = prices[:5]  # 只保留前5个价格信息
            
            return availability_info
            
        except Exception as e:
            logger.error(f"解析可获得性信息时出错: {e}")
            return {"error": f"解析数据失败: {str(e)}"}
    
    def check_compound_availability(self, smiles: str, similarity_threshold: float = 0.95) -> Dict[str, Any]:
        """
        检查化合物的商业可获得性（通过SMILES）/ Check compound commercial availability by SMILES
        
        Args:
            smiles: SMILES字符串
            similarity_threshold: 相似度阈值，用于判断是否为"可获得"
            
        Returns:
            可获得性评估结果
        """
        # 首先进行精确搜索
        exact_result = self.search_by_smiles(smiles, search_type=self.SEARCH_TYPE_EXACT, max_results=10)
        
        if "error" in exact_result:
            return exact_result
        
        result_data = exact_result.get("Data", {})
        molecules = result_data.get("Molecules", [])
        
        assessment = {
            "query_smiles": smiles,
            "exact_match_found": len(molecules) > 0,
            "match_count": len(molecules),
            "availability_status": "unknown",
            "best_match": None
        }
        
        if molecules:
            # 有精确匹配
            assessment["availability_status"] = "available"
            best_match = molecules[0]
            assessment["best_match"] = {
                "molport_id": best_match.get("Molport Id", ""),
                "smiles": best_match.get("SMILES", ""),
                "canonical_smiles": best_match.get("Canonical SMILES", ""),
                "verified_amount": best_match.get("Verified Amount", 0),
                "unverified_amount": best_match.get("Unverified Amount", 0)
            }
        else:
            # 尝试相似性搜索
            similar_result = self.search_by_smiles(
                smiles, 
                search_type=self.SEARCH_TYPE_SIMILARITY,
                similarity_index=similarity_threshold,
                max_results=10
            )
            
            if "error" not in similar_result:
                similar_molecules = similar_result.get("Data", {}).get("Molecules", [])
                if similar_molecules:
                    assessment["availability_status"] = "similar_available"
                    assessment["match_count"] = len(similar_molecules)
                    best_match = similar_molecules[0]
                    assessment["best_match"] = {
                        "molport_id": best_match.get("Molport Id", ""),
                        "smiles": best_match.get("SMILES", ""),
                        "canonical_smiles": best_match.get("Canonical SMILES", ""),
                        "similarity_index": best_match.get("Similarity Index", 0),
                        "verified_amount": best_match.get("Verified Amount", 0),
                        "unverified_amount": best_match.get("Unverified Amount", 0)
                    }
                else:
                    assessment["availability_status"] = "not_available"
        
        return assessment


# 单例模式 / Singleton pattern
_molport_tool_instance = None

def get_molport_tool(api_key: str = None) -> MolPortTool:
    """
    获取MolPort工具单例 / Get MolPort tool singleton
    
    Args:
        api_key: MolPort API密钥（可选）/ MolPort API key (optional)
        
    Returns:
        MolPortTool实例 / MolPortTool instance
    """
    global _molport_tool_instance
    if _molport_tool_instance is None:
        _molport_tool_instance = MolPortTool(api_key=api_key)
    return _molport_tool_instance

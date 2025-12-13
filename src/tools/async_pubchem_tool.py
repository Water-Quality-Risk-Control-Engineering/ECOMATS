"""
异步PubChem工具 - 支持CrewAI 1.7.0异步执行
Async PubChem Tool - Supports CrewAI 1.7.0 async execution
"""
import httpx
import logging
import asyncio
import time
import os
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class AsyncPubChemTool:
    """异步PubChem数据库查询工具
    
    相比同步版本的优势:
    - 支持并发查询多个化合物
    - 不阻塞事件循环
    - 与CrewAI 1.7.0异步API完全兼容
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.api_key = api_key or os.getenv('PUBCHEM_API_KEY')
        
        # 请求头
        self.headers = {
            "User-Agent": "ECOMATS-PubChem-Tool/2.0-Async"
        }
        if self.api_key:
            self.headers["X-PubChem-API-Key"] = self.api_key
        
        # 并发控制: 最多同时3个请求
        self.semaphore = asyncio.Semaphore(3)
        
        # 速率限制
        self.min_request_interval = 0.3  # 异步版本可以更快
        self.last_request_time = 0
        
    async def _rate_limit(self):
        """异步速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    async def _make_request(
        self, 
        endpoint: str, 
        timeout: int = 15, 
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """异步发送API请求，带并发控制和重试"""
        async with self.semaphore:  # 限制并发数
            await self._rate_limit()
            
            for attempt in range(max_retries):
                try:
                    url = f"{self.base_url}/{endpoint}"
                    logger.debug(f"异步请求PubChem API: {url}")
                    
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.get(url, headers=self.headers)
                        
                        # 处理503错误
                        if response.status_code == 503:
                            retry_after = int(response.headers.get('Retry-After', 10))
                            if attempt < max_retries - 1:
                                logger.warning(f"服务器繁忙，{retry_after}秒后重试")
                                await asyncio.sleep(retry_after)
                                continue
                        
                        response.raise_for_status()
                        return response.json()
                        
                except httpx.TimeoutException:
                    logger.warning(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        return {"error": "API请求超时"}
                        
                except httpx.HTTPStatusError as e:
                    logger.warning(f"HTTP错误 {e.response.status_code}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        return {"error": f"HTTP错误: {e.response.status_code}"}
                        
                except Exception as e:
                    logger.error(f"请求失败: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        return {"error": f"请求失败: {str(e)}"}
            
            return {"error": "达到最大重试次数"}
    
    async def get_basic_properties_by_name(self, compound_name: str) -> Dict[str, Any]:
        """异步查询基础信息"""
        endpoint = f"compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    async def get_properties_by_cid(self, cid: int) -> Dict[str, Any]:
        """异步获取CID详细信息"""
        endpoint = f"compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    async def search_by_molecular_formula(self, formula: str) -> Dict[str, Any]:
        """异步按分子式搜索"""
        endpoint = f"compound/fastformula/{formula}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    async def search_by_inchikey(self, inchikey: str) -> Dict[str, Any]:
        """异步按InChIKey搜索"""
        endpoint = f"compound/inchikey/{inchikey}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,Complexity/JSON"
        return await self._make_request(endpoint)
    
    def _is_molecular_formula(self, query: str) -> bool:
        """判断是否为分子式"""
        import re
        formula_pattern = r'^([A-Z][a-z]?[0-9]*)+([A-Z][a-z]?[0-9]*)*$|^([A-Z][a-z]?[0-9]*)*\([A-Z][a-z]?[0-9]*\)[0-9]*([A-Z][a-z]?[0-9]*)*$'
        return bool(re.match(formula_pattern, query))
    
    async def search_compound(
        self, 
        query: str, 
        search_type: str = "auto"
    ) -> Dict[str, Any]:
        """智能异步搜索"""
        if search_type == "auto":
            if len(query) == 27 and query.count('-') >= 2:
                return await self.search_by_inchikey(query)
            elif self._is_molecular_formula(query):
                return await self.search_by_molecular_formula(query)
            else:
                return await self.get_basic_properties_by_name(query)
        elif search_type == "name":
            return await self.get_basic_properties_by_name(query)
        elif search_type == "formula":
            return await self.search_by_molecular_formula(query)
        elif search_type == "inchikey":
            return await self.search_by_inchikey(query)
        else:
            return {"error": f"不支持的搜索类型: {search_type}"}
    
    async def get_compound_info(self, query: str) -> Dict[str, Any]:
        """异步获取完整化合物信息"""
        try:
            basic_info = await self.search_compound(query)
            
            if "error" in basic_info:
                return basic_info
            
            if "PropertyTable" in basic_info and "Properties" in basic_info["PropertyTable"]:
                properties = basic_info["PropertyTable"]["Properties"]
                if properties and len(properties) > 0:
                    cid = properties[0].get("CID")
                    if cid:
                        # 异步获取详细信息
                        details = await self.get_properties_by_cid(cid)
                        
                        if "PropertyTable" in details and "Properties" in details["PropertyTable"]:
                            detail_props = details["PropertyTable"]["Properties"][0]
                            
                            result = properties[0].copy()
                            result.update({
                                "canonical_smiles": detail_props.get("CanonicalSMILES", "N/A"),
                                "isomeric_smiles": detail_props.get("IsomericSMILES", "N/A"),
                                "inchi": detail_props.get("InChI", "N/A"),
                                "inchi_key": detail_props.get("InChIKey", "N/A"),
                                "molecular_formula": detail_props.get("MolecularFormula", "N/A"),
                                "molecular_weight": detail_props.get("MolecularWeight", "N/A"),
                                "iupac_name": detail_props.get("IUPACName", "N/A"),
                                "xlogp": detail_props.get("XLogP", "N/A"),
                                "hydrogen_bond_donor_count": detail_props.get("HBondDonorCount", "N/A"),
                                "hydrogen_bond_acceptor_count": detail_props.get("HBondAcceptorCount", "N/A"),
                                "rotatable_bond_count": detail_props.get("RotatableBondCount", "N/A"),
                                "tpsa": detail_props.get("TPSA", "N/A"),
                                "complexity": detail_props.get("Complexity", "N/A")
                            })
                            return {"Compound": result}
            
            return basic_info
            
        except Exception as e:
            logger.error(f"获取化合物信息失败: {e}")
            return {"error": f"获取化合物信息失败: {str(e)}"}
    
    async def batch_search(self, queries: list[str]) -> list[Dict[str, Any]]:
        """批量异步搜索 - 性能提升的关键!
        
        Args:
            queries: 化合物查询列表
            
        Returns:
            所有化合物信息列表
            
        示例:
            queries = ["benzene", "toluene", "xylene"]
            results = await tool.batch_search(queries)
            # 并发执行,速度比同步快3倍+
        """
        tasks = [self.get_compound_info(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "query": queries[i],
                    "error": f"查询失败: {str(result)}"
                })
            else:
                processed_results.append(result)
        
        return processed_results


# 全局实例
_async_pubchem_tool: Optional[AsyncPubChemTool] = None


def get_async_pubchem_tool(api_key: Optional[str] = None) -> AsyncPubChemTool:
    """获取异步PubChem工具单例"""
    global _async_pubchem_tool
    if _async_pubchem_tool is None:
        _async_pubchem_tool = AsyncPubChemTool(api_key)
    return _async_pubchem_tool


# CrewAI工具包装器
async def async_pubchem_search(compound_name: str) -> str:
    """CrewAI异步工具函数
    
    用法:
        from crewai import Tool
        
        pubchem_tool = Tool(
            name="PubChem异步搜索",
            func=async_pubchem_search,  # 直接传入异步函数
            description="异步查询PubChem化合物信息"
        )
    """
    tool = get_async_pubchem_tool()
    result = await tool.get_compound_info(compound_name)
    
    if "error" in result:
        return f"查询失败: {result['error']}"
    
    if "Compound" in result:
        compound = result["Compound"]
        return f"""化合物信息:
- CID: {compound.get('CID', 'N/A')}
- 分子式: {compound.get('molecular_formula', 'N/A')}
- 分子量: {compound.get('molecular_weight', 'N/A')}
- IUPAC名: {compound.get('iupac_name', 'N/A')}
- SMILES: {compound.get('canonical_smiles', 'N/A')}
- InChIKey: {compound.get('inchi_key', 'N/A')}
"""
    
    return "未找到化合物信息"

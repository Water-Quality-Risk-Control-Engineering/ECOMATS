"""
异步Materials Project工具 - 支持CrewAI 1.7.0
Async Materials Project Tool - Supports CrewAI 1.7.0

注意: mp-api本身不支持async,这里通过asyncio.to_thread实现非阻塞调用
"""
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    MP_API_AVAILABLE = False
    logger.warning("mp-api未安装")


class AsyncMaterialsProjectTool:
    """异步Materials Project工具
    
    虽然mp-api不支持async,但通过ThreadPoolExecutor实现非阻塞
    优势: 在CrewAI异步Crew中不会阻塞事件循环
    """
    
    def __init__(self, api_key: Optional[str] = None, max_workers: int = 3):
        if not MP_API_AVAILABLE:
            raise ImportError("请安装: pip install mp-api")
        
        self.api_key = api_key or os.getenv('MATERIALS_PROJECT_API_KEY')
        if not self.api_key:
            raise ValueError("未设置MATERIALS_PROJECT_API_KEY")
        
        # 使用线程池实现非阻塞
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.mpr = MPRester(self.api_key)
        
        # 简单缓存
        self._cache = {}
        self._cache_ttl = 600
    
    async def search_materials(
        self,
        formula: Optional[str] = None,
        elements: Optional[List[str]] = None,
        limit: int = 10,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """异步搜索材料"""
        
        # 在线程池中执行同步操作
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._sync_search,
            formula,
            elements,
            limit,
            fields
        )
        return result
    
    def _sync_search(
        self,
        formula: Optional[str],
        elements: Optional[List[str]],
        limit: int,
        fields: Optional[List[str]]
    ) -> Dict[str, Any]:
        """同步搜索(在线程池执行)"""
        try:
            kwargs = {}
            if formula:
                kwargs["formula"] = formula
            if elements:
                kwargs["elements"] = elements
            
            default_fields = ["material_id", "formula_pretty", "nsites"]
            fields = fields or default_fields
            
            docs = self.mpr.materials.search(
                **kwargs,
                num_chunks=1,
                chunk_size=min(limit, 50),
                fields=fields
            )
            
            if len(docs) > limit:
                docs = docs[:limit]
            
            materials_data = []
            for doc in docs:
                material_dict = {
                    "material_id": str(getattr(doc, "material_id", "N/A")),
                    "formula": getattr(doc, "formula_pretty", "N/A"),
                }
                
                # 添加额外字段
                if "nsites" in fields:
                    material_dict["nsites"] = getattr(doc, "nsites", "N/A")
                if "volume" in fields:
                    material_dict["volume"] = getattr(doc, "volume", "N/A")
                if "density" in fields:
                    material_dict["density"] = getattr(doc, "density", "N/A")
                
                materials_data.append(material_dict)
            
            return {
                "data": materials_data,
                "meta": {
                    "total_count": len(materials_data),
                    "limit": limit
                }
            }
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {"error": str(e)}
    
    async def get_material_by_id(self, material_id: str) -> Dict[str, Any]:
        """异步获取材料详情"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._sync_get_by_id,
            material_id
        )
        return result
    
    def _sync_get_by_id(self, material_id: str) -> Dict[str, Any]:
        """同步获取材料(在线程池执行)"""
        try:
            doc = self.mpr.materials.get_data_by_id(material_id)
            
            if not doc:
                return {"error": f"未找到材料: {material_id}"}
            
            return {
                "material_id": str(getattr(doc, "material_id", "N/A")),
                "formula": getattr(doc, "formula_pretty", "N/A"),
                "nsites": getattr(doc, "nsites", "N/A"),
                "volume": getattr(doc, "volume", "N/A"),
                "density": getattr(doc, "density", "N/A"),
            }
            
        except Exception as e:
            logger.error(f"获取材料失败: {e}")
            return {"error": str(e)}
    
    async def batch_search(
        self,
        queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量异步搜索
        
        Args:
            queries: [{"formula": "Fe2O3"}, {"elements": ["Cu", "O"]}, ...]
        
        Returns:
            所有搜索结果列表
        """
        tasks = []
        for query in queries:
            task = self.search_materials(
                formula=query.get("formula"),
                elements=query.get("elements"),
                limit=query.get("limit", 10)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "query": queries[i],
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# 全局单例
_async_mp_tool: Optional[AsyncMaterialsProjectTool] = None


def get_async_mp_tool(api_key: Optional[str] = None) -> AsyncMaterialsProjectTool:
    """获取异步MP工具单例"""
    global _async_mp_tool
    if _async_mp_tool is None:
        _async_mp_tool = AsyncMaterialsProjectTool(api_key)
    return _async_mp_tool


# CrewAI工具函数
async def async_mp_search(formula: str) -> str:
    """CrewAI异步搜索材料"""
    tool = get_async_mp_tool()
    result = await tool.search_materials(formula=formula, limit=5)
    
    if "error" in result:
        return f"搜索失败: {result['error']}"
    
    if "data" in result and result["data"]:
        materials = result["data"]
        output = f"找到 {len(materials)} 个材料:\n"
        for mat in materials[:5]:
            output += f"- {mat['material_id']}: {mat['formula']}\n"
        return output
    
    return "未找到材料"

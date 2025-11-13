#!/usr/bin/env python3
"""
Materials Project API 工具 / Materials Project API Tool
提供对Materials Project材料数据库的访问功能 / Provides access to Materials Project materials database
使用官方mp-api客户端 / Uses official mp-api client
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 添加调用间隔控制
_last_call_time = 0
_call_interval = 2.0  # 增加到2秒间隔，避免频繁调用
_max_retries = 3  # 最大重试次数

try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    # mp-api客户端未安装，Materials Project工具将不可用
    # mp-api client not installed, Materials Project tool will be unavailable
    MP_API_AVAILABLE = False
    logger.warning("mp-api客户端未安装，Materials Project工具将不可用 / mp-api client not installed, Materials Project tool will be unavailable")

class MaterialsProjectTool:
    """Materials Project API 工具类 / Materials Project API Tool Class
    
    支持多种无机材料的查询和验证：
    1. 纯金属材料
    2. 金属氧化物
    3. 金属硫化物
    4. 金属氮化物/碳化物
    5. MOF/COF材料
    6. 其他无机化合物
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Materials Project工具 / Initialize Materials Project tool
        
        Args:
            api_key (str, optional): Materials Project API密钥 / Materials Project API key
        """
        if not MP_API_AVAILABLE:
            raise ImportError("mp-api客户端未安装，请运行 'pip install mp-api'")
            
        self.api_key = api_key or os.getenv('MATERIALS_PROJECT_API_KEY')
        if not self.api_key:
            raise ValueError("Materials Project API密钥未设置")
            
        # 初始化MPRester客户端
        self.mpr = MPRester(self.api_key)
        self._cache = {
            "search": {},
            "search_norm": {},
            "by_id": {},
            "verify": {}
        }
        self._ttl_seconds = 600
    
    def search_materials(self, 
                        formula: Optional[str] = None,
                        elements: Optional[List[str]] = None,
                        exclude_elements: Optional[List[str]] = None,
                        crystal_system: Optional[str] = None,
                        limit: int = 100,
                        skip: int = 0,
                        fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        搜索材料 / Search materials
        
        Args:
            formula (str, optional): 化学式 / Chemical formula
            elements (List[str], optional): 必须包含的元素 / Required elements
            exclude_elements (List[str], optional): 要排除的元素 / Elements to exclude
            crystal_system (str, optional): 晶体系统 / Crystal system
            limit (int): 返回结果的最大数量 / Maximum number of results to return
            
        Returns:
            Dict: 材料搜索结果 / Material search results
        """
        try:
            # 添加调用间隔控制和重试机制
            global _last_call_time, _call_interval, _max_retries
            retries = 0
            
            while retries < _max_retries:
                try:
                    current_time = time.time()
                    time_since_last_call = current_time - _last_call_time
                    if time_since_last_call < _call_interval:
                        time.sleep(_call_interval - time_since_last_call)
                    _last_call_time = time.time()
                    
                    # 构建搜索参数
                    kwargs = {}
                    
                    if formula:
                        kwargs["formula"] = formula
                    if elements:
                        kwargs["elements"] = elements
                    if exclude_elements:
                        kwargs["exclude_elements"] = exclude_elements
                    if crystal_system:
                        kwargs["crystal_system"] = crystal_system
                        
                    chunk_size = min(limit, 50) if elements else min(limit, 100)  # 减少chunk_size
                    
                    default_fields = [
                        "material_id", 
                        "formula_pretty"
                    ]
                    fields = fields or default_fields
                    normalized_key = (
                        formula or "",
                        tuple(elements) if elements else (),
                        tuple(exclude_elements) if exclude_elements else (),
                        crystal_system or ""
                    )
                    # 优先尝试规范化缓存：忽略limit/skip，按需切片与字段子集
                    norm_entry = self._cache["search_norm"].get(normalized_key)
                    now = time.time()
                    if norm_entry and now - norm_entry["timestamp"] < self._ttl_seconds:
                        cached_materials = norm_entry["materials"]
                        cached_fields_set = norm_entry.get("fields_set", set())
                        requested_fields_set = set(fields)
                        if requested_fields_set.issubset(cached_fields_set) and len(cached_materials) >= (skip + limit):
                            slice_materials = cached_materials[skip:skip+limit]
                            # 根据请求字段返回子集
                            subset_list = []
                            for m in slice_materials:
                                subset = {k: v for k, v in m.items() if k in requested_fields_set or k in {"material_id", "formula"}}
                                # 确保存在formula字段
                                if "formula" not in subset and "formula" in m:
                                    subset["formula"] = m.get("formula")
                                subset_list.append(subset)
                            return {
                                "data": subset_list,
                                "meta": {
                                    "total_count": len(subset_list),
                                    "limit": limit
                                }
                            }
                    cache_key = (
                        formula or "",
                        tuple(elements) if elements else (),
                        tuple(exclude_elements) if exclude_elements else (),
                        crystal_system or "",
                        limit,
                        skip,
                        tuple(fields)
                    )
                    now = time.time()
                    cached = self._cache["search"].get(cache_key)
                    if cached and now - cached[0] < self._ttl_seconds:
                        return cached[1]
                    
                    # 执行搜索
                    docs = self.mpr.materials.search(
                        **kwargs,
                        num_chunks=1,
                        chunk_size=chunk_size,
                        fields=fields
                    )
                    
                    # 手动限制结果数量
                    if len(docs) > limit:
                        docs = docs[:limit]
                    
                    # 应用skip参数，跳过前skip个结果
                    if skip > 0:
                        docs = docs[skip:]
                    
                    # 转换为字典格式
                    materials_data = []
                    for doc in docs:
                        material_dict = {
                            "material_id": str(getattr(doc, "material_id", "N/A")),
                            "formula": getattr(doc, "formula_pretty", getattr(doc, "formula", "N/A")),
                            "chemsys": getattr(doc, "chemsys", "N/A")
                        }
                        if "volume" in fields:
                            volume_value = getattr(doc, "volume", "N/A")
                            material_dict["volume"] = f"{volume_value} Å³" if volume_value != "N/A" else "N/A"
                        if "density" in fields:
                            density_value = getattr(doc, "density", "N/A")
                            material_dict["density"] = f"{density_value} g/cm³" if density_value != "N/A" else "N/A"
                        if "nsites" in fields:
                            material_dict["nsites"] = getattr(doc, "nsites", "N/A")
                        materials_data.append(material_dict)
                    
                    result = {
                        "data": materials_data,
                        "meta": {
                            "total_count": len(materials_data),
                            "limit": limit
                        }
                    }
                    self._cache["search"][cache_key] = (time.time(), result)
                    # 更新规范化缓存：保存更大的列表与字段并供后续切片复用
                    prev = self._cache["search_norm"].get(normalized_key)
                    merged_list = materials_data
                    fields_set = set()
                    for item in merged_list:
                        fields_set.update(item.keys())
                    if prev and now - prev["timestamp"] < self._ttl_seconds:
                        # 若已有缓存，合并并取更大的结果集
                        if len(prev["materials"]) > len(merged_list):
                            merged_list = prev["materials"]
                            fields_set.update(prev.get("fields_set", set()))
                    self._cache["search_norm"][normalized_key] = {
                        "timestamp": time.time(),
                        "materials": merged_list,
                        "fields_set": fields_set
                    }
                    return result
                    
                except Exception as e:
                    retries += 1
                    if retries >= _max_retries:
                        logger.error(f"搜索材料时出错: {e}")
                        return {"error": f"搜索材料时出错: {str(e)}"}
                    else:
                        logger.warning(f"搜索材料时出错，正在重试 ({retries}/{_max_retries}): {e}")
                        time.sleep(_call_interval * retries)  # 指数退避
            
        except Exception as e:
            logger.error(f"搜索材料时出错: {e}")
            return {"error": f"搜索材料时出错: {str(e)}"}
    
    def get_material_by_id(self, material_id: str) -> Dict[str, Any]:
        """
        通过材料ID获取特定材料的详细信息
        
        Args:
            material_id (str): 材料唯一标识符
            
        Returns:
            Dict: 材料详细信息
        """
        try:
            # 验证material_id格式
            if not material_id or material_id == "N/A" or material_id == "":
                return {"error": f"无效的材料ID: {material_id}"}
            
            # 添加调用间隔控制和重试机制
            global _last_call_time, _call_interval, _max_retries
            retries = 0
            
            while retries < _max_retries:
                try:
                    now = time.time()
                    cached = self._cache["by_id"].get(material_id)
                    if cached and now - cached[0] < self._ttl_seconds:
                        return cached[1]
                    current_time = time.time()
                    time_since_last_call = current_time - _last_call_time
                    if time_since_last_call < _call_interval:
                        time.sleep(_call_interval - time_since_last_call)
                    _last_call_time = time.time()
                    
                    # 获取材料文档，限制只获取需要的字段
                    fields = [
                        "material_id", 
                        "formula_pretty", 
                        "chemsys", 
                        "volume", 
                        "density", 
                        "nsites",
                        "symmetry"
                    ]
                    
                    docs = self.mpr.materials.search(material_ids=[material_id], fields=fields)
                    
                    if not docs:
                        return {"error": f"未找到材料ID: {material_id}"}
                        
                    doc = docs[0]
                    
                    # 验证获取到的材料ID是否与查询的ID匹配
                    retrieved_material_id = str(getattr(doc, "material_id", ""))
                    if retrieved_material_id != material_id:
                        return {"error": f"材料ID不匹配: 查询 {material_id}, 获取到 {retrieved_material_id}"}
                    
                    # 提取关键信息并处理缺失值，确保所有值都能被JSON序列化
                    def safe_getattr(obj, attr, default="N/A"):
                        """安全获取属性值，确保能被JSON序列化"""
                        try:
                            value = getattr(obj, attr, default)
                            if value is None or value == "":
                                return default
                            # 转换为字符串以确保能被JSON序列化
                            return str(value)
                        except Exception:
                            return default
                    
                    def safe_get_nested_attr(obj, attr_chain, default="N/A"):
                        """安全获取嵌套属性值"""
                        try:
                            current = obj
                            for attr in attr_chain:
                                if current is None:
                                    return default
                                current = getattr(current, attr, None)
                            if current is None or current == "":
                                return default
                            return str(current)
                        except Exception:
                            return default
                    
                    # 为数值数据添加单位信息
                    volume_value = safe_getattr(doc, "volume", "N/A")
                    volume_with_unit = f"{volume_value} Å³" if volume_value != "N/A" else "N/A"
                    
                    density_value = safe_getattr(doc, "density", "N/A")
                    density_with_unit = f"{density_value} g/cm³" if density_value != "N/A" else "N/A"
                    
                    # 安全获取嵌套的晶体系统属性
                    crystal_system_value = safe_get_nested_attr(doc, ["symmetry", "crystal_system"], "N/A")
                    
                    material_info = {
                        "material_id": safe_getattr(doc, "material_id", "N/A"),
                        "formula": safe_getattr(doc, "formula_pretty", safe_getattr(doc, "formula", "N/A")),
                        "chemsys": safe_getattr(doc, "chemsys", "N/A"),
                        "volume": volume_with_unit,
                        "density": density_with_unit,
                        "nsites": safe_getattr(doc, "nsites", "N/A"),
                        "crystal_system": crystal_system_value,
                        "validated": True,
                        "validation_time": time.time()
                    }
                    self._cache["by_id"][material_id] = (time.time(), material_info)
                    return material_info
                    
                except Exception as e:
                    retries += 1
                    if retries >= _max_retries:
                        logger.error(f"获取材料详情时出错: {e}")
                        return {"error": f"获取材料详情时出错: {str(e)}"}
                    else:
                        logger.warning(f"获取材料详情时出错，正在重试 ({retries}/{_max_retries}): {e}")
                        time.sleep(_call_interval * retries)  # 指数退避
            
        except Exception as e:
            logger.error(f"获取材料详情时出错: {e}")
            return {"error": f"获取材料详情时出错: {str(e)}"}
    
    def validate_material_id(self, material_id: Any) -> bool:
        """
        验证材料ID是否有效
        
        Args:
            material_id: 材料ID
            
        Returns:
            材料ID是否有效
        """
        try:
            # 材料ID应该是以"mp-"开头的字符串
            if material_id is None or material_id == "" or material_id == "N/A":
                return False
            material_id_str = str(material_id)
            return material_id_str.startswith("mp-") and len(material_id_str) > 3
        except (ValueError, TypeError):
            return False
    
    def verify_material_id_exists(self, material_id: str) -> bool:
        """
        验证材料ID在Materials Project数据库中是否存在
        
        Args:
            material_id (str): 材料ID
            
        Returns:
            bool: 材料ID是否存在
        """
        try:
            if not self.validate_material_id(material_id):
                return False
            
            # 添加调用间隔控制
            global _last_call_time, _call_interval
            now = time.time()
            cached_by_id = self._cache["by_id"].get(material_id)
            if cached_by_id and now - cached_by_id[0] < self._ttl_seconds and isinstance(cached_by_id[1], dict) and not cached_by_id[1].get("error"):
                return True
            cached_verify = self._cache["verify"].get(material_id)
            if cached_verify and now - cached_verify[0] < self._ttl_seconds:
                return cached_verify[1]
            current_time = time.time()
            time_since_last_call = current_time - _last_call_time
            if time_since_last_call < _call_interval:
                time.sleep(_call_interval - time_since_last_call)
            _last_call_time = time.time()
            
            # 使用Materials Project API验证材料ID是否存在
            docs = self.mpr.materials.search(material_ids=[material_id], fields=["material_id"])
            
            # 如果返回了结果且第一个结果的material_id与查询的ID匹配，则材料存在
            if docs and len(docs) > 0:
                retrieved_material_id = str(getattr(docs[0], "material_id", ""))
                result = retrieved_material_id == material_id
                self._cache["verify"][material_id] = (time.time(), result)
                return result
            self._cache["verify"][material_id] = (time.time(), False)
            return False
        except Exception as e:
            logger.warning(f"验证材料ID时出错: {e}")
            return False
    
    def get_materials_summary(self, 
                             elements: Optional[List[str]] = None,
                             limit: int = 100) -> Dict[str, Any]:
        """
        获取材料摘要信息
        
        Args:
            elements (List[str], optional): 元素列表
            limit (int): 返回结果的最大数量
            
        Returns:
            Dict: 材料摘要信息
        """
        try:
            # 构建搜索参数
            kwargs = {}
            if elements:
                kwargs["elements"] = elements
                
            # 优化：只获取需要的字段以提高查询速度
            # 使用API支持的字段
            fields = [
                "material_id", 
                "formula_pretty", 
                "chemsys", 
                "density"
            ]
                
            # 执行搜索
            docs = self.mpr.materials.search(
                **kwargs,
                chunk_size=min(limit, 1000),
                fields=fields
            )
            
            # 转换为摘要格式
            materials_data = []
            for doc in docs:
                # 为数值数据添加单位信息
                density_value = getattr(doc, "density", "N/A")
                density_with_unit = f"{density_value} g/cm³" if density_value != "N/A" else "N/A"
                
                material_dict = {
                    "material_id": str(getattr(doc, "material_id", "N/A")),
                    "formula": getattr(doc, "formula_pretty", getattr(doc, "formula", "N/A")),
                    "chemsys": getattr(doc, "chemsys", "N/A"),
                    "density": density_with_unit
                }
                materials_data.append(material_dict)
            
            return {
                "data": materials_data,
                "meta": {
                    "total_count": len(materials_data),
                    "limit": limit
                }
            }
            
        except Exception as e:
            logger.error(f"获取材料摘要时出错: {e}")
            return {"error": f"获取材料摘要时出错: {str(e)}"}

# 创建全局实例
materials_project_tool = None

def get_materials_project_tool(api_key: Optional[str] = None) -> MaterialsProjectTool:
    """
    获取Materials Project工具实例
    
    Args:
        api_key (str, optional): Materials Project API密钥
        
    Returns:
        MaterialsProjectTool: 工具实例
    """
    global materials_project_tool
    if materials_project_tool is None:
        materials_project_tool = MaterialsProjectTool(api_key)
    return materials_project_tool

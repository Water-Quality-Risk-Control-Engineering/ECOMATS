#!/usr/bin/env python3
"""
Materials Project API 工具
提供对Materials Project材料数据库的访问功能
使用官方mp-api客户端
"""

import os
import logging
from typing import Dict, List, Optional, Any

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    MP_API_AVAILABLE = False
    logger.warning("mp-api客户端未安装，Materials Project工具将不可用")

class MaterialsProjectTool:
    """Materials Project API 工具类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Materials Project工具
        
        Args:
            api_key (str, optional): Materials Project API密钥
        """
        if not MP_API_AVAILABLE:
            raise ImportError("mp-api客户端未安装，请运行 'pip install mp-api'")
            
        self.api_key = api_key or os.getenv('MATERIALS_PROJECT_API_KEY')
        if not self.api_key:
            raise ValueError("Materials Project API密钥未设置")
            
        # 初始化MPRester客户端
        self.mpr = MPRester(self.api_key)
    
    def search_materials(self, 
                        formula: Optional[str] = None,
                        elements: Optional[List[str]] = None,
                        exclude_elements: Optional[List[str]] = None,
                        crystal_system: Optional[str] = None,
                        band_gap_min: Optional[float] = None,
                        band_gap_max: Optional[float] = None,
                        is_stable: Optional[bool] = None,
                        limit: int = 100,
                        skip: int = 0) -> Dict[str, Any]:
        """
        搜索材料
        
        Args:
            formula (str, optional): 要搜索的化学式
            elements (List[str], optional): 必须包含的元素
            exclude_elements (List[str], optional): 要排除的元素
            crystal_system (str, optional): 晶体系统
            band_gap_min (float, optional): 最小带隙
            band_gap_max (float, optional): 最大带隙
            is_stable (bool, optional): 热力学稳定性筛选
            limit (int): 返回结果的最大数量
            
        Returns:
            Dict: 材料搜索结果
        """
        try:
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
            # 注意：新版本API不直接支持band_gap_min和band_gap_max参数
            # 这些参数将在后处理中手动过滤
            # 注意：is_stable参数在新版本API中可能不被支持，暂时移除该过滤条件
            # 后处理中手动过滤稳定材料
                
            # 执行搜索
            docs = self.mpr.materials.search(
                **kwargs,
                chunk_size=min(limit, 1000)
            )
            
            # 后处理：手动过滤带隙范围
            if band_gap_min is not None or band_gap_max is not None:
                filtered_docs = []
                for doc in docs:
                    band_gap = getattr(doc, "band_gap", None)
                    if band_gap is not None:
                        # 检查是否在指定范围内
                        if band_gap_min is not None and band_gap < band_gap_min:
                            continue
                        if band_gap_max is not None and band_gap > band_gap_max:
                            continue
                        filtered_docs.append(doc)
                    else:
                        # 如果没有带隙信息，根据参数决定是否包含
                        if band_gap_min is None and band_gap_max is None:
                            filtered_docs.append(doc)
                docs = filtered_docs
            
            # 后处理：手动过滤稳定材料
            if is_stable is not None and is_stable:
                filtered_docs = []
                for doc in docs:
                    energy_above_hull = getattr(doc, "energy_above_hull", None)
                    if energy_above_hull is not None and energy_above_hull <= 0.05:
                        filtered_docs.append(doc)
                docs = filtered_docs
            
            # 应用skip参数，跳过前skip个结果
            if skip > 0:
                docs = docs[skip:]
            
            # 转换为字典格式
            materials_data = []
            for doc in docs:
                material_dict = {
                    "material_id": str(getattr(doc, "material_id", "")),
                    "formula": getattr(doc, "formula_pretty", getattr(doc, "formula", "")),
                    "chemsys": getattr(doc, "chemsys", ""),
                    "volume": getattr(doc, "volume", ""),
                    "density": getattr(doc, "density", ""),
                    "nsites": getattr(doc, "nsites", 0),
                    "band_gap": getattr(doc, "band_gap", None),
                    "energy_above_hull": getattr(doc, "energy_above_hull", None),
                    "formation_energy_per_atom": getattr(doc, "formation_energy_per_atom", None)
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
            # 获取材料文档
            docs = self.mpr.materials.search(material_ids=[material_id])
            
            if not docs:
                return {"error": f"未找到材料ID: {material_id}"}
                
            doc = docs[0]
            
            # 提取关键信息
            material_info = {
                "material_id": str(getattr(doc, "material_id", "")),
                "formula": getattr(doc, "formula_pretty", getattr(doc, "formula", "")),
                "chemsys": getattr(doc, "chemsys", ""),
                "volume": getattr(doc, "volume", ""),
                "density": getattr(doc, "density", ""),
                "nsites": getattr(doc, "nsites", 0),
                "band_gap": getattr(doc, "band_gap", None),
                "energy_above_hull": getattr(doc, "energy_above_hull", None),
                "formation_energy_per_atom": getattr(doc, "formation_energy_per_atom", None),
                "crystal_system": getattr(getattr(doc, "symmetry", None), "crystal_system", None) if hasattr(doc, "symmetry") else None
            }
            
            return material_info
            
        except Exception as e:
            logger.error(f"获取材料详情时出错: {e}")
            return {"error": f"获取材料详情时出错: {str(e)}"}
    
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
                
            # 执行搜索
            docs = self.mpr.materials.search(
                **kwargs,
                chunk_size=min(limit, 1000)
            )
            
            # 转换为摘要格式
            materials_data = []
            for doc in docs:
                material_dict = {
                    "material_id": str(getattr(doc, "material_id", "")),
                    "formula": getattr(doc, "formula_pretty", getattr(doc, "formula", "")),
                    "chemsys": getattr(doc, "chemsys", ""),
                    "density": getattr(doc, "density", ""),
                    "band_gap": getattr(doc, "band_gap", None)
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
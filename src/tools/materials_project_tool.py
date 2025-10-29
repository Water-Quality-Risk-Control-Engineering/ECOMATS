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
_call_interval = 1.0  # 1秒间隔

try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    # mp-api客户端未安装，Materials Project工具将不可用
    # mp-api client not installed, Materials Project tool will be unavailable
    MP_API_AVAILABLE = False
    logger.warning("mp-api客户端未安装，Materials Project工具将不可用 / mp-api client not installed, Materials Project tool will be unavailable")

class MaterialsProjectTool:
    """Materials Project API 工具类 / Materials Project API Tool Class"""
    
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
            band_gap_min (float, optional): 最小带隙（注意：当前API版本不支持此参数）
            band_gap_max (float, optional): 最大带隙（注意：当前API版本不支持此参数）
            is_stable (bool, optional): 热力学稳定性筛选（注意：当前API版本不支持此参数）
            limit (int): 返回结果的最大数量
            
        Returns:
            Dict: 材料搜索结果
        """
        try:
            # 添加调用间隔控制
            global _last_call_time, _call_interval
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
            # 注意：新版本API不直接支持band_gap_min和band_gap_max参数
            # 这些参数将在后处理中手动过滤
            # 注意：is_stable参数在新版本API中可能不被支持
            # 我们不使用energy_above_hull参数，因为它可能不被支持
                
            # 优化：限制搜索结果数量以避免超时
            # 对于元素搜索，使用更小的chunk_size
            chunk_size = min(limit, 100) if elements else min(limit, 1000)
            
            # 优化：只获取需要的字段以提高查询速度
            # 使用API支持的字段
            fields = [
                "material_id", 
                "formula_pretty", 
                "chemsys", 
                "volume", 
                "density", 
                "nsites", 
                "symmetry"
            ]
            
            # 执行搜索
            docs = self.mpr.materials.search(
                **kwargs,
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
                # 为数值数据添加单位信息
                volume_value = getattr(doc, "volume", "N/A")
                volume_with_unit = f"{volume_value} Å³" if volume_value != "N/A" else "N/A"
                
                density_value = getattr(doc, "density", "N/A")
                density_with_unit = f"{density_value} g/cm³" if density_value != "N/A" else "N/A"
                
                material_dict = {
                    "material_id": str(getattr(doc, "material_id", "N/A")),
                    "formula": getattr(doc, "formula_pretty", getattr(doc, "formula", "N/A")),
                    "chemsys": getattr(doc, "chemsys", "N/A"),
                    "volume": volume_with_unit,
                    "density": density_with_unit,
                    "nsites": getattr(doc, "nsites", "N/A")
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
            # 验证material_id格式
            if not material_id or material_id == "N/A" or material_id == "":
                return {"error": f"无效的材料ID: {material_id}"}
            
            # 添加调用间隔控制
            global _last_call_time, _call_interval
            current_time = time.time()
            time_since_last_call = current_time - _last_call_time
            if time_since_last_call < _call_interval:
                time.sleep(_call_interval - time_since_last_call)
            _last_call_time = time.time()
            
            # 获取材料文档
            docs = self.mpr.materials.search(material_ids=[material_id])
            
            if not docs:
                return {"error": f"未找到材料ID: {material_id}"}
                
            doc = docs[0]
            
            # 验证获取到的材料ID是否与查询的ID匹配
            retrieved_material_id = str(getattr(doc, "material_id", ""))
            if retrieved_material_id != material_id:
                return {"error": f"材料ID不匹配: 查询 {material_id}, 获取到 {retrieved_material_id}"}
            
            # 提取关键信息并处理缺失值
            band_gap = getattr(doc, "band_gap", None)
            band_gap_value = band_gap if band_gap is not None and band_gap != "" else "N/A"
            
            energy_above_hull = getattr(doc, "energy_above_hull", None)
            energy_above_hull_value = energy_above_hull if energy_above_hull is not None and energy_above_hull != "" else "N/A"
            
            formation_energy = getattr(doc, "formation_energy_per_atom", None)
            formation_energy_value = formation_energy if formation_energy is not None and formation_energy != "" else "N/A"
            
            # 为数值数据添加单位信息
            volume_value = getattr(doc, "volume", "N/A")
            volume_with_unit = f"{volume_value} Å³" if volume_value != "N/A" else "N/A"
            
            density_value = getattr(doc, "density", "N/A")
            density_with_unit = f"{density_value} g/cm³" if density_value != "N/A" else "N/A"
            
            band_gap_with_unit = f"{band_gap_value} eV" if band_gap_value != "N/A" else "N/A"
            energy_above_hull_with_unit = f"{energy_above_hull_value} eV/atom" if energy_above_hull_value != "N/A" else "N/A"
            formation_energy_with_unit = f"{formation_energy_value} eV/atom" if formation_energy_value != "N/A" else "N/A"
            
            material_info = {
                "material_id": str(getattr(doc, "material_id", "N/A")),
                "formula": getattr(doc, "formula_pretty", getattr(doc, "formula", "N/A")),
                "chemsys": getattr(doc, "chemsys", "N/A"),
                "volume": volume_with_unit,
                "density": density_with_unit,
                "nsites": getattr(doc, "nsites", "N/A"),
                "band_gap": band_gap_with_unit,
                "energy_above_hull": energy_above_hull_with_unit,
                "formation_energy_per_atom": formation_energy_with_unit,
                "crystal_system": getattr(getattr(doc, "symmetry", None), "crystal_system", "N/A") if hasattr(doc, "symmetry") else "N/A",
                "validated": True,
                "validation_time": time.time()
            }
            
            return material_info
            
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
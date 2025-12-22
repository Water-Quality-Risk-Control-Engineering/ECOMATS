#!/usr/bin/env python3
"""
Materials Project API Tool.
Provides access to Materials Project materials database.
Uses official mp-api client.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Add call interval control
_last_call_time = 0
_call_interval = 2.0  # Increased to 2 seconds interval to avoid frequent calls
_max_retries = 3  # Maximum retry attempts

try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    # mp-api client not installed, Materials Project tool will be unavailable
    MP_API_AVAILABLE = False
    logger.warning("mp-api client not installed, Materials Project tool will be unavailable")

class MaterialsProjectTool:
    """Materials Project API Tool Class.
    
    Supports querying and validation for various inorganic materials:
    1. Pure metal materials
    2. Metal oxides
    3. Metal sulfides
    4. Metal nitrides/carbides
    5. MOF/COF materials
    6. Other inorganic compounds
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Materials Project tool.
        
        Args:
            api_key (str, optional): Materials Project API key
        """
        if not MP_API_AVAILABLE:
            raise ImportError("mp-api client not installed, please run 'pip install mp-api'")
            
        self.api_key = api_key or os.getenv('MATERIALS_PROJECT_API_KEY')
        if not self.api_key:
            raise ValueError("Materials Project API key not set")
            
        # Initialize MPRester client
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
        Search materials.
        
        Args:
            formula (str, optional): Chemical formula
            elements (List[str], optional): Required elements
            exclude_elements (List[str], optional): Elements to exclude
            crystal_system (str, optional): Crystal system
            limit (int): Maximum number of results to return
            
        Returns:
            Dict: Material search results
        """
        try:
            # Add call interval control and retry mechanism
            global _last_call_time, _call_interval, _max_retries
            retries = 0
            
            while retries < _max_retries:
                try:
                    current_time = time.time()
                    time_since_last_call = current_time - _last_call_time
                    if time_since_last_call < _call_interval:
                        time.sleep(_call_interval - time_since_last_call)
                    _last_call_time = time.time()
                    
                    # Build search parameters
                    kwargs = {}
                    
                    if formula:
                        kwargs["formula"] = formula
                    if elements:
                        kwargs["elements"] = elements
                    if exclude_elements:
                        kwargs["exclude_elements"] = exclude_elements
                    if crystal_system:
                        kwargs["crystal_system"] = crystal_system
                        
                    chunk_size = min(limit, 50) if elements else min(limit, 100)  # Reduce chunk_size
                    
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
                    # Try normalized cache first: ignore limit/skip, slice and subset fields on demand
                    norm_entry = self._cache["search_norm"].get(normalized_key)
                    now = time.time()
                    if norm_entry and now - norm_entry["timestamp"] < self._ttl_seconds:
                        cached_materials = norm_entry["materials"]
                        cached_fields_set = norm_entry.get("fields_set", set())
                        requested_fields_set = set(fields)
                        if requested_fields_set.issubset(cached_fields_set) and len(cached_materials) >= (skip + limit):
                            slice_materials = cached_materials[skip:skip+limit]
                            # Return subset based on requested fields
                            subset_list = []
                            for m in slice_materials:
                                subset = {k: v for k, v in m.items() if k in requested_fields_set or k in {"material_id", "formula"}}
                                # Ensure formula field exists
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
                    
                    # Execute search
                    docs = self.mpr.materials.search(
                        **kwargs,
                        num_chunks=1,
                        chunk_size=chunk_size,
                        fields=fields
                    )
                    
                    # Manually limit result count
                    if len(docs) > limit:
                        docs = docs[:limit]
                    
                    # Apply skip parameter, skip first `skip` results
                    if skip > 0:
                        docs = docs[skip:]
                    
                    # Convert to dictionary format
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
                    # Update normalized cache: save larger list and fields for reuse in slicing
                    prev = self._cache["search_norm"].get(normalized_key)
                    merged_list = materials_data
                    fields_set = set()
                    for item in merged_list:
                        fields_set.update(item.keys())
                    if prev and now - prev["timestamp"] < self._ttl_seconds:
                        # If cache exists, merge and take larger result set
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
                        logger.error(f"Error searching materials: {e}")
                        return {"error": f"Error searching materials: {str(e)}"}
                    else:
                        logger.warning(f"Error searching materials, retrying ({retries}/{_max_retries}): {e}")
                        time.sleep(_call_interval * retries)  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Error searching materials: {e}")
            return {"error": f"Error searching materials: {str(e)}"}
    
    def get_material_by_id(self, material_id: str) -> Dict[str, Any]:
        """
        Get detailed info for a specific material by ID.
        
        Args:
            material_id (str): Material unique identifier
            
        Returns:
            Dict: Material detailed info
        """
        try:
            # Validate material_id format
            if not material_id or material_id == "N/A" or material_id == "":
                return {"error": f"Invalid material ID: {material_id}"}
            
            # Add call interval control and retry mechanism
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
                    
                    # Get material document, limit to only required fields
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
                        return {"error": f"Material ID not found: {material_id}"}
                        
                    doc = docs[0]
                    
                    # Verify retrieved material ID matches query ID
                    retrieved_material_id = str(getattr(doc, "material_id", ""))
                    if retrieved_material_id != material_id:
                        return {"error": f"Material ID mismatch: queried {material_id}, got {retrieved_material_id}"}
                    
                    # Extract key information and handle missing values, ensure all values are JSON serializable
                    def safe_getattr(obj, attr, default="N/A"):
                        """Safely get attribute value, ensure JSON serializable."""
                        try:
                            value = getattr(obj, attr, default)
                            if value is None or value == "":
                                return default
                            # Convert to string to ensure JSON serializable
                            return str(value)
                        except Exception:
                            return default
                    
                    def safe_get_nested_attr(obj, attr_chain, default="N/A"):
                        """Safely get nested attribute value."""
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
                    
                    # Add unit information for numerical data
                    volume_value = safe_getattr(doc, "volume", "N/A")
                    volume_with_unit = f"{volume_value} Å³" if volume_value != "N/A" else "N/A"
                    
                    density_value = safe_getattr(doc, "density", "N/A")
                    density_with_unit = f"{density_value} g/cm³" if density_value != "N/A" else "N/A"
                    
                    # Safely get nested crystal system attribute
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
                        logger.error(f"Error getting material details: {e}")
                        return {"error": f"Error getting material details: {str(e)}"}
                    else:
                        logger.warning(f"Error getting material details, retrying ({retries}/{_max_retries}): {e}")
                        time.sleep(_call_interval * retries)  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Error getting material details: {e}")
            return {"error": f"Error getting material details: {str(e)}"}
    
    def validate_material_id(self, material_id: Any) -> bool:
        """
        Validate if material ID is valid.
        
        Args:
            material_id: Material ID
            
        Returns:
            Whether material ID is valid
        """
        try:
            # Material ID should be a string starting with "mp-"
            if material_id is None or material_id == "" or material_id == "N/A":
                return False
            material_id_str = str(material_id)
            return material_id_str.startswith("mp-") and len(material_id_str) > 3
        except (ValueError, TypeError):
            return False
    
    def verify_material_id_exists(self, material_id: str) -> bool:
        """
        Verify if material ID exists in Materials Project database.
        
        Args:
            material_id (str): Material ID
            
        Returns:
            bool: Whether material ID exists
        """
        try:
            if not self.validate_material_id(material_id):
                return False
            
            # Add call interval control
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
            
            # Use Materials Project API to verify material ID existence
            docs = self.mpr.materials.search(material_ids=[material_id], fields=["material_id"])
            
            # If results returned and first result's material_id matches queried ID, material exists
            if docs and len(docs) > 0:
                retrieved_material_id = str(getattr(docs[0], "material_id", ""))
                result = retrieved_material_id == material_id
                self._cache["verify"][material_id] = (time.time(), result)
                return result
            self._cache["verify"][material_id] = (time.time(), False)
            return False
        except Exception as e:
            logger.warning(f"Error verifying material ID: {e}")
            return False
    
    def get_materials_summary(self, 
                             elements: Optional[List[str]] = None,
                             limit: int = 100) -> Dict[str, Any]:
        """
        Get material summary info.
        
        Args:
            elements (List[str], optional): Element list
            limit (int): Maximum number of results to return
            
        Returns:
            Dict: Material summary info
        """
        try:
            # Build search parameters
            kwargs = {}
            if elements:
                kwargs["elements"] = elements
                
            # Optimization: only get required fields to improve query speed
            # Use fields supported by API
            fields = [
                "material_id", 
                "formula_pretty", 
                "chemsys", 
                "density"
            ]
                
            # Execute search
            docs = self.mpr.materials.search(
                **kwargs,
                chunk_size=min(limit, 1000),
                fields=fields
            )
            
            # Convert to summary format
            materials_data = []
            for doc in docs:
                # Add unit information for numerical data
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
            logger.error(f"Error getting material summary: {e}")
            return {"error": f"Error getting material summary: {str(e)}"}

# Create global instance
materials_project_tool = None

def get_materials_project_tool(api_key: Optional[str] = None) -> MaterialsProjectTool:
    """
    Get Materials Project tool instance.
    
    Args:
        api_key (str, optional): Materials Project API key
        
    Returns:
        MaterialsProjectTool: Tool instance
    """
    global materials_project_tool
    if materials_project_tool is None:
        materials_project_tool = MaterialsProjectTool(api_key)
    return materials_project_tool

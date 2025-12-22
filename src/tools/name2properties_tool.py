#!/usr/bin/env python3
"""
Name to Properties Query Tool.
Query key physicochemical properties by material name.
"""

import json
import logging
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.materials_project_tool import get_materials_project_tool

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Name2PropertiesInput(BaseModel):
    """Name to Properties Query Tool Input Model"""
    name: str = Field(..., description="Material name")

class Name2PropertiesTool(BaseTool):
    """Name to Properties Query Tool"""
    
    name: str = "Name to Properties Query Tool"
    description: str = (
        "Query key physicochemical properties by material name. "
        "Input material name, returns property information."
    )
    args_schema: type[BaseModel] = Name2PropertiesInput
    
    def _run(self, name: str) -> str:
        """
        Query material properties by name.
        
        Args:
            name: Material name
            
        Returns:
            JSON formatted material property info
        """
        try:
            mp_tool = get_materials_project_tool()
            search_result = mp_tool.search_materials(formula=name, limit=5, fields=["material_id", "formula_pretty"])
            
            if "error" in search_result:
                return json.dumps({"error": search_result["error"]}, ensure_ascii=False)
            
            if not search_result.get("data"):
                return json.dumps({"error": f"No material found with name {name}"}, ensure_ascii=False)
            
            first_material = search_result["data"][0]
            material_id = first_material.get("material_id")
            
            if not material_id or material_id == "N/A":
                return json.dumps({"error": f"No valid material ID found for name {name}"}, ensure_ascii=False)
            
            detail_result = mp_tool.get_material_by_id(material_id)
            
            if "error" in detail_result:
                return json.dumps({"error": detail_result["error"]}, ensure_ascii=False)
            
            properties = {
                "name": name,
                "formula": detail_result.get("formula", "N/A"),
                "material_id": detail_result.get("material_id", "N/A"),
                "chemsys": detail_result.get("chemsys", "N/A"),
                "volume": detail_result.get("volume", "N/A"),
                "density": detail_result.get("density", "N/A"),
                "nsites": detail_result.get("nsites", "N/A"),
                "crystal_system": detail_result.get("crystal_system", "N/A")
            }
            
            return json.dumps(properties, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error querying properties for name {name}: {e}")
            return json.dumps({"error": f"Query error for name {name}: {str(e)}"}, ensure_ascii=False)

# Create tool instance
name2properties_tool = Name2PropertiesTool()

def get_name2properties_tool():
    """Get name to properties query tool instance"""
    return name2properties_tool

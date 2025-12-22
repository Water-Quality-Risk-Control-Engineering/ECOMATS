#!/usr/bin/env python3
"""
Formula to Properties Query Tool.
Query key physicochemical properties by material formula.
"""

import json
import logging
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.materials_project_tool import get_materials_project_tool

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Formula2PropertiesInput(BaseModel):
    """Formula to Properties Query Tool Input Model"""
    formula: str = Field(..., description="Chemical formula")

class Formula2PropertiesTool(BaseTool):
    """Formula to Properties Query Tool"""
    
    name: str = "Formula to Properties Query Tool"
    description: str = (
        "Query key physicochemical properties by material formula. "
        "Input formula, returns material property information."
    )
    args_schema: type[BaseModel] = Formula2PropertiesInput
    
    def _run(self, formula: str) -> str:
        """
        Query material properties by formula.
        
        Args:
            formula: Chemical formula
            
        Returns:
            JSON formatted material property info
        """
        try:
            mp_tool = get_materials_project_tool()
            search_result = mp_tool.search_materials(formula=formula, limit=5, fields=["material_id", "formula_pretty"])
            
            if "error" in search_result:
                return json.dumps({"error": search_result["error"]}, ensure_ascii=False)
            
            if not search_result.get("data"):
                return json.dumps({"error": f"No material found with formula {formula}"}, ensure_ascii=False)
            
            first_material = search_result["data"][0]
            material_id = first_material.get("material_id")
            
            if not material_id or material_id == "N/A":
                return json.dumps({"error": f"No valid material ID found for formula {formula}"}, ensure_ascii=False)
            
            detail_result = mp_tool.get_material_by_id(material_id)
            
            if "error" in detail_result:
                return json.dumps({"error": detail_result["error"]}, ensure_ascii=False)
            
            properties = {
                "formula": detail_result.get("formula", formula),
                "material_id": detail_result.get("material_id", "N/A"),
                "chemsys": detail_result.get("chemsys", "N/A"),
                "volume": detail_result.get("volume", "N/A"),
                "density": detail_result.get("density", "N/A"),
                "nsites": detail_result.get("nsites", "N/A"),
                "crystal_system": detail_result.get("crystal_system", "N/A")
            }
            
            return json.dumps(properties, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error querying properties for formula {formula}: {e}")
            return json.dumps({"error": f"Query error for formula {formula}: {str(e)}"}, ensure_ascii=False)

# Create tool instance
formula2properties_tool = Formula2PropertiesTool()

def get_formula2properties_tool():
    """Get formula to properties query tool instance"""
    return formula2properties_tool

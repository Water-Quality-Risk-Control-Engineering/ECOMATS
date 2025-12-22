#!/usr/bin/env python3
"""
Material Search Tool.
Search for materials with specific properties.
"""

import json
import logging
from typing import Optional, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.materials_project_tool import get_materials_project_tool

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MaterialSearchInput(BaseModel):
    """Material Search Tool Input Model"""
    query: str = Field(..., description="Search query: material type, formula or elements")
    limit: int = Field(default=10, description="Result limit")

class MaterialSearchTool(BaseTool):
    """Material Search Tool"""
    
    name: str = "Material Search Tool"
    description: str = (
        "Search for materials with specific properties. "
        "Search by material type, formula or element combination."
    )
    args_schema: type[BaseModel] = MaterialSearchInput
    
    def _run(self, query: str, limit: int = 10) -> str:
        """
        Search materials.
        
        Args:
            query: Search query
            limit: Result limit
            
        Returns:
            JSON formatted search results
        """
        try:
            mp_tool = get_materials_project_tool()
            materials = []
            
            # Try formula search first
            formula_result = mp_tool.search_materials(
                formula=query,
                limit=limit,
                fields=["material_id", "formula_pretty", "chemsys", "volume", "density", "nsites"]
            )
            
            if "error" not in formula_result and formula_result.get("data"):
                materials.extend(formula_result["data"])
            
            # If no results, try element search
            if not materials:
                elements = self._parse_elements(query)
                if elements:
                    element_result = mp_tool.search_materials(
                        elements=elements,
                        limit=limit,
                        fields=["material_id", "formula_pretty", "chemsys", "volume", "density", "nsites"]
                    )
                    if "error" not in element_result and element_result.get("data"):
                        materials.extend(element_result["data"])
            
            # Try element combination with "-" separator
            if not materials:
                if "-" in query:
                    element_list = [elem.strip() for elem in query.split("-") if elem.strip()]
                    if element_list:
                        combo_result = mp_tool.search_materials(
                            elements=element_list,
                            limit=limit,
                            fields=["material_id", "formula_pretty", "chemsys", "volume", "density", "nsites"]
                        )
                        if "error" not in combo_result and combo_result.get("data"):
                            materials.extend(combo_result["data"])
            
            if not materials:
                return json.dumps({
                    "query": query,
                    "results": [],
                    "message": f"No materials found matching '{query}'"
                }, ensure_ascii=False, indent=2)
            
            materials = materials[:limit]
            
            formatted_results = []
            for material in materials:
                formatted_material = {
                    "material_id": material.get("material_id", "N/A"),
                    "formula": material.get("formula", "N/A"),
                    "chemsys": material.get("chemsys", "N/A"),
                    "volume": material.get("volume", "N/A"),
                    "density": material.get("density", "N/A"),
                    "nsites": material.get("nsites", "N/A")
                }
                formatted_results.append(formatted_material)
            
            return json.dumps({
                "query": query,
                "results": formatted_results
            }, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error searching material '{query}': {e}")
            return json.dumps({"error": f"Search error for '{query}': {str(e)}"}, ensure_ascii=False)
    
    def _parse_elements(self, query: str) -> Optional[List[str]]:
        """
        Parse elements from query.
        
        Args:
            query: Query string
            
        Returns:
            Element list or None
        """
        elements = []
        import re
        element_chars = re.findall(r'[A-Z][a-z]?', query)
        
        valid_elements = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
                         "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
                         "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe"]
        
        for element in element_chars:
            if element in valid_elements:
                elements.append(element)
        
        return elements if elements else None

# Create tool instance
material_search_tool = MaterialSearchTool()

def get_material_search_tool():
    """Get material search tool instance"""
    return material_search_tool

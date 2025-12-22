"""
CrewAI wrapper for GDB graph database query tool.
Used for querying water treatment material knowledge graph in CrewAI Agents.
"""
import json
from typing import Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.tools.gdb_tool import get_gdb_tool
from src.utils.context_store import ContextStore


class GDBCatalystInput(BaseModel):
    """Catalyst Query Input Model"""
    catalyst_name: str = Field(
        description="Catalyst name, e.g.: TiO2, ZnO, Fe3O4, g-C3N4"
    )


class GDBPollutantInput(BaseModel):
    """Pollutant Query Input Model"""
    pollutant_name: str = Field(
        description="Pollutant name, e.g.: CIP, BPA, Tetracycline, PFOA"
    )


class CrewAIGDBCatalystTool(BaseTool):
    """
    Catalyst Knowledge Graph Query Tool.
    
    Query catalyst degradation capabilities and active species generation info,
    helping Agents understand catalyst application scope and reaction mechanisms.
    
    Knowledge graph contains 344 catalysts, 15 pollutants, 10 active species,
    and 1713 relationship edges.
    """
    name: str = "Catalyst Knowledge Graph Query"
    description: str = (
        "Query water treatment material knowledge graph for catalyst information. "
        "Graph contains 369 nodes and 1713 relationships: 344 catalysts, 15 pollutants, 10 active species. "
        "Input catalyst name (e.g. TiO2, ZnO), returns degradable pollutants and generated active species. "
        "Use for: material design catalyst scope, mechanism analysis reaction pathways."
    )
    args_schema: type[BaseModel] = GDBCatalystInput
    
    def _run(self, catalyst_name: str) -> str:
        """
        Execute catalyst information query.
        
        Args:
            catalyst_name: Catalyst name
            
        Returns:
            JSON formatted catalyst full information
        """
        # Check cache
        cache_key = f"gdb_catalyst:{catalyst_name}"
        cached_ctx = ContextStore.get(cache_key)
        if cached_ctx is not None:
            return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
        
        try:
            tool = get_gdb_tool()
            result = tool.query_catalyst_full_info(catalyst_name)
            
            # Cache result
            if result.get('success'):
                ContextStore.set(cache_key, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'catalyst': catalyst_name
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)


class CrewAIGDBPollutantTool(BaseTool):
    """
    Pollutant Degradation Query Tool.
    
    Query catalyst list that can degrade specific pollutants,
    helping Agents make material selection and design decisions.
    """
    name: str = "Pollutant Degradation Query"
    description: str = (
        "Query catalysts that can degrade specific pollutants. "
        "Supported pollutants: CIP, Atrazine, ibuprofen, PFOA, BPA, "
        "Sulfamethoxazole, TC, RhB, 4-NP, MO, Tetracycline, MB, Cr(VI), phenol, OTC. "
        "Input pollutant name, returns effective catalyst list and count. "
        "Use for: selecting suitable catalyst materials for specific pollutants."
    )
    args_schema: type[BaseModel] = GDBPollutantInput
    
    def _run(self, pollutant_name: str) -> str:
        """
        Execute pollutant catalyst query.
        
        Args:
            pollutant_name: Pollutant name
            
        Returns:
            JSON formatted catalyst list
        """
        # Check cache
        cache_key = f"gdb_pollutant:{pollutant_name}"
        cached_ctx = ContextStore.get(cache_key)
        if cached_ctx is not None:
            return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
        
        try:
            tool = get_gdb_tool()
            result = tool.query_pollutant_catalysts(pollutant_name)
            
            # Cache result
            if result.get('success'):
                ContextStore.set(cache_key, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'pollutant': pollutant_name
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)


# Create tool instances
gdb_catalyst_tool = CrewAIGDBCatalystTool()
gdb_pollutant_tool = CrewAIGDBPollutantTool()

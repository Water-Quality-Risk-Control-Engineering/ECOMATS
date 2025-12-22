#!/usr/bin/env python3
"""
Tool Factory.
Create and manage various database query tools.
"""

# CrewAI tool wrappers
from src.tools.crewai_materials_project_tool import materials_project_tool
from src.tools.crewai_pubchem_tool import pubchem_tool
from src.tools.crewai_name2cas_tool import CrewAIName2CASTool
from src.tools.crewai_name2properties_tool import CrewAIName2PropertiesTool
from src.tools.crewai_cid2properties_tool import CrewAICID2PropertiesTool
from src.tools.crewai_formula2properties_tool import CrewAIFormula2PropertiesTool
from src.tools.crewai_material_search_tool import CrewAIMaterialSearchTool
from src.tools.crewai_pnec_tool import CrewAIPNECTool
from src.tools.crewai_material_identifier_tool import CrewAIMaterialIdentifierTool
from src.tools.crewai_data_validator_tool import CrewAIDataValidatorTool
from src.tools.crewai_structure_validator_tool import CrewAIStructureValidatorTool
from src.tools.crewai_molport_tool import (
    molport_availability_tool,
    molport_search_tool,
    molport_molecule_info_tool
)


class ToolFactory:
    """Tool Factory Class"""
    
    @staticmethod
    def create_all_tools():
        """
        Create all tool instances.
        
        Returns:
            list: List of all tool instances
        """
        tools = [
            materials_project_tool,
            pubchem_tool,
            CrewAIName2CASTool(),
            CrewAIName2PropertiesTool(),
            CrewAICID2PropertiesTool(),
            CrewAIFormula2PropertiesTool(),
            CrewAIMaterialSearchTool(),
            CrewAIPNECTool(),
            CrewAIMaterialIdentifierTool(),
            CrewAIDataValidatorTool(),
            CrewAIStructureValidatorTool(),
            molport_availability_tool,
            molport_search_tool,
            molport_molecule_info_tool
        ]
        
        return tools
    
    @staticmethod
    def create_final_validation_tools():
        """
        Create final validation tool instances.
        Note: ASA Final needs no tools, only aggregates A/B/C outputs.
        
        Returns:
            list: Empty list (no tools needed)
        """
        return []  # Role reduction: Final only aggregates results
    
    @staticmethod
    def create_operation_guidance_tools():
        """
        Create operation guidance tool instances.
        Used by Operation_Suggesting_agent, matches task requirements.
        
        Returns:
            list: List of operation guidance tool instances
        """
        tools = [
            pubchem_tool,                  # Chemical safety data (task req)
            materials_project_tool,        # Material cost data (task req)
            CrewAIPNECTool(),              # Environmental impact (task req)
        ]
        return tools
    
    @staticmethod
    def create_literature_extraction_tools():
        """
        Create literature extraction tool instances.
        Used by Extracting_agent for extracting chemical info from literature.
        
        Strategy (Less is More):
        - Remove Name2Properties/MaterialSearch (calls MP internally, redundant)
        - Keep core query + local validation
        
        Returns:
            list: List of literature extraction tool instances
        """
        tools = [
            materials_project_tool,         # Material structure query
            pubchem_tool,                   # Compound info query
            CrewAIDataValidatorTool()       # Local data format validation (no external API)
        ]
        return tools
    
    @staticmethod
    def create_material_design_tools():
        """
        Create material design tool instances.
        
        Strategy (Less is More):
        - Keep only MP and PubChem core query tools
        - Remove redundant tools (MaterialIdentifier/StructureValidator/MaterialSearch all call MP+PubChem)
        
        Returns:
            list: List of material design tool instances
        """
        tools = [
            materials_project_tool,   # Material structure and properties
            pubchem_tool,             # Organic compound info
        ]
        return tools
    
    @staticmethod
    def create_material_assessment_tools():
        """
        Create material assessment tool instances.
        
        Strategy (Less is More):
        - Remove MaterialIdentifier/StructureValidator (redundant)
        - Keep core data sources + independent function tools
        
        Returns:
            list: List of material assessment tool instances
        """
        tools = [
            materials_project_tool,          # Material structure and properties
            pubchem_tool,                    # Compound info
            CrewAIPNECTool(),                # Environmental risk
            molport_availability_tool        # Commercial availability
        ]
        return tools
    
    @staticmethod
    def create_material_search_tools():
        """
        Create material search tool instances (for SynthesisGuidingAgent).
        
        Strategy (Less is More):
        - Remove MaterialSearch/StructureValidator (calls MP, redundant)
        - Use core tools directly
        
        Returns:
            list: List of material search tool instances
        """
        tools = [
            materials_project_tool,             # Material structure and synthesis info
            pubchem_tool,                       # Reagent safety data
        ]
        return tools
    
    @staticmethod
    def create_mechanism_analysis_tools():
        """
        Create mechanism analysis tool instances.
        Used by MechanismMiningAgent, matches task requirements.
        Note: Prioritize reusing upstream results.
        
        Returns:
            list: List of mechanism analysis tool instances
        """
        tools = [
            materials_project_tool,          # Material structure and electronic structure
            pubchem_tool,                    # Chemical reactivity
        ]
        return tools
    
    @staticmethod
    def create_unified_assessment_tools():
        """
        Create unified ASA assessment toolset (shared by Expert A/B/C).
        
        Strategy (Less is More):
        - Remove MaterialIdentifier/StructureValidator (calls MP+PubChem, highly redundant)
        - Keep core data sources + independent function tools
        
        Assessment dimension to tool mapping:
        - Catalytic performance (50%) -> materials_project
        - Economic feasibility (10%) -> molport
        - Environmental friendliness (10%) -> PNEC
        - Technical feasibility (10%) -> materials_project
        - Structural rationality (20%) -> pubchem
        
        Returns:
            list: Unified assessment tool instance list
        """
        tools = [
            materials_project_tool,          # Material structure, electronic structure, stability
            pubchem_tool,                    # Chemical properties, toxicity, structure validation
            CrewAIPNECTool(),                # Environmental risk assessment (independent API)
            molport_availability_tool,       # Commercial availability (independent API)
        ]
        return tools

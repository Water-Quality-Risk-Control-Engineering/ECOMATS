"""
Tools module initialization file.
"""

# Import all functional tools
from .materials_project_tool import get_materials_project_tool
from .pubchem_tool import get_pubchem_tool
# EvaluationTool removed - not used in ECOMATS, only in BioCrew
from .name2cas_tool import get_name2cas_tool
from .name2properties_tool import get_name2properties_tool
from .cid2properties_tool import get_cid2properties_tool
from .formula2properties_tool import get_formula2properties_tool
from .material_search_tool import get_material_search_tool
from .pnec_tool import get_pnec_tool
from .material_identifier_tool import get_material_identifier_tool
from .data_validator_tool import get_data_validator_tool
from .structure_validator_tool import get_structure_validator_tool
from .molport_tool import get_molport_tool

# Import database query tools
from .pg_vector_tool import PGVectorTool, get_pg_vector_tool
from .gdb_tool import GDBTool, get_gdb_tool
from .crewai_pg_vector_tool import CrewAIPGVectorTool
from .crewai_gdb_tool import CrewAIGDBCatalystTool, CrewAIGDBPollutantTool

# Import CrewAI tool wrappers
from .crewai_materials_project_tool import materials_project_tool
from .crewai_pubchem_tool import pubchem_tool
from .crewai_name2cas_tool import CrewAIName2CASTool
from .crewai_name2properties_tool import CrewAIName2PropertiesTool
from .crewai_cid2properties_tool import CrewAICID2PropertiesTool
from .crewai_formula2properties_tool import CrewAIFormula2PropertiesTool
from .crewai_material_search_tool import CrewAIMaterialSearchTool
from .crewai_pnec_tool import CrewAIPNECTool
from .crewai_material_identifier_tool import CrewAIMaterialIdentifierTool
from .crewai_data_validator_tool import CrewAIDataValidatorTool
from .crewai_structure_validator_tool import CrewAIStructureValidatorTool
from .crewai_molport_tool import (
    molport_availability_tool,
    molport_search_tool,
    molport_molecule_info_tool,
    CrewAIMolPortAvailabilityTool,
    CrewAIMolPortSearchTool,
    CrewAIMolPortMoleculeInfoTool
)

# Import tool factory
from .factory import ToolFactory

# Import assessment tool executor
from src.utils.assessment_tool_executor import AssessmentToolExecutor

# Import assessment scoring logic
from src.utils.assessment_scoring_logic import AssessmentScoringLogic

# Define public interface of this module
__all__ = [
    'get_materials_project_tool',
    'get_pubchem_tool',
    # 'EvaluationTool',  # Removed - not used in ECOMATS
    'get_name2cas_tool',
    'get_name2properties_tool',
    'get_cid2properties_tool',
    'get_formula2properties_tool',
    'get_material_search_tool',
    'get_pnec_tool',
    'get_material_identifier_tool',
    'get_data_validator_tool',
    'get_structure_validator_tool',
    'get_molport_tool',
    'materials_project_tool',
    'pubchem_tool',
    'CrewAIName2CASTool',
    'CrewAIName2PropertiesTool',
    'CrewAICID2PropertiesTool',
    'CrewAIFormula2PropertiesTool',
    'CrewAIMaterialSearchTool',
    'CrewAIPNECTool',
    'CrewAIMaterialIdentifierTool',
    'CrewAIDataValidatorTool',
    'ToolFactory',
    'CrewAIStructureValidatorTool',
    'molport_availability_tool',
    'molport_search_tool',
    'molport_molecule_info_tool',
    'CrewAIMolPortAvailabilityTool',
    'CrewAIMolPortSearchTool',
    'CrewAIMolPortMoleculeInfoTool',
    'AssessmentToolExecutor',
    'AssessmentScoringLogic',
    # Database query tools
    'PGVectorTool',
    'get_pg_vector_tool',
    'GDBTool',
    'get_gdb_tool',
    'CrewAIPGVectorTool',
    'CrewAIGDBCatalystTool',
    'CrewAIGDBPollutantTool'
]

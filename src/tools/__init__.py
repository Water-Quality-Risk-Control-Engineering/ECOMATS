"""
Tools module initialization file / 工具模块初始化文件
"""

# Import all functional tools / 导入所有功能工具
from .materials_project_tool import get_materials_project_tool
from .pubchem_tool import get_pubchem_tool
from .evaluation_tool import EvaluationTool
from .name2cas_tool import get_name2cas_tool
from .name2properties_tool import get_name2properties_tool
from .cid2properties_tool import get_cid2properties_tool
from .formula2properties_tool import get_formula2properties_tool
from .material_search_tool import get_material_search_tool
from .pnec_tool import get_pnec_tool
from .material_identifier_tool import get_material_identifier_tool

# Import CrewAI tool wrappers / 导入CrewAI工具包装器
from .crewai_materials_project_tool import materials_project_tool
from .crewai_pubchem_tool import pubchem_tool
from .crewai_name2cas_tool import CrewAIName2CASTool
from .crewai_name2properties_tool import CrewAIName2PropertiesTool
from .crewai_cid2properties_tool import CrewAICID2PropertiesTool
from .crewai_formula2properties_tool import CrewAIFormula2PropertiesTool
from .crewai_material_search_tool import CrewAIMaterialSearchTool
from .crewai_pnec_tool import CrewAIPNECTool
from .crewai_material_identifier_tool import CrewAIMaterialIdentifierTool

# Create instances of CrewAI tools / 创建CrewAI工具实例
name2cas_tool = CrewAIName2CASTool()
name2properties_tool = CrewAIName2PropertiesTool()
cid2properties_tool = CrewAICID2PropertiesTool()
formula2properties_tool = CrewAIFormula2PropertiesTool()
material_search_tool = CrewAIMaterialSearchTool()
pnec_tool = CrewAIPNECTool()
material_identifier_tool = CrewAIMaterialIdentifierTool()

# Define the public interface of this module / 定义此模块的公共接口
__all__ = [
    'get_materials_project_tool',
    'get_pubchem_tool',
    'EvaluationTool',
    'get_name2cas_tool',
    'get_name2properties_tool',
    'get_cid2properties_tool',
    'get_formula2properties_tool',
    'get_material_search_tool',
    'get_pnec_tool',
    'materials_project_tool',
    'pubchem_tool',
    'name2cas_tool',
    'name2properties_tool',
    'cid2properties_tool',
    'formula2properties_tool',
    'material_search_tool',
    'pnec_tool'
]
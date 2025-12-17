#!/usr/bin/env python3
"""
工具工厂
用于创建和管理各种数据库查询工具

优化说明:
- 使用单例模式缓存工具实例，避免重复创建
- 评估专家工具集按职责精简，减少LLM决策复杂度
"""

# CrewAI工具包装器
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

# 数据库查询工具 / Database query tools
from src.tools.crewai_pg_vector_tool import CrewAIPGVectorTool
from src.tools.crewai_gdb_tool import CrewAIGDBCatalystTool, CrewAIGDBPollutantTool

# =============================================================================
# 工具实例单例缓存 - 避免重复创建实例
# =============================================================================
_tool_instances = {}

def _get_tool(tool_class, key: str):
    """获取工具单例实例"""
    if key not in _tool_instances:
        _tool_instances[key] = tool_class()
    return _tool_instances[key]


class ToolFactory:
    """工具工厂类 - 使用单例模式缓存工具实例"""
    
    # 工具集缓存
    _toolset_cache = {}
    
    @staticmethod
    def create_all_tools():
        """
        创建所有工具实例（使用单例缓存）
        
        Returns:
            list: 所有工具实例的列表
        """
        if 'all' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['all'] = [
                materials_project_tool,
                pubchem_tool,
                _get_tool(CrewAIName2CASTool, 'name2cas'),
                _get_tool(CrewAIName2PropertiesTool, 'name2props'),
                _get_tool(CrewAICID2PropertiesTool, 'cid2props'),
                _get_tool(CrewAIFormula2PropertiesTool, 'formula2props'),
                _get_tool(CrewAIMaterialSearchTool, 'material_search'),
                _get_tool(CrewAIPNECTool, 'pnec'),
                _get_tool(CrewAIMaterialIdentifierTool, 'material_id'),
                _get_tool(CrewAIDataValidatorTool, 'data_validator'),
                _get_tool(CrewAIStructureValidatorTool, 'structure_validator'),
                molport_availability_tool,
                molport_search_tool,
                molport_molecule_info_tool
            ]
        return ToolFactory._toolset_cache['all']
    
    # 已移除 create_enhanced_validation_tools() - 未被使用的方法
    
    @staticmethod
    def create_final_validation_tools():
        """
        创建最终验证专用工具实例（轻量级，1个工具）
        """
        if 'final_validation' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['final_validation'] = [
                _get_tool(CrewAIDataValidatorTool, 'data_validator')
            ]
        return ToolFactory._toolset_cache['final_validation']
    
    @staticmethod
    def create_operation_guidance_tools():
        """
        创建操作指导专用工具实例（精简版，3个核心工具）
        """
        if 'operation' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['operation'] = [
                pubchem_tool,                                    # 试剂性质
                _get_tool(CrewAIMaterialSearchTool, 'material_search'),  # 参考工艺
                molport_availability_tool                        # 原料可获得性
            ]
        return ToolFactory._toolset_cache['operation']
    
    @staticmethod
    def create_literature_extraction_tools():
        """
        创建文献提取专用工具实例（精简版，3个核心工具）
        """
        if 'literature' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['literature'] = [
                pubchem_tool,                                    # 化学名称验证
                _get_tool(CrewAIName2PropertiesTool, 'name2props'),  # 名称查性质
                _get_tool(CrewAIDataValidatorTool, 'data_validator')  # 数据验证
            ]
        return ToolFactory._toolset_cache['literature']
    
    @staticmethod
    def create_material_design_tools():
        """
        创建材料设计专用工具实例（精简版，5个核心工具）
        
        Returns:
            list: 材料设计工具实例的列表
        """
        if 'material_design' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['material_design'] = [
                materials_project_tool,                          # 材料数据库
                _get_tool(CrewAIMaterialIdentifierTool, 'material_id'),  # 材料识别
                _get_tool(CrewAIStructureValidatorTool, 'structure_validator'),  # 结构验证
                _get_tool(CrewAIPGVectorTool, 'pg_vector'),      # 历史案例检索
                _get_tool(CrewAIGDBCatalystTool, 'gdb_catalyst') # 知识图谱
            ]
        return ToolFactory._toolset_cache['material_design']
    
    @staticmethod
    def create_material_assessment_tools():
        """
        创建材料评估专用工具实例（使用增强验证机制）
        包含商业可获得性检查工具（MolPort）用于经济性评估
        
        Returns:
            list: 材料评估工具实例的列表
        """
        tools = [
            materials_project_tool,
            pubchem_tool,
            CrewAIMaterialIdentifierTool(),
            CrewAIStructureValidatorTool(),
            CrewAIPNECTool(),
            CrewAIDataValidatorTool(),
            molport_availability_tool  # 用于评估前驱体和材料的商业可获得性
        ]
        return tools
    
    @staticmethod
    def create_material_search_tools():
        """
        创建材料搜索专用工具实例（精简版，4个核心工具）
        用于 SynthesisGuidingAgent
        """
        if 'material_search' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['material_search'] = [
                pubchem_tool,                                    # 试剂信息
                _get_tool(CrewAIMaterialSearchTool, 'material_search'),  # 材料搜索
                _get_tool(CrewAIName2CASTool, 'name2cas'),       # CAS号查询
                molport_availability_tool                        # 商业可获得性
            ]
        return ToolFactory._toolset_cache['material_search']
    
    @staticmethod
    def create_mechanism_analysis_tools():
        """
        创建机理分析专用工具实例（精简版，3个核心工具）
        """
        if 'mechanism' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['mechanism'] = [
                materials_project_tool,                          # 材料结构/电子结构
                _get_tool(CrewAIMaterialIdentifierTool, 'material_id'),  # 材料识别
                _get_tool(CrewAIGDBCatalystTool, 'gdb_catalyst') # 活性物种/降解关系
            ]
        return ToolFactory._toolset_cache['mechanism']
    
    @staticmethod
    def create_unified_assessment_tools():
        """
        创建统一的 ASA 评估工具集 (Expert A/B/C 共用，精简版)
        
        Returns:
            list: 统一的评估工具实例列表
        """
        if 'unified_assessment' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['unified_assessment'] = [
                materials_project_tool,
                pubchem_tool,
                _get_tool(CrewAIMaterialIdentifierTool, 'material_id'),
                _get_tool(CrewAIStructureValidatorTool, 'structure_validator'),
                _get_tool(CrewAIPNECTool, 'pnec'),
                _get_tool(CrewAIDataValidatorTool, 'data_validator')
            ]
        return ToolFactory._toolset_cache['unified_assessment']
    
    @staticmethod
    def create_expert_a_tools():
        """
        Expert A 专用工具集（催化性能 + 技术可行性，3个工具）
        """
        if 'expert_a' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['expert_a'] = [
                materials_project_tool,                          # 催化性能数据
                _get_tool(CrewAIStructureValidatorTool, 'structure_validator'),  # 技术可行性
                _get_tool(CrewAIDataValidatorTool, 'data_validator')  # 数据验证
            ]
        return ToolFactory._toolset_cache['expert_a']
    
    @staticmethod
    def create_expert_b_tools():
        """
        Expert B 专用工具集（经济可行性 + 环境友好性，3个工具）
        """
        if 'expert_b' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['expert_b'] = [
                pubchem_tool,                                    # 化学品性质/毒性
                _get_tool(CrewAIPNECTool, 'pnec'),               # 环境风险
                molport_availability_tool                        # 商业可获得性
            ]
        return ToolFactory._toolset_cache['expert_b']
    
    @staticmethod
    def create_expert_c_tools():
        """
        Expert C 专用工具集（结构合理性，3个工具）
        """
        if 'expert_c' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['expert_c'] = [
                _get_tool(CrewAIMaterialIdentifierTool, 'material_id'),  # 材料类型识别
                _get_tool(CrewAIStructureValidatorTool, 'structure_validator'),  # 结构验证
                _get_tool(CrewAIDataValidatorTool, 'data_validator')  # 数据验证
            ]
        return ToolFactory._toolset_cache['expert_c']
    
    # 保留旧方法作为别名，保持向后兼容 / Keep old methods as aliases for backward compatibility
    @staticmethod
    def create_catalytic_assessment_tools():
        """已废弃：请使用 create_unified_assessment_tools() / Deprecated: use create_unified_assessment_tools()"""
        return ToolFactory.create_unified_assessment_tools()
    
    @staticmethod
    def create_economic_assessment_tools():
        """已废弃：请使用 create_unified_assessment_tools() / Deprecated: use create_unified_assessment_tools()"""
        return ToolFactory.create_unified_assessment_tools()
    
    @staticmethod
    def create_environmental_assessment_tools():
        """已废弃：请使用 create_unified_assessment_tools() / Deprecated: use create_unified_assessment_tools()"""
        return ToolFactory.create_unified_assessment_tools()
    
    @staticmethod
    def create_materials_project_tool():
        """创建Materials Project工具实例"""
        return materials_project_tool
    
    @staticmethod
    def create_pubchem_tool():
        """创建PubChem工具实例"""
        return pubchem_tool
    
    @staticmethod
    def create_name2cas_tool():
        """创建名称到CAS号查询工具实例（单例）"""
        return _get_tool(CrewAIName2CASTool, 'name2cas')
    
    @staticmethod
    def create_name2properties_tool():
        """创建名称到性质查询工具实例（单例）"""
        return _get_tool(CrewAIName2PropertiesTool, 'name2props')
    
    @staticmethod
    def create_cid2properties_tool():
        """创建CID到性质查询工具实例（单例）"""
        return _get_tool(CrewAICID2PropertiesTool, 'cid2props')
    
    @staticmethod
    def create_formula2properties_tool():
        """创建化学式到性质查询工具实例（单例）"""
        return _get_tool(CrewAIFormula2PropertiesTool, 'formula2props')
    
    @staticmethod
    def create_material_search_tool():
        """创建材料搜索工具实例（单例）"""
        return _get_tool(CrewAIMaterialSearchTool, 'material_search')
    
    @staticmethod
    def create_pnec_tool():
        """创建PNEC工具实例（单例）"""
        return _get_tool(CrewAIPNECTool, 'pnec')
    
    @staticmethod
    def create_material_identifier_tool():
        """创建材料识别工具实例（单例）"""
        return _get_tool(CrewAIMaterialIdentifierTool, 'material_id')
    
    @staticmethod
    def create_data_validator_tool():
        """创建数据验证工具实例（单例）"""
        return _get_tool(CrewAIDataValidatorTool, 'data_validator')
    
    @staticmethod
    def create_structure_validator_tool():
        """创建结构验证工具实例（单例）"""
        return _get_tool(CrewAIStructureValidatorTool, 'structure_validator')
    
    @staticmethod
    def create_knowledge_query_tools():
        """
        创建知识库查询工具集（单例）
        
        Returns:
            list: 知识库查询工具列表
        """
        if 'knowledge_query' not in ToolFactory._toolset_cache:
            ToolFactory._toolset_cache['knowledge_query'] = [
                _get_tool(CrewAIPGVectorTool, 'pg_vector'),
                _get_tool(CrewAIGDBCatalystTool, 'gdb_catalyst'),
                _get_tool(CrewAIGDBPollutantTool, 'gdb_pollutant')
            ]
        return ToolFactory._toolset_cache['knowledge_query']
    
    @staticmethod
    def create_pg_vector_tool():
        """创建PostgreSQL向量数据库查询工具实例（单例）"""
        return _get_tool(CrewAIPGVectorTool, 'pg_vector')
    
    @staticmethod
    def create_gdb_catalyst_tool():
        """创建催化剂知识图谱查询工具实例（单例）"""
        return _get_tool(CrewAIGDBCatalystTool, 'gdb_catalyst')
    
    @staticmethod
    def create_gdb_pollutant_tool():
        """创建污染物降解查询工具实例（单例）"""
        return _get_tool(CrewAIGDBPollutantTool, 'gdb_pollutant')

#!/usr/bin/env python3
"""
工具工厂
用于创建和管理各种数据库查询工具
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


class ToolFactory:
    """工具工厂类"""
    
    @staticmethod
    def create_all_tools():
        """
        创建所有工具实例
        
        Returns:
            list: 所有工具实例的列表
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
    
    # 已移除 create_enhanced_validation_tools() - 未被使用的方法
    
    @staticmethod
    def create_final_validation_tools():
        """
        创建最终验证专用工具实例
        注意：ASA Final 不需要工具，仅对 A/B/C 输出做综合分析
        
        Returns:
            list: 空列表（无工具）
        """
        return []  # 角色收缩：Final 仅做结果聚合，不需要工具
    
    @staticmethod
    def create_operation_guidance_tools():
        """
        创建操作指导专用工具实例
        用于 Operation_Suggesting_agent，与任务需求匹配
        
        Returns:
            list: 操作指导工具实例的列表
        """
        tools = [
            pubchem_tool,                  # 查询化学品安全数据 (任务需求)
            materials_project_tool,        # 查询材料成本数据 (任务需求)
            CrewAIPNECTool(),              # 环境影响评估 (任务需求)
        ]
        return tools
    
    @staticmethod
    def create_literature_extraction_tools():
        """
        创建文献提取专用工具实例
        用于 Extracting_agent，专注于从文献中提取化学信息
        
        Returns:
            list: 文献提取工具实例的列表
        """
        tools = [
            pubchem_tool,                   # 验证提取的化学名称和性质
            CrewAIName2PropertiesTool(),    # 通过名称查询性质
            CrewAICID2PropertiesTool(),     # 通过CID查询性质
            CrewAIMaterialSearchTool(),     # 搜索材料数据库
            CrewAIDataValidatorTool()       # 验证提取数据的准确性
        ]
        return tools
    
    @staticmethod
    def create_material_design_tools():
        """
        创建材料设计专用工具实例（使用增强验证机制）
        
        Returns:
            list: 材料设计工具实例的列表
        """
        # 恢复完整工具集，测试 max_iter=1 + 全工具的效果
        tools = [
            materials_project_tool,
            pubchem_tool,
            CrewAIMaterialIdentifierTool(),      # 材料识别
            CrewAIStructureValidatorTool(),      # 结构验证
            CrewAIMaterialSearchTool()           # 材料搜索
        ]
        return tools
    
    @staticmethod
    def create_material_assessment_tools():
        """
        创建材料评估专用工具实例（使用增强验证机制）
        包含商业可获得性检查工具（MolPort）用于经济性评估
        
        Returns:
            list: 材料评估工具实例的列表
        """
        # 角色收缩：移除 DataValidatorTool，数据已经来自可信数据库
        tools = [
            materials_project_tool,
            pubchem_tool,
            CrewAIMaterialIdentifierTool(),
            CrewAIStructureValidatorTool(),
            CrewAIPNECTool(),
            molport_availability_tool  # 用于评估前驱体和材料的商业可获得性
        ]
        return tools
    
    @staticmethod
    def create_material_search_tools():
        """
        创建材料搜索专用工具实例 (SynthesisGuidingAgent 使用)
        优化版：减少冗余工具，与任务需求匹配
        
        Returns:
            list: 材料搜索工具实例的列表
        """
        tools = [
            pubchem_tool,                       # 查询试剂安全数据 (Prompt 要求)
            CrewAIMaterialSearchTool(),         # 相似材料合成方法
            CrewAIStructureValidatorTool(),     # 结构验证 (任务需求)
        ]
        
        return tools
    
    @staticmethod
    def create_mechanism_analysis_tools():
        """
        创建机理分析专用工具实例
        用于 MechanismMiningAgent，与任务需求匹配
        注意：优先复用上游结果
        
        Returns:
            list: 机理分析工具实例的列表
        """
        tools = [
            materials_project_tool,          # 查询材料结构和电子结构
            pubchem_tool,                    # 查询化学品反应活性
        ]
        return tools
    
    @staticmethod
    def create_unified_assessment_tools():
        """
        创建统一的 ASA 评估工具集 (Expert A/B/C 共用)
        Create unified ASA assessment tools (shared by Expert A/B/C)
        
        根据 Prompt 要求，每个 ASA 都需要从 5 个维度进行全面评估：
        According to Prompt requirements, each ASA needs to evaluate from 5 dimensions:
        - 催化性能 (50%) - 需要 materials_project
        - 经济可行性 (10%) - 需要 pubchem, molport
        - 环境友好性 (10%) - 需要 pubchem, PNEC
        - 技术可行性 (10%) - 需要 materials_project, structure_validator
        - 结构合理性 (20%) - 需要 structure_validator, material_identifier
        
        Returns:
            list: 统一的评估工具实例列表 / Unified assessment tools list
        """
        # 角色收缩：移除 DataValidatorTool，数据直接来自 Materials Project / PubChem，无需再验证
        # 添加 MolPort 用于经济可行性评估（前驱体商业可获得性）
        tools = [
            materials_project_tool,          # 材料结构和电子结构 / Material structure
            pubchem_tool,                    # 化学品性质和毒性 / Chemical properties and toxicity
            CrewAIMaterialIdentifierTool(),  # 材料识别 / Material identification
            CrewAIStructureValidatorTool(),  # 结构验证 / Structure validation
            CrewAIPNECTool(),                # 环境风险评估 / Environmental risk (PNEC)
            molport_availability_tool,       # 经济可行性 - 商业可获得性 / Economic - commercial availability
        ]
        return tools
    
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
        """创建名称到CAS号查询工具实例"""
        return CrewAIName2CASTool()
    
    @staticmethod
    def create_name2properties_tool():
        """创建名称到性质查询工具实例"""
        return CrewAIName2PropertiesTool()
    
    @staticmethod
    def create_cid2properties_tool():
        """创建CID到性质查询工具实例"""
        return CrewAICID2PropertiesTool()
    
    @staticmethod
    def create_formula2properties_tool():
        """创建化学式到性质查询工具实例"""
        return CrewAIFormula2PropertiesTool()
    
    @staticmethod
    def create_material_search_tool():
        """创建材料搜索工具实例"""
        return CrewAIMaterialSearchTool()
    
    @staticmethod
    def create_pnec_tool():
        """创建PNEC工具实例"""
        return CrewAIPNECTool()
    
    @staticmethod
    def create_material_identifier_tool():
        """创建材料识别工具实例"""
        return CrewAIMaterialIdentifierTool()
    
    @staticmethod
    def create_data_validator_tool():
        """创建数据验证工具实例"""
        return CrewAIDataValidatorTool()
    
    @staticmethod
    def create_structure_validator_tool():
        """创建结构验证工具实例"""
        return CrewAIStructureValidatorTool()

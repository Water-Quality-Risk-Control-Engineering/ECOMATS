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
        
        优化策略（Less is More）：
        - 移除 Name2Properties/MaterialSearch（内部调用 MP，冗余）
        - 保留核心查询 + 本地验证
        
        Returns:
            list: 文献提取工具实例的列表
        """
        tools = [
            materials_project_tool,         # 材料结构查询
            pubchem_tool,                   # 化合物信息查询
            CrewAIDataValidatorTool()       # 本地数据格式验证（不调用外部 API）
        ]
        return tools
    
    @staticmethod
    def create_material_design_tools():
        """
        创建材料设计专用工具实例
        
        优化策略（Less is More）：
        - 仅保留 MP 和 PubChem 核心查询工具
        - 移除冗余工具（MaterialIdentifier/StructureValidator/MaterialSearch 内部都调用 MP+PubChem）
        
        Returns:
            list: 材料设计工具实例的列表
        """
        tools = [
            materials_project_tool,   # 材料结构和属性查询
            pubchem_tool,             # 有机化合物信息查询
        ]
        return tools
    
    @staticmethod
    def create_material_assessment_tools():
        """
        创建材料评估专用工具实例
        
        优化策略（Less is More）：
        - 移除 MaterialIdentifier/StructureValidator（冗余）
        - 保留核心数据源 + 独立功能工具
        
        Returns:
            list: 材料评估工具实例的列表
        """
        tools = [
            materials_project_tool,          # 材料结构和属性
            pubchem_tool,                    # 化合物信息
            CrewAIPNECTool(),                # 环境风险
            molport_availability_tool        # 商业可获得性
        ]
        return tools
    
    @staticmethod
    def create_material_search_tools():
        """
        创建材料搜索专用工具实例 (SynthesisGuidingAgent 使用)
        
        优化策略（Less is More）：
        - 移除 MaterialSearch/StructureValidator（内部调用 MP，冗余）
        - 直接使用核心工具
        
        Returns:
            list: 材料搜索工具实例的列表
        """
        tools = [
            materials_project_tool,             # 材料结构和合成信息
            pubchem_tool,                       # 试剂安全数据
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
        
        优化策略（Less is More）：
        - 移除 MaterialIdentifier/StructureValidator（内部调用 MP+PubChem，严重冗余）
        - 保留核心数据源 + 独立功能工具
        
        评估维度与工具映射：
        - 催化性能 (50%) → materials_project
        - 经济可行性 (10%) → molport
        - 环境友好性 (10%) → PNEC
        - 技术可行性 (10%) → materials_project
        - 结构合理性 (20%) → pubchem
        
        Returns:
            list: 统一的评估工具实例列表
        """
        tools = [
            materials_project_tool,          # 材料结构、电子结构、稳定性
            pubchem_tool,                    # 化学品性质、毒性、结构验证
            CrewAIPNECTool(),                # 环境风险评估（独立 API）
            molport_availability_tool,       # 商业可获得性（独立 API）
        ]
        return tools

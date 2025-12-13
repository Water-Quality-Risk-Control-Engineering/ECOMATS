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
        创建最终验证专用工具实例（轻量级）
        用于 Assessment_Overall_agent，仅用于数据验证和格式检查
        
        Returns:
            list: 最终验证工具实例的列表
        """
        tools = [
            CrewAIDataValidatorTool()  # 仅用于验证三位专家的评估结果格式
        ]
        return tools
    
    @staticmethod
    def create_operation_guidance_tools():
        """
        创建操作指导专用工具实例
        用于 Operation_Suggesting_agent，聚焦于材料参数和试剂查询
        
        Returns:
            list: 操作指导工具实例的列表
        """
        tools = [
            materials_project_tool,        # 查询材料的物理化学参数
            pubchem_tool,                  # 查询试剂和化学品性质
            CrewAIMaterialSearchTool(),    # 查找参考材料和工艺
            molport_availability_tool      # 验证试剂和原料的可获得性
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
        # 轻量化设计模式：减少即时工具数量，优先标识与结构验证，MP最小字段查询
        tools = [
            materials_project_tool,
            pubchem_tool,
            CrewAIMaterialIdentifierTool(),
            CrewAIStructureValidatorTool(),
            CrewAIMaterialSearchTool()
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
        创建材料搜索专用工具实例
        包含商业可获得性检查，用于验证前驱体和试剂的可获得性
        
        Returns:
            list: 材料搜索工具实例的列表
        """
        tools = [
            CrewAIMaterialSearchTool(),         # 材料搜索工具
            CrewAIName2CASTool(),               # 名称到CAS号查询工具
            CrewAIMaterialIdentifierTool(),     # 材料识别工具
            molport_availability_tool           # 商业可获得性检查
        ]
        
        return tools
    
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

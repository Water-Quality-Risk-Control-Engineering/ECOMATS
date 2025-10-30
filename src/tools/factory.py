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
            CrewAIStructureValidatorTool()
        ]
        
        return tools
    
    @staticmethod
    def create_enhanced_validation_tools():
        """
        创建增强验证工具实例（包含更频繁的验证机制）
        
        Returns:
            list: 增强验证工具实例的列表
        """
        tools = [
            materials_project_tool,             # Materials Project数据库工具（用于验证MP-ID）
            pubchem_tool,                       # PubChem数据库工具（用于验证有机物）
            CrewAIMaterialIdentifierTool(),     # 材料识别工具（用于获取标识符）
            CrewAIStructureValidatorTool(),     # 结构验证工具（用于验证材料结构）
            CrewAIName2PropertiesTool(),        # 名称到性质查询工具（用于验证材料性质）
            CrewAICID2PropertiesTool()          # CID到性质查询工具（用于验证化合物性质）
        ]
        
        return tools
    
    @staticmethod
    def create_material_design_tools():
        """
        创建材料设计专用工具实例（使用增强验证机制）
        
        Returns:
            list: 材料设计工具实例的列表
        """
        # 使用增强验证工具确保更频繁的工具调用
        tools = ToolFactory.create_enhanced_validation_tools()
        return tools
    
    @staticmethod
    def create_material_assessment_tools():
        """
        创建材料评估专用工具实例（使用增强验证机制）
        
        Returns:
            list: 材料评估工具实例的列表
        """
        # 使用增强验证工具确保更频繁的工具调用
        tools = ToolFactory.create_enhanced_validation_tools()
        
        # 添加评估专用工具
        tools.extend([
            CrewAIPNECTool(),                   # PNEC工具（用于环境风险评估）
            CrewAIDataValidatorTool(),          # 数据验证工具（用于验证数据质量）
        ])
        
        return tools
    
    @staticmethod
    def create_material_search_tools():
        """
        创建材料搜索专用工具实例
        
        Returns:
            list: 材料搜索工具实例的列表
        """
        tools = [
            CrewAIMaterialSearchTool(),         # 材料搜索工具
            CrewAIName2CASTool(),               # 名称到CAS号查询工具
            CrewAIMaterialIdentifierTool()      # 材料识别工具
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
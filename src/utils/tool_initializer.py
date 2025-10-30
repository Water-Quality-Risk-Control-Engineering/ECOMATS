#!/usr/bin/env python3
"""
工具初始化器
提供可靠的工具实例创建和错误处理机制
"""

import logging
from typing import List, Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ToolInitializer:
    """工具初始化器类 - 提供可靠的工具实例创建和错误处理机制"""
    
    @staticmethod
    def initialize_tool(tool_name: str, tool_factory_func, *args, **kwargs) -> Optional[Any]:
        """
        安全地初始化单个工具
        
        Args:
            tool_name (str): 工具名称
            tool_factory_func: 工具工厂函数
            *args: 传递给工厂函数的位置参数
            **kwargs: 传递给工厂函数的关键字参数
            
        Returns:
            Optional[Any]: 工具实例或None（如果初始化失败）
        """
        try:
            tool_instance = tool_factory_func(*args, **kwargs)
            logger.info(f"成功初始化工具: {tool_name}")
            return tool_instance
        except ImportError as e:
            logger.warning(f"工具 {tool_name} 依赖未安装: {e}")
            return None
        except Exception as e:
            logger.error(f"初始化工具 {tool_name} 时出错: {e}")
            return None
    
    @staticmethod
    def initialize_tools(tool_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量初始化工具
        
        Args:
            tool_configs (List[Dict[str, Any]]): 工具配置列表，每个配置包含：
                - name: 工具名称
                - factory: 工具工厂函数
                - args: 位置参数（可选）
                - kwargs: 关键字参数（可选）
                
        Returns:
            Dict[str, Any]: 工具实例字典
        """
        tools = {}
        
        for config in tool_configs:
            name = config.get("name")
            factory = config.get("factory")
            args = config.get("args", ())
            kwargs = config.get("kwargs", {})
            
            if not name or not factory:
                logger.warning(f"工具配置无效，缺少名称或工厂函数: {config}")
                continue
                
            tool_instance = ToolInitializer.initialize_tool(name, factory, *args, **kwargs)
            if tool_instance is not None:
                tools[name] = tool_instance
            else:
                logger.warning(f"工具 {name} 初始化失败，将在代理中跳过")
        
        return tools

# 创建特定代理的工具初始化函数
def initialize_assessment_agent_a_tools() -> List[Any]:
    """初始化评估代理A的工具"""
    from src.tools import (
        materials_project_tool,
        pubchem_tool,
        name2properties_tool,
        cid2properties_tool,
        pnec_tool,
        data_validator_tool,
        structure_validator_tool
    )
    
    # 直接使用CrewAI工具包装器实例，确保它们继承自BaseTool
    tools = [
        materials_project_tool,      # CrewAIMaterialsProjectTool
        pubchem_tool,                # CrewAIPubChemTool
        name2properties_tool,        # CrewAIName2PropertiesTool
        cid2properties_tool,         # CrewAICID2PropertiesTool
        pnec_tool,                   # CrewAIPNECTool
        data_validator_tool,         # CrewAIDataValidatorTool
        structure_validator_tool     # CrewAIStructureValidatorTool
    ]
    
    return tools

def initialize_assessment_agent_b_tools() -> List[Any]:
    """初始化评估代理B的工具"""
    from src.tools import (
        materials_project_tool,
        pubchem_tool,
        name2properties_tool,
        cid2properties_tool,
        pnec_tool,
        structure_validator_tool
    )
    
    # 直接使用CrewAI工具包装器实例，确保它们继承自BaseTool
    tools = [
        materials_project_tool,      # CrewAIMaterialsProjectTool
        pubchem_tool,                # CrewAIPubChemTool
        name2properties_tool,        # CrewAIName2PropertiesTool
        cid2properties_tool,         # CrewAICID2PropertiesTool
        pnec_tool,                   # CrewAIPNECTool
        structure_validator_tool     # CrewAIStructureValidatorTool
    ]
    
    return tools

def initialize_assessment_agent_c_tools() -> List[Any]:
    """初始化评估代理C的工具"""
    from src.tools import (
        materials_project_tool,
        pubchem_tool,
        name2properties_tool,
        cid2properties_tool,
        pnec_tool
    )
    
    # 直接使用CrewAI工具包装器实例，确保它们继承自BaseTool
    tools = [
        materials_project_tool,      # CrewAIMaterialsProjectTool
        pubchem_tool,                # CrewAIPubChemTool
        name2properties_tool,        # CrewAIName2PropertiesTool
        cid2properties_tool,         # CrewAICID2PropertiesTool
        pnec_tool                     # CrewAIPNECTool
    ]
    
    return tools

def initialize_final_validator_tools() -> List[Any]:
    """初始化最终验证代理的工具"""
    from src.tools import (
        materials_project_tool,
        pubchem_tool,
        name2properties_tool,
        cid2properties_tool,
        pnec_tool,
        material_search_tool,
        data_validator_tool,
        structure_validator_tool
    )
    
    # 直接使用CrewAI工具包装器实例，确保它们继承自BaseTool
    tools = [
        materials_project_tool,      # CrewAIMaterialsProjectTool
        pubchem_tool,                # CrewAIPubChemTool
        name2properties_tool,        # CrewAIName2PropertiesTool
        cid2properties_tool,         # CrewAICID2PropertiesTool
        pnec_tool,                   # CrewAIPNECTool
        material_search_tool,        # CrewAIMaterialSearchTool
        data_validator_tool,         # CrewAIDataValidatorTool
        structure_validator_tool     # CrewAIStructureValidatorTool
    ]
    
    return tools
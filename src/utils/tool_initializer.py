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
        get_materials_project_tool,
        get_pubchem_tool,
        get_name2properties_tool,
        get_cid2properties_tool,
        get_pnec_tool,
        get_data_validator_tool,
        get_structure_validator_tool
    )
    
    tool_configs = [
        {"name": "materials_project_tool", "factory": get_materials_project_tool},
        {"name": "pubchem_tool", "factory": get_pubchem_tool},
        {"name": "name2properties_tool", "factory": get_name2properties_tool},
        {"name": "cid2properties_tool", "factory": get_cid2properties_tool},
        {"name": "pnec_tool", "factory": get_pnec_tool},
        {"name": "data_validator_tool", "factory": get_data_validator_tool},
        {"name": "structure_validator_tool", "factory": get_structure_validator_tool}
    ]
    
    tools_dict = ToolInitializer.initialize_tools(tool_configs)
    return list(tools_dict.values())

def initialize_assessment_agent_b_tools() -> List[Any]:
    """初始化评估代理B的工具"""
    from src.tools import (
        get_materials_project_tool,
        get_pubchem_tool,
        get_name2properties_tool,
        get_cid2properties_tool,
        get_pnec_tool,
        get_structure_validator_tool
    )
    
    tool_configs = [
        {"name": "materials_project_tool", "factory": get_materials_project_tool},
        {"name": "pubchem_tool", "factory": get_pubchem_tool},
        {"name": "name2properties_tool", "factory": get_name2properties_tool},
        {"name": "cid2properties_tool", "factory": get_cid2properties_tool},
        {"name": "pnec_tool", "factory": get_pnec_tool},
        {"name": "structure_validator_tool", "factory": get_structure_validator_tool}
    ]
    
    tools_dict = ToolInitializer.initialize_tools(tool_configs)
    return list(tools_dict.values())

def initialize_assessment_agent_c_tools() -> List[Any]:
    """初始化评估代理C的工具"""
    from src.tools import (
        get_materials_project_tool,
        get_pubchem_tool,
        get_name2properties_tool,
        get_cid2properties_tool,
        get_pnec_tool
    )
    
    tool_configs = [
        {"name": "materials_project_tool", "factory": get_materials_project_tool},
        {"name": "pubchem_tool", "factory": get_pubchem_tool},
        {"name": "name2properties_tool", "factory": get_name2properties_tool},
        {"name": "cid2properties_tool", "factory": get_cid2properties_tool},
        {"name": "pnec_tool", "factory": get_pnec_tool}
    ]
    
    tools_dict = ToolInitializer.initialize_tools(tool_configs)
    return list(tools_dict.values())

def initialize_final_validator_tools() -> List[Any]:
    """初始化最终验证代理的工具"""
    from src.tools import (
        get_materials_project_tool,
        get_pubchem_tool,
        get_name2properties_tool,
        get_cid2properties_tool,
        get_pnec_tool,
        get_material_search_tool,
        get_data_validator_tool,
        get_structure_validator_tool
    )
    
    tool_configs = [
        {"name": "materials_project_tool", "factory": get_materials_project_tool},
        {"name": "pubchem_tool", "factory": get_pubchem_tool},
        {"name": "name2properties_tool", "factory": get_name2properties_tool},
        {"name": "cid2properties_tool", "factory": get_cid2properties_tool},
        {"name": "pnec_tool", "factory": get_pnec_tool},
        {"name": "material_search_tool", "factory": get_material_search_tool},
        {"name": "data_validator_tool", "factory": get_data_validator_tool},
        {"name": "structure_validator_tool", "factory": get_structure_validator_tool}
    ]
    
    tools_dict = ToolInitializer.initialize_tools(tool_configs)
    return list(tools_dict.values())
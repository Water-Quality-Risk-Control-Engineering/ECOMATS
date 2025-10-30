#!/usr/bin/env python3
"""
工具初始化器
提供可靠的工具实例创建和错误处理机制
"""

import logging
from typing import List, Dict, Any, Optional

# 导入所有工具类
from src.tools import (
    materials_project_tool,
    pubchem_tool,
    CrewAIName2PropertiesTool,
    CrewAICID2PropertiesTool,
    CrewAIPNECTool,
    CrewAIMaterialSearchTool,
    CrewAIDataValidatorTool,
    CrewAIStructureValidatorTool
)

# 导入工具工厂
from src.tools.factory import ToolFactory

# 导入评估工具执行器
from src.utils.assessment_tool_executor import AssessmentToolExecutor

# 导入评估评分逻辑
from src.utils.assessment_scoring_logic import AssessmentScoringLogic

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def initialize_final_validator_tools():
    """
    初始化最终验证代理的工具
    返回所有可用工具的列表
    """
    try:
        tools = ToolFactory.create_all_tools()
        logger.info("成功初始化最终验证代理的工具")
        return tools
    except Exception as e:
        logger.error(f"初始化最终验证代理工具时出错: {e}")
        # 回退到手动创建的工具列表
        return [
            materials_project_tool,
            pubchem_tool,
            CrewAIName2PropertiesTool(),
            CrewAICID2PropertiesTool(),
            CrewAIPNECTool(),
            CrewAIMaterialSearchTool(),
            CrewAIDataValidatorTool(),
            CrewAIStructureValidatorTool()
        ]

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
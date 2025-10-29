import logging
from .base_agent import BaseAgent
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
from src.utils.tool_initializer import initialize_final_validator_tools

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class EnhancedFinalValidator(BaseAgent):
    """增强型最终验证专家智能体 / Enhanced final validation expert agent"""
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Enhanced_Final_Validator",  # 增强型最终验证专家 / Enhanced final validation expert
            goal="综合各专家评估结果，进行加权计算并形成最终材料评估报告，同时提供改进建议",  # Synthesize evaluation results from various experts, perform weighted calculations, and generate final material evaluation report, while providing improvement suggestions
            prompt_file="enhanced_final_validator_prompt.md",
            temperature=Config.FINAL_VALIDATOR_TEMPERATURE
        )
    
    def create_agent(self):
        # 尝试创建EAS模型实例
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("成功创建EAS LLM实例 / Successfully created EAS LLM instance")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"创建EAS模型实例失败: {e} / Failed to create EAS model instance: {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # 为最终验证专家添加化学数据库查询工具
        # Add chemical database query tools for the final validation expert
        # 使用改进的工具初始化器确保工具调用的可靠性
        try:
            agent.tools = initialize_final_validator_tools()
            if not agent.tools:
                logger.warning("增强型最终验证代理的工具初始化失败，使用默认工具列表")
                agent.tools = [materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool, material_search_tool, data_validator_tool, structure_validator_tool]
        except Exception as e:
            logger.error(f"初始化增强型最终验证代理工具时出错: {e}")
            # 回退到原始工具列表
            agent.tools = [materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool, material_search_tool, data_validator_tool, structure_validator_tool]
        
        return agent
import logging
from .base_agent import BaseAgent

# 导入必要的工具
from src.tools import (
    materials_project_tool,
    pubchem_tool,
    name2properties_tool,
    cid2properties_tool,
    pnec_tool,
    material_search_tool
)

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentScreeningAgentOverall(BaseAgent):
    """综合评估筛选专家智能体 / Comprehensive assessment and screening expert agent"""
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Assessment_Screening_agent_Overall",  # 最终验证专家 / Final validation expert
            goal="综合各专家评估结果，进行加权计算并形成最终材料评估报告",  # Synthesize evaluation results from various experts, perform weighted calculations, and generate final material evaluation report
            prompt_file="final_validator_prompt.md",
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
        agent.tools = [materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool, material_search_tool]
        return agent

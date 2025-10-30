import logging
from .base_agent import BaseAgent
from src.tools import ToolFactory

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
        # 最终验证需要所有工具来进行交叉验证
        # Final validation needs all tools for cross-validation
        agent.tools = ToolFactory.create_all_tools()
        
        # 强化提示词，明确其聚合角色
        agent.backstory += "\n\n你的核心职责是从AssessmentScreeningAgentA、B、C三位专家处收集评估结果，进行加权计算和一致性分析，生成最终报告。你不需要重新评估材料本身，而是综合已有意见。"
        
        return agent

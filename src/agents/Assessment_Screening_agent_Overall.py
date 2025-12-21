import logging
from .base_agent import BaseAgent
from src.tools import ToolFactory
from src.utils.llm_config import tools_enabled

# Configure logging / 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentScreeningAgentOverall(BaseAgent):
    """Comprehensive assessment and screening expert agent / 综合评估筛选专家智能体"""
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Assessment_Screening_agent_Overall",  # Final validation expert / 最终验证专家
            goal="Synthesize evaluation results from various experts, perform weighted calculations, and generate final material evaluation report, while providing improvement suggestions",  # 综合各专家评估结果，进行加权计算并形成最终材料评估报告，同时提供改进建议
            prompt_file="assessment_screening_agent_overall_prompt.md",
            temperature=Config.FINAL_VALIDATOR_TEMPERATURE,
            max_iter=1  # Less is More: Reduced to 1 iteration (original: 8) - Only synthesize existing results, no iteration needed / 降至1次（原值：8）- 仅综合已有结果，无需迭代
        )
    
    def create_agent(self):
        # Try to create EAS model instance / 尝试创建EAS模型实例
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("Successfully created EAS LLM instance / 成功创建EAS LLM实例")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"Failed to create EAS model instance / 创建EAS模型实例失败: {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # ASA Final 不需要工具，仅对 ASA A/B/C 的输出做综合分析
        # ASA Final does not need tools, only synthesizes outputs from ASA A/B/C
        agent.tools = []
        
        # Enhance prompt to clarify its aggregation role / 强化提示词，明确其聚合角色
        agent.backstory += "\n\nYour core responsibility is to collect evaluation results from three experts (AssessmentScreeningAgentA, B, C), perform weighted calculations and consistency analysis, and generate the final report. You do not need to re-evaluate the material itself, but synthesize existing opinions.\n\n你的核心职责是从AssessmentScreeningAgentA、B、C三位专家处收集评估结果，进行加权计算和一致性分析，生成最终报告。你不需要重新评估材料本身，而是综合已有意见。"

        return agent

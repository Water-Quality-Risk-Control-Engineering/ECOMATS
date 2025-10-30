import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory
from src.utils.tool_call_spec import AssessmentExpertToolSpec
from src.utils.assessment_tool_executor import AssessmentToolExecutor

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Expert B class / 评估筛选专家B
class AssessmentScreeningAgentB(BaseAgent):
    """Assessment and screening expert B agent"""
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Assessment_Screening_agent_B",  # Assessment and screening expert B / 评估筛选专家B
            goal="Comprehensively evaluate various aspects of material proposals",  # Comprehensively evaluate various aspects of material proposals / 全面评估材料方案的各个方面
            prompt_file="expert_b_prompt.md",
            temperature=Config.EXPERT_B_TEMPERATURE
        )
    
    def create_agent(self):
        # 尝试创建EAS模型实例
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("成功创建EAS LLM实例")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"创建EAS模型实例失败: {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # 移除数据库查询工具，评估应基于设计阶段的结果
        # Remove database query tools, assessment should be based on design phase results
        agent.tools = []  # 仅保留基本工具或空工具列表
        
        return agent
import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Expert B class / 评估筛选专家B
class AssessmentScreeningAgentB(BaseAgent):
    """Assessment and screening expert B agent
    评估筛选专家B智能体
    """
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Assessment_Screening_agent_B",  # Assessment and screening expert B
            goal="Comprehensively evaluate various aspects of material proposals",
            prompt_file="expert_template_prompt.md",  # Use parameterized template / 使用参数化模板
            temperature=Config.EXPERT_B_TEMPERATURE,
            max_iter=2,  # Less is More: Reduced to 2 iterations (original: 15) - Focus on core evaluation logic / 降至2次（原值：15）- 聚焦核心评估逻辑
            prompt_params={"EXPERT_ID": "B"}  # Parameterized replacement / 参数化替换
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
        # Use unified ASA evaluation toolset (shared by A/B/C) / 使用统一的 ASA 评估工具集 (A/B/C 共用)
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_unified_assessment_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_unified_assessment_tools()
        
        return agent
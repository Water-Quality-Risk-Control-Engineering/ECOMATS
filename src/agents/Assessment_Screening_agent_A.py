import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging
# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Expert A class for material assessment and screening
# 专家A类 - 负责材料方案的全面评估与筛选
class AssessmentScreeningAgentA(BaseAgent):
    def __init__(self, llm):
        """
        Initialize the Assessment Screening Agent A
        
        Args:
            llm: The language model instance to be used by this agent
                 用于此智能体的语言模型实例
        """
        from src.config.config import Config
        super().__init__(
            llm, 
            "Assessment_Screening_agent_A",  # Expert A / 专家A
            "Comprehensively evaluate various aspects of material proposals",  # 全面评估材料方案的各个方面
            "assessment_screening_agent_a_prompt.md",  # Use Agent-specific prompt / 使用Agent专用prompt
            temperature=Config.EXPERT_A_TEMPERATURE,
            max_iter=2,  # Less is More: Reduced to 2 iterations (original: 15) - Focus on core evaluation logic / 降至2次（原值：15）- 聚焦核心评估逻辑
            prompt_params={"EXPERT_ID": "A"}  # Parameterized replacement / 参数化替换
        )
    
    def create_agent(self):
        """Create and configure the agent with appropriate tools
        创建并配置带有适当工具的智能体
        
        Returns:
            Configured agent instance with chemical database query tools
            配置好的智能体实例，包含化学数据库查询工具
        """
        # Try to create EAS model instance
        # 尝试创建EAS模型实例
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("Successfully created EAS LLM instance / 成功创建EAS LLM实例")
            # Update the llm attribute to use EAS
            # 更新llm属性以使用EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"Failed to create EAS model instance / 创建EAS模型实例失败: {e}")
            # If EAS configuration fails, use the passed LLM
            # 如果EAS配置失败，则使用传入的LLM
            # Keep self.llm as is
            # 保持self.llm不变
        
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

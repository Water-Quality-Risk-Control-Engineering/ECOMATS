import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory
from src.utils.tool_call_spec import AssessmentExpertToolSpec
from src.utils.assessment_tool_executor import AssessmentToolExecutor

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
            "全面评估材料方案的各个方面",  # Conduct comprehensive evaluation of material proposals from various aspects / 全面评估材料方案的各个方面
            "expert_a_prompt.md",  # Prompt file for expert A / 专家A的提示文件
            temperature=Config.EXPERT_A_TEMPERATURE  # Temperature setting from config / 从配置中获取的温度设置
        )
    
    def create_agent(self):
        """
        Create and configure the agent with appropriate tools
        
        Returns:
            Configured agent instance with chemical database query tools
            配置好的智能体实例，包含化学数据库查询工具
        """
        # Try to create EAS model instance
        # 尝试创建EAS模型实例
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("成功创建EAS LLM实例")  # Successfully created EAS LLM instance
            # Update the llm attribute to use EAS
            # 更新llm属性以使用EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"创建EAS模型实例失败: {e}")  # Failed to create EAS model instance
            # If EAS configuration fails, use the passed LLM
            # 如果EAS配置失败，则使用传入的LLM
            # Keep self.llm as is
            # 保持self.llm不变
        
        agent = super().create_agent()
        # 移除数据库查询工具，评估应基于设计阶段的结果
        # Remove database query tools, assessment should be based on design phase results
        agent.tools = []  # 仅保留基本工具或空工具列表
        
        return agent

import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging / 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Operation Suggestion Expert Agent class / 操作建议专家智能体类
# This agent provides operational guidance for material synthesis, production and application
# 此智能体为材料合成、生产和应用提供操作指导
class OperationSuggestingAgent(BaseAgent):
    def __init__(self, llm):
        """Initialize the Operation Suggestion Agent
        初始化操作建议智能体
        
        Args:
            llm: The language model instance to be used by the agent
                 用于此智能体的语言模型实例
        """
        from src.config.config import Config
        super().__init__(
            llm, 
            "Operation_Suggesting_agent",  # Role: Operation Suggestion Expert / 角色：操作建议专家
            "Provide detailed operational guidance for material synthesis, production and application",  # 为材料合成、生产和应用提供详细的操作指导建议
            "operation_suggesting_prompt.md",  # Prompt template file
            temperature=Config.OPERATION_SUGGESTING_TEMPERATURE,  # Temperature setting from config
            max_iter=2  # Less is More: Reduced to 2 iterations (original: 8) - Reuse upstream synthesis routes, focus on operational details / 降至2次（原值：8）- 复用上游合成路线，聚焦操作细节
        )
    
    def create_agent(self):
        """Create and configure the operation suggesting agent with appropriate tools
        创建并配置带有适当工具的操作建议智能体
        
        Returns:
            Configured agent instance with chemical database query tools
            配置好的智能体实例，包含化学数据库查询工具
        """
        # Try to create EAS model instance
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
        # Use operation guidance toolset, focusing on material parameters and reagent queries / 使用操作指导专用工具集，聚焦于材料参数和试剂查询
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_operation_guidance_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_operation_guidance_tools()
        return agent
import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging / 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ExtractingAgent(BaseAgent):
    """
    Literature Processing Agent / 文献处理专家
    An intelligent agent responsible for processing and analyzing scientific literature 
    to extract relevant information for material evaluation.
    """

    def __init__(self, llm):
        """Initialize the ExtractingAgent with specified parameters.
        初始化文献提取智能体
        
        Args:
            llm: The language model instance to be used by the agent
                 用于此智能体的语言模型实例
        """
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Extracting_agent",  # Literature Processing Expert
            goal="Process and analyze relevant technical literature to provide background information for material evaluation",  # 处理和分析相关技术文献，为材料评估提供背景信息
            prompt_file="extracting_agent_prompt.md",
            temperature=Config.LITERATURE_PROCESSOR_TEMPERATURE
        )
    
    def create_agent(self):
        """Create and configure the agent with appropriate tools.
        创建并配置带有适当工具的智能体
        
        This method attempts to create an EAS LLM instance first, falling back to 
        the provided LLM if EAS creation fails. It then adds chemical database 
        query tools to enhance the agent's capabilities.
        此方法首先尝试创建EAS LLM实例，如果创建失败则回退到提供的LLM。
        然后添加化学数据库查询工具来增强智能体的能力。
        
        Returns:
            Configured agent instance with necessary tools
            配置好的智能体实例，包含必要的工具
        """
        # Attempt to create EAS model instance
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
        # Use standardized literature extraction toolset / 使用标准化的文献提取工具集
        agent.tools = ToolFactory.create_literature_extraction_tools()
        return agent
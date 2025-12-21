import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging / 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class SynthesisGuidingAgent(BaseAgent):
    """Synthesis Guiding Agent / 合成方法专家类
    
    This agent specializes in designing material synthesis methods and 
    process flows. It inherits from BaseAgent and extends functionality
    with chemistry database tools.
    """
    
    def __init__(self, llm):
        """Initialize the Synthesis Guiding Agent.
        初始化合成指导智能体
        
        Args:
            llm: The language model instance to be used by the agent
                 用于此智能体的语言模型实例
        """
        from src.config.config import Config
        super().__init__(
            llm, 
            "Synthesis_Guiding_agent",  # Role: Synthesis Method Expert / 角色：合成方法专家
            "Design material synthesis methods and process flows",  # 设计材料的合成方法和工艺流程
            "synthesis_expert_prompt.md",  # Prompt template file
            temperature=Config.SYNTHESIS_EXPERT_TEMPERATURE,  # Temperature setting from config
            max_iter=2  # Less is More: Reduced to 2 iterations (original: 8) - Reuse upstream design, focus on synthesis routes / 降至2次（原值：8）- 复用上游设计，聚焦合成路线
        )
    
    def create_agent(self):
        """Create and configure the agent instance.
        创建并配置智能体实例
        
        Attempts to create an EAS LLM instance first, falls back to 
        the provided LLM if EAS creation fails. Adds chemistry database
        query tools to the agent.
        首先尝试创建EAS LLM实例，如果创建失败则回退到提供的LLM。
        为智能体添加化学数据库查询工具。
        
        Returns:
            Configured agent instance with necessary tools
            配置好的智能体实例，包含必要的工具
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
        # Disable tool calls by default on DashScope compatible endpoint / 在 DashScope 兼容端点默认禁用工具调用
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_material_search_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_material_search_tools()
        return agent
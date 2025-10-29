import logging
from src.agents.base_agent import BaseAgent
from src.tools import pubchem_tool, name2cas_tool, name2properties_tool, cid2properties_tool, data_validator_tool

# Configure logging
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
        
        Args:
            llm: The language model instance to be used by the agent
        """
        from src.config.config import Config
        super().__init__(
            llm, 
            "Synthesis_Guiding_agent",  # Role in Chinese
            "设计材料的合成方法和工艺流程",  # Goal in Chinese
            "synthesis_expert_prompt.md",  # Prompt template file
            temperature=Config.SYNTHESIS_EXPERT_TEMPERATURE  # Temperature setting from config
        )
    
    def create_agent(self):
        """Create and configure the agent instance.
        
        Attempts to create an EAS LLM instance first, falls back to 
        the provided LLM if EAS creation fails. Adds chemistry database
        query tools to the agent.
        
        Returns:
            Configured agent instance with necessary tools
        """
        # Try to create EAS model instance
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("成功创建EAS LLM实例")  # Successfully created EAS LLM instance
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"创建EAS模型实例失败: {e}")  # Failed to create EAS model instance
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # Add chemical database query tools for the synthesis guiding agent
        agent.tools = [pubchem_tool, name2cas_tool, name2properties_tool, cid2properties_tool, data_validator_tool]
        return agent
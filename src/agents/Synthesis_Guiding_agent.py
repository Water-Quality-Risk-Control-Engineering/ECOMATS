import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging 
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class SynthesisGuidingAgent(BaseAgent):
    """Synthesis Guiding Agent 
    
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
            "Synthesis_Guiding_agent",  # Role: Synthesis Method Expert 
            "Design material synthesis methods and process flows",  
            "synthesis_guiding_agent_prompt.md",  # Prompt template file
            temperature=Config.SYNTHESIS_EXPERT_TEMPERATURE,  # Temperature setting from config
            max_iter=2  # Less is More: Reduced to 2 iterations (original: 8) - Reuse upstream design, focus on synthesis routes 
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
            logger.info("Successfully created EAS LLM instance ")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"Failed to create EAS model instance : {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # Disable tool calls by default on DashScope compatible endpoint 
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_material_search_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_material_search_tools()
        return agent
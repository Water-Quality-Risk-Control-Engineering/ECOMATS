import logging
from .base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging 
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MechanismMiningAgent(BaseAgent):
    """Mechanism mining expert agent """
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Mechanism_Mining_agent",  # Mechanism mining expert 
            goal="Mine reaction mechanisms and kinetic characteristics of pollutant degradation", 
            prompt_file="mechanism_mining_agent_prompt.md",
            temperature=Config.MECHANISM_EXPERT_TEMPERATURE,
            max_iter=2  # Less is More: Reduced to 2 iterations (original: 8) - Reuse upstream results, focus on mechanism analysis 
        )
    
    def create_agent(self):
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
        # Use mechanism analysis toolset, focusing on material structure and chemical properties 
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_mechanism_analysis_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_mechanism_analysis_tools()
        return agent

import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ExtractingAgent(BaseAgent):
    """
    Literature Processing Agent 
    An intelligent agent responsible for processing and analyzing scientific literature 
    to extract relevant information for material evaluation.
    """

    def __init__(self, llm):
        """Initialize the ExtractingAgent with specified parameters.
        
        Args:
            llm: The language model instance to be used by the agent
        """
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Extracting_agent",  # Literature Processing Expert
            goal="Process and analyze relevant technical literature to provide background information for material evaluation",  
            prompt_file="extracting_agent_prompt.md",
            temperature=Config.LITERATURE_PROCESSOR_TEMPERATURE
        )
    
    def create_agent(self):
        """Create and configure the agent with appropriate tools.
        
        This method attempts to create an EAS LLM instance first, falling back to 
        the provided LLM if EAS creation fails. It then adds chemical database 
        query tools to enhance the agent's capabilities.
        
        Returns:
            Configured agent instance with necessary tools

        """
        # Attempt to create EAS model instance
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
        # Use standardized literature extraction toolset 
        agent.tools = ToolFactory.create_literature_extraction_tools()
        return agent
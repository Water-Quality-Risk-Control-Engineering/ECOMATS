import logging
from src.agents.base_agent import BaseAgent
from src.tools import pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Operation Suggestion Expert Agent class
# This agent provides operational guidance for material synthesis, production and application
class OperationSuggestingAgent(BaseAgent):
    def __init__(self, llm):
        """
        Initialize the Operation Suggestion Agent
        
        Args:
            llm: The language model instance to be used by the agent
        """
        from src.config.config import Config
        super().__init__(
            llm, 
            "Operation_Suggesting_agent",  # Role: Operation Suggestion Expert
            "为材料合成、生产和应用提供详细的操作指导建议",  # Goal: Provide detailed operational guidance for material synthesis, production and application
            "operation_suggesting_prompt.md",  # Prompt template file
            temperature=Config.OPERATION_SUGGESTING_TEMPERATURE  # Temperature setting from config
        )
    
    def create_agent(self):
        """
        Create and configure the operation suggesting agent with appropriate tools
        
        Returns:
            Configured agent instance with chemical database query tools
        """
        # Try to create EAS model instance
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("Successfully created EAS LLM instance")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"Failed to create EAS model instance: {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # Add chemical database query tools for the operation suggesting agent
        agent.tools = [pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool]
        return agent
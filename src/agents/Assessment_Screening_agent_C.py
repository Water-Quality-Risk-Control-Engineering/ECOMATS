import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging / 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentScreeningAgentC(BaseAgent):
    """Assessment and Screening Expert C Agent
    
    A specialized agent responsible for comprehensive evaluation of material proposals
    from multiple perspectives including environmental impact, safety, and feasibility.
    """
    
    def __init__(self, llm):
        """Initialize the Assessment Screening Agent C.
        
        Args:
            llm: The language model instance to be used by this agent

        """
        from src.config.config import Config
        super().__init__(llm, "Assessment_Screening_agent_C", "Comprehensively evaluate various aspects of material proposals",  
                         "assessment_screening_agent_c_prompt.md",  # Use Agent-specific prompt 
                         temperature=Config.EXPERT_C_TEMPERATURE, max_iter=2,  # Less is More: Reduced to 2 iterations (original: 15) - Focus on core evaluation logic 
                         prompt_params={"EXPERT_ID": "C"})  # Parameterized replacement 
    
    def create_agent(self):
        """Create and configure the assessment screening agent.
        
        This method attempts to create an EAS (Expert Agent System) LLM instance first,
        falling back to the provided LLM if EAS creation fails. It then adds chemical
        database query tools to the agent for comprehensive material assessment.
        
        Returns:
            Configured agent instance with necessary tools for material evaluation
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
        # Use unified ASA evaluation toolset (shared by A/B/C) 
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_unified_assessment_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_unified_assessment_tools()
        
        return agent

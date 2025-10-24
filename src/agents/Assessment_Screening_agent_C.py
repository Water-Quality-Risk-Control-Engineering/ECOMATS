import logging
from src.agents.base_agent import BaseAgent
from src.tools import materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool

# Configure logging
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
        super().__init__(llm, "专家C", "全面评估材料方案的各个方面", "expert_c_prompt.md",
                        temperature=Config.EXPERT_C_TEMPERATURE)
    
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
        # Add chemical database query tools for the assessment expert
        agent.tools = [materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool]
        return agent
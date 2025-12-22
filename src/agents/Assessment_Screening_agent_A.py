import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Expert A class for material assessment and screening
class AssessmentScreeningAgentA(BaseAgent):
    def __init__(self, llm):
        """
        Initialize the Assessment Screening Agent A
        
        Args:
            llm: The language model instance to be used by this agent
        """
        from src.config.config import Config
        super().__init__(
            llm, 
            "Assessment_Screening_agent_A",  # Expert A 
            "Comprehensively evaluate various aspects of material proposals",  
            "assessment_screening_agent_a_prompt.md",  # Use Agent-specific prompt 
            temperature=Config.EXPERT_A_TEMPERATURE,
            max_iter=2,  # Less is More: Reduced to 2 iterations (original: 15) - Focus on core evaluation logic 
            prompt_params={"EXPERT_ID": "A"}  # Parameterized replacement 
        )
    
    def create_agent(self):
        """Create and configure the agent with appropriate tools
        
        Returns:
            Configured agent instance with chemical database query tools
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

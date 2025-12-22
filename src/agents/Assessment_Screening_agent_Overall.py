import logging
from .base_agent import BaseAgent
from src.tools import ToolFactory
from src.utils.llm_config import tools_enabled

# Configure logging 
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentScreeningAgentOverall(BaseAgent):
    """Comprehensive assessment and screening expert agent """
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Assessment_Screening_agent_Overall",  # Final validation expert 
            goal="Synthesize evaluation results from various experts, perform weighted calculations, and generate final material evaluation report, while providing improvement suggestions",  # 综合各专家评估结果，进行加权计算并形成最终材料评估报告，同时提供改进建议
            prompt_file="assessment_screening_agent_overall_prompt.md",
            temperature=Config.FINAL_VALIDATOR_TEMPERATURE,
            max_iter=1  # Less is More: Reduced to 1 iteration (original: 8) - Only synthesize existing results, no iteration needed 
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
        # ASA Final 
        # ASA Final does not need tools, only synthesizes outputs from ASA A/B/C
        agent.tools = []
        
        # Enhance prompt to clarify its aggregation role 
        agent.backstory += "\n\nYour core responsibility is to collect evaluation results from three experts (AssessmentScreeningAgentA, B, C), perform weighted calculations and consistency analysis, and generate the final report. You do not need to re-evaluate the material itself, but synthesize existing opinions."

        return agent

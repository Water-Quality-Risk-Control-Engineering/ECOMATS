import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Material Design Expert class
class CreativeDesigningAgent(BaseAgent):
    """Creative Designing Agent for water treatment materials"""
    
    def __init__(self, llm):
        """Initialize the Creative Designing Agent
        
        Args:
            llm: The language model instance
        """
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Creative_Designing_agent",  # Material Design Expert
            goal="Design and optimize water treatment material solutions, strictly following material type classification and structural description specifications",  
            prompt_file="creative_designing_agent_prompt.md",
            temperature=Config.MATERIAL_DESIGNER_TEMPERATURE,
            max_iter=1  # Performance test: Reduced to 1 iteration (original: 8) 
        )
    
    def create_agent(self):
        """Create the agent instance with appropriate tools
        
        Returns:
            Agent: Configured agent instance with tools attached
        """
        # Only try EAS LLM when EAS config is valid
        try:
            from src.config.config import Config
            if Config.EAS_ENDPOINT and Config.EAS_TOKEN and Config.EAS_MODEL_NAME:
                from src.utils.llm_config import create_eas_llm
                eas_llm = create_eas_llm()
                logger.info("Successfully created EAS LLM instance ")
                self.llm = eas_llm
            # Otherwise, silently use the passed LLM without error 
        except Exception as e:
            logger.debug(f"EAS LLM not available, using default : {e}")
        
        agent = super().create_agent()
        # Disable tool calls by default on DashScope compatible endpoint to avoid 500 errors from incompatible function calls 
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_material_design_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_material_design_tools()
        
        # Enhance prompt to require context reuse, minimal fields and rate-limited calls
        agent.backstory += (
            "\n\nWhen outputting design results, include the following detailed information whenever possible:\n"
            "- Materials Project ID (mp-xxx) (if the material exists in the database)\n"
            "- Chemical formula and crystal structure description\n"
            "- Key physical properties (e.g., band gap, density)\n"
            "- Thermodynamic stability (height above convex hull)\n"
            "\nTool Usage Strategy (Rate Limiting & Reuse):\n"
            "- Prioritize reusing already-obtained structure validation or material identifier results; avoid duplicate database searches\n"
            "- Only call Materials Project search when essential information is missing, using minimal field sets\n"
            "- Limit result count for element combination queries to avoid large-scale data retrieval\n"
        )
        
        return agent

# Create instance
material_designer_instance = None

def get_material_designer(llm=None):
    global material_designer_instance
    if material_designer_instance is None and llm is not None:
        material_designer_instance = CreativeDesigningAgent(llm).create_agent()
    return material_designer_instance

# Compatible with old version direct access 
material_designer = None

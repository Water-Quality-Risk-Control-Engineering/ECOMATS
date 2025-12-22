import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging
# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Material Design Expert class / 材料设计专家类
class CreativeDesigningAgent(BaseAgent):
    """Creative Designing Agent for water treatment materials"""
    
    def __init__(self, llm):
        """Initialize the Creative Designing Agent
        初始化创意设计智能体
        
        Args:
            llm: The language model instance
                 语言模型实例
        """
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Creative_Designing_agent",  # Material Design Expert
            goal="Design and optimize water treatment material solutions, strictly following material type classification and structural description specifications",  # 设计和优化水处理材料方案，严格按照材料类型分类和结构描述规范进行设计
            prompt_file="creative_designing_agent_prompt.md",
            temperature=Config.MATERIAL_DESIGNER_TEMPERATURE,
            max_iter=1  # Performance test: Reduced to 1 iteration (original: 8) / 性能测试：降至1次（原值：8）
        )
    
    def create_agent(self):
        """Create the agent instance with appropriate tools
        创建带有适当工具的智能体实例
        
        Returns:
            Agent: Configured agent instance with tools attached
                   配置好的带有工具的智能体实例
        """
        # 仅在 EAS 配置有效时尝试创建 EAS LLM
        # Only try EAS LLM when EAS config is valid
        try:
            from src.config.config import Config
            if Config.EAS_ENDPOINT and Config.EAS_TOKEN and Config.EAS_MODEL_NAME:
                from src.utils.llm_config import create_eas_llm
                eas_llm = create_eas_llm()
                logger.info("Successfully created EAS LLM instance / 成功创建EAS LLM实例")
                self.llm = eas_llm
            # Otherwise, silently use the passed LLM without error / 否则静默使用传入的 LLM，无需报错
        except Exception as e:
            logger.debug(f"EAS LLM not available, using default / EAS LLM不可用，使用默认: {e}")
        
        agent = super().create_agent()
        # Disable tool calls by default on DashScope compatible endpoint to avoid 500 errors from incompatible function calls / 在 DashScope 兼容端点默认禁用工具调用，避免函数调用不兼容导致 500
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

# Create instance / 创建实例
material_designer_instance = None

def get_material_designer(llm=None):
    global material_designer_instance
    if material_designer_instance is None and llm is not None:
        material_designer_instance = CreativeDesigningAgent(llm).create_agent()
    return material_designer_instance

# Compatible with old version direct access / 兼容旧版本的直接访问方式
material_designer = None

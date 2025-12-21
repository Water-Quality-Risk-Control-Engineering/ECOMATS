import logging
from src.agents.base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging / 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentScreeningAgentC(BaseAgent):
    """Assessment and Screening Expert C Agent
    评估筛选专家C智能体
    
    A specialized agent responsible for comprehensive evaluation of material proposals
    from multiple perspectives including environmental impact, safety, and feasibility.
    从环境影响、安全性和可行性等多个角度负责对材料方案进行全面评估的专业智能体
    """
    
    def __init__(self, llm):
        """Initialize the Assessment Screening Agent C.
        初始化评估筛选专家C智能体
        
        Args:
            llm: The language model instance to be used by this agent
                 用于此智能体的语言模型实例
        """
        from src.config.config import Config
        super().__init__(llm, "Assessment_Screening_agent_C", "Comprehensively evaluate various aspects of material proposals",  # 全面评估材料方案的各个方面
                         "expert_template_prompt.md",  # Use parameterized template / 使用参数化模板
                         temperature=Config.EXPERT_C_TEMPERATURE, max_iter=2,  # Less is More: Reduced to 2 iterations (original: 15) - Focus on core evaluation logic / 降至2次（原值：15）- 聚焦核心评估逻辑
                         prompt_params={"EXPERT_ID": "C"})  # Parameterized replacement / 参数化替换
    
    def create_agent(self):
        """Create and configure the assessment screening agent.
        创建并配置评估筛选智能体
        
        This method attempts to create an EAS (Expert Agent System) LLM instance first,
        falling back to the provided LLM if EAS creation fails. It then adds chemical
        database query tools to the agent for comprehensive material assessment.
        此方法首先尝试创建EAS模型实例，如果创建失败则回退到传入的LLM。
        然后添加化学数据库查询工具以进行全面的材料评估。
        
        Returns:
            Configured agent instance with necessary tools for material evaluation
            配置好的智能体实例，包含材料评估所需的工具
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
        # Use unified ASA evaluation toolset (shared by A/B/C) / 使用统一的 ASA 评估工具集 (A/B/C 共用)
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_unified_assessment_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_unified_assessment_tools()
        
        return agent

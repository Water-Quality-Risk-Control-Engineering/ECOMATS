import logging
from .base_agent import BaseAgent
from src.tools import ToolFactory

# Configure logging / 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MechanismMiningAgent(BaseAgent):
    """Mechanism mining expert agent / 机理挖掘专家智能体"""
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Mechanism_Mining_agent",  # Mechanism mining expert / 机理挖掘专家
            goal="Mine reaction mechanisms and kinetic characteristics of pollutant degradation",  # 挖掘污染物降解的反应机理和动力学特性
            prompt_file="mechanism_mining_agent_prompt.md",
            temperature=Config.MECHANISM_EXPERT_TEMPERATURE,
            max_iter=2  # Less is More: Reduced to 2 iterations (original: 8) - Reuse upstream results, focus on mechanism analysis / 降至2次（原值：8）- 复用上游结果，聚焦机理分析
        )
    
    def create_agent(self):
        # Try to create EAS model instance / 尝试创建EAS模型实例
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
        # Use mechanism analysis toolset, focusing on material structure and chemical properties / 使用机理分析专用工具集，聚焦于材料结构和化学性质
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_mechanism_analysis_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_mechanism_analysis_tools()
        return agent

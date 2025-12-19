import logging
from .base_agent import BaseAgent
from src.tools import ToolFactory

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class MechanismMiningAgent(BaseAgent):
    """机理挖掘专家智能体 / Mechanism mining expert agent"""
    
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Mechanism_Mining_agent",  # 机理挖掘专家 / Mechanism mining expert
            goal="挖掘污染物降解的反应机理和动力学特性",  # 挖掘污染物降解的反应机理和动力学特性 / Mine reaction mechanisms and kinetic characteristics of pollutant degradation
            prompt_file="mechanism_expert_prompt.md",
            temperature=Config.MECHANISM_EXPERT_TEMPERATURE,
            max_iter=8  # 复用上游结果，较少迭代
        )
    
    def create_agent(self):
        # 尝试创建EAS模型实例
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("成功创建EAS LLM实例")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"创建EAS模型实例失败: {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # 使用机理分析专用工具集，聚焦于材料结构和化学性质
        try:
            from src.utils.llm_config import tools_enabled
            if tools_enabled():
                agent.tools = ToolFactory.create_mechanism_analysis_tools()
            else:
                agent.tools = []
        except Exception:
            agent.tools = ToolFactory.create_mechanism_analysis_tools()
        return agent

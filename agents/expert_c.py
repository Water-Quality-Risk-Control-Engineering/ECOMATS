import logging
from agents.base_agent import BaseAgent

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 专家C类
class ExpertC(BaseAgent):
    def __init__(self, llm):
        from config.config import Config
        super().__init__(llm, "专家C", "全面评估材料方案的各个方面", "expert_c_prompt.md",
                        temperature=Config.EXPERT_EVALUATION_TEMPERATURE)
    
    def create_agent(self):
        # 尝试创建EAS模型实例
        try:
            eas_llm = create_eas_llm()
            logger.warning("成功创建EAS LLM实例")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"创建EAS模型实例失败: {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        return super().create_agent()
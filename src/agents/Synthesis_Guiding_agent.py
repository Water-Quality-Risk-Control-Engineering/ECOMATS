import logging
from src.agents.base_agent import BaseAgent
from tools import pubchem_tool, name2cas_tool, name2properties_tool, cid2properties_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 合成方法专家类
class SynthesisGuidingAgent(BaseAgent):
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(llm, "合成方法专家", "设计材料的合成方法和工艺流程", "synthesis_expert_prompt.md",
                        temperature=Config.SYNTHESIS_EXPERT_TEMPERATURE)
    
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
        # 为合成方法专家添加化学数据库查询工具
        agent.tools = [pubchem_tool, name2cas_tool, name2properties_tool, cid2properties_tool]
        return agent
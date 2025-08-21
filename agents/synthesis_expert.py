import logging
from agents.base_agent import BaseAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 合成方法专家类
class SynthesisExpert(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "合成方法专家", "设计材料的合成方法和工艺流程", "synthesis_expert_prompt.md")
    
    def create_agent(self):
        return super().create_agent()
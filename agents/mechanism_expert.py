import logging
from agents.base_agent import BaseAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 机理分析专家类
class MechanismExpert(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "机理分析专家", "分析材料的催化机理和作用机制，提供理论支持", "mechanism_expert_prompt.md")
    
    def create_agent(self):
        return super().create_agent()
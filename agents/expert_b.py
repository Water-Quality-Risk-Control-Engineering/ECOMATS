import logging
from agents.base_agent import BaseAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 专家B类
class ExpertB(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "专家B", "全面评估材料方案的各个方面", "expert_b_prompt.md")
    
    def create_agent(self):
        return super().create_agent()
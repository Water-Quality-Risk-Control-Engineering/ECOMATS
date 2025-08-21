import logging
from agents.base_agent import BaseAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 最终验证专家类
class FinalValidator(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "最终验证专家", "综合各专家评估结果，进行加权计算并形成最终材料评估报告", "final_validator_prompt.md")
    
    def create_agent(self):
        return super().create_agent()
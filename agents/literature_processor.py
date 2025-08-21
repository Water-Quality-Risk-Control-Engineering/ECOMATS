import logging
from agents.base_agent import BaseAgent
from tools import pubchem_tool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 文献处理专家类
class LiteratureProcessor(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "文献处理专家", "处理和分析相关技术文献，为材料评估提供背景信息", "literature_processor_prompt.md")
    
    def create_agent(self):
        agent = super().create_agent()
        # 为文献处理专家添加化学数据库查询工具
        agent.tools = [pubchem_tool]
        return agent
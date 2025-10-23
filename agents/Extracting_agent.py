import logging
from agents.base_agent import BaseAgent
from tools import pubchem_tool, name2properties_tool, cid2properties_tool, material_search_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 文献处理专家类
class ExtractingAgent(BaseAgent):
    def __init__(self, llm):
        from config.config import Config
        super().__init__(llm, "文献处理专家", "处理和分析相关技术文献，为材料评估提供背景信息", "literature_processor_prompt.md",
                        temperature=Config.LITERATURE_PROCESSOR_TEMPERATURE)
    
    def create_agent(self):
        # 尝试创建EAS模型实例
        try:
            from utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("成功创建EAS LLM实例")
            # Update the llm attribute to use EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"创建EAS模型实例失败: {e}")
            # If EAS configuration fails, use the passed LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # 为文献处理专家添加化学数据库查询工具
        agent.tools = [pubchem_tool, name2properties_tool, cid2properties_tool, material_search_tool]
        return agent
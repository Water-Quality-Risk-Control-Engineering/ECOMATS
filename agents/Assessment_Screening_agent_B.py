import logging
from agents.base_agent import BaseAgent
from tools import materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 专家B类
class AssessmentScreeningAgentB(BaseAgent):
    def __init__(self, llm):
        from config.config import Config
        super().__init__(llm, "专家B", "全面评估材料方案的各个方面", "expert_b_prompt.md",
                        temperature=Config.EXPERT_B_TEMPERATURE)
    
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
        # 为评估专家添加化学数据库查询工具
        agent.tools = [materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, pnec_tool]
        return agent
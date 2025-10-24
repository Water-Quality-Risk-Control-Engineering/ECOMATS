import logging
from .base_agent import BaseAgent

class MechanismMiningAgent(BaseAgent):
    """机理挖掘专家智能体 / Mechanism mining expert agent"""
    
    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="机理挖掘专家",  # 机理挖掘专家 / Mechanism mining expert
            goal="挖掘污染物降解的反应机理和动力学特性",  # 挖掘污染物降解的反应机理和动力学特性 / Mine reaction mechanisms and kinetic characteristics of pollutant degradation
            prompt_file="mechanism_expert_prompt.md",
            temperature=0.3
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
        # 为机理分析专家添加化学数据库查询工具
        agent.tools = [materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, material_search_tool]
        return agent

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 机理分析专家类
class MechanismMiningAgent(BaseAgent):
    def __init__(self, llm):
        from src.config.config import Config
        super().__init__(llm, "机理分析专家", "分析材料的催化机理和作用机制，提供理论支持", "mechanism_expert_prompt.md",
                        temperature=Config.MECHANISM_EXPERT_TEMPERATURE)
    
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
        # 为机理分析专家添加化学数据库查询工具
        agent.tools = [materials_project_tool, pubchem_tool, name2properties_tool, cid2properties_tool, material_search_tool]
        return agent

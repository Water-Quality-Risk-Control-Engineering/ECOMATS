import logging
from agents.base_agent import BaseAgent
from crewai import Agent
from utils.prompt_loader import load_prompt
from tools import materials_project_tool, pubchem_tool, name2cas_tool, name2properties_tool, formula2properties_tool, material_search_tool

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 材料设计专家类
class CreativeDesigningAgent(BaseAgent):
    def __init__(self, llm):
        from config.config import Config
        super().__init__(llm, "材料设计专家", "设计和优化水处理材料方案", "material_designer_prompt.md", 
                        temperature=Config.MATERIAL_DESIGNER_TEMPERATURE)
    
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
        # 为材料设计专家添加化学数据库查询工具
        agent.tools = [materials_project_tool, pubchem_tool, name2cas_tool, name2properties_tool, formula2properties_tool, material_search_tool]
        return agent

# 创建实例
material_designer_instance = None

def get_material_designer(llm=None):
    global material_designer_instance
    if material_designer_instance is None and llm is not None:
        material_designer_instance = CreativeDesigningAgent(llm).create_agent()
    return material_designer_instance

# 兼容旧版本的直接访问方式
material_designer = None
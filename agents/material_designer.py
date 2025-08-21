import logging
from agents.base_agent import BaseAgent
from crewai import Agent
from utils.prompt_loader import load_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 材料设计专家类
class MaterialDesigner(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "材料设计专家", "设计和优化水处理材料方案", "material_designer_prompt.md")
    
    def create_agent(self):
        return super().create_agent()

# 创建实例
material_designer_instance = None

def get_material_designer(llm=None):
    global material_designer_instance
    if material_designer_instance is None and llm is not None:
        material_designer_instance = MaterialDesigner(llm).create_agent()
    return material_designer_instance

# 兼容旧版本的直接访问方式
material_designer = None
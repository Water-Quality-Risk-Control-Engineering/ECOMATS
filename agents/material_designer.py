import logging
import os
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 读取材料设计专家的Prompt文件内容作为backstory
def load_prompt(file_path):
    """加载Prompt文件内容"""
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建Prompt文件的完整路径 (现在在上级目录的prompt文件夹中)
        prompt_file_path = os.path.join(current_dir, "..", "prompt", file_path)
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.warning(f"Prompt文件 {file_path} 未找到，使用默认backstory")
        return """你是一位专业的材料设计专家，熟悉各种水处理材料的设计原理和方法。
        你能够根据目标需求设计材料结构，优化材料性能。"""
    except Exception as e:
        logger.error(f"读取Prompt文件时出错: {e}")
        return """你是一位专业的材料设计专家，熟悉各种水处理材料的设计原理和方法。
        你能够根据目标需求设计材料结构，优化材料性能。"""

# 材料设计专家类
class MaterialDesigner:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        return Agent(
            role="材料设计专家",
            goal="设计和优化水处理材料方案",
            backstory=load_prompt("material_designer_prompt.md"),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

# 创建实例
material_designer_instance = None

def get_material_designer(llm=None):
    global material_designer_instance
    if material_designer_instance is None and llm is not None:
        material_designer_instance = MaterialDesigner(llm).create_agent()
    return material_designer_instance

# 兼容旧版本的直接访问方式
material_designer = None
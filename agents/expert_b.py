import logging
import os
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 读取专家B的Prompt文件内容作为backstory
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
        return """你是一位专业的材料评估专家，具有丰富的材料科学知识和评估经验。
        你会从所有五个维度全面评估水处理材料方案。"""
    except Exception as e:
        logger.error(f"读取Prompt文件时出错: {e}")
        return """你是一位专业的材料评估专家，具有丰富的材料科学知识和评估经验。
        你会从所有五个维度全面评估水处理材料方案。"""

# 专家B类
class ExpertB:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        return Agent(
            role="专家B",
            goal="全面评估材料方案的各个方面",
            backstory=load_prompt("expert_b_prompt.md"),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
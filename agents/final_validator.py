import logging
import os
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 读取最终验证专家的Prompt文件内容作为backstory
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
        return """你是一位资深的材料科学专家，具有丰富的项目评审和方案验证经验。
        你能够综合各专家的评估结果，计算平均分并应用权重，生成最终的材料评估报告。"""
    except Exception as e:
        logger.error(f"读取Prompt文件时出错: {e}")
        return """你是一位资深的材料科学专家，具有丰富的项目评审和方案验证经验。
        你能够综合各专家的评估结果，计算平均分并应用权重，生成最终的材料评估报告。"""

# 最终验证专家类
class FinalValidator:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        return Agent(
            role="最终验证专家",
            goal="综合各专家评估结果，进行加权计算并形成最终材料评估报告",
            backstory=load_prompt("final_validator_prompt.md"),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
import logging
import os
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 读取机理分析专家的Prompt文件内容作为backstory
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
        return """你是一位专业的材料机理分析专家，熟悉各种材料的催化机理和作用机制。
        你能够结合材料的结构特征，深入分析其催化过程和反应机理。"""
    except Exception as e:
        logger.error(f"读取Prompt文件时出错: {e}")
        return """你是一位专业的材料机理分析专家，熟悉各种材料的催化机理和作用机制。
        你能够结合材料的结构特征，深入分析其催化过程和反应机理。"""

# 机理分析专家
mechanism_expert = Agent(
    role="机理分析专家",
    goal="分析材料的催化机理和作用机制，提供理论支持",
    backstory=load_prompt("mechanism_expert_prompt.md"),
    verbose=True,
    allow_delegation=False,
)
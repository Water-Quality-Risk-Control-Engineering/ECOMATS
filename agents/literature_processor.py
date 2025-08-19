import logging
import os
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 读取文献处理专家的Prompt文件内容作为backstory
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
        return """你是一位专业的文献处理专家，熟悉科技文献的处理和分析方法。
        你能够快速提取文献中的关键信息，为材料设计和评估提供参考。"""
    except Exception as e:
        logger.error(f"读取Prompt文件时出错: {e}")
        return """你是一位专业的文献处理专家，熟悉科技文献的处理和分析方法。
        你能够快速提取文献中的关键信息，为材料设计和评估提供参考。"""

# 文献处理专家
literature_processor = Agent(
    role="文献处理专家",
    goal="处理和分析相关技术文献，为材料评估提供背景信息",
    backstory=load_prompt("literature_processor_prompt.md"),
    verbose=True,
    allow_delegation=False,
)
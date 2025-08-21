import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        return """你是一位专业的项目协调专家，熟悉材料设计和评估的各个环节。
        你能够根据任务需求，智能地选择和协调相关专家参与工作。"""
    except Exception as e:
        logger.error(f"读取Prompt文件时出错: {e}")
        return """你是一位专业的项目协调专家，熟悉材料设计和评估的各个环节。
        你能够根据任务需求，智能地选择和协调相关专家参与工作。"""
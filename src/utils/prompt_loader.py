import logging
import os

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def load_prompt(file_path):
    """加载Prompt文件内容 / Load Prompt file content"""
    try:
        # 获取当前文件所在目录 / Get the directory where the current file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建Prompt文件的完整路径 (现在在上级目录的prompts文件夹中)
        # Build the full path of the Prompt file (now in the prompts folder of the parent directory)
        prompt_file_path = os.path.join(current_dir, "..", "prompts", file_path)
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        # Prompt文件未找到，使用默认backstory / Prompt file not found, using default backstory
        logger.warning(f"Prompt文件 {file_path} 未找到，使用默认backstory / Prompt file {file_path} not found, using default backstory")
        return """你是一位专业的项目协调专家，熟悉材料设计和评估的各个环节。
        你能够根据任务需求，智能地选择和协调相关专家参与工作。
        / You are a professional project coordination expert, familiar with all aspects of material design and evaluation.
        You can intelligently select and coordinate relevant experts to participate in the work according to task requirements."""
    except Exception as e:
        # 加载Prompt文件时发生未知错误 / Unknown error occurred while loading Prompt file
        logger.error(f"加载Prompt文件 {file_path} 时发生错误: {str(e)} / Error occurred while loading Prompt file {file_path}: {str(e)}")
        return """你是一位专业的项目协调专家，熟悉材料设计和评估的各个环节。
        你能够根据任务需求，智能地选择和协调相关专家参与工作。
        / You are a professional project coordination expert, familiar with all aspects of material design and evaluation.
        You can intelligently select and coordinate relevant experts to participate in the work according to task requirements."""
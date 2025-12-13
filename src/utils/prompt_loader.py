import logging
import os

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_language():
    """获取当前语言设置 / Get current language setting"""
    try:
        from src.config.config import Config
        return Config.LANGUAGE
    except Exception:
        return os.getenv("LANGUAGE", "zh")


def load_prompt(file_path):
    """加载Prompt文件内容，支持多语言 / Load Prompt file content with multilingual support"""
    try:
        # 获取当前语言 / Get current language
        lang = get_language()
        
        # 获取当前文件所在目录 / Get the directory where the current file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 优先尝试加载多语言版本 / Try to load multilingual version first
        locale_prompt_path = os.path.join(current_dir, "..", "locales", lang, "prompts", file_path)
        
        if os.path.exists(locale_prompt_path):
            with open(locale_prompt_path, 'r', encoding='utf-8') as file:
                logger.debug(f"Loaded {lang} prompt: {file_path}")
                return file.read()
        
        # 回退到默认prompts目录 / Fallback to default prompts directory
        default_prompt_path = os.path.join(current_dir, "..", "prompts", file_path)
        
        if os.path.exists(default_prompt_path):
            with open(default_prompt_path, 'r', encoding='utf-8') as file:
                logger.debug(f"Loaded default prompt: {file_path}")
                return file.read()
        
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
        
    except FileNotFoundError:
        # Prompt文件未找到，使用默认backstory / Prompt file not found, using default backstory
        logger.warning(f"Prompt文件 {file_path} 未找到，使用默认backstory / Prompt file {file_path} not found, using default backstory")
        return get_default_backstory()
    except Exception as e:
        # 加载Prompt文件时发生未知错误 / Unknown error occurred while loading Prompt file
        logger.error(f"加载Prompt文件 {file_path} 时发生错误: {str(e)} / Error occurred while loading Prompt file {file_path}: {str(e)}")
        return get_default_backstory()


def get_default_backstory():
    """获取默认backstory / Get default backstory"""
    lang = get_language()
    if lang == "en":
        return """You are a professional project coordination expert, familiar with all aspects of material design and evaluation.
You can intelligently select and coordinate relevant experts to participate in the work according to task requirements."""
    else:
        return """你是一位专业的项目协调专家，熟悉材料设计和评估的各个环节。
你能够根据任务需求，智能地选择和协调相关专家参与工作。"""
"""
ECOMATS 多语言支持模块
Multilingual support module for ECOMATS

支持语言 / Supported languages:
- zh: 中文 (Chinese)
- en: English

使用方法 / Usage:
    from src.locales import get_text, get_prompt_path, set_language
    
    # 设置语言 / Set language
    set_language("zh")  # 或 "en"
    
    # 获取文本 / Get text
    text = get_text("tasks", "design_task", "description")
    
    # 获取prompt文件路径 / Get prompt file path
    path = get_prompt_path("material_designer_prompt.md")
"""

import os
from typing import Optional

# 默认语言 / Default language
_current_language = "zh"

# 支持的语言列表 / Supported languages
SUPPORTED_LANGUAGES = ["zh", "en"]

# 模块根目录 / Module root directory
LOCALES_DIR = os.path.dirname(os.path.abspath(__file__))


def set_language(lang: str) -> None:
    """
    设置当前语言 / Set current language
    
    Args:
        lang: 语言代码 ("zh" 或 "en") / Language code ("zh" or "en")
    """
    global _current_language
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}. Supported: {SUPPORTED_LANGUAGES}")
    _current_language = lang


def get_language() -> str:
    """
    获取当前语言 / Get current language
    
    Returns:
        当前语言代码 / Current language code
    """
    return _current_language


def get_prompt_path(prompt_name: str) -> str:
    """
    获取prompt文件路径 / Get prompt file path
    
    Args:
        prompt_name: prompt文件名 / Prompt filename
        
    Returns:
        prompt文件的完整路径 / Full path to prompt file
    """
    path = os.path.join(LOCALES_DIR, _current_language, "prompts", prompt_name)
    
    # 如果当前语言的文件不存在,回退到默认prompts目录
    # Fallback to default prompts directory if not found
    if not os.path.exists(path):
        fallback_path = os.path.join(os.path.dirname(LOCALES_DIR), "prompts", prompt_name)
        if os.path.exists(fallback_path):
            return fallback_path
    
    return path


def get_text(category: str, key: str, field: str) -> str:
    """
    获取本地化文本 / Get localized text
    
    Args:
        category: 文本分类 (如 "tasks", "agents") / Text category
        key: 文本键 (如 "design_task") / Text key
        field: 字段名 (如 "description") / Field name
        
    Returns:
        本地化文本 / Localized text
    """
    from src.locales.texts import TEXTS
    
    lang = _current_language
    try:
        return TEXTS[lang][category][key][field]
    except KeyError:
        # 回退到中文
        try:
            return TEXTS["zh"][category][key][field]
        except KeyError:
            return f"[Missing text: {category}.{key}.{field}]"


def load_prompt(prompt_name: str) -> str:
    """
    Load prompt file content.
    Delegates to utils.prompt_loader for unified implementation.
    
    Args:
        prompt_name: prompt filename
        
    Returns:
        prompt content
    """
    from src.utils.prompt_loader import load_prompt as _load_prompt
    return _load_prompt(prompt_name)

"""
ECOMATS
Multilingual support module for ECOMATS

Supported languages:
- zh: (Chinese)
- en: English

Usage:
    from src.locales import get_text, get_prompt_path, set_language
    
    Set language
    set_language("zh")  # or "en"
    
    Get text
    text = get_text("tasks", "design_task", "description")
    
    Get prompt file path
    path = get_prompt_path("material_designer_prompt.md")
"""

import os
from typing import Optional

# Default language
_current_language = "zh"

# Supported languages
SUPPORTED_LANGUAGES = ["zh", "en"]

# Module root directory
LOCALES_DIR = os.path.dirname(os.path.abspath(__file__))


def set_language(lang: str) -> None:
    """
    Set current language
    
    Args:
        lang: Language code ("zh" or "en")
    """
    global _current_language
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}. Supported: {SUPPORTED_LANGUAGES}")
    _current_language = lang


def get_language() -> str:
    """
    Get current language
    
    Returns:
        Current language code
    """
    return _current_language


def get_prompt_path(prompt_name: str) -> str:
    """
    Get prompt file path
    
    Args:
        prompt_name: Prompt filename
        
    Returns:
        Full path to prompt file
    """
    path = os.path.join(LOCALES_DIR, _current_language, "prompts", prompt_name)
    
    # Fallback to default prompts directory if not found
    if not os.path.exists(path):
        fallback_path = os.path.join(os.path.dirname(LOCALES_DIR), "prompts", prompt_name)
        if os.path.exists(fallback_path):
            return fallback_path
    
    return path


def get_text(category: str, key: str, field: str) -> str:
    """
    Get localized text
    
    Args:
        category: Text category
        key: Text key
        field: Field name
        
    Returns:
        Localized text
    """
    from src.locales.texts import TEXTS
    
    lang = _current_language
    try:
        return TEXTS[lang][category][key][field]
    except KeyError:
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

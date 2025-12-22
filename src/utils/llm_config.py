#!/usr/bin/env python3
"""
LLM Configuration Tool.
Provides EAS model instance creation and CrewAI native LLM factory.
"""

import os
from dotenv import load_dotenv
from crewai import LLM as CrewLLM
from ..config.config import Config


def _ensure_openai_env():
    """Disable bridging of OPENAI_* environment variables to avoid conflicts between domestic sites and OpenAI defaults."""
    # Keep only DashScope recommended environment variables for third-party dependencies
    if Config.QWEN_API_KEY and not os.getenv("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = Config.QWEN_API_KEY


def _resolve_base_url():
    """Resolve available base_url (strictly use QWEN_API_BASE)."""
    return os.getenv("QWEN_API_BASE") or Config.QWEN_API_BASE


def _resolve_api_key():
    """Resolve available api_key (strictly use QWEN_API_KEY or DASHSCOPE_API_KEY)."""
    return os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or Config.QWEN_API_KEY

def _force_load_env():
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        dotenv_path = os.path.join(project_root, '.env')
        load_dotenv(dotenv_path, override=True)
    except Exception:
        pass

def create_llm(temperature=None, max_tokens=None):
    """
    Create and configure language model instance (CrewAI native).
    
    Args:
        temperature (float, optional): Model temperature parameter, controlling output randomness
        max_tokens (int, optional): Maximum token limit
        
    Returns:
        CrewLLM: Configured language model instance
    """
    # Force load .env from project root with override to avoid IDE/terminal environment differences
    _force_load_env()
    # Only set DashScope environment variables to avoid OPENAI_* interference
    _ensure_openai_env()

    # Check model name
    # Automatic fallback to domestic model if model name is unavailable
    model_name = Config.QWEN_MODEL_NAME or "qwen-plus"
    if not model_name:
        raise ValueError("QWEN_MODEL_NAME not set in environment variables")
    # Check API key
    api_key = _resolve_api_key()
    if not api_key:
        raise ValueError("API key not detected, please set QWEN_API_KEY in .env or export OPENAI_API_KEY/DASHSCOPE_API_KEY")
    base_url = _resolve_base_url()
    # Automatic correction for domestic sites: prioritize domestic endpoint if not explicitly set to domestic site
    if not base_url or "dashscope-intl" in (base_url or ""):
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # Use CrewAI native LLM for better compatibility with OpenAI-compatible interfaces
    llm = CrewLLM(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature or Config.MODEL_TEMPERATURE,
        max_tokens=max_tokens or Config.MODEL_MAX_TOKENS,
    )

    return llm

def create_eas_llm(temperature=None):
    """Create EAS model instance.
    
    Returns:
        CrewLLM: EAS model instance
    """
    # Force load .env from project root with override to avoid IDE/terminal environment differences
    _force_load_env()
    # Check if EAS config exists
    if not Config.EAS_ENDPOINT or not Config.EAS_TOKEN:
        raise ValueError("EAS config not set, please configure valid EAS_ENDPOINT and EAS_TOKEN in .env file")
    
    # Check model name
    model_name = Config.EAS_MODEL_NAME
    if not model_name:
        raise ValueError("EAS_MODEL_NAME not set in environment variables")
    
    # Use full model name defined in environment variables without prefix processing
    # Use configured EAS endpoint URL (without adding extra path)
    base_url = Config.EAS_ENDPOINT
    
    try:
        # Create EAS model instance (CrewAI native)
        eas_llm = CrewLLM(
            model=model_name,
            base_url=base_url,
            api_key=Config.EAS_TOKEN,
            temperature=temperature or Config.MODEL_TEMPERATURE,
            max_tokens=Config.MODEL_MAX_TOKENS,
        )
        return eas_llm
    except Exception as e:
        print(f"Failed to create EAS model instance: {e}")
        raise

def tools_enabled() -> bool:
    """Determine whether to enable tool calls based on endpoint and environment variables.
    - If `ENABLE_TOOLS=false` is set, disable
    - If endpoint is DashScope compatible mode (contains `dashscope` and `compatible-mode`), disable by default
    - Otherwise enable by default.
    """
    env = os.getenv("ENABLE_TOOLS")
    if env is not None:
        return env.lower() == "true"
    base = _resolve_base_url() or ""
    if "dashscope" in base and "compatible-mode" in base:
        return False
    return True

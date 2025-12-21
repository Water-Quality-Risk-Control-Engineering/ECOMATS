#!/usr/bin/env python3
"""
LLM Configuration Tool / LLM配置工具
Provides EAS model instance creation and CrewAI native LLM factory
提供EAS模型实例创建功能与CrewAI原生LLM工厂
"""

import os
from dotenv import load_dotenv
from crewai import LLM as CrewLLM
from ..config.config import Config


def _ensure_openai_env():
    """Disable bridging of OPENAI_* environment variables to avoid conflicts between domestic sites and OpenAI defaults
    禁用对 OPENAI_* 环境变量的桥接，避免国内站点与OpenAI默认配置冲突
    """
    # Keep only DashScope recommended environment variables for third-party dependencies / 仅保留 DashScope 推荐的环境变量，供可能依赖 DASHSCOPE_API_KEY 的第三方使用
    if Config.QWEN_API_KEY and not os.getenv("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = Config.QWEN_API_KEY


def _resolve_base_url():
    """Resolve available base_url (strictly use QWEN_API_BASE)
    解析可用的 base_url（严格使用 QWEN_API_BASE）
    """
    return os.getenv("QWEN_API_BASE") or Config.QWEN_API_BASE


def _resolve_api_key():
    """Resolve available api_key (strictly use QWEN_API_KEY or DASHSCOPE_API_KEY)
    解析可用的 api_key（严格使用 QWEN_API_KEY 或 DASHSCOPE_API_KEY）
    """
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
    创建并配置语言模型实例（CrewAI原生） / Create and configure language model instance (CrewAI native)
    
    Args:
        temperature (float, optional): 模型温度参数，控制输出随机性 / Model temperature parameter, controlling output randomness
        max_tokens (int, optional): 最大令牌数限制 / Maximum token limit
        
    Returns:
        CrewLLM: 配置好的语言模型实例 / Configured language model instance
    """
    # Force load .env from project root with override to avoid IDE/terminal environment differences / 强制加载项目根目录的 .env 并覆盖，避免IDE/终端环境差异
    _force_load_env()
    # Only set DashScope environment variables to avoid OPENAI_* interference / 仅设置 DashScope 环境变量，避免 OPENAI_* 干扰
    _ensure_openai_env()

    # Check model name / 检查模型名称
    # Automatic fallback to domestic model if model name is unavailable / 若模型名不可用，进行国内站模型的自动回退
    model_name = Config.QWEN_MODEL_NAME or "qwen-plus"
    if not model_name:
        raise ValueError("QWEN_MODEL_NAME not set in environment variables / QWEN_MODEL_NAME 未在环境变量中设置")
    # Check API key / 检查API密钥
    api_key = _resolve_api_key()
    if not api_key:
        raise ValueError("API key not detected, please set QWEN_API_KEY in .env or export OPENAI_API_KEY/DASHSCOPE_API_KEY / 未检测到API密钥，请在.env中设置 QWEN_API_KEY 或导出 OPENAI_API_KEY/DASHSCOPE_API_KEY")
    base_url = _resolve_base_url()
    # Automatic correction for domestic sites: prioritize domestic endpoint if not explicitly set to domestic site / 国内站自动修正：若未显式设置为国内站，优先使用国内站端点
    if not base_url or "dashscope-intl" in (base_url or ""):
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # Use CrewAI native LLM for better compatibility with OpenAI-compatible interfaces / 使用CrewAI原生LLM以提高与OpenAI兼容接口的兼容性
    llm = CrewLLM(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature or Config.MODEL_TEMPERATURE,
        max_tokens=max_tokens or Config.MODEL_MAX_TOKENS,
    )

    return llm

def create_eas_llm(temperature=None):
    """Create EAS model instance
    创建EAS模型实例
    
    Returns:
        CrewLLM: EAS model instance / EAS模型实例
    """
    # Force load .env from project root with override to avoid IDE/terminal environment differences / 强制加载项目根目录的 .env 并覆盖，避免IDE/终端环境差异
    _force_load_env()
    # Check if EAS config exists / 检查EAS配置是否存在
    if not Config.EAS_ENDPOINT or not Config.EAS_TOKEN:
        raise ValueError("EAS config not set, please configure valid EAS_ENDPOINT and EAS_TOKEN in .env file / EAS配置未设置，请在.env文件中配置有效的EAS_ENDPOINT和EAS_TOKEN")
    
    # Check model name / 检查模型名称
    model_name = Config.EAS_MODEL_NAME
    if not model_name:
        raise ValueError("EAS_MODEL_NAME not set in environment variables / EAS_MODEL_NAME 未在环境变量中设置")
    
    # Use full model name defined in environment variables without prefix processing / 使用环境变量中定义的完整模型名称，不进行前缀处理
    # Use configured EAS endpoint URL (without adding extra path) / 使用配置的EAS端点URL（不添加额外路径）
    base_url = Config.EAS_ENDPOINT
    
    try:
        # Create EAS model instance (CrewAI native) / 创建EAS模型实例（CrewAI原生）
        eas_llm = CrewLLM(
            model=model_name,
            base_url=base_url,
            api_key=Config.EAS_TOKEN,
            temperature=temperature or Config.MODEL_TEMPERATURE,
            max_tokens=Config.MODEL_MAX_TOKENS,
        )
        return eas_llm
    except Exception as e:
        print(f"Failed to create EAS model instance / 创建EAS模型实例失败: {e}")
        raise

def tools_enabled() -> bool:
    """Determine whether to enable tool calls based on endpoint and environment variables.
    根据端点与环境变量判断是否启用工具调用。
    - If `ENABLE_TOOLS=false` is set, disable / 若设置 `ENABLE_TOOLS=false` 则禁用
    - If endpoint is DashScope compatible mode (contains `dashscope` and `compatible-mode`), disable by default / 若端点为 DashScope 兼容模式（包含 `dashscope` 与 `compatible-mode`），默认禁用
    - Otherwise enable by default / 其他情况默认启用。
    """
    env = os.getenv("ENABLE_TOOLS")
    if env is not None:
        return env.lower() == "true"
    base = _resolve_base_url() or ""
    if "dashscope" in base and "compatible-mode" in base:
        return False
    return True

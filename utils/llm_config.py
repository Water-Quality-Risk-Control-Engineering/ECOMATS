#!/usr/bin/env python3
"""
LLM配置工具
提供EAS模型实例创建功能
"""

import os
from langchain_openai import ChatOpenAI
from config.config import Config

def create_eas_llm():
    """
    创建EAS模型实例
    
    Returns:
        ChatOpenAI: EAS模型实例
    """
    # 检查EAS配置是否存在
    if not Config.EAS_ENDPOINT or not Config.EAS_TOKEN:
        raise ValueError("EAS配置未设置，请在.env文件中配置EAS_ENDPOINT和EAS_TOKEN")
    
    # 创建EAS模型实例
    eas_llm = ChatOpenAI(
        base_url=Config.EAS_ENDPOINT,
        api_key=Config.EAS_TOKEN,
        model=Config.EAS_MODEL_NAME if Config.EAS_MODEL_NAME else "qwen3-30b-a3b-instruct-2507",
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    return eas_llm
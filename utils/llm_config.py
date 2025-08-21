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
    if not Config.EAS_ENDPOINT or not Config.EAS_TOKEN or Config.EAS_ENDPOINT == "your-eas-endpoint" or Config.EAS_TOKEN == "your-eas-token":
        raise ValueError("EAS配置未设置或使用默认值，请在.env文件中配置有效的EAS_ENDPOINT和EAS_TOKEN")
    
    # 检查模型名称
    model_name = Config.EAS_MODEL_NAME if Config.EAS_MODEL_NAME and Config.EAS_MODEL_NAME != "your-model-name" else "qwen3-30b-a3b-instruct-2507"
    
    # 为EAS模型添加正确的前缀
    if not model_name.startswith("openai/"):
        model_name = "openai/" + model_name
    
    # 使用配置的EAS端点URL（不添加额外路径）
    base_url = Config.EAS_ENDPOINT
    
    try:
        # 创建EAS模型实例
        # 直接使用API密钥进行认证
        api_key = Config.EAS_TOKEN
        
        eas_llm = ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model_name,
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
        return eas_llm
    except Exception as e:
        print(f"创建EAS模型实例失败: {e}")
        # 如果EAS配置失败，回退到默认配置
        return ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,
            model="openai/" + Config.QWEN_MODEL_NAME,
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
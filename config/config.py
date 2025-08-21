import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # Qwen3模型配置
    QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")  # API密钥应通过环境变量设置
    QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen3-30b-a3b-instruct-2507")
    
    # 兼容OpenAI的配置（CrewAI需要）
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # API密钥应通过环境变量设置
    
    # Materials Project API配置
    MATERIALS_PROJECT_API_KEY = os.getenv("MATERIALS_PROJECT_API_KEY", "")
    
    # 模型参数配置
    MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "2048"))
    
    # 特定智能体的温度配置
    MATERIAL_DESIGNER_TEMPERATURE = float(os.getenv("MATERIAL_DESIGNER_TEMPERATURE", "0.8"))
    EXPERT_EVALUATION_TEMPERATURE = float(os.getenv("EXPERT_EVALUATION_TEMPERATURE", "0.3"))
    
    # 其他配置
    VERBOSE = os.getenv("VERBOSE", "True").lower() == "true"
    
    # EAS模型配置（可选）
    EAS_ENDPOINT = os.getenv("EAS_ENDPOINT", "")
    EAS_TOKEN = os.getenv("EAS_TOKEN", "")
    EAS_MODEL_NAME = os.getenv("EAS_MODEL_NAME", "")
    
    @classmethod
    def is_api_key_valid(cls, api_key):
        """验证API密钥是否有效"""
        return api_key and api_key.strip() and len(api_key.strip()) > 0
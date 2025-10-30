import os
from dotenv import load_dotenv

# 加载环境变量 / Load environment variables
load_dotenv()

class Config:
    # Qwen3模型配置 / Qwen3 model configuration
    QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")  # API密钥应通过环境变量设置 / API key should be set through environment variables
    QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen3-30b-a3b-instruct-2507")  # 使用项目规范的默认模型
    
    # 兼容OpenAI的配置（CrewAI需要） / OpenAI-compatible configuration (required by CrewAI)
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # API密钥应通过环境变量设置 / API key should be set through environment variables
    
    # Materials Project API配置 / Materials Project API configuration
    MATERIALS_PROJECT_API_KEY = os.getenv("MATERIALS_PROJECT_API_KEY")
    
    # PubChem API配置 / PubChem API configuration
    PUBCHEM_API_KEY = os.getenv("PUBCHEM_API_KEY")
    
    # 模型参数配置 / Model parameter configuration
    MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "2048"))
    
    # 特定智能体的温度配置 / Temperature configuration for specific agents
    # 材料设计专家使用较高温度以增加多样性 / Material design expert uses higher temperature to increase diversity
    MATERIAL_DESIGNER_TEMPERATURE = float(os.getenv("MATERIAL_DESIGNER_TEMPERATURE", "0.8"))
    
    # 评估专家使用较低温度以确保准确性 / Evaluation experts use lower temperature to ensure accuracy
    EXPERT_A_TEMPERATURE = float(os.getenv("EXPERT_A_TEMPERATURE", "0.3"))
    EXPERT_B_TEMPERATURE = float(os.getenv("EXPERT_B_TEMPERATURE", "0.3"))
    EXPERT_C_TEMPERATURE = float(os.getenv("EXPERT_C_TEMPERATURE", "0.3"))
    
    # 最终验证专家使用适中温度 / Final validator uses moderate temperature
    FINAL_VALIDATOR_TEMPERATURE = float(os.getenv("FINAL_VALIDATOR_TEMPERATURE", "0.5"))
    
    # 其他专家使用默认评估温度 / Other experts use default evaluation temperature
    MECHANISM_EXPERT_TEMPERATURE = float(os.getenv("MECHANISM_EXPERT_TEMPERATURE", "0.3"))
    SYNTHESIS_EXPERT_TEMPERATURE = float(os.getenv("SYNTHESIS_EXPERT_TEMPERATURE", "0.3"))
    OPERATION_SUGGESTING_TEMPERATURE = float(os.getenv("OPERATION_SUGGESTING_TEMPERATURE", "0.3"))
    LITERATURE_PROCESSOR_TEMPERATURE = float(os.getenv("LITERATURE_PROCESSOR_TEMPERATURE", "0.3"))
    
    # 统一的评估专家温度配置（向后兼容） / Unified evaluation expert temperature configuration (backward compatible)
    EXPERT_EVALUATION_TEMPERATURE = float(os.getenv("EXPERT_EVALUATION_TEMPERATURE", "0.3"))
    
    # 迭代设计配置 / Iterative design configuration
    MAX_DESIGN_ITERATIONS = int(os.getenv("MAX_DESIGN_ITERATIONS", "3"))
    MIN_ACCEPTABLE_SCORE = float(os.getenv("MIN_ACCEPTABLE_SCORE", "7.0"))
    
    # 一致性分析配置 / Consistency analysis configuration
    HIGH_CONSISTENCY_THRESHOLD = float(os.getenv("HIGH_CONSISTENCY_THRESHOLD", "1.0"))
    MEDIUM_CONSISTENCY_THRESHOLD = float(os.getenv("MEDIUM_CONSISTENCY_THRESHOLD", "2.0"))
    
    # 其他配置 / Other configurations
    VERBOSE = os.getenv("VERBOSE", "True").lower() == "true"
    
    # EAS模型配置（可选） / EAS model configuration (optional)
    EAS_ENDPOINT = os.getenv("EAS_ENDPOINT")
    EAS_TOKEN = os.getenv("EAS_TOKEN")
    EAS_MODEL_NAME = os.getenv("EAS_MODEL_NAME")
    
    @classmethod
    def is_api_key_valid(cls, api_key):
        """验证API密钥是否有效"""
        return api_key and api_key.strip() and len(api_key.strip()) > 0
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Qwen3 model configuration
    # Default to international endpoint to avoid region mismatch errors
    QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")  # API key should be set through environment variables
    # Default to stable commercial model to avoid thinking mode / streaming errors on OpenAI-compatible interface
    QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen-plus")
    
    # OpenAI-compatible configuration (required by CrewAI)
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # API key should be set through environment variables
    
    # Materials Project API configuration
    MATERIALS_PROJECT_API_KEY = os.getenv("MATERIALS_PROJECT_API_KEY")
    
    # PubChem API configuration
    PUBCHEM_API_KEY = os.getenv("PUBCHEM_API_KEY")
    
    # Model parameter configuration
    MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "2048"))
    
    # Temperature configuration for specific agents
    # Material design expert uses higher temperature to increase diversity
    MATERIAL_DESIGNER_TEMPERATURE = float(os.getenv("MATERIAL_DESIGNER_TEMPERATURE", "0.8"))
    
    # Evaluation experts use lower temperature to ensure accuracy
    EXPERT_A_TEMPERATURE = float(os.getenv("EXPERT_A_TEMPERATURE", "0.3"))
    EXPERT_B_TEMPERATURE = float(os.getenv("EXPERT_B_TEMPERATURE", "0.3"))
    EXPERT_C_TEMPERATURE = float(os.getenv("EXPERT_C_TEMPERATURE", "0.3"))
    
    # Final validator uses moderate temperature
    FINAL_VALIDATOR_TEMPERATURE = float(os.getenv("FINAL_VALIDATOR_TEMPERATURE", "0.5"))
    
    # Other experts use default evaluation temperature
    MECHANISM_EXPERT_TEMPERATURE = float(os.getenv("MECHANISM_EXPERT_TEMPERATURE", "0.3"))
    SYNTHESIS_EXPERT_TEMPERATURE = float(os.getenv("SYNTHESIS_EXPERT_TEMPERATURE", "0.3"))
    OPERATION_SUGGESTING_TEMPERATURE = float(os.getenv("OPERATION_SUGGESTING_TEMPERATURE", "0.3"))
    LITERATURE_PROCESSOR_TEMPERATURE = float(os.getenv("LITERATURE_PROCESSOR_TEMPERATURE", "0.3"))
    
    # Unified evaluation expert temperature configuration (backward compatible)
    EXPERT_EVALUATION_TEMPERATURE = float(os.getenv("EXPERT_EVALUATION_TEMPERATURE", "0.3"))
    
    # Iterative design configuration
    MAX_DESIGN_ITERATIONS = int(os.getenv("MAX_DESIGN_ITERATIONS", "3"))
    MIN_ACCEPTABLE_SCORE = float(os.getenv("MIN_ACCEPTABLE_SCORE", "7.0"))
    
    # Consistency analysis configuration
    HIGH_CONSISTENCY_THRESHOLD = float(os.getenv("HIGH_CONSISTENCY_THRESHOLD", "1.0"))
    MEDIUM_CONSISTENCY_THRESHOLD = float(os.getenv("MEDIUM_CONSISTENCY_THRESHOLD", "2.0"))
    
    # Language configuration
    # Available options: "zh" (Chinese), "en" (English)
    LANGUAGE = os.getenv("LANGUAGE", "zh")
    
    # Other configurations
    VERBOSE = os.getenv("VERBOSE", "True").lower() == "true"
    
    # EAS model configuration (optional)
    EAS_ENDPOINT = os.getenv("EAS_ENDPOINT")
    EAS_TOKEN = os.getenv("EAS_TOKEN")
    EAS_MODEL_NAME = os.getenv("EAS_MODEL_NAME")
    
    @classmethod
    def is_api_key_valid(cls, api_key):
        """Validate if API key is valid."""
        return api_key and api_key.strip() and len(api_key.strip()) > 0
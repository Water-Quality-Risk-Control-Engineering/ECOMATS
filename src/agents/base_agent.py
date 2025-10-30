import logging
import os
from crewai import Agent
from src.utils.prompt_loader import load_prompt
from src.config.config import Config

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BaseAgent:
    """基础智能体类，提供通用的智能体创建功能 / Base agent class that provides general agent creation functionality"""
    
    def __init__(self, llm, role, goal, prompt_file, temperature=None):
        self.llm = llm
        self.role = role
        self.goal = goal
        self.prompt_file = prompt_file
        self.temperature = temperature
    
    def create_agent(self):
        # 如果提供了特定温度，则使用该温度，否则使用LLM的默认温度
        # If a specific temperature is provided, use that temperature, otherwise use the LLM's default temperature
        agent_llm = self.llm
        if self.temperature is not None:
            # 创建一个新的LLM实例，使用指定的温度
            # Create a new LLM instance with the specified temperature
            # 获取原始LLM的属性
            base_url = getattr(self.llm, 'base_url', None) or getattr(self.llm, 'openai_api_base', None)
            api_key = getattr(self.llm, 'api_key', None) or getattr(self.llm, 'openai_api_key', None)
            model = getattr(self.llm, 'model', None) or getattr(self.llm, 'model_name', None)
            streaming = getattr(self.llm, 'streaming', False)
            max_tokens = getattr(self.llm, 'max_tokens', None)
            
            # 根据API基础URL判断使用哪种前缀
            if model and not model.startswith(('openai/', 'qwen/')):
                if base_url and 'dashscope' in base_url:
                    model = 'qwen/' + model
                else:
                    model = 'openai/' + model
            
            agent_llm = type(self.llm)(
                base_url=base_url,
                api_key=api_key,
                model=model,
                temperature=self.temperature,
                streaming=streaming,
                max_tokens=max_tokens
            )
        
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=load_prompt(self.prompt_file),
            verbose=False,
            allow_delegation=False,
            llm=agent_llm
        )
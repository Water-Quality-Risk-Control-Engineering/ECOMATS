
import logging
import os
from crewai import Agent
from utils.prompt_loader import load_prompt

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BaseAgent:
    """基础智能体类，提供通用的智能体创建功能"""
    
    def __init__(self, llm, role, goal, prompt_file, temperature=None):
        self.llm = llm
        self.role = role
        self.goal = goal
        self.prompt_file = prompt_file
        self.temperature = temperature
    
    def create_agent(self):
        # 如果提供了特定温度，则使用该温度，否则使用LLM的默认温度
        agent_llm = self.llm
        if self.temperature is not None:
            # 创建一个新的LLM实例，使用指定的温度
            agent_llm = type(self.llm)(
                base_url=getattr(self.llm, 'base_url', None) or getattr(self.llm, 'openai_api_base', None),
                api_key=getattr(self.llm, 'api_key', None) or getattr(self.llm, 'openai_api_key', None),
                model=getattr(self.llm, 'model', None) or getattr(self.llm, 'model_name', None),
                temperature=self.temperature,
                streaming=getattr(self.llm, 'streaming', False),
                max_tokens=getattr(self.llm, 'max_tokens', None)
            )
        
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=load_prompt(self.prompt_file),
            verbose=False,
            allow_delegation=False,
            llm=agent_llm
        )
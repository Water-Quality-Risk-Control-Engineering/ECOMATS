import logging
import os
from crewai import Agent
from utils.prompt_loader import load_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent:
    """基础智能体类，提供通用的智能体创建功能"""
    
    def __init__(self, llm, role, goal, prompt_file):
        self.llm = llm
        self.role = role
        self.goal = goal
        self.prompt_file = prompt_file
    
    def create_agent(self):
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=load_prompt(self.prompt_file),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
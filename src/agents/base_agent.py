import logging
from crewai import Agent
from src.utils.prompt_loader import load_prompt

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
        agent_llm = self.llm
        try:
            from src.config.config import Config
            # 优先使用EAS模式 / Prefer EAS mode
            if Config.EAS_ENDPOINT and Config.EAS_TOKEN and Config.EAS_MODEL_NAME:
                if self.temperature is not None:
                    from src.utils.llm_config import create_eas_llm
                    agent_llm = create_eas_llm(temperature=self.temperature)
            # 标准模式：如果指定了温度，创建独立的LLM实例 / Standard mode: create independent LLM if temperature specified
            elif self.temperature is not None:
                from src.utils.llm_config import create_llm
                agent_llm = create_llm(temperature=self.temperature)
        except Exception as e:
            logger.debug(f"Failed to create custom LLM with temperature {self.temperature}: {e}")

        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=load_prompt(self.prompt_file),
            verbose=False,
            allow_delegation=False,
            llm=agent_llm
        )

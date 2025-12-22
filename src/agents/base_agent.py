import logging
from crewai import Agent
from src.utils.prompt_loader import load_prompt

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Memory优先使用指导 / Memory-first usage guidance
MEMORY_GUIDANCE_ZH = """

## 工具使用优化策略 ##
1. **Memory优先**: 在调用外部工具前，先检查是否已有相关信息在上下文或记忆中
2. **避免重复查询**: 如果某材料/化学品信息已被之前的任务查询过，直接复用结果
3. **最小化工具调用**: 只查询必要的信息，避免过度使用工具
4. **结果复用**: 将查询结果整理后传递给下游任务，供其复用
"""

MEMORY_GUIDANCE_EN = """

## Tool Usage Optimization Strategy ##
1. **Memory First**: Check context or memory for existing information before calling external tools
2. **Avoid Duplicate Queries**: Reuse results if material/chemical info was queried by previous tasks
3. **Minimize Tool Calls**: Only query necessary information, avoid overusing tools
4. **Result Reuse**: Pass organized query results to downstream tasks for reuse
"""


class BaseAgent:
    """基础智能体类，提供通用的智能体创建功能 / Base agent class that provides general agent creation functionality"""
    
    # 默认迭代次数限制 - 防止工具过度调用 / Default iteration limit to prevent excessive tool calls
    DEFAULT_MAX_ITER = 10
    
    def __init__(self, llm, role, goal, prompt_file, temperature=None, max_iter=None, prompt_params=None):
        self.llm = llm
        self.role = role
        self.goal = goal
        self.prompt_file = prompt_file
        self.temperature = temperature
        self.max_iter = max_iter or self.DEFAULT_MAX_ITER
        self.prompt_params = prompt_params or {}  # 参数化替换支持
    
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

        # 加载提示词并添加Memory优先指导 / Load prompt and add Memory-first guidance
        backstory = load_prompt(self.prompt_file)
        
        # 参数化替换支持 / Parameterized replacement support
        if self.prompt_params:
            for key, value in self.prompt_params.items():
                backstory = backstory.replace(f"{{{key}}}", value)
        
        try:
            from src.config.config import Config
            if Config.LANGUAGE == 'en':
                backstory += MEMORY_GUIDANCE_EN
            else:
                backstory += MEMORY_GUIDANCE_ZH
        except Exception:
            backstory += MEMORY_GUIDANCE_ZH

        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=backstory,
            verbose=False,
            allow_delegation=False,
            llm=agent_llm,
            max_iter=self.max_iter  
        )

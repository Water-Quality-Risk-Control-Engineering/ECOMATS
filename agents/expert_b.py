import logging
from crewai import Agent
from utils.prompt_loader import load_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 专家B
expert_b = Agent(
    role="专家B",
    goal="全面评估材料方案的各个方面",
    backstory=load_prompt("expert_b_prompt.md"),
    verbose=True,
    allow_delegation=False,
)
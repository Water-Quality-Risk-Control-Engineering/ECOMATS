import logging
from crewai import Agent
from utils.prompt_loader import load_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 材料设计专家
material_designer = Agent(
    role="材料设计专家",
    goal="设计和优化水处理材料方案",
    backstory=load_prompt("material_designer_prompt.md"),
    verbose=True,
    allow_delegation=False,
)
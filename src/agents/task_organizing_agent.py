import logging
from crewai import Agent
from src.utils.prompt_loader import load_prompt
from src.agents.base_agent import BaseAgent

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 任务组织代理类 / Task organizing agent class
class TaskOrganizingAgent(BaseAgent):
    """任务组织代理智能体 / Task organizing agent"""
    
    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="Task_Organizing_agent",  # 任务组织代理 / Task organizing agent
            goal="组织和协调各个专家智能体的工作，确保任务按计划完成",  # 组织和协调各个专家智能体的工作，确保任务按计划完成 / Organize and coordinate the work of various expert agents to ensure tasks are completed according to plan
            prompt_file="coordinator_prompt.md"
        )
    
    def create_agent(self):
        return Agent(
            role="Task_Organizing_agent",
            goal="组织和协调各专家工作，确保任务高效完成",
            backstory=load_prompt("coordinator_prompt.md"),
            verbose=False,
            allow_delegation=True,
            llm=self.llm
        )
    
    def delegate_task(self, task_type, task_allocator, task_description):
        """
        根据任务类型委派任务给合适的智能体
        
        Args:
            task_type: 任务类型
            task_allocator: 任务分配器实例
            task_description: 任务描述
            
        Returns:
            合适的智能体实例
        """
        # 获取适合任务类型的智能体
        agent = task_allocator.get_agent_for_task(task_type)
        if agent:
            logger.info(f"委派任务类型 '{task_type}' 给智能体: {agent.role}")
            return agent
        else:
            logger.warning(f"未找到适合任务类型 '{task_type}' 的智能体")
            # 如果没有找到合适的智能体，则返回第一个可用的智能体
            all_agents = []
            for agents in task_allocator.available_agents.values():
                all_agents.extend(agents)
            if all_agents:
                return all_agents[0]
            return None
    
    def delegate_tasks_dynamically(self, task_allocator, task_description):
        """
        根据任务描述动态委派任务给合适的智能体
        
        Args:
            task_allocator: 任务分配器实例
            task_description: 任务描述
            
        Returns:
            需要参与任务的智能体列表
        """
        # 根据任务描述决定需要哪些任务类型
        required_task_types = task_allocator.determine_required_task_types(task_description)
        
        # 根据任务类型获取相应的智能体
        required_agents = []
        for task_type in required_task_types:
            agent = task_allocator.get_agent_for_task(task_type)
            if agent:
                required_agents.append((task_type, agent))
            else:
                logger.warning(f"未找到适合任务类型 '{task_type}' 的智能体")
        
        return required_agents
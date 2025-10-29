import logging
from typing import List, Dict, Any, Union
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class TaskAllocator:
    """
    任务分配器，根据任务类型自动选择合适的智能体 / Task allocator that automatically selects the appropriate agent based on task type
    """
    
    def __init__(self):
        """
        初始化任务分配器 / Initialize the TaskAllocator
        """
        # 定义任务类型到智能体的映射关系 / Define mapping from task types to agents
        self.task_agent_mapping = {
            "material_design": "CreativeDesigningAgent",
            "evaluation": "AssessmentScreeningAgent",
            "final_validation": "AssessmentScreeningAgentOverall",
            "mechanism_analysis": "MechanismMiningAgent",
            "synthesis_method": "SynthesisGuidingAgent",
            "literature_processing": "ExtractingAgent",
            "operation_suggestion": "OperationSuggestingAgent",
            "coordinator": "TaskOrganizingAgent"
        }
        
        # 存储所有可用的智能体
        self.available_agents = {}
        
    def determine_required_task_types(self, task_description):
        """
        根据任务描述动态决定需要哪些任务类型
        / Dynamically determine which task types are needed based on task description
        
        Args:
            task_description: 任务描述 / Task description
            
        Returns:
            需要的任务类型列表 / List of required task types
        """
        required_task_types = ["material_design"]  # 材料设计任务总是需要
        
        # 检查是否需要评估任务 / Check if evaluation tasks are needed
        if "评估" in task_description or "评价" in task_description or "性能" in task_description:
            required_task_types.append("evaluation")
            required_task_types.append("final_validation")
            
            # 检查是否需要机理分析任务 / Check if mechanism analysis task is needed
            if "机理" in task_description or "机制" in task_description or "反应" in task_description:
                required_task_types.append("mechanism_analysis")
        
        # 检查是否需要合成方法任务 / Check if synthesis method task is needed
        if "合成" in task_description or "制备" in task_description or "工艺" in task_description:
            required_task_types.append("synthesis_method")
        
        # 检查是否需要操作建议任务 / Check if operation suggestion task is needed
        if "操作" in task_description or "运行" in task_description or "应用" in task_description:
            required_task_types.append("operation_suggestion")
            
        return required_task_types
        
    def register_agent(self, agent_type: str, agent: Union[Agent, List[Agent]]) -> None:
        """
        注册智能体到可用列表 / Register an agent to the available list
        
        Args:
            agent_type: 智能体类型 / The type of the agent
            agent: 智能体实例或实例列表 / The agent instance or list of instances
        """
        # 如果传入的是单个智能体，转换为列表
        if isinstance(agent, Agent):
            agent = [agent]
            
        if agent_type in self.available_agents:
            self.available_agents[agent_type].extend(agent)
        else:
            self.available_agents[agent_type] = agent
        logger.info(f"Registered {len(agent)} agent(s) of type {agent_type}")
        
    def _get_agent_type_for_task(self, task_type: str) -> str:
        """
        根据任务类型获取对应的智能体类型 / Get the corresponding agent type for a given task type
        
        Args:
            task_type: 任务类型 / The type of the task
            
        Returns:
            对应的智能体类型 / The corresponding agent type
        """
        return self.task_agent_mapping.get(task_type)
    
    def _get_default_agent(self) -> Agent:
        """
        获取默认的智能体（第一个可用的智能体） / Get the default agent (the first available agent)
        
        Returns:
            默认的智能体实例 / The default agent instance
        """
        for agents in self.available_agents.values():
            if agents:
                return agents[0]
        return None
    
    def _get_all_available_agents(self) -> List[Agent]:
        """
        获取所有可用的智能体 / Get all available agents
        
        Returns:
            所有可用的智能体实例列表 / A list of all available agent instances
        """
        all_agents = []
        for agents in self.available_agents.values():
            all_agents.extend(agents)
        return all_agents
        
    def get_agent_for_task(self, task_type: str) -> Agent:
        """
        根据任务类型获取合适的智能体 / Get the appropriate agent for a given task type
        
        Args:
            task_type: 任务类型 / The type of the task
            
        Returns:
            合适的智能体实例 / The appropriate agent instance
        """
        # 根据任务类型查找对应的智能体类型
        agent_type = self._get_agent_type_for_task(task_type)
        
        if not agent_type:
            logger.warning(f"No agent type mapping found for task type: {task_type}")
            # 默认返回第一个可用的智能体
            return self._get_default_agent()
            
        # 查找可用的智能体
        if agent_type in self.available_agents and self.available_agents[agent_type]:
            # 返回该类型的第一个智能体（可以扩展为更复杂的分配策略）
            return self.available_agents[agent_type][0]
        else:
            logger.warning(f"No available agent of type: {agent_type}")
            return None
            
    def get_all_agents_for_task(self, task_type: str) -> List[Agent]:
        """
        根据任务类型获取所有合适的智能体 / Get all suitable agents for a given task type
        
        Args:
            task_type: 任务类型 / The type of the task
            
        Returns:
            所有合适的智能体实例列表 / A list of all suitable agent instances
        """
        # 根据任务类型查找对应的智能体类型
        agent_type = self._get_agent_type_for_task(task_type)
        
        if not agent_type:
            logger.warning(f"No agent type mapping found for task type: {task_type}")
            # 返回所有可用的智能体
            return self._get_all_available_agents()
            
        # 返回该类型的所有智能体
        if agent_type in self.available_agents:
            return self.available_agents[agent_type]
        else:
            logger.warning(f"No available agents of type: {agent_type}")
            return []
            
    def get_agent_by_name(self, agent_name: str) -> Agent:
        """
        根据智能体名称获取智能体实例 / Get an agent instance by its name
        
        Args:
            agent_name: 智能体名称 / The name of the agent
            
        Returns:
            智能体实例 / The agent instance
        """
        for agents in self.available_agents.values():
            for agent in agents:
                if agent.role == agent_name:
                    return agent
        logger.warning(f"No agent found with name: {agent_name}")
        return None
        
    def get_task_types(self) -> List[str]:
        """
        获取所有支持的任务类型 / Get all supported task types
        
        Returns:
            任务类型列表 / A list of task types
        """
        return list(self.task_agent_mapping.keys())
        
    def get_agent_types(self) -> List[str]:
        """
        获取所有注册的智能体类型 / Get all registered agent types
        
        Returns:
            智能体类型列表 / A list of agent types
        """
        return list(self.available_agents.keys())
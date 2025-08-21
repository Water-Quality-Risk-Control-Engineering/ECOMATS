import logging
from typing import List, Dict, Any, Union
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class TaskAllocator:
    """
    任务分配器，根据任务类型自动选择合适的智能体
    """
    
    def __init__(self):
        # 定义任务类型到智能体的映射关系
        self.task_agent_mapping = {
            "material_design": "MaterialDesigner",
            "evaluation": "Expert",
            "final_validation": "FinalValidator",
            "mechanism_analysis": "MechanismExpert",
            "synthesis_method": "SynthesisExpert",
            "literature_processing": "LiteratureProcessor"
        }
        
        # 存储所有可用的智能体
        self.available_agents = {}
        
    def register_agent(self, agent_type: str, agent: Union[Agent, List[Agent]]) -> None:
        """
        注册智能体到可用列表
        
        Args:
            agent_type: 智能体类型
            agent: 智能体实例或实例列表
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
        根据任务类型获取对应的智能体类型
        
        Args:
            task_type: 任务类型
            
        Returns:
            对应的智能体类型
        """
        return self.task_agent_mapping.get(task_type)
    
    def _get_default_agent(self) -> Agent:
        """
        获取默认的智能体（第一个可用的智能体）
        
        Returns:
            默认的智能体实例
        """
        for agents in self.available_agents.values():
            if agents:
                return agents[0]
        return None
    
    def _get_all_available_agents(self) -> List[Agent]:
        """
        获取所有可用的智能体
        
        Returns:
            所有可用的智能体实例列表
        """
        all_agents = []
        for agents in self.available_agents.values():
            all_agents.extend(agents)
        return all_agents
        
    def get_agent_for_task(self, task_type: str) -> Agent:
        """
        根据任务类型获取合适的智能体
        
        Args:
            task_type: 任务类型
            
        Returns:
            合适的智能体实例
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
        根据任务类型获取所有合适的智能体
        
        Args:
            task_type: 任务类型
            
        Returns:
            所有合适的智能体实例列表
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
        根据智能体名称获取智能体实例
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            智能体实例
        """
        for agents in self.available_agents.values():
            for agent in agents:
                if agent.role == agent_name:
                    return agent
        logger.warning(f"No agent found with name: {agent_name}")
        return None
        
    def get_task_types(self) -> List[str]:
        """
        获取所有支持的任务类型
        
        Returns:
            任务类型列表
        """
        return list(self.task_agent_mapping.keys())
        
    def get_agent_types(self) -> List[str]:
        """
        获取所有注册的智能体类型
        
        Returns:
            智能体类型列表
        """
        return list(self.available_agents.keys())
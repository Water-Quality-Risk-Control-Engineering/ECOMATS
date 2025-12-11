import logging
import json
from typing import List, Union
from crewai import Agent

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class TaskAllocator:
    """
    任务分配器，根据任务类型自动选择合适的智能体 / Task allocator that automatically selects the appropriate agent based on task type
    """
    
    def __init__(self, llm=None):
        """
        初始化任务分配器 / Initialize the TaskAllocator
        
        Args:
            llm: 语言模型实例，用于智能任务分配 / Language model instance for intelligent task allocation
        """
        # 定义任务类型到智能体的映射关系 / Define mapping from task types to agents
        self.task_agent_mapping = {
            "material_design": "CreativeDesigningAgent",
            "evaluation": "AssessmentScreeningAgent",
            "final_validation": "AssessmentScreeningAgentOverall",
            "enhanced_final_validation": "AssessmentScreeningAgentOverall",
            "mechanism_analysis": "MechanismMiningAgent",
            "synthesis_method": "SynthesisGuidingAgent",
            "literature_processing": "ExtractingAgent",
            "operation_suggestion": "OperationSuggestingAgent",
            "coordinator": "TaskOrganizingAgent"
        }
        
        # 存储所有可用的智能体
        self.available_agents = {}
        
        # 存储语言模型实例
        self.llm = llm
        
    def determine_required_task_types(self, task_description: str) -> List[str]:
        """
        根据任务描述动态决定需要哪些任务类型
        / Dynamically determine which task types are needed based on task description
        
        Args:
            task_description: 任务描述 / Task description
            
        Returns:
            需要的任务类型列表 / List of required task types
        """
        # 输入验证
        if not task_description or not task_description.strip():
            logger.warning("Empty task description provided, using default task")
            return ["material_design"]
            
        desc = task_description.strip()
        if not desc:
            return ["material_design"]
        d = desc.lower()
        result: List[str] = []
        
        # 检查是否只要评估不要总结（优先级最高）
        only_evaluation_keywords = ["仅评估", "只评估", "不总结", "不要总结", "不需要总结", 
                                   "只要评分", "仅评分", "三个ASA", "3个ASA", "三个评分",
                                   "only evaluation", "no summary", 
                                   "evaluation only", "without summary"]
        if any(k in d or k in desc for k in only_evaluation_keywords):
            # 仅返回评估任务，不包含final_validation
            if "material_design" not in result:
                result.append("material_design")
            result.append("evaluation_only")
            return result
        
        if any(k in desc for k in ["设计", "设计出", "方案"]):
            result.append("material_design")
        if any(k in desc for k in ["评估", "评价", "assessment", "evaluate"]):
            result.extend(["evaluation", "final_validation"])
        if any(k in desc for k in ["机理", "机制", "mechanism"]):
            result.append("mechanism_analysis")
        if any(k in desc for k in ["合成", "制备", "synthesis"]):
            result.append("synthesis_method")
        if any(k in desc for k in ["操作", "运行", "建议", "operation"]):
            result.append("operation_suggestion")
        if not result:
            result = ["material_design"]
        # 独立任务单独返回
        independent_tasks = ["mechanism_analysis", "synthesis_method", "operation_suggestion"]
        if len(result) == 1 and result[0] in independent_tasks:
            return result
        # 确保评估链需要设计任务
        if "material_design" not in result and any(t in ["evaluation", "final_validation"] for t in result):
            result.insert(0, "material_design")
        # 去重并保持顺序
        seen = set()
        ordered = []
        for t in result:
            if t not in seen:
                seen.add(t)
                ordered.append(t)
        return ordered
        
    def register_agent(self, agent_type: str, agent: Union[Agent, List[Agent]]) -> None:
        """
        注册智能体到可用列表 / Register an agent to the available list
        
        Args:
            agent_type: 智能体类型 / The type of the agent
            agent: 智能体实例或实例列表 / The agent instance or list of instances
            
        Raises:
            ValueError: 当agent_type为空或agent为None时
        """
        # 输入验证
        if not agent_type or not agent_type.strip():
            raise ValueError("agent_type cannot be empty")
        if agent is None:
            raise ValueError("agent cannot be None")
            
        agent_type = agent_type.strip()
        
        # 如果传入的是单个智能体，转换为列表
        if isinstance(agent, Agent):
            agent = [agent]
        elif not isinstance(agent, list):
            raise ValueError("agent must be an Agent instance or a list of Agent instances")
            
        # 验证列表中的每个元素都是Agent实例
        for item in agent:
            if not isinstance(item, Agent):
                raise ValueError(f"All items in agent list must be Agent instances, got {type(item)}")
        
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

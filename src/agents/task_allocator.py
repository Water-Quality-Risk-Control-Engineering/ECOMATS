import logging
import json
from typing import List, Dict, Any, Union
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
            
        # 使用LLM进行智能分配
        if self.llm:
            try:
                # 加载提示文件
                from src.utils.prompt_loader import load_prompt
                prompt_template = load_prompt("task_allocation_prompt.md")
                
                # 格式化提示
                prompt = prompt_template.format(user_requirement=task_description.strip())
                
                # 调用LLM获取任务类型
                response = self.llm.invoke(prompt)
                
                # 确保response是字符串格式
                if hasattr(response, 'content'):
                    response_content = response.content
                else:
                    response_content = str(response)
                
                # 记录LLM响应用于调试
                logger.debug(f"LLM task allocation response: {response_content}")
                
                # 解析LLM响应
                task_types = json.loads(response_content)
                
                # 验证task_types是否为列表
                if not isinstance(task_types, list):
                    logger.warning(f"LLM response is not a list: {task_types}")
                    return ["material_design"]
                
                # 验证任务类型是否有效
                valid_task_types = []
                available_task_types = set(self.task_agent_mapping.keys())
                
                for task_type in task_types:
                    if not isinstance(task_type, str):
                        logger.warning(f"Invalid task type format: {task_type}")
                        continue
                    if task_type in available_task_types:
                        valid_task_types.append(task_type)
                    else:
                        logger.warning(f"Invalid task type detected: {task_type}")
                
                # 特殊处理：如果只包含独立任务，则只返回该任务
                independent_tasks = ["mechanism_analysis", "synthesis_method", "operation_suggestion"]
                if len(valid_task_types) == 1 and valid_task_types[0] in independent_tasks:
                    logger.info(f"User requested {valid_task_types[0]} only, returning that task only")
                    return valid_task_types
                
                # 确保返回非空列表
                if not valid_task_types:
                    logger.warning("LLM returned no valid task types, falling back to default")
                    return ["material_design"]
                
                # 如果LLM没有包含material_design但其他任务需要它，则添加
                if "material_design" not in valid_task_types:
                    # 检查是否需要material_design（除了独立任务外的其他任务通常需要）
                    # 但如果是评估现有材料，则不需要设计任务
                    needs_material_design = any(task_type in ["evaluation", "final_validation"] 
                                              for task_type in valid_task_types)
                    # 检查用户是否明确表示要评估现有材料
                    lower_desc = task_description.lower()
                    is_evaluating_existing = ("评估" in task_description or "evaluate" in lower_desc) and \
                                           ("现有" in task_description or "existing" in lower_desc or 
                                            "已有的" in task_description or "已有" in task_description)
                    if needs_material_design and not is_evaluating_existing:
                        logger.info("Adding material_design task as it's required by other tasks")
                        valid_task_types.insert(0, "material_design")
                    elif needs_material_design and is_evaluating_existing:
                        logger.info("User wants to evaluate existing material, skipping material_design task")
                
                logger.info(f"LLM task allocation result: {valid_task_types}")
                return valid_task_types
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing LLM response as JSON: {e}")
                logger.error(f"LLM response was: {response_content if 'response_content' in locals() else 'N/A'}")
            except ImportError as e:
                logger.error(f"Failed to import prompt_loader: {e}")
            except Exception as e:
                logger.error(f"Error using LLM for task allocation: {e}")
            
            # 如果LLM调用失败，回退到默认模式
            logger.warning("Falling back to default task allocation")
        
        # 当LLM调用失败时，直接返回一个安全的默认值
        logger.warning("LLM task allocation failed, returning default material design task")
        return ["material_design"]
        
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
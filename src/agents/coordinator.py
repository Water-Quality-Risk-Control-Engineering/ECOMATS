import logging
from crewai import Agent
from src.utils.prompt_loader import load_prompt

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 协调者类
class Coordinator:
    def __init__(self, llm):
        self.llm = llm
    
    def create_agent(self):
        return Agent(
            role="协调者",
            goal="协调各专家工作，确保任务高效完成",
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
        # 根据任务描述决定需要哪些专家参与
        required_agents = []
        
        # 材料设计专家总是需要参与
        design_agent = task_allocator.get_agent_for_task("material_design")
        if design_agent:
            required_agents.append(("design", design_agent))
        
        # 根据任务描述中的关键词决定需要哪些评估专家
        if "重金属" in task_description or "镉" in task_description:
            # 对于重金属处理任务，需要所有评估专家
            evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
            for i, agent in enumerate(evaluation_agents):
                required_agents.append((f"evaluation_{i+1}", agent))
        else:
            # 对于其他任务，只需要一个评估专家
            evaluation_agent = task_allocator.get_agent_for_task("evaluation")
            if evaluation_agent:
                required_agents.append(("evaluation", evaluation_agent))
        
        # 最终验证专家总是需要参与
        final_validator_agent = task_allocator.get_agent_for_task("final_validation")
        if final_validator_agent:
            required_agents.append(("final_validation", final_validator_agent))
        
        # 根据任务描述中的关键词决定是否需要机理分析专家
        if "机理" in task_description or "机制" in task_description:
            mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
            if mechanism_agent:
                required_agents.append(("mechanism_analysis", mechanism_agent))
        
        # 根据任务描述中的关键词决定是否需要合成专家
        if "合成" in task_description or "制备" in task_description:
            synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
            if synthesis_agent:
                required_agents.append(("synthesis_method", synthesis_agent))
        
        # 操作建议专家总是需要参与
        operation_suggesting_agent = task_allocator.get_agent_for_task("operation_suggestion")
        if operation_suggesting_agent:
            required_agents.append(("operation_suggestion", operation_suggesting_agent))
        
        return required_agents
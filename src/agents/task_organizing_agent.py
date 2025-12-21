import logging
import json
import re
from typing import List, Union, Dict, Any
from crewai import Agent
from src.utils.prompt_loader import load_prompt
from src.agents.base_agent import BaseAgent

# 配置日志 / Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 任务组织代理类 / Task organizing agent class
class TaskOrganizingAgent(BaseAgent):
    """Task organizing agent - responsible for intent recognition and agent scheduling
    任务组织代理智能体 - 负责意图识别和智能体调度
    """
    
    # 任务类型到智能体的映射 / Task type to agent mapping
    TASK_AGENT_MAPPING = {
        "material_design": "CreativeDesigningAgent",
        "evaluation": "AssessmentScreeningAgent",
        "final_validation": "AssessmentScreeningAgentOverall",
        "mechanism_analysis": "MechanismMiningAgent",
        "synthesis_method": "SynthesisGuidingAgent",
        "operation_suggestion": "OperationSuggestingAgent",
        "literature_processing": "ExtractingAgent",
        "coordinator": "TaskOrganizingAgent"
    }
    
    def __init__(self, llm):
        super().__init__(
            llm=llm,
            role="Task_Organizing_agent",
            goal="Organize and coordinate the work of various expert agents to ensure tasks are completed according to plan",  # 组织和协调各个专家智能体的工作，确保任务按计划完成
            prompt_file="coordinator_prompt.md"
        )
        # 智能体注册表 / Agent registry
        self._agent_registry: Dict[str, Union[Agent, List[Agent]]] = {}
    
    def create_agent(self):
        return Agent(
            role="Task_Organizing_agent",
            goal="Organize and coordinate experts' work to ensure efficient task completion",  # 组织和协调各专家工作，确保任务高效完成
            backstory=load_prompt("coordinator_prompt.md"),
            verbose=False,
            allow_delegation=True,
            llm=self.llm
        )
    
    # ============================================================
    # 智能体注册表功能 / Agent Registry Functions
    # ============================================================
    
    def register_agent(self, agent_type: str, agent: Union[Agent, List[Agent]]):
        """Register agent to registry
        注册智能体到注册表
        
        Args:
            agent_type: Agent type name / 智能体类型名称
            agent: Agent instance or list of agents / 智能体实例或智能体列表
        """
        self._agent_registry[agent_type] = agent
        logger.debug(f"Registered agent: {agent_type}")
    
    def register_agents(self, agents_dict: Dict[str, Any]):
        """Batch register agents
        批量注册智能体
        
        Args:
            agents_dict: Agent dict in format {type: agent} / 智能体字典，格式为 {type: agent}
        """
        for agent_type, agent in agents_dict.items():
            self.register_agent(agent_type, agent)
    
    def get_agent_for_task(self, task_type: str) -> Union[Agent, None]:
        """Get agent for task type
        根据任务类型获取对应的智能体
        
        Args:
            task_type: Task type / 任务类型
            
        Returns:
            Agent instance or None / 智能体实例或 None
        """
        # 查找任务类型对应的智能体类型 / Find agent type for task type
        agent_type = self.TASK_AGENT_MAPPING.get(task_type)
        if not agent_type:
            logger.warning(f"No agent mapping for task type: {task_type}")
            return None
        
        # 从注册表获取智能体 / Get agent from registry
        agent = self._agent_registry.get(agent_type)
        if agent is None:
            logger.warning(f"Agent type '{agent_type}' not registered")
            return None
        
        # 如果是列表，返回第一个 / If list, return first one
        if isinstance(agent, list):
            return agent[0] if agent else None
        return agent
    
    def get_all_agents_for_task(self, task_type: str) -> List[Agent]:
        """Get all agents for task type
        获取任务类型对应的所有智能体
        
        Args:
            task_type: Task type / 任务类型
            
        Returns:
            List of agents / 智能体列表
        """
        agent_type = self.TASK_AGENT_MAPPING.get(task_type)
        if not agent_type:
            logger.warning(f"No agent mapping for task type: {task_type}")
            return []
        
        agent = self._agent_registry.get(agent_type)
        if agent is None:
            logger.warning(f"Agent type '{agent_type}' not registered")
            return []
        
        if isinstance(agent, list):
            return agent
        return [agent]
    
    # ============================================================
    # 意图识别功能 / Intent Recognition Functions
    # ============================================================
    
    def analyze_user_intent(self, user_requirement: str) -> dict:
        """Use LLM to analyze user intent and determine tasks to execute
        使用 LLM 分析用户意图，确定需要执行的任务
        
        Args:
            user_requirement: User requirement description / 用户需求描述
            
        Returns:
            Intent analysis result (dict) / 意图分析结果
            {
                "needs_design": bool,
                "needs_evaluation": bool,
                "evaluation_mode": "experts_only" | "with_summary" | null,
                "needs_mechanism": bool,
                "needs_synthesis": bool,
                "needs_operation": bool,
                "material_provided": str | null,
                "reasoning": str
            }
        """
        try:
            # Load intent recognition Prompt / 加载意图识别 Prompt
            intent_prompt = load_prompt("intent_recognition_prompt.md")
            
            # Build complete Prompt / 构建完整的 Prompt
            full_prompt = f"{intent_prompt}\n\nUser requirement:\n{user_requirement}"
            
            # Call LLM to analyze intent / 调用 LLM 分析意图
            response = self.llm.call([{"role": "user", "content": full_prompt}])
            response_text = response.strip()
            
            # Remove possible Markdown code block markers / 移除可能的 Markdown 代码块标记
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON / 解析 JSON
            intent = json.loads(response_text)
            
            logger.info(f"TOA Intent Analysis: {intent['reasoning']}")
            return intent
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            logger.error(f"Response text: {response_text}")
            # Fallback to default intent / 回退到默认意图
            return {
                "needs_design": True,
                "needs_evaluation": True,
                "evaluation_mode": "with_summary",
                "needs_mechanism": False,
                "needs_synthesis": False,
                "needs_operation": False,
                "material_provided": None,
                "reasoning": "Fallback to default due to JSON parse error"
            }
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            # Fallback to default intent / 回退到默认意图
            return {
                "needs_design": True,
                "needs_evaluation": True,
                "evaluation_mode": "with_summary",
                "needs_mechanism": False,
                "needs_synthesis": False,
                "needs_operation": False,
                "material_provided": None,
                "reasoning": "Fallback to default due to error"
            }
    
    def intent_to_task_types(self, intent: dict) -> list:
        """Convert intent analysis result to task type list
        将意图分析结果转换为任务类型列表
        
        Args:
            intent: Intent analysis result / 意图分析结果
            
        Returns:
            Task type list / 任务类型列表
        """
        result = []
        
        # Material design / 材料设计
        if intent.get("needs_design", False):
            result.append("material_design")
        
        # Evaluation task / 评估任务
        if intent.get("needs_evaluation", False):
            evaluation_mode = intent.get("evaluation_mode", "with_summary")
            if evaluation_mode == "experts_only":
                result.append("evaluation_only")
            else:
                result.extend(["evaluation", "final_validation"])
        
        # Mechanism analysis / 机理分析
        if intent.get("needs_mechanism", False):
            result.append("mechanism_analysis")
        
        # Synthesis method / 合成方法
        if intent.get("needs_synthesis", False):
            result.append("synthesis_method")
        
        # Operation guidance / 操作指导
        if intent.get("needs_operation", False):
            result.append("operation_suggestion")
        
        # If no tasks, default to material design / 如果没有任何任务，默认返回材料设计
        if not result:
            result.append("material_design")
        
        return result
    
    # ============================================================
    # 任务委派功能 / Task Delegation Functions
    # ============================================================
    
    def delegate_task(self, task_type: str, task_description: str = None) -> Union[Agent, None]:
        """Delegate task to appropriate agent based on task type
        根据任务类型委派任务给合适的智能体
        
        Args:
            task_type: Task type / 任务类型
            task_description: Task description (optional) / 任务描述（可选）
            
        Returns:
            Appropriate agent instance / 合适的智能体实例
        """
        agent = self.get_agent_for_task(task_type)
        if agent:
            logger.info(f"Delegated task type '{task_type}' to agent / 委派任务类型 '{task_type}' 给智能体: {agent.role}")
            return agent
        else:
            logger.warning(f"No suitable agent found for task type / 未找到适合任务类型 '{task_type}' 的智能体")
            return None
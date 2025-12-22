import logging
import json
import re
from typing import List, Union, Dict, Any
from crewai import Agent
from src.utils.prompt_loader import load_prompt
from src.agents.base_agent import BaseAgent

#  Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

#  Task organizing agent class
class TaskOrganizingAgent(BaseAgent):
    """Task organizing agent - responsible for intent recognition and agent scheduling
    """
    
    #  Task type to agent mapping
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
            goal="Organize and coordinate the work of various expert agents to ensure tasks are completed according to plan",  
            prompt_file="task_organizing_agent_prompt.md"
        )
        # Agent registry
        self._agent_registry: Dict[str, Union[Agent, List[Agent]]] = {}
    
    def create_agent(self):
        return Agent(
            role="Task_Organizing_agent",
            goal="Organize and coordinate experts' work to ensure efficient task completion",  
            backstory=load_prompt("coordinator_prompt.md"),
            verbose=False,
            allow_delegation=True,
            llm=self.llm
        )
    
    # ============================================================
    #  Agent Registry Functions
    # ============================================================
    
    def register_agent(self, agent_type: str, agent: Union[Agent, List[Agent]]):
        """Register agent to registry
        
        Args:
            agent_type: Agent type name 
            agent: Agent instance or list of agents 
        """
        self._agent_registry[agent_type] = agent
        logger.debug(f"Registered agent: {agent_type}")
    
    def register_agents(self, agents_dict: Dict[str, Any]):
        """Batch register agents
        
        Args:
            agents_dict: Agent dict in format {type: agent} 
        """
        for agent_type, agent in agents_dict.items():
            self.register_agent(agent_type, agent)
    
    def get_agent_for_task(self, task_type: str) -> Union[Agent, None]:
        """Get agent for task type
        
        Args:
            task_type: Task type 
            
        Returns:
            Agent instance or None 
        """
        #  Find agent type for task type
        agent_type = self.TASK_AGENT_MAPPING.get(task_type)
        if not agent_type:
            logger.warning(f"No agent mapping for task type: {task_type}")
            return None
        
        #  Get agent from registry
        agent = self._agent_registry.get(agent_type)
        if agent is None:
            logger.warning(f"Agent type '{agent_type}' not registered")
            return None
        
        # If list, return first one
        if isinstance(agent, list):
            return agent[0] if agent else None
        return agent
    
    def get_all_agents_for_task(self, task_type: str) -> List[Agent]:
        """Get all agents for task type
        
        Args:
            task_type: Task type 
            
        Returns:
            List of agents 
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
    #  Intent Recognition Functions
    # ============================================================
    
    def analyze_user_intent(self, user_requirement: str) -> dict:
        """Use LLM to analyze user intent and determine tasks to execute
        
        Args:
            user_requirement: User requirement description 
            
        Returns:
            Intent analysis result (dict) 
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
            # Load intent recognition Prompt 
            intent_prompt = load_prompt("intent_recognition_prompt.md")
            
            # Build complete Prompt 
            full_prompt = f"{intent_prompt}\n\nUser requirement:\n{user_requirement}"
            
            # Call LLM to analyze intent 
            response = self.llm.call([{"role": "user", "content": full_prompt}])
            response_text = response.strip()
            
            # Remove possible Markdown code block markers 
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON 
            intent = json.loads(response_text)
            
            logger.info(f"TOA Intent Analysis: {intent['reasoning']}")
            return intent
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {e}")
            logger.error(f"Response text: {response_text}")
            # Fallback to default intent 
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
            # Fallback to default intent 
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
        
        Args:
            intent: Intent analysis result 
            
        Returns:
            Task type list 
        """
        result = []
        
        # Material design 
        if intent.get("needs_design", False):
            result.append("material_design")
        
        # Evaluation task 
        if intent.get("needs_evaluation", False):
            evaluation_mode = intent.get("evaluation_mode", "with_summary")
            if evaluation_mode == "experts_only":
                result.append("evaluation_only")
            else:
                result.extend(["evaluation", "final_validation"])
        
        # Mechanism analysis 
        if intent.get("needs_mechanism", False):
            result.append("mechanism_analysis")
        
        # Synthesis method 
        if intent.get("needs_synthesis", False):
            result.append("synthesis_method")
        
        # Operation guidance 
        if intent.get("needs_operation", False):
            result.append("operation_suggestion")
        
        # If no tasks, default to material design 
        if not result:
            result.append("material_design")
        
        return result
    
    # ============================================================
    #  Task Delegation Functions
    # ============================================================
    
    def delegate_task(self, task_type: str, task_description: str = None) -> Union[Agent, None]:
        """Delegate task to appropriate agent based on task type
        
        Args:
            task_type: Task type 
            task_description: Task description (optional) ）
            
        Returns:
            Appropriate agent instance 
        """
        agent = self.get_agent_for_task(task_type)
        if agent:
            logger.info(f"Delegated task type '{task_type}' to agent: {agent.role}")
            return agent
        else:
            logger.warning(f"No suitable agent found for task type:'{task_type}'")
            return None
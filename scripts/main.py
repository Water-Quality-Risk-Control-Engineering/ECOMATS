#!/usr/bin/env python3
"""
ECOMATS - Multi-Agent System for Water Treatment Material Design Based on CrewAI

This is the synchronous main program entry point that coordinates multiple AI agents
to design, evaluate, and optimize water treatment materials through a structured workflow.
"""

import sys
import os
import json
import signal
import time
from dotenv import load_dotenv
from crewai import Crew, Process
import dashscope

# Add project path to import monitoring module
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

from src.utils.workflow_monitor import WorkflowMonitor, create_monitor, get_monitor

# Windows compatibility patch: SIGHUP signal support
if sys.platform == 'win32':
    if not hasattr(signal, 'SIGHUP'):
        signal.SIGHUP = None  # Windows doesn't support SIGHUP, create placeholder
    # Set console encoding to UTF-8 to avoid Chinese garbled text
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass  # Python < 3.7 doesn't support reconfigure

def get_user_input():
    """Get user-defined material design requirements"""
    print("Please enter your material design requirements:")
    print("Example: Design an efficient catalyst for treating cadmium-containing heavy metal wastewater")
    print("Note: The system supports detailed material type classification and structural description requirements")
    user_input = input("Material design requirements: ")
    return user_input

def get_workflow_mode():
    """Get user-selected workflow mode"""
    print("\nPlease select workflow mode:")
    print("1. Preset workflow mode (execute all tasks in fixed order)")
    print("2. Agent autonomous scheduling mode (tasks dynamically assigned by coordinator)")
    while True:
        choice = input("Please enter option (1 or 2): ").strip()
        if choice == "1":
            return "preset"
        elif choice == "2":
            return "autonomous"
        else:
            print("Invalid option, please enter 1 or 2")

def check_environment_variables():
    """
    Check if required environment variables are set
    
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    from src.config.config import Config
    required_vars = {
        "QWEN_API_KEY": Config.QWEN_API_KEY,
        "QWEN_MODEL_NAME": Config.QWEN_MODEL_NAME
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        print("Error: The following required environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file in the project root and configure these variables")
        print("Example:")
        print("  QWEN_API_KEY=your_api_key_here")
        print("  QWEN_MODEL_NAME=qwen-max")
        return False
    
    return True

def create_all_agents(llm):
    """
    Create all agents used in the workflow
    
    Args:
        llm: Language model instance
    
    Returns:
        dict: Dictionary mapping agent names to agent instances
    """
    from src.agents.task_organizing_agent import TaskOrganizingAgent
    from src.agents.Creative_Designing_agent import CreativeDesigningAgent
    from src.agents.Assessment_Screening_agent_A import AssessmentScreeningAgentA
    from src.agents.Assessment_Screening_agent_B import AssessmentScreeningAgentB
    from src.agents.Assessment_Screening_agent_C import AssessmentScreeningAgentC
    from src.agents.Assessment_Screening_agent_Overall import AssessmentScreeningAgentOverall
    from src.agents.Extracting_agent import ExtractingAgent
    from src.agents.Mechanism_Mining_agent import MechanismMiningAgent
    from src.agents.Synthesis_Guiding_agent import SynthesisGuidingAgent
    from src.agents.Operation_Suggesting_agent import OperationSuggestingAgent
    coordinator_agent = TaskOrganizingAgent(llm).create_agent()
    material_designer_agent = CreativeDesigningAgent(llm).create_agent()
    expert_a_agent = AssessmentScreeningAgentA(llm).create_agent()
    expert_b_agent = AssessmentScreeningAgentB(llm).create_agent()
    expert_c_agent = AssessmentScreeningAgentC(llm).create_agent()
    final_validator_agent = AssessmentScreeningAgentOverall(llm).create_agent()
    literature_processor_agent = ExtractingAgent(llm).create_agent()
    mechanism_expert_agent = MechanismMiningAgent(llm).create_agent()
    synthesis_expert_agent = SynthesisGuidingAgent(llm).create_agent()
    operation_suggesting_agent = OperationSuggestingAgent(llm).create_agent()
    
    return {
        'coordinator': coordinator_agent,
        'material_designer': material_designer_agent,
        'expert_a': expert_a_agent,
        'expert_b': expert_b_agent,
        'expert_c': expert_c_agent,
        'final_validator': final_validator_agent,
        'literature_processor': literature_processor_agent,
        'mechanism_expert': mechanism_expert_agent,
        'synthesis_expert': synthesis_expert_agent,
        'operation_suggesting': operation_suggesting_agent
    }

def extract_feedback_from_result(result):
    """
    Extract feedback information from task results for iterative improvement
    
    Args:
        result: Task execution result (string or dict)
    
    Returns:
        str: Extracted feedback text
    """
    try:
        # Try to parse JSON results
        if isinstance(result, str):
            result_data = json.loads(result)
        else:
            result_data = result
            
        # Find feedback information
        feedback = ""
        if isinstance(result_data, dict):
            # Check for feedback from final validation expert
            if "results" in result_data and isinstance(result_data["results"], list):
                for item in result_data["results"]:
                    if "recommendations" in item:
                        feedback += f"Recommendations: {item['recommendations']}\n"
                    if "cons" in item:
                        feedback += f"Issues found: {item['cons']}\n"
            # Check for feedback from evaluation experts
            elif "evaluator" in result_data:
                if result_data["evaluator"] in ["A", "B", "C"]:
                    if "results" in result_data and isinstance(result_data["results"], list):
                        for item in result_data["results"]:
                            if "cons" in item:
                                feedback += f"Issues pointed out by evaluator {result_data['evaluator']}: {item['cons']}\n"
        return feedback
    except Exception as e:
        print(f"Error parsing feedback information: {e}")
        return "Unable to extract specific feedback information, please redesign the material solution."

def check_if_iteration_needed(result):
    """
    Check if the design needs iteration based on evaluation scores
    
    Args:
        result: Evaluation result containing scores and rankings
    
    Returns:
        bool: True if iteration is needed, False otherwise
    """
    from src.config.config import Config
    try:
        # Try to parse JSON results
        if isinstance(result, str):
            result_data = json.loads(result)
        else:
            result_data = result
            
        # Check results from final validation expert
        if isinstance(result_data, dict) and "results" in result_data:
            if isinstance(result_data["results"], list):
                for item in result_data["results"]:
                    if "rank" in item:
                        # If rank is Invalid or Poor, iteration is needed
                        if item["rank"] in ["Invalid", "Poor"]:
                            return True
                        # If comprehensive score is below threshold, iteration is needed
                        if "weighted_total" in item and item["weighted_total"] < Config.MIN_ACCEPTABLE_SCORE:
                            return True
            # Check results from evaluation experts
            elif "evaluator" in result_data and result_data["evaluator"] in ["A", "B", "C"]:
                if "results" in result_data and isinstance(result_data["results"], list):
                    for item in result_data["results"]:
                        if "scores" in item and isinstance(item["scores"], list):
                            # Calculate average score
                            avg_score = sum(item["scores"]) / len(item["scores"]) if item["scores"] else 0
                            if avg_score < Config.MIN_ACCEPTABLE_SCORE:
                                return True
        return False
    except Exception as e:
        print(f"Error checking iteration requirements: {e}")
        return False

def run_design_iteration(user_requirement, llm, iteration_count=0):
    """
    Run iterative design process until acceptable results or max iterations
    
    Args:
        user_requirement: User's material design requirements
        llm: Language model instance
        iteration_count: Current iteration count (default: 0)
    
    Returns:
        str: Final design result or max iteration message
    """
    from src.config.config import Config
    if iteration_count >= Config.MAX_DESIGN_ITERATIONS:
        return "Maximum iterations reached, stopping iterative design."
    
    print(f"Starting design iteration {iteration_count + 1}...")
    
    # Run preset workflow
    result = run_preset_workflow(user_requirement, llm)
    
    # Check if iteration is needed
    if check_if_iteration_needed(result):
        print("Current design does not meet requirements, iterative optimization needed...")
        # Extract feedback information
        feedback = extract_feedback_from_result(result)
        if feedback:
            # Update user requirements with feedback
            updated_requirement = f"{user_requirement}\n\nImprovement suggestions based on previous evaluation: {feedback}"
            # Proceed to next iteration
            return run_design_iteration(updated_requirement, llm, iteration_count + 1)
        else:
            return result
    else:
        return result

def run_preset_workflow(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Run preset workflow mode with fixed task sequence
    
    This mode executes all tasks in a predefined order:
    1. Material Design
    2. Evaluation (3 experts in parallel)
    3. Final Validation
    4. Synthesis Method
    5. Mechanism Analysis
    6. Operation Suggestion
    
    Args:
        user_requirement: User's material design requirements
        llm: Language model instance
        monitor: Workflow monitor instance (optional)
    
    Returns:
        Result from crew execution
    """
    print("Starting preset workflow mode...")
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    from src.config.config import Config
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask
    
    if monitor is None:
        monitor = create_monitor()
    
    monitor.set_workflow_info(user_requirement, "preset", is_async=False)
    
    # Create all agents for the workflow
    agents = create_all_agents(llm)
    
    # Create tasks and pass user requirements to each task
    # 1. First create material design task
    design_task = DesignTask(llm).create_task(agents['material_designer'], user_requirement=user_requirement)
    
    # Tools are called by Agents on-demand and cached via ContextStore
    # Pre-execution removed to avoid redundancy
    
    # 2. Create evaluation tasks for each expert, all dependent on design task
    # Explicitly pass user requirements to ensure tool calling strategy is executed
    evaluation_task_a = EvaluationTask(llm).create_task(agents['expert_a'], design_task, user_requirement=user_requirement)
    evaluation_task_b = EvaluationTask(llm).create_task(agents['expert_b'], design_task, user_requirement=user_requirement)
    evaluation_task_c = EvaluationTask(llm).create_task(agents['expert_c'], design_task, user_requirement=user_requirement)
    
    # 3. Create final validation task that synthesizes all evaluation results
    final_validation_task = FinalValidationTask(llm).create_task(agents['final_validator'], 
                                                           [design_task, evaluation_task_a, evaluation_task_b, evaluation_task_c], user_requirement=user_requirement)
    
    # 4. Create synthesis method task for material preparation guidance
    synthesis_method_task = SynthesisMethodTask(llm).create_task(agents['synthesis_expert'], final_validation_task, user_requirement=user_requirement)
    
    # 5. Create mechanism analysis task to understand material properties
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(agents['mechanism_expert'], final_validation_task, user_requirement=user_requirement)
    
    # 6. Create operation suggestion task for practical application guidance
    operation_suggesting_task = OperationSuggestingTask(llm).create_task(agents['operation_suggesting'], final_validation_task, user_requirement=user_requirement)
    
    # Create task list and Agent mapping for monitoring and tracking
    task_agent_map = [
        (design_task, agents['material_designer'], 'Creative_Designing_agent'),
        (evaluation_task_a, agents['expert_a'], 'Assessment_Screening_agent_A'),
        (evaluation_task_b, agents['expert_b'], 'Assessment_Screening_agent_B'),
        (evaluation_task_c, agents['expert_c'], 'Assessment_Screening_agent_C'),
        (final_validation_task, agents['final_validator'], 'Assessment_Screening_agent_Overall'),
        (synthesis_method_task, agents['synthesis_expert'], 'Synthesis_Guiding_agent'),
        (mechanism_analysis_task, agents['mechanism_expert'], 'Mechanism_Mining_agent'),
        (operation_suggesting_task, agents['operation_suggesting'], 'Operation_Suggesting_agent'),
    ]
    
    # Create mapping from task description to Agent for callback tracking
    task_desc_to_agent = {}
    for task, agent, role_name in task_agent_map:
        desc_key = str(task.description)[:100]  # Use first 100 chars of description as key
        task_desc_to_agent[desc_key] = (agent, role_name)

    import datetime
    global_workflow_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    task_start_times = {}
    task_completion_order = []
    last_task_end_time = time.time()
    
    def task_callback(task_output):
        nonlocal last_task_end_time
        import json
        import os
        
        # outputs
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        workflow_result_filename = f"workflow_result_{global_workflow_timestamp}.txt"
        workflow_result_filepath = os.path.join(outputs_dir, workflow_result_filename)
        
        task_description = getattr(task_output, 'description', 'N/A')
        task_name_raw = getattr(task_output, 'name', None)
        
        desc_key = str(task_description)[:100]
        agent_info = task_desc_to_agent.get(desc_key)
        
        if agent_info:
            agent, agent_role = agent_info
            agent_name = getattr(agent, 'name', agent_role)
        else:
            # TaskOutput
            agent = getattr(task_output, 'agent', None)
            agent_name = getattr(agent, 'name', 'Unknown') if agent else 'Unknown'
            agent_role = getattr(agent, 'role', 'Unknown') if agent else 'Unknown'
        
        task_idx = len(task_completion_order) + 1
        task_name = task_name_raw or f"Task_{task_idx}_{agent_role}"
        task_completion_order.append(task_name)
        
        # JSON
        json_output = None
        if hasattr(task_output, 'json_dict') and task_output.json_dict:
            json_output = task_output.json_dict
        
        current_time = time.time()
        task_start_time = last_task_end_time
        task_duration = current_time - task_start_time
        
        if monitor:
            monitor.start_agent_execution(agent_name, agent_role, task_name, str(task_description)[:200])
            if monitor._current_execution:
                monitor._current_execution.start_time = task_start_time
            monitor.end_agent_execution(output=str(task_output)[:5000], json_output=json_output)
        
        last_task_end_time = current_time
        
        with open(workflow_result_filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"Task Name: {task_name}\n")
            f.write(f"Agent: {agent_role}\n")
            f.write(f"Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {task_duration:.2f}s ({task_duration/60:.1f}min)\n")
            f.write("=" * 60 + "\n")
            f.write(f"Task Description: {str(task_description)[:500]}\n")
            f.write(f"Expected Output: {getattr(task_output, 'expected_output', 'N/A')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Actual Output:\n{str(task_output)}\n")
            
            if json_output:
                f.write("\n" + "=" * 60 + "\n")
                f.write("JSON Output:\n")
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            f.write(f"\n{'='*60}\n")
    
    # Create Crew with all agents and tasks
    ecomats_crew = Crew(
        agents=[
            agents['coordinator'], 
            agents['material_designer'],
            agents['expert_a'], 
            agents['expert_b'], 
            agents['expert_c'],
            agents['final_validator'],
            agents['literature_processor'],
            agents['mechanism_expert'],
            agents['synthesis_expert'],
            agents['operation_suggesting']
        ],
        tasks=[
            design_task, 
            evaluation_task_a, 
            evaluation_task_b, 
            evaluation_task_c, 
            final_validation_task,
            synthesis_method_task,
            mechanism_analysis_task,
            operation_suggesting_task
        ],  # Tasks executed in sequential order
        process=Process.sequential,  # Use sequential process for task execution
        verbose=Config.VERBOSE,
        task_callback=task_callback  # Add task callback for monitoring
    )
    
    # Execute
    try:
        result = ecomats_crew.kickoff()
        
        if monitor:
            monitor.set_final_result(result, "completed")
            monitor.save_report()
            monitor.save_readable_report()
            monitor.print_summary()
        
        return result
    except Exception as e:
        if monitor:
            monitor.set_final_result(None, "error", str(e))
            monitor.save_report()
            monitor.save_readable_report()
        return run_tool_only_summary(user_requirement)

def _execute_material_tools(user_requirement: str, project_root: str):
    """
    DEPRECATED: Pre-execute material-related tool calls
    
    This function is no longer used. Agents will call tools as needed and cache results via ContextStore.
    
    Keeping this function for backward compatibility.
    """
    pass  # No longer pre-execute


def run_autonomous_workflow(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Run agent autonomous scheduling mode based on TOA intent recognition
    
    New architecture based on TOA (Task Organizing Agent) that analyzes user intent
    and dynamically creates only necessary tasks instead of executing all tasks.
    
    Args:
        user_requirement: User's material design requirements
        llm: Language model instance
        monitor: Workflow monitor instance (optional)
    
    Returns:
        Crew execution result
    """
    print("Starting autonomous scheduling mode...")
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    from src.config.config import Config
    from src.agents.task_organizing_agent import TaskOrganizingAgent
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask
    from crewai import Task

    agents = create_all_agents(llm)
    
    # Create task organizing agent instance
    coordinator = TaskOrganizingAgent(llm)
    coordinator_agent = coordinator.create_agent()
    
    # Register all agents to TOA
    coordinator.register_agent("TaskOrganizingAgent", coordinator_agent)
    coordinator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    coordinator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    coordinator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    coordinator.register_agent("ExtractingAgent", agents['literature_processor'])
    coordinator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    coordinator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    coordinator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # Initialize monitor
    if monitor is None:
        monitor = create_monitor()
    monitor.set_workflow_info(user_requirement, "autonomous", is_async=False)
    
    # ============================================================
    # ✨ TOA Intent-Driven Workflow
    # ============================================================
    print("\n🧠 TOA analyzing user intent...")
    intent = coordinator.analyze_user_intent(user_requirement)
    print(f"✅ Intent analysis complete: {intent['reasoning']}")
    
    # Print detailed intent information
    print(f"\n📊 Intent Details:")
    print(f"   • Needs Design: {intent.get('needs_design', False)}")
    print(f"   • Needs Evaluation: {intent.get('needs_evaluation', False)}")
    print(f"   • Evaluation Mode: {intent.get('evaluation_mode', None)}")
    print(f"   • Needs Mechanism: {intent.get('needs_mechanism', False)}")
    print(f"   • Needs Synthesis: {intent.get('needs_synthesis', False)}")
    print(f"   • Needs Operation: {intent.get('needs_operation', False)}")
    print(f"   • Material Provided: {intent.get('material_provided', None)}")
    
    # Initialize task and agent lists
    required_tasks = []
    required_agents = []
    seen_roles = set()
    design_task = None
    final_validation_task = None
    
    # ============================================================
    # Step 1: Handle Material Design
    # ============================================================
    if intent.get('needs_design', False):
        print("\n🛠️ Creating material design task...")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
        
        # Tools are called by Agents on-demand and cached via ContextStore
        
    elif intent.get('needs_evaluation', False) or intent.get('needs_mechanism', False) or intent.get('needs_synthesis', False) or intent.get('needs_operation', False):
        # User provided material, create virtual context task (not executed)
        material_info = intent.get('material_provided') or user_requirement
        print(f"\n📝 Using user-provided material info: {material_info[:50]}...")
        
        # Create virtual context task for passing material info, not added to task list
        design_task = Task(
            description=f"Existing material provided by user:\n{user_requirement}",
            expected_output="Material information for downstream tasks",
            agent=coordinator_agent  # Use coordinator as placeholder
        )
        # Note: Virtual task NOT added to required_tasks
        # Tools are called by Agents on-demand and cached via ContextStore
    
    # ============================================================
    # Step 2: Handle Evaluation Tasks
    # ============================================================
    if intent.get('needs_evaluation', False):
        evaluation_mode = intent.get('evaluation_mode', 'with_summary')
        
        # Get all evaluation agents (3 experts: A, B, C)
        evaluation_agents = coordinator.get_all_agents_for_task("evaluation")
        evaluation_tasks = []
        
        for agent in evaluation_agents:
            if agent.role not in seen_roles:
                required_agents.append(agent)
                seen_roles.add(agent.role)
            task = EvaluationTask(llm).create_task(agent, design_task, user_requirement)
            evaluation_tasks.append(task)
        
        required_tasks.extend(evaluation_tasks)
        
        if evaluation_mode == 'experts_only':
            # Experts-only mode: 3 ASA experts scoring, no final summary
            print(f"\n✅ Experts-only mode: 3 ASA experts scoring, no final summary")
            print(f"   Experts-only mode: 3 ASA experts scoring, no final summary")
        else:
            # Full evaluation mode (with final summary)
            print(f"\n📊 Full evaluation mode: 3 ASA experts + final summary")
            print(f"   Full evaluation mode: 3 ASA experts + final summary")
            
            final_validation_agent = coordinator.get_agent_for_task("final_validation")
            if final_validation_agent and final_validation_agent.role not in seen_roles:
                required_agents.append(final_validation_agent)
                seen_roles.add(final_validation_agent.role)
            
            final_validation_task = FinalValidationTask(llm).create_task(
                final_validation_agent, 
                [design_task] + evaluation_tasks if design_task else evaluation_tasks,
                user_requirement=user_requirement
            )
            required_tasks.append(final_validation_task)
    
    # ============================================================
    # Step 3: Handle Mechanism Analysis Task
    # ============================================================
    if intent.get('needs_mechanism', False):
        print(f"\n🔬 Creating mechanism analysis task...")
        mechanism_agent = coordinator.get_agent_for_task("mechanism_analysis")
        if mechanism_agent and mechanism_agent.role not in seen_roles:
            required_agents.append(mechanism_agent)
            seen_roles.add(mechanism_agent.role)
        
        context_task = final_validation_task or design_task
        mechanism_task = MechanismAnalysisTask(llm).create_task(
            mechanism_agent, context_task, user_requirement=user_requirement
        )
        required_tasks.append(mechanism_task)
    
    # ============================================================
    # Step 4: Handle Synthesis Method Task
    # ============================================================
    if intent.get('needs_synthesis', False):
        print(f"\n🧪 Creating synthesis method task...")
        synthesis_agent = coordinator.get_agent_for_task("synthesis_method")
        if synthesis_agent and synthesis_agent.role not in seen_roles:
            required_agents.append(synthesis_agent)
            seen_roles.add(synthesis_agent.role)
        
        context_task = final_validation_task or design_task
        synthesis_task = SynthesisMethodTask(llm).create_task(
            synthesis_agent, context_task, user_requirement=user_requirement
        )
        required_tasks.append(synthesis_task)
    
    # ============================================================
    # Step 5: Handle Operation Guidance Task
    # ============================================================
    if intent.get('needs_operation', False):
        print(f"\n📖 Creating operation guidance task...")
        operation_agent = coordinator.get_agent_for_task("operation_suggestion")
        if operation_agent and operation_agent.role not in seen_roles:
            required_agents.append(operation_agent)
            seen_roles.add(operation_agent.role)
        
        context_task = final_validation_task or design_task
        operation_task = OperationSuggestingTask(llm).create_task(
            operation_agent, context_task, user_requirement=user_requirement
        )
        required_tasks.append(operation_task)
    
    # ============================================================
    # Check if there are any tasks
    # ============================================================
    if not required_tasks:
        print("\n⚠️ No tasks identified, defaulting to material design")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
    
    # ============================================================
    # Print task summary
    # ============================================================
    print(f"\n{'='*60}")
    print(f"📝 Task Summary")
    print(f"{'='*60}")
    print(f"   Total tasks: {len(required_tasks)}")
    print(f"   Total agents: {len(required_agents)}")
    for i, task in enumerate(required_tasks, 1):
        agent_role = getattr(task.agent, 'role', 'Unknown') if task.agent else 'None'
        print(f"   {i}. {agent_role}")
    print(f"{'='*60}\n")
    
    # Create mapping from task description to Agent for callback tracking
    task_desc_to_agent = {}
    for task in required_tasks:
        if task and task.agent:
            desc_key = str(task.description)[:100]
            task_desc_to_agent[desc_key] = (task.agent, getattr(task.agent, 'role', 'Unknown'))
    
    import datetime
    global_workflow_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    task_start_times = {}
    task_completion_order = []
    last_task_end_time = time.time()
    
    def task_callback(task_output):
        nonlocal last_task_end_time
        import json
        import os
        
        # outputs
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        workflow_result_filename = f"workflow_result_{global_workflow_timestamp}.txt"
        workflow_result_filepath = os.path.join(outputs_dir, workflow_result_filename)
        
        task_description = getattr(task_output, 'description', 'N/A')
        task_name_raw = getattr(task_output, 'name', None)
        
        desc_key = str(task_description)[:100]
        agent_info = task_desc_to_agent.get(desc_key)
        
        if agent_info:
            agent, agent_role = agent_info
            agent_name = getattr(agent, 'name', agent_role)
        else:
            # TaskOutput
            agent = getattr(task_output, 'agent', None)
            agent_name = getattr(agent, 'name', 'Unknown') if agent else 'Unknown'
            agent_role = getattr(agent, 'role', 'Unknown') if agent else 'Unknown'
        
        task_idx = len(task_completion_order) + 1
        task_name = task_name_raw or f"Task_{task_idx}_{agent_role}"
        task_completion_order.append(task_name)
        
        # JSON
        json_output = None
        if hasattr(task_output, 'json_dict') and task_output.json_dict:
            json_output = task_output.json_dict
        
        current_time = time.time()
        task_start_time = last_task_end_time
        task_duration = current_time - task_start_time
        
        if monitor:
            monitor.start_agent_execution(agent_name, agent_role, task_name, str(task_description)[:200])
            if monitor._current_execution:
                monitor._current_execution.start_time = task_start_time
            monitor.end_agent_execution(output=str(task_output)[:5000], json_output=json_output)
        
        last_task_end_time = current_time
        
        with open(workflow_result_filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"Task Name: {task_name}\n")
            f.write(f"Agent: {agent_role}\n")
            f.write(f"Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {task_duration:.2f}s ({task_duration/60:.1f}min)\n")
            f.write("=" * 60 + "\n")
            f.write(f"Task Description: {str(task_description)[:500]}\n")
            f.write(f"Expected Output: {getattr(task_output, 'expected_output', 'N/A')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Actual Output:\n{str(task_output)}\n")
            
            if json_output:
                f.write("\n" + "=" * 60 + "\n")
                f.write("JSON Output:\n")
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            f.write(f"\n{'='*60}\n")
    
    # Create Crew based on intent-driven task selection
    # Based on intent to determine if design task is needed
    all_tasks = required_tasks
    if design_task and intent.get('needs_design', False):
        # If design needed, design task is already in required_tasks
        # Note: design_task already added to required_tasks in Step 1, no need to re-add
        all_tasks = required_tasks
    elif design_task:
        # If virtual context task (user provided material), don't add to task list
        all_tasks = required_tasks
    
    ecomats_crew = Crew(
        agents=required_agents,
        tasks=all_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE,
        task_callback=task_callback
    )
    
    # Execute
    try:
        result = ecomats_crew.kickoff()
        
        if monitor:
            monitor.set_final_result(result, "completed")
            monitor.save_report()
            monitor.save_readable_report()
            monitor.print_summary()
        
        return result
    except Exception as e:
        if monitor:
            monitor.set_final_result(None, "error", str(e))
            monitor.save_report()
            monitor.save_readable_report()
        return run_tool_only_summary(user_requirement)

def main():
    """
    Main entry point for synchronous mode
    
    This function:
    1. Loads environment variables
    2. Gets user input for material design requirements
    3. Selects workflow mode (preset or autonomous)
    4. Creates LLM instance
    5. Executes selected workflow
    """
    print("ECOMATS Multi-Agent System Based on CrewAI")
    print("=" * 50)
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    # Force load .env from project root and override to ensure consistency with standalone tests
    from dotenv import load_dotenv, dotenv_values
    import os as _os
    _dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(_dotenv_path, override=True)
    # Write .env values to environment again to avoid IDE/task runner override
    try:
        _vals = dotenv_values(_dotenv_path)
        for k, v in (_vals or {}).items():
            if v is not None:
                _os.environ[k] = v
    except Exception:
        pass
    from src.config.config import Config

    if not check_environment_variables():
        return

    # Get user-defined input for material design requirements
    user_requirement = get_user_input()
    
    # Get user-selected workflow mode
    workflow_mode = get_workflow_mode()
    
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("Error: API key not set correctly")
        return
    
    # Set dashscope API key
    dashscope.api_key = Config.QWEN_API_KEY
    # Explicitly set OPENAI compatible environment to ensure underlying Provider doesn't read old variables
    import os as _os
    _os.environ["OPENAI_API_KEY"] = Config.QWEN_API_KEY or ""
    _os.environ["OPENAI_API_BASE"] = Config.QWEN_API_BASE or ""
    _os.environ["OPENAI_BASE_URL"] = Config.QWEN_API_BASE or ""
    
    from src.utils.llm_config import create_llm
    llm = create_llm()
    print("Successfully created Qwen3 LLM instance for main program")
    
    # Create monitor for tracking workflow execution
    monitor = create_monitor()
    print("📊 Workflow monitor initialized")
    
    # Execute corresponding workflow based on user-selected mode
    if workflow_mode == "preset":
        run_design_iteration(user_requirement, llm)
    else:
        run_autonomous_workflow(user_requirement, llm, monitor)
    
    # Workflow results and monitoring reports have been saved to outputs folder via task_callback
    print("\nWorkflow execution completed, results saved to outputs folder")
    print("📊 Monitoring reports include: JSON format (monitor_report_*.json) and readable format (monitor_report_*.txt)")

def run_tool_only_summary(user_requirement):
    """
    Fallback function when crew execution fails - executes only mandatory tool calls
    
    Args:
        user_requirement: User's requirement containing material formula
    
    Returns:
        dict: Tool execution results
    """
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    from src.utils.assessment_tool_executor import AssessmentToolExecutor
    executor = AssessmentToolExecutor()
    import re as _re
    m = _re.search(r"\b(?:[A-Z][a-z]?\d*){2,}\b", user_requirement or "")
    material_formula = m.group(0) if m else (user_requirement or "")
    results = executor.execute_mandatory_tool_calls(material_formula)
    import datetime, json
    outputs_dir = os.path.join(project_root, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fp = os.path.join(outputs_dir, f"workflow_result_{ts}.txt")
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(json.dumps(results, ensure_ascii=False, indent=2))
    print("Switched to tool-only execution mode, results saved to", fp)
    return results

if __name__ == "__main__":
    main()

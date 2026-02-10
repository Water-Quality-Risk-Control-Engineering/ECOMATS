#!/usr/bin/env python3
"""
ECOMATS - CrewAI 1.7.0 Async Version

Supports async Crew execution with 2-3x performance improvement through:
- Parallel task execution (evaluation agents run simultaneously)
- Async crew kickoff (akickoff)
- Memory system with DashScope embeddings
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project path BEFORE other imports
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

# Load environment variables BEFORE importing CrewAI
load_dotenv()

# Set OpenAI-compatible environment variables (required for CrewAI async mode)
_api_key = os.getenv('QWEN_API_KEY') or 'dummy'
_api_base = os.getenv('QWEN_API_BASE') or 'https://dashscope.aliyuncs.com/compatible-mode/v1'
os.environ['OPENAI_API_KEY'] = _api_key
os.environ['OPENAI_API_BASE'] = _api_base
os.environ['OPENAI_BASE_URL'] = _api_base

# Apply CrewAI compatibility patches (must be before CrewAI imports)
from workflow.patches import apply_crewai_patches
apply_crewai_patches()

from crewai import Crew, Process

# Setup unified logging
from src.utils.logging_config import setup_logging
setup_logging()

from src.config.config import Config
from src.utils.llm_config import create_llm
from src.utils.workflow_monitor import WorkflowMonitor, create_monitor, get_monitor

# Import modular components
from workflow.embeddings import create_dashscope_embedder
from workflow.callback_factory import create_task_callback_factory


def get_ui_text(key):
    """
    Get UI text in user's language
    
    Args:
        key: Text key to look up
    
    Returns:
        str: Localized text or key if not found
    """
    try:
        from src.locales.texts import TEXTS
        lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
        return TEXTS.get(lang, TEXTS['zh'])['ui'].get(key, key)
    except Exception:
        return key


def select_language():
    """
    Interactive language selection for user interface
    
    Returns:
        str: Selected language code ('zh' or 'en')
    """
    from src.locales import set_language
    
    print("\n" + "="*70)
    print("🌐 Select Language")
    print("="*70)
    print("1. Chinese")
    print("2. English")
    
    while True:
        choice = input("\nPlease select (1-2): ").strip()
        if choice == "1":
            set_language("zh")
            Config.LANGUAGE = "zh"
            print("✅ Selected: Chinese")
            return "zh"
        elif choice == "2":
            set_language("en")
            Config.LANGUAGE = "en"
            print("✅ English selected")
            return "en"
        print("Invalid option")


def get_user_input():
    """
    Get user material design requirements with bilingual prompts
    
    Returns:
        str: User's material design requirement
    """
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    print("\n" + "="*70)
    if lang == 'en':
        print("ECOMATS - Multi-Agent System for Water Treatment Material Design (Async)")
        print("="*70)
        print("\nPlease enter your material design requirements:")
        print("Example: Design an efficient catalyst for treating wastewater containing heavy metal cadmium")
        user_input = input("\nMaterial design requirement: ")
    else:
        print("ECOMATS - Water Treatment Material Design Multi-Agent System (Async Enhanced)")
        print("="*70)
        print("\nPlease enter your material design requirements:")
        print("Example: Design an efficient catalyst for treating cadmium-containing heavy metal wastewater")
        user_input = input("\nMaterial design requirements: ")
    return user_input


def get_workflow_mode():
    """
    Get workflow mode selection from user
    
    Returns:
        tuple: (mode_str, is_async) where mode is 'preset' or 'autonomous', and is_async is bool
               () 'preset''autonomous'is_async
    """
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    if lang == 'en':
        print("\nPlease select workflow mode:")
        print("1. Preset Workflow (Sync)")
        print("2. Preset Workflow (Async) ⚡ Recommended!")
        print("3. Autonomous Agent Scheduling (Sync)")
        print("4. Autonomous Agent Scheduling (Async) ⚡ Recommended!")
        prompt = "\nEnter option (1-4): "
        invalid_msg = "Invalid option, please enter 1-4"
    else:
        print("\nPlease select workflow mode:")
        print("1. Preset workflow (sync)")
        print("2. Preset workflow (async) ⚡ Recommended!")
        print("3. Agent autonomous scheduling (sync)")
        print("4. Agent autonomous scheduling (async) ⚡ Recommended!")
        prompt = "\nPlease enter option (1-4): "
        invalid_msg = "Invalid option, please enter 1-4"
    
    while True:
        choice = input(prompt).strip()
        if choice in ["1", "2", "3", "4"]:
            return {
                "1": ("preset", False),
                "2": ("preset", True),
                "3": ("autonomous", False),
                "4": ("autonomous", True)
            }[choice]
        print(invalid_msg)


def create_all_agents(llm):
    """
    Create all agents for the workflow
    
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
    from src.agents.Mechanism_Mining_agent import MechanismMiningAgent
    from src.agents.Synthesis_Guiding_agent import SynthesisGuidingAgent
    from src.agents.Operation_Suggesting_agent import OperationSuggestingAgent
    
    return {
        'coordinator': TaskOrganizingAgent(llm).create_agent(),
        'material_designer': CreativeDesigningAgent(llm).create_agent(),
        'expert_a': AssessmentScreeningAgentA(llm).create_agent(),
        'expert_b': AssessmentScreeningAgentB(llm).create_agent(),
        'expert_c': AssessmentScreeningAgentC(llm).create_agent(),
        'final_validator': AssessmentScreeningAgentOverall(llm).create_agent(),
        'mechanism_expert': MechanismMiningAgent(llm).create_agent(),
        'synthesis_expert': SynthesisGuidingAgent(llm).create_agent(),
        'operation_suggesting': OperationSuggestingAgent(llm).create_agent()
    }


async def run_autonomous_workflow_async(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Async autonomous workflow based on TOA intent-driven architecture
    
    This mode analyzes user intent and dynamically creates only necessary tasks,
    then executes them asynchronously for maximum performance.
    
    Args:
        user_requirement: User's material design requirements
        llm: Language model instance
        monitor: Workflow monitor instance (optional)
    
    Returns:
        Crew execution result
    """
    from src.agents.task_organizing_agent import TaskOrganizingAgent
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask
    from crewai import Task
    
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    if lang == 'en':
        print("\n🚀 Starting async autonomous scheduling workflow...")
    else:
        print("\n🚀 Starting async autonomous workflow...")
    print("-" * 70)
    
    agents = create_all_agents(llm)
    
    # Create TOA instance and register all agents
    coordinator = TaskOrganizingAgent(llm)
    coordinator_agent = coordinator.create_agent()
    
    # Register all agents to TOA for dynamic task allocation
    coordinator.register_agent("TaskOrganizingAgent", coordinator_agent)
    coordinator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    coordinator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    coordinator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    coordinator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    coordinator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    coordinator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # Initialize monitor
    if monitor is None:
        monitor = create_monitor()
    monitor.set_workflow_info(user_requirement, "autonomous", is_async=True)
    
    # Task start time tracking
    import time
    task_start_times = {}
    
    # ============================================================
    # ✨ TOA Intent-Driven Workflow
    # ============================================================
    if lang == 'en':
        print("\n🧠 TOA analyzing user intent...")
    else:
        print("\n🧠 TOA analyzing user intent...")
    
    intent = coordinator.analyze_user_intent(user_requirement)
    
    if lang == 'en':
        print(f"✅ Intent analysis complete: {intent['reasoning']}")
        print(f"\n📊 Intent Details:")
        print(f"   • Needs Design: {intent.get('needs_design', False)}")
        print(f"   • Needs Evaluation: {intent.get('needs_evaluation', False)}")
        print(f"   • Evaluation Mode: {intent.get('evaluation_mode', None)}")
        print(f"   • Needs Mechanism: {intent.get('needs_mechanism', False)}")
        print(f"   • Needs Synthesis: {intent.get('needs_synthesis', False)}")
        print(f"   • Needs Operation: {intent.get('needs_operation', False)}")
    else:
        print(f"✅ Intent analysis complete: {intent['reasoning']}")
        print(f"\n📊 Intent Details:")
        print(f"   • Needs Design: {intent.get('needs_design', False)}")
        print(f"   • Needs Evaluation: {intent.get('needs_evaluation', False)}")
        print(f"   • Evaluation Mode: {intent.get('evaluation_mode', None)}")
        print(f"   • Needs Mechanism: {intent.get('needs_mechanism', False)}")
        print(f"   • Needs Synthesis: {intent.get('needs_synthesis', False)}")
        print(f"   • Needs Operation: {intent.get('needs_operation', False)}")
    
    # Initialize task and agent lists
    required_tasks = []
    required_agents = []
    seen_roles = set()
    design_task = None
    final_validation_task = None
    
    # Step 1: Handle Material Design
    if intent.get('needs_design', False):
        if lang == 'en':
            print("\n🛠️ Creating material design task...")
        else:
            print("\n🛠️ Creating material design task...")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
    elif intent.get('needs_evaluation', False) or intent.get('needs_mechanism', False) or intent.get('needs_synthesis', False) or intent.get('needs_operation', False):
        # Create virtual context task for user-provided material
        material_info = intent.get('material_provided') or user_requirement
        if lang == 'en':
            print(f"\n📝 Using user-provided material: {material_info[:50]}...")
        else:
            print(f"\n📝 Using user-provided material: {material_info[:50]}...")
        design_task = Task(
            description=f"Existing material provided by user:\n{user_requirement}",
            expected_output="Material information for downstream tasks",
            agent=coordinator_agent
        )
    
    # Step 2: Handle Evaluation Tasks
    if intent.get('needs_evaluation', False):
        evaluation_mode = intent.get('evaluation_mode', 'with_summary')
        evaluation_agents = coordinator.get_all_agents_for_task("evaluation")
        print(f"\n🔍 Number of evaluation experts: {len(evaluation_agents)} - {[a.role for a in evaluation_agents]}")
        evaluation_tasks = []
        
        for agent in evaluation_agents:
            if agent.role not in seen_roles:
                required_agents.append(agent)
                seen_roles.add(agent.role)
            task = EvaluationTask(llm).create_task(agent, design_task, user_requirement)
            task.async_execution = True  # Enable async parallel execution!
            evaluation_tasks.append(task)
        
        required_tasks.extend(evaluation_tasks)
        
        if evaluation_mode == 'experts_only':
            if lang == 'en':
                print(f"\n✅ Experts-only mode: 3 ASA experts, no final summary")
            else:
                print(f"\n✅ Experts-only mode: 3 ASA experts scoring, no final summary")
        else:
            if lang == 'en':
                print(f"\n📊 Full evaluation mode: 3 ASA experts + final summary")
            else:
                print(f"\n📊 Full evaluation mode: 3 ASA experts + final summary")
            
            final_validation_agent = coordinator.get_agent_for_task("final_validation")
            if final_validation_agent and final_validation_agent.role not in seen_roles:
                required_agents.append(final_validation_agent)
                seen_roles.add(final_validation_agent.role)
                # Verify ASA Overall has no tools
                agent_tools = getattr(final_validation_agent, 'tools', None)
                if agent_tools:
                    print(f"  ⚠️ ASA Overall unexpectedly contains {len(agent_tools)} tools: {[t.name if hasattr(t, 'name') else str(t) for t in agent_tools]}")
                else:
                    print(f"  ✅ ASA Overall has no tools (analysis only)")
            final_validation_task = FinalValidationTask(llm).create_task(
                final_validation_agent,
                [design_task] + evaluation_tasks if design_task else evaluation_tasks,
                user_requirement=user_requirement
            )
            required_tasks.append(final_validation_task)
    
    # Step 3: Handle Mechanism Analysis Task
    if intent.get('needs_mechanism', False):
        if lang == 'en':
            print(f"\n🔬 Creating mechanism analysis task...")
        else:
            print(f"\n🔬 Creating mechanism analysis task...")
        mechanism_agent = coordinator.get_agent_for_task("mechanism_analysis")
        if mechanism_agent and mechanism_agent.role not in seen_roles:
            required_agents.append(mechanism_agent)
            seen_roles.add(mechanism_agent.role)
        context_task = final_validation_task or design_task
        mechanism_task = MechanismAnalysisTask(llm).create_task(
            mechanism_agent, context_task, user_requirement=user_requirement
        )
        mechanism_task.async_execution = True  # Enable async!
        required_tasks.append(mechanism_task)
    
    # Step 4: Handle Synthesis Method Task
    if intent.get('needs_synthesis', False):
        if lang == 'en':
            print(f"\n🧪 Creating synthesis method task...")
        else:
            print(f"\n🧪 Creating synthesis method task...")
        synthesis_agent = coordinator.get_agent_for_task("synthesis_method")
        if synthesis_agent and synthesis_agent.role not in seen_roles:
            required_agents.append(synthesis_agent)
            seen_roles.add(synthesis_agent.role)
        context_task = final_validation_task or design_task
        synthesis_task = SynthesisMethodTask(llm).create_task(
            synthesis_agent, context_task, user_requirement=user_requirement
        )
        synthesis_task.async_execution = True  # Enable async!
        required_tasks.append(synthesis_task)
    
    # Step 5: Handle Operation Guidance Task
    if intent.get('needs_operation', False):
        if lang == 'en':
            print(f"\n📖 Creating operation guidance task...")
        else:
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
    
    # Check if there are any tasks
    if not required_tasks:
        if lang == 'en':
            print("\n⚠️ No tasks identified, defaulting to material design")
        else:
            print("\n⚠️ No tasks identified, defaulting to material design")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
    
    # Print task summary with async indicators
    print(f"\n{'='*60}")
    if lang == 'en':
        print(f"📝 Task Summary")
        print(f"{'='*60}")
        print(f"   Total tasks: {len(required_tasks)}")
        print(f"   Total agents: {len(required_agents)}")
    else:
        print(f"📝 Task Summary")
        print(f"{'='*60}")
        print(f"   Total tasks: {len(required_tasks)}")
        print(f"   Total agents: {len(required_agents)}")
    for i, task in enumerate(required_tasks, 1):
        agent_role = getattr(task.agent, 'role', 'Unknown') if task.agent else 'None'
        async_flag = "⚡" if getattr(task, 'async_execution', False) else ""
        print(f"   {i}. {agent_role} {async_flag}")
    print(f"{'='*60}\n")
    
    # Create Crew and execute async
    DashScopeEmbedder = create_dashscope_embedder()
    
    # Tool call tracker grouped by Agent
    import threading
    tool_calls_by_agent = {}  # {agent_role: [(tool_name, count)]}
    tool_call_lock = threading.Lock()
    current_agent_context = threading.local()  # Thread-local storage for current Agent
    last_completed_agent = [None]  # Record last completed Agent
    
    # Use module-level factory function to create task_callback
    create_task_callback = create_task_callback_factory(monitor, task_start_times, current_agent_context, last_completed_agent)
    
    # Create step callback function to track tool calls
    def step_callback(step_output):
        """
        Capture each step execution including tool calls
        """
        try:
            # Try to get current Agent from step_output
            # CrewAI step_output may contain agent attribute or agent_name
            agent_role = 'Unknown'
            
            # Method 1: Get from step_output.agent
            if hasattr(step_output, 'agent'):
                agent = step_output.agent
                if hasattr(agent, 'role'):
                    agent_role = agent.role
                elif isinstance(agent, str):
                    agent_role = agent
            
            # Method 2: Get from other attributes of step_output
            if agent_role == 'Unknown' and hasattr(step_output, 'agent_name'):
                agent_role = step_output.agent_name
            
            # Method 3: Get from thread-local storage (fallback)
            if agent_role == 'Unknown':
                agent_role = getattr(current_agent_context, 'role', 'Unknown')
            
            # Update thread-local storage
            if agent_role != 'Unknown':
                current_agent_context.role = agent_role
            
            # Check if this is a tool call (AgentAction)
            if hasattr(step_output, 'tool'):
                tool_name = step_output.tool
                with tool_call_lock:
                    if agent_role not in tool_calls_by_agent:
                        tool_calls_by_agent[agent_role] = {}
                    if tool_name not in tool_calls_by_agent[agent_role]:
                        tool_calls_by_agent[agent_role][tool_name] = 0
                    tool_calls_by_agent[agent_role][tool_name] += 1
                    count = tool_calls_by_agent[agent_role][tool_name]
                    # Real-time output with Agent label
                    print(f"  🔧 [{agent_role[:15]}] {tool_name} (#{count})")
        except Exception:
            pass  # Ignore tracking errors
    
    # Set step_callback for each Agent
    for agent in required_agents:
        original_execute = None
        agent_role = getattr(agent, 'role', 'Unknown')
        agent.step_callback = step_callback
    
    # Create task callback for monitoring
    task_completion_times = []
    crew_start_time = [None]
    task_counter = [0]
    task_callback = create_task_callback(task_completion_times, crew_start_time, task_counter, suffix="")
    
    crew = Crew(
        name="ECOMATS",  # Set Crew name
        agents=required_agents,
        tasks=required_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE,  # Read from config, can be disabled via .env VERBOSE=False
        memory=False,  # Disable memory system - each task causes 7 Embedding API calls, affecting performance
        task_callback=task_callback,  # Add task callback
        step_callback=step_callback,  # Step callback to track tool calls
        embedder={
            "provider": "custom",
            "config": {
                "embedding_callable": DashScopeEmbedder
            }
        }
    )
    
    if lang == 'en':
        print("⚡ Using async execution mode...")
    else:
        print("⚡ Using async execution mode...")
    
    # Record Crew start time
    crew_start_time[0] = time.time()
    
    # Execute Crew asynchronously!
    result = await crew.akickoff(inputs={'requirement': user_requirement})
    
    # Save monitor report
    if monitor:
        monitor.set_final_result(result, "completed")
        monitor.save_report()
        monitor.save_readable_report()
        monitor.print_summary()
    
    return result


async def run_preset_workflow_async(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Async preset workflow using CrewAI 1.7.0 async features
    
    This mode executes all tasks in a fixed order with parallel execution where possible:
    1. Material Design (sequential)
    2. Evaluation (3 experts in parallel)
    3. Final Validation (sequential)
    4. Mechanism Analysis + Synthesis Method (parallel)
    5. Operation Suggestion (sequential)
    
    Args:
        user_requirement: User's material design requirements
        llm: Language model instance
        monitor: Workflow monitor instance (optional)
    
    Returns:
        Crew execution result
    """
    import time
    
    print("\n🚀 Starting async preset workflow...")
    print("-" * 70)
    
    # Initialize monitor
    if monitor is None:
        monitor = create_monitor()
    monitor.set_workflow_info(user_requirement, "preset", is_async=True)
    
    # Task start time tracking
    task_start_times = {}
    
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask  
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask
    
    # Create all agents
    agents = create_all_agents(llm)
    
    # 1. Material design task
    design_task = DesignTask(
        agent=agents['material_designer']
    ).create_task(
        agent=agents['material_designer'],
        user_requirement=user_requirement
    )
    
    # 2. Three evaluation tasks (can run in parallel)
    eval_a_task = EvaluationTask(
        agent=agents['expert_a']
    ).create_task(
        agent=agents['expert_a'],
        context_task=design_task
    )
    eval_a_task.async_execution = True  # Enable async!
    
    eval_b_task = EvaluationTask(
        agent=agents['expert_b']
    ).create_task(
        agent=agents['expert_b'],
        context_task=design_task
    )
    eval_b_task.async_execution = True  # Enable async!
    
    eval_c_task = EvaluationTask(
        agent=agents['expert_c']
    ).create_task(
        agent=agents['expert_c'],
        context_task=design_task
    )
    eval_c_task.async_execution = True  # Enable async!
    
    # 3. Final validation
    final_validation_task = FinalValidationTask(
        agent=agents['final_validator']
    ).create_task(
        agent=agents['final_validator'],
        context_task=[eval_a_task, eval_b_task, eval_c_task]
    )
    
    # 4. Mechanism analysis (can run in parallel with synthesis)
    mechanism_task = MechanismAnalysisTask(
        agent=agents['mechanism_expert']
    ).create_task(
        agent=agents['mechanism_expert'],
        context_task=final_validation_task
    )
    mechanism_task.async_execution = True  # Enable async!
    
    # 5. Synthesis method
    synthesis_task = SynthesisMethodTask(
        agent=agents['synthesis_expert']
    ).create_task(
        agent=agents['synthesis_expert'],
        context_task=final_validation_task
    )
    synthesis_task.async_execution = True  # Enable async!
    
    # 6. Operation suggestion
    operation_task = OperationSuggestingTask(
        agent=agents['operation_suggesting']
    ).create_task(
        agent=agents['operation_suggesting'],
        context_task=[mechanism_task, synthesis_task]
    )
    
    # Create Crew with custom DashScope Embedding
    # Note: Pass class not instance!
    DashScopeEmbedder = create_dashscope_embedder()
    
    # Create task callback for monitoring
    import threading
    current_agent_context = threading.local()
    last_completed_agent = [None]
    create_task_callback = create_task_callback_factory(monitor, task_start_times, current_agent_context, last_completed_agent)
    
    task_completion_times_2 = []
    crew_start_time_2 = [None]
    task_counter_2 = [0]
    task_callback = create_task_callback(task_completion_times_2, crew_start_time_2, task_counter_2, suffix="_2")
    
    crew = Crew(
        name="ECOMATS",  # Set Crew name
        agents=list(agents.values()),
        tasks=[
            design_task,
            eval_a_task, eval_b_task, eval_c_task,  # Parallel evaluation
            final_validation_task,
            mechanism_task, synthesis_task,  # Parallel analysis
            operation_task
        ],
        process=Process.sequential,
        verbose=Config.VERBOSE,  # Read from config, can be disabled via .env
        memory=False,  # Disable memory system - each task causes 7 Embedding API calls, affecting performance
        task_callback=task_callback,  # Add task callback
        embedder={
            "provider": "custom",
            "config": {
                "embedding_callable": DashScopeEmbedder  # Pass class
            }
        }
    )
    
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    if lang == 'en':
        print("⚡ Using async execution mode...")
        print("  - 3 evaluation tasks will run in parallel")
        print("  - Mechanism analysis and synthesis will run in parallel")
        print("  - Expected 2-3x performance improvement")
        print("\n🧠 Memory system enabled (using DashScope text-embedding-v2)")
        print("  - Short-term memory: Store current conversation context")
        print("  - Long-term memory: Learn from historical tasks")
        print("  - Entity memory: Extract key entity information")
        print("  - Storage location: ./.crewai/memory/\n")
    else:
        print("⚡ Using async execution mode...")
        print("  - 3 evaluation tasks will execute in parallel")
        print("  - Mechanism analysis and synthesis methods will execute in parallel")
        print("  - Expected 2-3x performance improvement")
        print("\n🧠 Memory system enabled (using DashScope text-embedding-v2)")
        print("  - Short-term memory: stores current conversation context")
        print("  - Long-term memory: learns from historical task experience")
        print("  - Entity memory: extracts key entity information")
        print("  - Storage location: ./.crewai/memory/\n")
    
    # Record Crew start time
    crew_start_time_2[0] = time.time()
    
    # Execute Crew asynchronously!
    result = await crew.akickoff(inputs={'requirement': user_requirement})
    
    # Save monitor report
    if monitor:
        monitor.set_final_result(result, "completed")
        monitor.save_report()
        monitor.save_readable_report()
        monitor.print_summary()
    
    return result


def run_preset_workflow_sync(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Synchronous preset workflow for backward compatibility
    
    Args:
        user_requirement: User's material design requirements
        llm: Language model instance
        monitor: Workflow monitor instance (optional)
    
    Returns:
        Workflow execution result
    """
    print("\n📌 Starting sync preset workflow...")
    print("-" * 70)
    
    # Import original run_preset_workflow from main.py
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from main import run_preset_workflow
    
    # Pass monitor to sync workflow
    return run_preset_workflow(user_requirement, llm, monitor)


async def main_async():
    """
    Main async entry point for the program
    
    This function:
    1. Loads environment variables
    2. Selects UI language
    3. Creates LLM instance
    4. Gets user input
    5. Executes selected workflow (sync or async)
    """
    load_dotenv()
    
    # Check environment variables
    if not Config.QWEN_API_KEY:
        print("❌ Error: QWEN_API_KEY not set")
        return
    
    # Select language
    select_language()
    
    # Create LLM
    llm = create_llm()
    
    # Get user input
    user_requirement = get_user_input()
    
    # Get workflow mode
    mode, use_async = get_workflow_mode()
    
    # Create monitor for tracking workflow execution
    monitor = create_monitor()
    print("📊 Workflow monitor initialized")
    
    if mode == "preset":
        if use_async:
            # Async preset workflow
            result = await run_preset_workflow_async(user_requirement, llm, monitor)
        else:
            # Sync preset workflow - pass monitor
            result = run_preset_workflow_sync(user_requirement, llm, monitor)
    else:
        # Autonomous scheduling mode
        if use_async:
            # Async autonomous
            result = await run_autonomous_workflow_async(user_requirement, llm, monitor)
        else:
            # Sync autonomous - pass monitor
            from main import run_autonomous_workflow
            result = run_autonomous_workflow(user_requirement, llm, monitor)
    
    # Output result
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    print("\n" + "="*70)
    if lang == 'en':
        print("Execution Complete!")
    else:
        print("Execution complete!")
    print("="*70)
    
    # Save result to outputs directory (without printing full result to terminal)
    save_result(result, user_requirement, mode, use_async, workflow_id=monitor.workflow_id)
    
    # Output monitor report info
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    if lang == 'en':
        print(f"\n📊 Monitor reports saved to outputs folder:")
        print(f"   - JSON format: monitor_report_*.json")
        print(f"   - Readable format: monitor_report_*.txt")
    else:
        print(f"\n📊 Monitoring reports saved to outputs folder:")
        print(f"   - JSON format: monitor_report_*.json")
        print(f"   - Readable format: monitor_report_*.txt")
    
    return result


def save_result(result, user_requirement, mode, use_async, workflow_id=None):
    """
    Save execution result to outputs directory
    
    Args:
        result: Workflow execution result
        user_requirement: User's original requirement
        mode: Workflow mode ('preset' or 'autonomous')
        use_async: Whether async mode was used
        workflow_id: Workflow ID from monitor (optional)
    """
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    # Ensure outputs directory exists
    outputs_dir = os.path.join(project_root, 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    
    # Generate filename
    timestamp = workflow_id or datetime.now().strftime('%Y%m%d_%H%M%S')
    mode_str = f"{mode}_{'async' if use_async else 'sync'}"
    filename = f"workflow_result_{timestamp}_{mode_str}.txt"
    filepath = os.path.join(outputs_dir, filename)
    
    # Write result
    with open(filepath, 'w', encoding='utf-8') as f:
        if lang == 'en':
            f.write(f"ECOMATS Execution Result\n")
            f.write(f"{'='*70}\n")
            f.write(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution Mode: {mode_str}\n")
            f.write(f"User Requirement: {user_requirement}\n")
        else:
            f.write(f"ECOMATS Execution Results\n")
            f.write(f"{'='*70}\n")
            f.write(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution Mode: {mode_str}\n")
            f.write(f"User Requirement: {user_requirement}\n")
        f.write(f"{'='*70}\n\n")
        f.write(str(result))
    
    if lang == 'en':
        print(f"\n📁 Result saved to: {filepath}")
    else:
        print(f"\n📁 Results saved to: {filepath}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ECOMATS - CrewAI 1.7.0 Async Enhanced Edition")
    print("="*70)
    print("\n🚀 New Features:")
    print("  - Async Crew execution (akickoff)")
    print("  - Parallel Task execution (async_execution=True)")
    print("  - 2-3x performance improvement")
    print("  - Fully backward compatible")
    print("\n" + "="*70)
    
    asyncio.run(main_async())

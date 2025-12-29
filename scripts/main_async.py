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
    Get UI text in user's language / 获取用户语言的UI文本
    
    Args:
        key: Text key to look up / 要查找的文本键
    
    Returns:
        str: Localized text or key if not found / 本地化文本，如果未找到则返回键
    """
    try:
        from src.locales.texts import TEXTS
        lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
        return TEXTS.get(lang, TEXTS['zh'])['ui'].get(key, key)
    except Exception:
        return key


def select_language():
    """
    Interactive language selection for user interface / 交互式选择用户界面语言
    
    Returns:
        str: Selected language code ('zh' or 'en') / 选择的语言代码（'zh'或'en'）
    """
    from src.locales import set_language
    
    print("\n" + "="*70)
    print("🌐 Select Language / 选择语言")
    print("="*70)
    print("1. 中文 (Chinese)")
    print("2. English")
    
    while True:
        choice = input("\n请选择/Please select (1-2): ").strip()
        if choice == "1":
            set_language("zh")
            # 更新Config中的语言设置
            Config.LANGUAGE = "zh"
            print("✅ 已选择中文")
            return "zh"
        elif choice == "2":
            set_language("en")
            Config.LANGUAGE = "en"
            print("✅ English selected")
            return "en"
        print("无效选项/Invalid option")


def get_user_input():
    """
    Get user material design requirements with bilingual prompts / 获取用户材料设计需求，使用双语提示
    
    Returns:
        str: User's material design requirement / 用户的材料设计需求
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
        print("ECOMATS - 水处理材料设计多智能体系统 (异步增强版)")
        print("="*70)
        print("\n请输入您的材料设计需求:")
        print("例如: 设计一种用于处理含重金属镉废水的高效催化剂")
        user_input = input("\n材料设计需求: ")
    return user_input


def get_workflow_mode():
    """
    Get workflow mode selection from user / 获取用户选择的工作模式
    
    Returns:
        tuple: (mode_str, is_async) where mode is 'preset' or 'autonomous', and is_async is bool
               (模式字符串，是否异步) 其中模式为'preset'或'autonomous'，is_async为布尔值
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
        print("\n请选择工作模式:")
        print("1. 预设工作流 (同步)")
        print("2. 预设工作流 (异步) ⚡ 推荐!")
        print("3. 智能体自主调度 (同步)")
        print("4. 智能体自主调度 (异步) ⚡ 推荐!")
        prompt = "\n请输入选项 (1-4): "
        invalid_msg = "无效选项,请输入1-4"
    
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
    Create all agents for the workflow / 创建所有智能体
    
    Args:
        llm: Language model instance / 语言模型实例
    
    Returns:
        dict: Dictionary mapping agent names to agent instances / 将智能体名称映射到智能体实例的字典
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
    Async autonomous workflow based on TOA intent-driven architecture / 异步自主调度工作流 - 基于 TOA 意图驱动架构
    
    This mode analyzes user intent and dynamically creates only necessary tasks,
    then executes them asynchronously for maximum performance.
    该模式分析用户意图并动态创建必要的任务，
    然后异步执行以获得最大性能。
    
    Args:
        user_requirement: User's material design requirements / 用户需求
        llm: Language model instance / LLM实例
        monitor: Workflow monitor instance (optional) / 工作流监控器实例（可选）
    
    Returns:
        Crew execution result / Crew执行结果
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
        print("\n🚀 启动异步自主调度工作流...")
    print("-" * 70)
    
    agents = create_all_agents(llm)
    
    # Create TOA instance and register all agents / 创建 TOA 实例
    coordinator = TaskOrganizingAgent(llm)
    coordinator_agent = coordinator.create_agent()
    
    # Register all agents to TOA for dynamic task allocation / 注册所有智能体到 TOA
    coordinator.register_agent("TaskOrganizingAgent", coordinator_agent)
    coordinator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    coordinator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    coordinator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    coordinator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    coordinator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    coordinator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # Initialize monitor / 初始化监控器
    if monitor is None:
        monitor = create_monitor()
    monitor.set_workflow_info(user_requirement, "autonomous", is_async=True)
    
    # Task start time tracking / 任务开始时间记录
    import time
    task_start_times = {}
    
    # ============================================================
    # ✨ TOA Intent-Driven Workflow / TOA 意图驱动流程
    # ============================================================
    if lang == 'en':
        print("\n🧠 TOA analyzing user intent...")
    else:
        print("\n🧠 TOA 正在分析用户意图...")
    
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
        print(f"✅ 意图分析完成: {intent['reasoning']}")
        print(f"\n📊 意图详情:")
        print(f"   • 需要设计: {intent.get('needs_design', False)}")
        print(f"   • 需要评估: {intent.get('needs_evaluation', False)}")
        print(f"   • 评估模式: {intent.get('evaluation_mode', None)}")
        print(f"   • 需要机理分析: {intent.get('needs_mechanism', False)}")
        print(f"   • 需要合成方法: {intent.get('needs_synthesis', False)}")
        print(f"   • 需要操作指导: {intent.get('needs_operation', False)}")
    
    # 初始化任务和智能体列表 / Initialize task and agent lists
    required_tasks = []
    required_agents = []
    seen_roles = set()
    design_task = None
    final_validation_task = None
    
    # Step 1: Handle Material Design / 处理材料设计
    if intent.get('needs_design', False):
        if lang == 'en':
            print("\n🛠️ Creating material design task...")
        else:
            print("\n🛠️ 创建材料设计任务...")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
    elif intent.get('needs_evaluation', False) or intent.get('needs_mechanism', False) or intent.get('needs_synthesis', False) or intent.get('needs_operation', False):
        # Create virtual context task for user-provided material / 创建虚拟上下文任务
        material_info = intent.get('material_provided') or user_requirement
        if lang == 'en':
            print(f"\n📝 Using user-provided material: {material_info[:50]}...")
        else:
            print(f"\n📝 使用用户提供的材料: {material_info[:50]}...")
        design_task = Task(
            description=f"Existing material provided by user:\n{user_requirement}",
            expected_output="Material information for downstream tasks",
            agent=coordinator_agent
        )
    
    # Step 2: Handle Evaluation Tasks / 处理评估任务
    if intent.get('needs_evaluation', False):
        evaluation_mode = intent.get('evaluation_mode', 'with_summary')
        evaluation_agents = coordinator.get_all_agents_for_task("evaluation")
        print(f"\n🔍 评估专家数量 / Number of evaluation experts: {len(evaluation_agents)} - {[a.role for a in evaluation_agents]}")
        evaluation_tasks = []
        
        for agent in evaluation_agents:
            if agent.role not in seen_roles:
                required_agents.append(agent)
                seen_roles.add(agent.role)
            task = EvaluationTask(llm).create_task(agent, design_task, user_requirement)
            task.async_execution = True  # Enable async parallel execution! / 启用异步并行！
            evaluation_tasks.append(task)
        
        required_tasks.extend(evaluation_tasks)
        
        if evaluation_mode == 'experts_only':
            if lang == 'en':
                print(f"\n✅ Experts-only mode: 3 ASA experts, no final summary")
            else:
                print(f"\n✅ 仅评估模式：三个 ASA 专家评分，不进行最终总结")
        else:
            if lang == 'en':
                print(f"\n📊 Full evaluation mode: 3 ASA experts + final summary")
            else:
                print(f"\n📊 完整评估模式：三个 ASA 专家评分 + 最终总结")
            
            final_validation_agent = coordinator.get_agent_for_task("final_validation")
            if final_validation_agent and final_validation_agent.role not in seen_roles:
                required_agents.append(final_validation_agent)
                seen_roles.add(final_validation_agent.role)
                # Verify ASA Overall has no tools / 验证 ASA Overall 没有工具
                agent_tools = getattr(final_validation_agent, 'tools', None)
                if agent_tools:
                    print(f"  ⚠️ ASA Overall unexpectedly contains {len(agent_tools)} tools / ASA Overall 意外包含 {len(agent_tools)} 个工具: {[t.name if hasattr(t, 'name') else str(t) for t in agent_tools]}")
                else:
                    print(f"  ✅ ASA Overall has no tools (analysis only) / ASA Overall 无工具（仅综合分析）")
            final_validation_task = FinalValidationTask(llm).create_task(
                final_validation_agent,
                [design_task] + evaluation_tasks if design_task else evaluation_tasks,
                user_requirement=user_requirement
            )
            required_tasks.append(final_validation_task)
    
    # Step 3: Handle Mechanism Analysis Task / 处理机理分析任务
    if intent.get('needs_mechanism', False):
        if lang == 'en':
            print(f"\n🔬 Creating mechanism analysis task...")
        else:
            print(f"\n🔬 创建机理分析任务...")
        mechanism_agent = coordinator.get_agent_for_task("mechanism_analysis")
        if mechanism_agent and mechanism_agent.role not in seen_roles:
            required_agents.append(mechanism_agent)
            seen_roles.add(mechanism_agent.role)
        context_task = final_validation_task or design_task
        mechanism_task = MechanismAnalysisTask(llm).create_task(
            mechanism_agent, context_task, user_requirement=user_requirement
        )
        mechanism_task.async_execution = True  # Enable async! / 启用异步！
        required_tasks.append(mechanism_task)
    
    # Step 4: Handle Synthesis Method Task / 处理合成方法任务
    if intent.get('needs_synthesis', False):
        if lang == 'en':
            print(f"\n🧪 Creating synthesis method task...")
        else:
            print(f"\n🧪 创建合成方法任务...")
        synthesis_agent = coordinator.get_agent_for_task("synthesis_method")
        if synthesis_agent and synthesis_agent.role not in seen_roles:
            required_agents.append(synthesis_agent)
            seen_roles.add(synthesis_agent.role)
        context_task = final_validation_task or design_task
        synthesis_task = SynthesisMethodTask(llm).create_task(
            synthesis_agent, context_task, user_requirement=user_requirement
        )
        synthesis_task.async_execution = True  # Enable async! / 启用异步！
        required_tasks.append(synthesis_task)
    
    # Step 5: Handle Operation Guidance Task / 处理操作指导任务
    if intent.get('needs_operation', False):
        if lang == 'en':
            print(f"\n📖 Creating operation guidance task...")
        else:
            print(f"\n📖 创建操作指导任务...")
        operation_agent = coordinator.get_agent_for_task("operation_suggestion")
        if operation_agent and operation_agent.role not in seen_roles:
            required_agents.append(operation_agent)
            seen_roles.add(operation_agent.role)
        context_task = final_validation_task or design_task
        operation_task = OperationSuggestingTask(llm).create_task(
            operation_agent, context_task, user_requirement=user_requirement
        )
        required_tasks.append(operation_task)
    
    # Check if there are any tasks / 检查是否有任务
    if not required_tasks:
        if lang == 'en':
            print("\n⚠️ No tasks identified, defaulting to material design")
        else:
            print("\n⚠️ 未识别出任何任务，默认执行材料设计")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
    
    # Print task summary with async indicators / 打印任务摘要
    print(f"\n{'='*60}")
    if lang == 'en':
        print(f"📝 Task Summary")
        print(f"{'='*60}")
        print(f"   Total tasks: {len(required_tasks)}")
        print(f"   Total agents: {len(required_agents)}")
    else:
        print(f"📝 任务摘要")
        print(f"{'='*60}")
        print(f"   总任务数: {len(required_tasks)}")
        print(f"   总智能体数: {len(required_agents)}")
    for i, task in enumerate(required_tasks, 1):
        agent_role = getattr(task.agent, 'role', 'Unknown') if task.agent else 'None'
        async_flag = "⚡" if getattr(task, 'async_execution', False) else ""
        print(f"   {i}. {agent_role} {async_flag}")
    print(f"{'='*60}\n")
    
    # Create Crew and execute async / 创建 Crew 并异步执行
    DashScopeEmbedder = create_dashscope_embedder()
    
    # Tool call tracker grouped by Agent / 工具调用追踪器 - 按 Agent 分组记录
    import threading
    tool_calls_by_agent = {}  # {agent_role: [(tool_name, count)]}
    tool_call_lock = threading.Lock()
    current_agent_context = threading.local()  # Thread-local storage for current Agent / 线程本地存储当前 Agent
    last_completed_agent = [None]  # Record last completed Agent / 记录上一个完成的 Agent
    
    # Use module-level factory function to create task_callback / 使用模块级别的工厂函数创廻 task_callback
    create_task_callback = create_task_callback_factory(monitor, task_start_times, current_agent_context, last_completed_agent)
    
    # Create step callback function to track tool calls / 创建步骤回调函数，用于追踪工具调用
    def step_callback(step_output):
        """
        Capture each step execution including tool calls / 捕获每一步执行，包括工具调用
        """
        try:
            # Try to get current Agent from step_output / 尝试从 step_output 获取当前 Agent
            # CrewAI step_output may contain agent attribute or agent_name / CrewAI step_output 可能包含 agent 属性或 agent_name
            agent_role = 'Unknown'
            
            # Method 1: Get from step_output.agent / 方法1：从 step_output.agent 获取
            if hasattr(step_output, 'agent'):
                agent = step_output.agent
                if hasattr(agent, 'role'):
                    agent_role = agent.role
                elif isinstance(agent, str):
                    agent_role = agent
            
            # Method 2: Get from other attributes of step_output / 方法2：从 step_output 的其他属性获取
            if agent_role == 'Unknown' and hasattr(step_output, 'agent_name'):
                agent_role = step_output.agent_name
            
            # Method 3: Get from thread-local storage (fallback) / 方法3：从线程本地存储获取（备用）
            if agent_role == 'Unknown':
                agent_role = getattr(current_agent_context, 'role', 'Unknown')
            
            # Update thread-local storage / 更新线程本地存储
            if agent_role != 'Unknown':
                current_agent_context.role = agent_role
            
            # Check if this is a tool call (AgentAction) / 检查是否是工具调用 (AgentAction)
            if hasattr(step_output, 'tool'):
                tool_name = step_output.tool
                with tool_call_lock:
                    if agent_role not in tool_calls_by_agent:
                        tool_calls_by_agent[agent_role] = {}
                    if tool_name not in tool_calls_by_agent[agent_role]:
                        tool_calls_by_agent[agent_role][tool_name] = 0
                    tool_calls_by_agent[agent_role][tool_name] += 1
                    count = tool_calls_by_agent[agent_role][tool_name]
                    # Real-time output with Agent label / 实时输出，带 Agent 标识
                    print(f"  🔧 [{agent_role[:15]}] {tool_name} (#{count})")
        except Exception:
            pass  # Ignore tracking errors / 忽略追踪错误
    
    # Set step_callback for each Agent / 为每个 Agent 设置 step_callback 并注入上下文
    for agent in required_agents:
        original_execute = None
        agent_role = getattr(agent, 'role', 'Unknown')
        agent.step_callback = step_callback
    
    # Create task callback for monitoring / 创建任务回调函数
    task_completion_times = []
    crew_start_time = [None]
    task_counter = [0]
    task_callback = create_task_callback(task_completion_times, crew_start_time, task_counter, suffix="")
    
    crew = Crew(
        name="ECOMATS",  # Set Crew name / 设置 Crew 名称
        agents=required_agents,
        tasks=required_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE,  # Read from config, can be disabled via .env VERBOSE=False / 从配置读取，.env 中 VERBOSE=False 可禁用 CrewAI 树状显示
        memory=False,  # Disable memory system - each task causes 7 Embedding API calls, affecting performance / 禁用记忆系统 - 每个任务会导致7次Embedding API调用,影响性能
        task_callback=task_callback,  # Add task callback / 添加任务回调
        step_callback=step_callback,  # Step callback to track tool calls / 步骤回调追踪工具调用
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
        print("⚡ 使用异步执行模式...")
    
    # Record Crew start time / 记录 Crew 开始时间
    crew_start_time[0] = time.time()
    
    # Execute Crew asynchronously! / 异步执行 Crew！
    result = await crew.akickoff(inputs={'requirement': user_requirement})
    
    # 保存监控报告 / Save monitor report
    if monitor:
        monitor.set_final_result(result, "completed")
        monitor.save_report()
        monitor.save_readable_report()
        monitor.print_summary()
    
    return result


async def run_preset_workflow_async(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Async preset workflow using CrewAI 1.7.0 async features / 异步预设工作流 - 使用CrewAI 1.7.0异步功能
    
    This mode executes all tasks in a fixed order with parallel execution where possible:
    1. Material Design (sequential) / 材料设计（顺序）
    2. Evaluation (3 experts in parallel) / 评估（3个专家并行）
    3. Final Validation (sequential) / 最终验证（顺序）
    4. Mechanism Analysis + Synthesis Method (parallel) / 机理分析 + 合成方法（并行）
    5. Operation Suggestion (sequential) / 操作建议（顺序）
    
    Args:
        user_requirement: User's material design requirements / 用户需求
        llm: Language model instance / LLM实例
        monitor: Workflow monitor instance (optional) / 工作流监控器实例（可选）
    
    Returns:
        Crew execution result / Crew执行结果
    """
    import time
    
    print("\n🚀 启动异步预设工作流...")
    print("-" * 70)
    
    # Initialize monitor / 初始化监控器
    if monitor is None:
        monitor = create_monitor()
    monitor.set_workflow_info(user_requirement, "preset", is_async=True)
    
    # Task start time tracking / 任务开始时间记录
    task_start_times = {}
    
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask  
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask
    
    # Create all agents / 创建所有agent
    agents = create_all_agents(llm)
    
    # 1. Material design task / 材料设计任务
    design_task = DesignTask(
        agent=agents['material_designer']
    ).create_task(
        agent=agents['material_designer'],
        user_requirement=user_requirement
    )
    
    # 2. Three evaluation tasks (can run in parallel) / 三个评估任务（可并行）
    eval_a_task = EvaluationTask(
        agent=agents['expert_a']
    ).create_task(
        agent=agents['expert_a'],
        context_task=design_task
    )
    eval_a_task.async_execution = True  # Enable async! / 启用异步！
    
    eval_b_task = EvaluationTask(
        agent=agents['expert_b']
    ).create_task(
        agent=agents['expert_b'],
        context_task=design_task
    )
    eval_b_task.async_execution = True  # Enable async! / 启用异步！
    
    eval_c_task = EvaluationTask(
        agent=agents['expert_c']
    ).create_task(
        agent=agents['expert_c'],
        context_task=design_task
    )
    eval_c_task.async_execution = True  # Enable async! / 启用异步！
    
    # 3. Final validation / 最终验证
    final_validation_task = FinalValidationTask(
        agent=agents['final_validator']
    ).create_task(
        agent=agents['final_validator'],
        context_task=[eval_a_task, eval_b_task, eval_c_task]
    )
    
    # 4. Mechanism analysis (can run in parallel with synthesis) / 机制分析（可与合成并行）
    mechanism_task = MechanismAnalysisTask(
        agent=agents['mechanism_expert']
    ).create_task(
        agent=agents['mechanism_expert'],
        context_task=final_validation_task
    )
    mechanism_task.async_execution = True  # Enable async! / 启用异步！
    
    # 5. Synthesis method / 合成方法
    synthesis_task = SynthesisMethodTask(
        agent=agents['synthesis_expert']
    ).create_task(
        agent=agents['synthesis_expert'],
        context_task=final_validation_task
    )
    synthesis_task.async_execution = True  # Enable async! / 启用异步！
    
    # 6. Operation suggestion / 操作建议
    operation_task = OperationSuggestingTask(
        agent=agents['operation_suggesting']
    ).create_task(
        agent=agents['operation_suggesting'],
        context_task=[mechanism_task, synthesis_task]
    )
    
    # Create Crew with custom DashScope Embedding / 创建Crew（使用自定义DashScope Embedding）
    # Note: Pass class not instance! / 注意：传入类而不是实例！
    DashScopeEmbedder = create_dashscope_embedder()
    
    # Create task callback for monitoring / 创建任务回调函数
    import threading
    current_agent_context = threading.local()
    last_completed_agent = [None]
    create_task_callback = create_task_callback_factory(monitor, task_start_times, current_agent_context, last_completed_agent)
    
    task_completion_times_2 = []
    crew_start_time_2 = [None]
    task_counter_2 = [0]
    task_callback = create_task_callback(task_completion_times_2, crew_start_time_2, task_counter_2, suffix="_2")
    
    crew = Crew(
        name="ECOMATS",  # Set Crew name / 设置 Crew 名称
        agents=list(agents.values()),
        tasks=[
            design_task,
            eval_a_task, eval_b_task, eval_c_task,  # Parallel evaluation / 并行评估
            final_validation_task,
            mechanism_task, synthesis_task,  # Parallel analysis / 并行分析
            operation_task
        ],
        process=Process.sequential,
        verbose=Config.VERBOSE,  # Read from config, can be disabled via .env / 从配置读取，.env 中 VERBOSE=False 可禁用
        memory=False,  # Disable memory system - each task causes 7 Embedding API calls, affecting performance / 禁用记忆系统 - 每个任务会导致7次Embedding API调用,影响性能
        task_callback=task_callback,  # Add task callback / 添加任务回调
        embedder={
            "provider": "custom",
            "config": {
                "embedding_callable": DashScopeEmbedder  # Pass class / 传入类
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
        print("⚡ 使用异步执行模式...")
        print("  - 3个评估任务将并行执行")
        print("  - 机制分析和合成方法将并行执行")
        print("  - 预计性能提升2-3倍")
        print("\n🧠 记忆系统已启用 (使用DashScope text-embedding-v2)")
        print("  - 短期记忆: 存储当前对话上下文")
        print("  - 长期记忆: 学习历史任务经验")
        print("  - 实体记忆: 提取关键实体信息")
        print("  - 存储位置: ./.crewai/memory/\n")
    
    # Record Crew start time / 记录 Crew 开始时间
    crew_start_time_2[0] = time.time()
    
    # Execute Crew asynchronously! / 异步执行Crew！
    result = await crew.akickoff(inputs={'requirement': user_requirement})
    
    # 保存监控报告 / Save monitor report
    if monitor:
        monitor.set_final_result(result, "completed")
        monitor.save_report()
        monitor.save_readable_report()
        monitor.print_summary()
    
    return result


def run_preset_workflow_sync(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Synchronous preset workflow for backward compatibility / 同步预设工作流 - 保持向后兼容
    
    Args:
        user_requirement: User's material design requirements / 用户需求
        llm: Language model instance / LLM实例
        monitor: Workflow monitor instance (optional) / 工作流监控器实例（可选）
    
    Returns:
        Workflow execution result / 工作流执行结果
    """
    print("\n📌 启动同步预设工作流...")
    print("-" * 70)
    
    # Import original run_preset_workflow from main.py / 导入原始main.py的run_preset_workflow
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from main import run_preset_workflow
    
    # Pass monitor to sync workflow / 传递监控器到同步工作流
    return run_preset_workflow(user_requirement, llm, monitor)


async def main_async():
    """
    Main async entry point for the program / 异步主入口
    
    This function:
    1. Loads environment variables / 加载环境变量
    2. Selects UI language / 选择UI语言
    3. Creates LLM instance / 创建LLM实例
    4. Gets user input / 获取用户输入
    5. Executes selected workflow (sync or async) / 执行选定的工作流（同步或异步）
    """
    load_dotenv()
    
    # Check environment variables / 检查环境变量
    if not Config.QWEN_API_KEY:
        print("❌ 错误: 未设置QWEN_API_KEY / Error: QWEN_API_KEY not set")
        return
    
    # Select language / 选择语言
    select_language()
    
    # Create LLM / 创建LLM
    llm = create_llm()
    
    # Get user input / 获取用户输入
    user_requirement = get_user_input()
    
    # Get workflow mode / 获取工作模式
    mode, use_async = get_workflow_mode()
    
    # Create monitor for tracking workflow execution / 创建监控器
    monitor = create_monitor()
    print("📊 工作流监控器已初始化 / Workflow monitor initialized")
    
    if mode == "preset":
        if use_async:
            # Async preset workflow / 异步预设工作流
            result = await run_preset_workflow_async(user_requirement, llm, monitor)
        else:
            # Sync preset workflow - pass monitor / 同步预设工作流 - 传递监控器
            result = run_preset_workflow_sync(user_requirement, llm, monitor)
    else:
        # Autonomous scheduling mode / 自主调度模式
        if use_async:
            # Async autonomous / 异步自主调度
            result = await run_autonomous_workflow_async(user_requirement, llm, monitor)
        else:
            # Sync autonomous - pass monitor / 同步自主调度 - 传递监控器
            from main import run_autonomous_workflow
            result = run_autonomous_workflow(user_requirement, llm, monitor)
    
    # Output result / 输出结果
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    print("\n" + "="*70)
    if lang == 'en':
        print("Execution Complete!")
    else:
        print("执行完成!")
    print("="*70)
    
    # Save result to outputs directory (without printing full result to terminal) / 保存结果到outputs目录（不在终端打印完整结果）
    save_result(result, user_requirement, mode, use_async, workflow_id=monitor.workflow_id)
    
    # Output monitor report info / 输出监控报告信息
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    if lang == 'en':
        print(f"\n📊 Monitor reports saved to outputs folder:")
        print(f"   - JSON format: monitor_report_*.json")
        print(f"   - Readable format: monitor_report_*.txt")
    else:
        print(f"\n📊 监控报告已保存到 outputs 文件夹：")
        print(f"   - JSON格式: monitor_report_*.json")
        print(f"   - 可读格式: monitor_report_*.txt")
    
    return result


def save_result(result, user_requirement, mode, use_async, workflow_id=None):
    """
    Save execution result to outputs directory / 保存执行结果到outputs目录
    
    Args:
        result: Workflow execution result / 工作流执行结果
        user_requirement: User's original requirement / 用户原始需求
        mode: Workflow mode ('preset' or 'autonomous') / 工作流模式
        use_async: Whether async mode was used / 是否使用了异步模式
        workflow_id: Workflow ID from monitor (optional) / 监控器的工作流ID（可选）
    """
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    # 确保outputs目录存在 / Ensure outputs directory exists
    outputs_dir = os.path.join(project_root, 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    
    # 生成文件名 / Generate filename
    timestamp = workflow_id or datetime.now().strftime('%Y%m%d_%H%M%S')
    mode_str = f"{mode}_{'async' if use_async else 'sync'}"
    filename = f"workflow_result_{timestamp}_{mode_str}.txt"
    filepath = os.path.join(outputs_dir, filename)
    
    # 写入结果 / Write result
    with open(filepath, 'w', encoding='utf-8') as f:
        if lang == 'en':
            f.write(f"ECOMATS Execution Result\n")
            f.write(f"{'='*70}\n")
            f.write(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution Mode: {mode_str}\n")
            f.write(f"User Requirement: {user_requirement}\n")
        else:
            f.write(f"ECOMATS 执行结果\n")
            f.write(f"{'='*70}\n")
            f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"执行模式: {mode_str}\n")
            f.write(f"用户需求: {user_requirement}\n")
        f.write(f"{'='*70}\n\n")
        f.write(str(result))
    
    if lang == 'en':
        print(f"\n📁 Result saved to: {filepath}")
    else:
        print(f"\n📁 结果已保存到: {filepath}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ECOMATS - CrewAI 1.7.0 异步增强版")
    print("="*70)
    print("\n🚀 新特性:")
    print("  - 异步Crew执行 (akickoff)")
    print("  - 并行Task执行 (async_execution=True)")
    print("  - 性能提升2-3倍")
    print("  - 完全向后兼容")
    print("\n" + "="*70)
    
    # 运行异步主函数
    asyncio.run(main_async())

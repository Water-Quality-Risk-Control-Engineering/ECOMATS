#!/usr/bin/env python3
"""
ECOMATS - Multi-Agent System for Water Treatment Material Design Based on CrewAI
ECOMATS - 基于CrewAI的水处理材料设计多智能体系统

This is the synchronous main program entry point that coordinates multiple AI agents
to design, evaluate, and optimize water treatment materials through a structured workflow.
这是同步模式的主程序入口，通过结构化工作流协调多个AI智能体来设计、评估和优化水处理材料。
"""

import sys
import os
import json
import signal
import time
from dotenv import load_dotenv
from crewai import Crew, Process
import dashscope

# Add project path to import monitoring module / 添加项目路径以便导入监控模块
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

from src.utils.workflow_monitor import WorkflowMonitor, create_monitor, get_monitor

# Windows compatibility patch: SIGHUP signal support / Windows 兼容性补丁：SIGHUP 信号支持
if sys.platform == 'win32':
    if not hasattr(signal, 'SIGHUP'):
        signal.SIGHUP = None  # Windows doesn't support SIGHUP, create placeholder / Windows 不支持 SIGHUP，创建占位符
    # Set console encoding to UTF-8 to avoid Chinese garbled text / 设置控制台编码为 UTF-8，避免中文乱码
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass  # Python < 3.7 doesn't support reconfigure / Python < 3.7 不支持 reconfigure

def get_user_input():
    """获取用户自定义的材料设计需求 / Get user-defined material design requirements"""
    print("请输入您的材料设计需求: / Please enter your material design requirements:")
    print("例如: 设计一种用于处理含重金属镉废水的高效催化剂 / Example: Design an efficient catalyst for treating cadmium-containing heavy metal wastewater")
    print("注意: 系统支持详细的材料类型分类和结构描述要求 / Note: The system supports detailed material type classification and structural description requirements")
    user_input = input("材料设计需求: / Material design requirements: ")
    return user_input

def get_workflow_mode():
    """获取用户选择的工作模式 / Get user-selected workflow mode"""
    print("\n请选择工作模式: / Please select workflow mode:")
    print("1. 预设工作流模式 (按固定顺序执行所有任务) / Preset workflow mode (execute all tasks in fixed order)")
    print("2. 智能体自主调度模式 (由协调者动态分配任务) / Agent autonomous scheduling mode (tasks dynamically assigned by coordinator)")
    while True:
        choice = input("请输入选项 (1 或 2): / Please enter option (1 or 2): ").strip()
        if choice == "1":
            return "preset"
        elif choice == "2":
            return "autonomous"
        else:
            print("无效选项，请输入 1 或 2 / Invalid option, please enter 1 or 2")

def check_environment_variables():
    """
    Check if required environment variables are set / 检查必要的环境变量是否已设置
    
    Returns:
        bool: True if all required variables are set, False otherwise
              如果所有必需的变量都已设置则返回True，否则返回False
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
        print("错误：以下必要的环境变量未设置 / Error: The following required environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n请在项目根目录创建.env文件并配置这些变量 / Please create a .env file in the project root and configure these variables")
        print("示例：/ Example:")
        print("  QWEN_API_KEY=your_api_key_here")
        print("  QWEN_MODEL_NAME=qwen-max")
        return False
    
    return True

def create_all_agents(llm):
    """
    Create all agents used in the workflow / 创建所有智能体的公共函数
    
    Args:
        llm: Language model instance / 语言模型实例
    
    Returns:
        dict: Dictionary mapping agent names to agent instances
              将智能体名称映射到智能体实例的字典
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
    Extract feedback information from task results for iterative improvement / 从结果中提取反馈信息用于迭代改进
    
    Args:
        result: Task execution result (string or dict) / 任务执行结果（字符串或字典）
    
    Returns:
        str: Extracted feedback text / 提取的反馈文本
    """
    try:
        # 尝试解析JSON结果 / Try to parse JSON results
        if isinstance(result, str):
            result_data = json.loads(result)
        else:
            result_data = result
            
        # 查找反馈信息 / Find feedback information
        feedback = ""
        if isinstance(result_data, dict):
            # 检查是否有最终验证专家的反馈 / Check for feedback from final validation expert
            if "results" in result_data and isinstance(result_data["results"], list):
                for item in result_data["results"]:
                    if "recommendations" in item:
                        feedback += f"改进建议: {item['recommendations']}\n"
                    if "cons" in item:
                        feedback += f"存在的问题: {item['cons']}\n"
            # 检查评估专家的反馈 / Check for feedback from evaluation experts
            elif "evaluator" in result_data:
                if result_data["evaluator"] in ["A", "B", "C"]:
                    if "results" in result_data and isinstance(result_data["results"], list):
                        for item in result_data["results"]:
                            if "cons" in item:
                                feedback += f"评估专家{result_data['evaluator']}指出的问题: {item['cons']}\n / Issues pointed out by evaluator {result_data['evaluator']}: {item['cons']}\n"
        return feedback
    except Exception as e:
        print(f"解析反馈信息时出错: {e} / Error parsing feedback information: {e}")
        return "无法提取具体反馈信息，请重新设计材料方案。/ Unable to extract specific feedback information, please redesign the material solution."

def check_if_iteration_needed(result):
    """
    Check if the design needs iteration based on evaluation scores / 根据评估分数检查是否需要迭代设计
    
    Args:
        result: Evaluation result containing scores and rankings / 包含分数和排名的评估结果
    
    Returns:
        bool: True if iteration is needed, False otherwise / 如需迭代返回True，否则返回False
    """
    from src.config.config import Config
    try:
        # 尝试解析JSON结果 / Try to parse JSON results
        if isinstance(result, str):
            result_data = json.loads(result)
        else:
            result_data = result
            
        # 检查最终验证专家的结果 / Check results from final validation expert
        if isinstance(result_data, dict) and "results" in result_data:
            if isinstance(result_data["results"], list):
                for item in result_data["results"]:
                    if "rank" in item:
                        # 如果排名为Invalid或Poor，则需要迭代 / If rank is Invalid or Poor, iteration is needed
                        if item["rank"] in ["Invalid", "Poor"]:
                            return True
                        # 如果综合评分低于阈值，则需要迭代 / If comprehensive score is below threshold, iteration is needed
                        if "weighted_total" in item and item["weighted_total"] < Config.MIN_ACCEPTABLE_SCORE:
                            return True
            # 检查评估专家的结果 / Check results from evaluation experts
            elif "evaluator" in result_data and result_data["evaluator"] in ["A", "B", "C"]:
                if "results" in result_data and isinstance(result_data["results"], list):
                    for item in result_data["results"]:
                        if "scores" in item and isinstance(item["scores"], list):
                            # 计算平均分 / Calculate average score
                            avg_score = sum(item["scores"]) / len(item["scores"]) if item["scores"] else 0
                            if avg_score < Config.MIN_ACCEPTABLE_SCORE:
                                return True
        return False
    except Exception as e:
        print(f"检查迭代需求时出错: {e}")
        return False

def run_design_iteration(user_requirement, llm, iteration_count=0):
    """
    Run iterative design process until acceptable results or max iterations / 运行迭代设计过程直到获得可接受的结果或达到最大迭代次数
    
    Args:
        user_requirement: User's material design requirements / 用户的材料设计需求
        llm: Language model instance / 语言模型实例
        iteration_count: Current iteration count (default: 0) / 当前迭代次数（默认：0）
    
    Returns:
        str: Final design result or max iteration message / 最终设计结果或最大迭代次数消息
    """
    from src.config.config import Config
    if iteration_count >= Config.MAX_DESIGN_ITERATIONS:
        return "已达到最大迭代次数，停止迭代设计。"
    
    print(f"开始第 {iteration_count + 1} 轮设计迭代...")
    
    # 运行预设工作流 / Run preset workflow
    result = run_preset_workflow(user_requirement, llm)
    
    # 检查是否需要迭代 / Check if iteration is needed
    if check_if_iteration_needed(result):
        print("当前设计方案未达到要求，需要进行迭代优化...")
        # 提取反馈信息 / Extract feedback information
        feedback = extract_feedback_from_result(result)
        if feedback:
            # 更新用户需求，加入反馈 / Update user requirements with feedback
            updated_requirement = f"{user_requirement}\n\n基于上一轮评估的改进建议：{feedback}"
            # 进行下一轮迭代 / Proceed to next iteration
            return run_design_iteration(updated_requirement, llm, iteration_count + 1)
        else:
            return result
    else:
        return result

def run_preset_workflow(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Run preset workflow mode with fixed task sequence / 运行预设工作流模式，按固定任务序列执行
    
    This mode executes all tasks in a predefined order:
    1. Material Design / 材料设计
    2. Evaluation (3 experts in parallel) / 评估（3个专家）
    3. Final Validation / 最终验证
    4. Synthesis Method / 合成方法
    5. Mechanism Analysis / 机理分析
    6. Operation Suggestion / 操作建议
    
    Args:
        user_requirement: User's material design requirements / 用户需求
        llm: Language model instance / LLM实例
        monitor: Workflow monitor instance (optional) / 工作流监控器实例（可选）
    
    Returns:
        Result from crew execution / Crew执行结果
    """
    print("启动预设工作流模式...")
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    from src.config.config import Config
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask
    
    # 如果没有传入监控器，创建一个新的
    if monitor is None:
        monitor = create_monitor()
    
    # 设置监控器信息
    monitor.set_workflow_info(user_requirement, "preset", is_async=False)
    
    # Create all agents for the workflow / 创建所有智能体
    agents = create_all_agents(llm)
    
    # Create tasks and pass user requirements to each task / 创建任务，将用户需求传递给任务
    # 1. First create material design task / 首先创建材料设计任务
    design_task = DesignTask(llm).create_task(agents['material_designer'], user_requirement=user_requirement)
    
    # Tools are called by Agents on-demand and cached via ContextStore / 工具由 Agent 按需调用，通过 ContextStore 缓存结果
    # Pre-execution removed to avoid redundancy / 移除了预执行调用以避免冗余
    
    # 2. Create evaluation tasks for each expert, all dependent on design task / 为每个评估专家创建评估任务，都依赖于设计任务
    # Explicitly pass user requirements to ensure tool calling strategy is executed / 明确传递用户需求给评估任务，以确保工具调用策略得到执行
    evaluation_task_a = EvaluationTask(llm).create_task(agents['expert_a'], design_task, user_requirement=user_requirement)
    evaluation_task_b = EvaluationTask(llm).create_task(agents['expert_b'], design_task, user_requirement=user_requirement)
    evaluation_task_c = EvaluationTask(llm).create_task(agents['expert_c'], design_task, user_requirement=user_requirement)
    
    # 3. Create final validation task that synthesizes all evaluation results / 创建最终验证任务，依赖于所有评估任务
    final_validation_task = FinalValidationTask(llm).create_task(agents['final_validator'], 
                                                           [design_task, evaluation_task_a, evaluation_task_b, evaluation_task_c], user_requirement=user_requirement)
    
    # 4. Create synthesis method task for material preparation guidance / 创建合成方法任务，依赖于最终验证任务
    synthesis_method_task = SynthesisMethodTask(llm).create_task(agents['synthesis_expert'], final_validation_task, user_requirement=user_requirement)
    
    # 5. Create mechanism analysis task to understand material properties / 创建机理分析任务，依赖于最终验证任务
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(agents['mechanism_expert'], final_validation_task, user_requirement=user_requirement)
    
    # 6. Create operation suggestion task for practical application guidance / 创建操作建议任务，依赖于最终验证任务
    operation_suggesting_task = OperationSuggestingTask(llm).create_task(agents['operation_suggesting'], final_validation_task, user_requirement=user_requirement)
    
    # Create task list and Agent mapping for monitoring and tracking / 创建任务列表和 Agent 映射（用于监控器）
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
    
    # Create mapping from task description to Agent for callback tracking / 创建任务描述到 Agent 的映射
    task_desc_to_agent = {}
    for task, agent, role_name in task_agent_map:
        desc_key = str(task.description)[:100]  # Use first 100 chars of description as key / 使用描述前100字符作为键
        task_desc_to_agent[desc_key] = (agent, role_name)

    # 定义任务回调函数，用于保存整体流程结果和监控数据
    # 生成全局时间戳，确保所有任务使用相同的流程结果文件
    import datetime
    global_workflow_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 任务开始时间记录（用于计算每个任务耗时）
    task_start_times = {}
    task_completion_order = []  # 记录任务完成顺序
    last_task_end_time = time.time()  # 上一个任务的结束时间
    
    def task_callback(task_output):
        nonlocal last_task_end_time
        import json
        import os
        
        # 确保outputs目录存在
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        # 生成流程结果文件名
        workflow_result_filename = f"workflow_result_{global_workflow_timestamp}.txt"
        workflow_result_filepath = os.path.join(outputs_dir, workflow_result_filename)
        
        # 获取任务信息
        task_description = getattr(task_output, 'description', 'N/A')
        task_name_raw = getattr(task_output, 'name', None)
        
        # 通过任务描述查找对应的 Agent
        desc_key = str(task_description)[:100]
        agent_info = task_desc_to_agent.get(desc_key)
        
        if agent_info:
            agent, agent_role = agent_info
            agent_name = getattr(agent, 'name', agent_role)
        else:
            # 回退方案：从 TaskOutput 尝试获取
            agent = getattr(task_output, 'agent', None)
            agent_name = getattr(agent, 'name', 'Unknown') if agent else 'Unknown'
            agent_role = getattr(agent, 'role', 'Unknown') if agent else 'Unknown'
        
        # 生成唯一任务名
        task_idx = len(task_completion_order) + 1
        task_name = task_name_raw or f"Task_{task_idx}_{agent_role}"
        task_completion_order.append(task_name)
        
        # 获取JSON输出
        json_output = None
        if hasattr(task_output, 'json_dict') and task_output.json_dict:
            json_output = task_output.json_dict
        
        # 计算实际耗时
        current_time = time.time()
        task_start_time = last_task_end_time
        task_duration = current_time - task_start_time
        
        # 使用监控器记录执行
        if monitor:
            monitor.start_agent_execution(agent_name, agent_role, task_name, str(task_description)[:200])
            if monitor._current_execution:
                monitor._current_execution.start_time = task_start_time
            monitor.end_agent_execution(output=str(task_output)[:5000], json_output=json_output)
        
        # 更新上一个任务结束时间
        last_task_end_time = current_time
        
        # 将任务输出追加到流程结果文件
        with open(workflow_result_filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"任务名称: {task_name}\n")
            f.write(f"Agent: {agent_role}\n")
            f.write(f"执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"耗时: {task_duration:.2f}s ({task_duration/60:.1f}min)\n")
            f.write("=" * 60 + "\n")
            f.write(f"任务描述: {str(task_description)[:500]}\n")
            f.write(f"预期输出: {getattr(task_output, 'expected_output', 'N/A')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"实际输出:\n{str(task_output)}\n")
            
            # 如果有JSON输出，也保存
            if json_output:
                f.write("\n" + "=" * 60 + "\n")
                f.write("JSON输出:\n")
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            f.write(f"\n{'='*60}\n")
    
    # Create Crew with all agents and tasks / 创建Crew包含所有智能体和任务
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
        ],  # Tasks executed in sequential order / 任务按顺序执行
        process=Process.sequential,  # Use sequential process for task execution / 使用顺序流程执行任务
        verbose=Config.VERBOSE,
        task_callback=task_callback  # Add task callback for monitoring / 添加任务回调函数
    )
    
    # 执行 / Execute
    try:
        result = ecomats_crew.kickoff()
        
        # 设置最终结果并保存监控报告
        if monitor:
            monitor.set_final_result(result, "completed")
            monitor.save_report()
            monitor.save_readable_report()
            monitor.print_summary()
        
        return result
    except Exception as e:
        # 记录错误
        if monitor:
            monitor.set_final_result(None, "error", str(e))
            monitor.save_report()
            monitor.save_readable_report()
        return run_tool_only_summary(user_requirement)

def _execute_material_tools(user_requirement: str, project_root: str):
    """
    已废弃: 预执行材料相关工具调用 / DEPRECATED: Pre-execute material-related tool calls
    
    此函数已不再使用。Agent 会根据需要自行调用工具，并通过 ContextStore 缓存结果。
    This function is no longer used. Agents will call tools as needed and cache results via ContextStore.
    
    保留此函数以保持向后兼容。 / Keeping this function for backward compatibility.
    """
    pass  # 不再预执行 / No longer pre-execute


def run_autonomous_workflow(user_requirement, llm, monitor: WorkflowMonitor = None):
    """
    Run agent autonomous scheduling mode based on TOA intent recognition / 运行智能体自主调度模式，基于TOA意图识别
    
    New architecture based on TOA (Task Organizing Agent) that analyzes user intent
    and dynamically creates only necessary tasks instead of executing all tasks.
    基于TOA（任务组织代理）的全新架构，分析用户意图并动态创建必要的任务，而不是执行所有任务。
    
    Args:
        user_requirement: User's material design requirements / 用户需求
        llm: Language model instance / LLM实例
        monitor: Workflow monitor instance (optional) / 工作流监控器实例（可选）
    
    Returns:
        Crew execution result / Crew执行结果
    """
    print("启动智能体自主调度模式... / Starting autonomous scheduling mode...")
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
    
    # 创建任务组织代理实例 / Create task organizing agent instance
    coordinator = TaskOrganizingAgent(llm)
    coordinator_agent = coordinator.create_agent()
    
    # 注册所有智能体到 TOA / Register all agents to TOA
    coordinator.register_agent("TaskOrganizingAgent", coordinator_agent)
    coordinator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    coordinator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    coordinator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    coordinator.register_agent("ExtractingAgent", agents['literature_processor'])
    coordinator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    coordinator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    coordinator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # 初始化监控器 / Initialize monitor
    if monitor is None:
        monitor = create_monitor()
    monitor.set_workflow_info(user_requirement, "autonomous", is_async=False)
    
    # ============================================================
    # ✨ TOA Intent-Driven Workflow / TOA 意图驱动流程
    # ============================================================
    print("\n🧠 TOA 正在分析用户意图... / TOA analyzing user intent...")
    intent = coordinator.analyze_user_intent(user_requirement)
    print(f"✅ 意图分析完成 / Intent analysis complete: {intent['reasoning']}")
    
    # Print detailed intent information / 打印意图详情
    print(f"\n📊 意图详情 / Intent Details:")
    print(f"   • 需要设计 / Needs Design: {intent.get('needs_design', False)}")
    print(f"   • 需要评估 / Needs Evaluation: {intent.get('needs_evaluation', False)}")
    print(f"   • 评估模式 / Evaluation Mode: {intent.get('evaluation_mode', None)}")
    print(f"   • 需要机理分析 / Needs Mechanism: {intent.get('needs_mechanism', False)}")
    print(f"   • 需要合成方法 / Needs Synthesis: {intent.get('needs_synthesis', False)}")
    print(f"   • 需要操作指导 / Needs Operation: {intent.get('needs_operation', False)}")
    print(f"   • 提供的材料 / Material Provided: {intent.get('material_provided', None)}")
    
    # Initialize task and agent lists / 初始化任务和智能体列表
    required_tasks = []
    required_agents = []
    seen_roles = set()
    design_task = None
    final_validation_task = None
    
    # ============================================================
    # Step 1: Handle Material Design / 处理材料设计
    # ============================================================
    if intent.get('needs_design', False):
        print("\n🛠️ 创建材料设计任务 / Creating material design task...")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
        
        # Tools are called by Agents on-demand and cached via ContextStore / 工具由 Agent 按需调用，通过 ContextStore 缓存结果
        
    elif intent.get('needs_evaluation', False) or intent.get('needs_mechanism', False) or intent.get('needs_synthesis', False) or intent.get('needs_operation', False):
        # User provided material, create virtual context task (not executed) / 用户提供了材料，创建虚拟上下文任务（不实际执行）
        material_info = intent.get('material_provided') or user_requirement
        print(f"\n📝 使用用户提供的材料信息 / Using user-provided material info: {material_info[:50]}...")
        
        # Create virtual context task for passing material info, not added to task list / 创建虚拟上下文任务，仅用于传递材料信息，不添加到任务列表
        design_task = Task(
            description=f"Existing material provided by user:\n{user_requirement}",
            expected_output="Material information for downstream tasks",
            agent=coordinator_agent  # Use coordinator as placeholder / 使用协调员作为占位符
        )
        # Note: Virtual task NOT added to required_tasks / 注意：虚拟任务不添加到 required_tasks
        # Tools are called by Agents on-demand and cached via ContextStore / 工具由 Agent 按需调用，通过 ContextStore 缓存结果
    
    # ============================================================
    # Step 2: Handle Evaluation Tasks / 处理评估任务
    # ============================================================
    if intent.get('needs_evaluation', False):
        evaluation_mode = intent.get('evaluation_mode', 'with_summary')
        
        # Get all evaluation agents (3 experts: A, B, C) / 获取评估智能体
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
            # Experts-only mode: 3 ASA experts scoring, no final summary / 仅专家评分模式
            print(f"\n✅ 仅评估模式：三个 ASA 专家评分，不进行最终总结")
            print(f"   Experts-only mode: 3 ASA experts scoring, no final summary")
        else:
            # Full evaluation mode (with final summary) / 完整评估模式（包含最终总结）
            print(f"\n📊 完整评估模式：三个 ASA 专家评分 + 最终总结")
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
    # Step 3: Handle Mechanism Analysis Task / 处理机理分析任务
    # ============================================================
    if intent.get('needs_mechanism', False):
        print(f"\n🔬 创建机理分析任务 / Creating mechanism analysis task...")
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
    # Step 4: Handle Synthesis Method Task / 处理合成方法任务
    # ============================================================
    if intent.get('needs_synthesis', False):
        print(f"\n🧪 创建合成方法任务 / Creating synthesis method task...")
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
    # Step 5: Handle Operation Guidance Task / 处理操作指导任务
    # ============================================================
    if intent.get('needs_operation', False):
        print(f"\n📖 创建操作指导任务 / Creating operation guidance task...")
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
    # Check if there are any tasks / 检查是否有任务
    # ============================================================
    if not required_tasks:
        print("\n⚠️ 未识别出任何任务，默认执行材料设计 / No tasks identified, defaulting to material design")
        design_agent = coordinator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
    
    # ============================================================
    # Print task summary / 打印任务摘要
    # ============================================================
    print(f"\n{'='*60}")
    print(f"📝 任务摘要 / Task Summary")
    print(f"{'='*60}")
    print(f"   总任务数 / Total tasks: {len(required_tasks)}")
    print(f"   总智能体数 / Total agents: {len(required_agents)}")
    for i, task in enumerate(required_tasks, 1):
        agent_role = getattr(task.agent, 'role', 'Unknown') if task.agent else 'None'
        print(f"   {i}. {agent_role}")
    print(f"{'='*60}\n")
    
    # Create mapping from task description to Agent for callback tracking / 创建任务描述到 Agent 的映射（用于监控器）
    task_desc_to_agent = {}
    for task in required_tasks:
        if task and task.agent:
            desc_key = str(task.description)[:100]
            task_desc_to_agent[desc_key] = (task.agent, getattr(task.agent, 'role', 'Unknown'))
    
    # 定义任务回调函数，用于保存整体流程结果和监控数据
    # 生成全局时间戳，确保所有任务使用相同的流程结果文件
    import datetime
    global_workflow_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 任务开始时间记录（用于计算每个任务耗时）
    task_start_times = {}
    task_completion_order = []  # 记录任务完成顺序
    last_task_end_time = time.time()  # 上一个任务的结束时间
    
    def task_callback(task_output):
        nonlocal last_task_end_time
        import json
        import os
        
        # 确保outputs目录存在
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        # 生成流程结果文件名
        workflow_result_filename = f"workflow_result_{global_workflow_timestamp}.txt"
        workflow_result_filepath = os.path.join(outputs_dir, workflow_result_filename)
        
        # 获取任务信息
        task_description = getattr(task_output, 'description', 'N/A')
        task_name_raw = getattr(task_output, 'name', None)
        
        # 通过任务描述查找对应的 Agent
        desc_key = str(task_description)[:100]
        agent_info = task_desc_to_agent.get(desc_key)
        
        if agent_info:
            agent, agent_role = agent_info
            agent_name = getattr(agent, 'name', agent_role)
        else:
            # 回退方案：从 TaskOutput 尝试获取
            agent = getattr(task_output, 'agent', None)
            agent_name = getattr(agent, 'name', 'Unknown') if agent else 'Unknown'
            agent_role = getattr(agent, 'role', 'Unknown') if agent else 'Unknown'
        
        # 生成唯一任务名
        task_idx = len(task_completion_order) + 1
        task_name = task_name_raw or f"Task_{task_idx}_{agent_role}"
        task_completion_order.append(task_name)
        
        # 获取JSON输出
        json_output = None
        if hasattr(task_output, 'json_dict') and task_output.json_dict:
            json_output = task_output.json_dict
        
        # 计算实际耗时
        current_time = time.time()
        task_start_time = last_task_end_time
        task_duration = current_time - task_start_time
        
        # 使用监控器记录执行
        if monitor:
            monitor.start_agent_execution(agent_name, agent_role, task_name, str(task_description)[:200])
            if monitor._current_execution:
                monitor._current_execution.start_time = task_start_time
            monitor.end_agent_execution(output=str(task_output)[:5000], json_output=json_output)
        
        # 更新上一个任务结束时间
        last_task_end_time = current_time
        
        # 将任务输出追加到流程结果文件
        with open(workflow_result_filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"任务名称: {task_name}\n")
            f.write(f"Agent: {agent_role}\n")
            f.write(f"执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"耗时: {task_duration:.2f}s ({task_duration/60:.1f}min)\n")
            f.write("=" * 60 + "\n")
            f.write(f"任务描述: {str(task_description)[:500]}\n")
            f.write(f"预期输出: {getattr(task_output, 'expected_output', 'N/A')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"实际输出:\n{str(task_output)}\n")
            
            # 如果有JSON输出，也保存
            if json_output:
                f.write("\n" + "=" * 60 + "\n")
                f.write("JSON输出:\n")
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            f.write(f"\n{'='*60}\n")
    
    # Create Crew based on intent-driven task selection / 创建Crew
    # Based on intent to determine if design task is needed / 基于 intent 判断是否需要设计任务
    all_tasks = required_tasks
    if design_task and intent.get('needs_design', False):
        # If design needed, design task is already in required_tasks / 如果需要设计，design_task 已经在 required_tasks中
        # Note: design_task already added to required_tasks in Step 1, no need to re-add / 注意：design_task 已经在 Step 1 中添加到 required_tasks，无需重复添加
        all_tasks = required_tasks
    elif design_task:
        # If virtual context task (user provided material), don't add to task list / 如果是虚拟上下文任务（用户提供材料），不将其添加到任务列表中
        all_tasks = required_tasks
    
    ecomats_crew = Crew(
        agents=required_agents,
        tasks=all_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE,
        task_callback=task_callback  # 添加任务回调函数
    )
    
    # 执行 / Execute
    try:
        result = ecomats_crew.kickoff()
        
        # 设置最终结果并保存监控报告
        if monitor:
            monitor.set_final_result(result, "completed")
            monitor.save_report()
            monitor.save_readable_report()
            monitor.print_summary()
        
        return result
    except Exception as e:
        # 记录错误
        if monitor:
            monitor.set_final_result(None, "error", str(e))
            monitor.save_report()
            monitor.save_readable_report()
        return run_tool_only_summary(user_requirement)

def main():
    """
    Main entry point for synchronous mode / 同步模式主入口
    
    This function:
    1. Loads environment variables / 加载环境变量
    2. Gets user input for material design requirements / 获取用户输入的材料设计需求
    3. Selects workflow mode (preset or autonomous) / 选择工作流模式（预设或自主）
    4. Creates LLM instance / 创建LLM实例
    5. Executes selected workflow / 执行选定的工作流
    """
    print("基于CrewAI的ecomats多智能体系统 / ECOMATS Multi-Agent System Based on CrewAI")
    print("=" * 50)
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    # Force load .env from project root and override to ensure consistency with standalone tests / 强制从项目根目录加载 .env 并覆盖，确保与独立测试一致
    from dotenv import load_dotenv, dotenv_values
    import os as _os
    _dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(_dotenv_path, override=True)
    # Write .env values to environment again to avoid IDE/task runner override / 再次将 .env 的值写入环境，避免IDE/任务运行器覆盖
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

    # Get user-defined input for material design requirements / 获取用户自定义输入
    user_requirement = get_user_input()
    
    # Get user-selected workflow mode / 获取用户选择的工作模式
    workflow_mode = get_workflow_mode()
    
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("错误：API密钥未正确设置 / Error: API key not set correctly")
        return
    
    # Set dashscope API key / 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    # Explicitly set OPENAI compatible environment to ensure underlying Provider doesn't read old variables / 显式设置 OPENAI 兼容环境，确保底层Provider不读取旧变量
    import os as _os
    _os.environ["OPENAI_API_KEY"] = Config.QWEN_API_KEY or ""
    _os.environ["OPENAI_API_BASE"] = Config.QWEN_API_BASE or ""
    _os.environ["OPENAI_BASE_URL"] = Config.QWEN_API_BASE or ""
    
    from src.utils.llm_config import create_llm
    llm = create_llm()
    print("成功创建Qwen3 LLM实例用于主程序 / Successfully created Qwen3 LLM instance for main program")
    
    # Create monitor for tracking workflow execution / 创建监控器
    monitor = create_monitor()
    print("📊 工作流监控器已初始化 / Workflow monitor initialized")
    
    # Execute corresponding workflow based on user-selected mode / 根据用户选择的工作模式执行相应的流程
    if workflow_mode == "preset":
        run_design_iteration(user_requirement, llm)
    else:
        run_autonomous_workflow(user_requirement, llm, monitor)
    
    # Workflow results and monitoring reports have been saved to outputs folder via task_callback / 工作流结果和监控报告已经通过task_callback保存到outputs文件夹中
    print("\n工作流执行完成，结果已保存到 outputs 文件夹 / Workflow execution completed, results saved to outputs folder")
    print("📊 监控报告包括：JSON格式 (monitor_report_*.json) 和 可读格式 (monitor_report_*.txt) / Monitoring reports include: JSON format (monitor_report_*.json) and readable format (monitor_report_*.txt)")

def run_tool_only_summary(user_requirement):
    """
    Fallback function when crew execution fails - executes only mandatory tool calls / 当crew执行失败时的回退函数 - 仅执行必要的工具调用
    
    Args:
        user_requirement: User's requirement containing material formula / 用户需求，包含材料化学式
    
    Returns:
        dict: Tool execution results / 工具执行结果
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
    print("已切换为工具仅执行模式，结果已保存到", fp)
    return results

if __name__ == "__main__":
    main()

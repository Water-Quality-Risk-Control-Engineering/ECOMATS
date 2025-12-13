#!/usr/bin/env python3
"""
ECOMATS - 基于CrewAI的水处理材料设计多智能体系统
"""

import sys
import os
import json
from dotenv import load_dotenv
from crewai import Crew, Process
import dashscope

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
    """检查必要的环境变量是否已设置"""
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
    """创建所有智能体的公共函数 / Public function to create all agents"""
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
    """从结果中提取反馈信息 / Extract feedback information from results"""
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
    """检查是否需要迭代设计 / Check if iterative design is needed"""
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
    """运行设计迭代 / Run design iteration"""
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

def run_preset_workflow(user_requirement, llm):
    """运行预设工作流模式 / Run preset workflow mode"""
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
    
    # 创建所有智能体 / Create all agents
    agents = create_all_agents(llm)
    
    # 创建任务，将用户需求传递给任务 / Create tasks and pass user requirements to tasks
    # 1. 首先创建材料设计任务 / First create material design task
    design_task = DesignTask(llm).create_task(agents['material_designer'], user_requirement=user_requirement)
    try:
        from src.utils.assessment_tool_executor import AssessmentToolExecutor
        executor = AssessmentToolExecutor()
        material_formula = None
        import re as _re
        m = _re.search(r"\b(?:[A-Z][a-z]?\d*){2,}\b", user_requirement or "")
        material_formula = m.group(0) if m else (user_requirement or "")
        executor.execute_mandatory_tool_calls(material_formula)
    except Exception:
        pass
    
    # 2. 为每个评估专家创建评估任务，都依赖于设计任务 / Create evaluation tasks for each evaluation expert, all dependent on design task
    # 明确传递用户需求给评估任务，以确保工具调用策略得到执行
    evaluation_task_a = EvaluationTask(llm).create_task(agents['expert_a'], design_task, user_requirement=user_requirement)
    evaluation_task_b = EvaluationTask(llm).create_task(agents['expert_b'], design_task, user_requirement=user_requirement)
    evaluation_task_c = EvaluationTask(llm).create_task(agents['expert_c'], design_task, user_requirement=user_requirement)
    
    # 3. 创建最终验证任务，依赖于所有评估任务 / Create final validation task, dependent on all evaluation tasks
    final_validation_task = FinalValidationTask(llm).create_task(agents['final_validator'], 
                                                           [design_task, evaluation_task_a, evaluation_task_b, evaluation_task_c], user_requirement=user_requirement)
    
    # 4. 创建合成方法任务，依赖于最终验证任务 / Create synthesis method task, dependent on final validation task
    synthesis_method_task = SynthesisMethodTask(llm).create_task(agents['synthesis_expert'], final_validation_task, user_requirement=user_requirement)
    
    # 5. 创建机理分析任务，依赖于最终验证任务 / Create mechanism analysis task, dependent on final validation task
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(agents['mechanism_expert'], final_validation_task, user_requirement=user_requirement)
    
    # 6. 创建操作建议任务，依赖于最终验证任务 / Create operation suggestion task, dependent on final validation task
    operation_suggesting_task = OperationSuggestingTask(llm).create_task(agents['operation_suggesting'], final_validation_task, user_requirement=user_requirement)
    
    # 定义任务回调函数，用于保存整体流程结果
    # 生成全局时间戳，确保所有任务使用相同的流程结果文件
    import datetime
    global_workflow_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def task_callback(task_output):
        import json
        import os
        
        # 确保outputs目录存在
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        # 生成流程结果文件名
        workflow_result_filename = f"workflow_result_{global_workflow_timestamp}.txt"
        workflow_result_filepath = os.path.join(outputs_dir, workflow_result_filename)
        
        # 获取任务名称
        task_name = getattr(task_output, 'name', 'unknown_task')
        if not task_name:
            task_name = 'unknown_task'
        
        # 将任务输出追加到流程结果文件
        with open(workflow_result_filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"任务名称: {task_name}\n")
            f.write(f"执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"任务描述: {getattr(task_output, 'description', 'N/A')}\n")
            f.write(f"预期输出: {getattr(task_output, 'expected_output', 'N/A')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"实际输出:\n{str(task_output)}\n")
            
            # 如果有JSON输出，也保存
            if hasattr(task_output, 'json_dict') and task_output.json_dict:
                f.write("\n" + "=" * 60 + "\n")
                f.write("JSON输出:\n")
                json.dump(task_output.json_dict, f, ensure_ascii=False, indent=2)
            f.write(f"\n{'='*60}\n")
    
    # 创建Crew / Create Crew
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
        ],  # 任务按顺序执行 / Tasks executed in order
        process=Process.sequential,  # 使用顺序流程执行任务 / Use sequential process to execute tasks
        verbose=Config.VERBOSE,
        task_callback=task_callback  # 添加任务回调函数
    )
    
    # 执行 / Execute
    try:
        result = ecomats_crew.kickoff()
        return result
    except Exception:
        return run_tool_only_summary(user_requirement)

def _execute_material_tools(user_requirement: str, project_root: str):
    """预执行材料相关工具调用 / Pre-execute material-related tool calls"""
    try:
        import sys
        sys.path.insert(0, os.path.abspath(project_root))
        from src.utils.assessment_tool_executor import AssessmentToolExecutor
        import re as _re
        
        executor = AssessmentToolExecutor()
        m = _re.search(r"\b(?:[A-Z][a-z]?\d*){2,}\b", user_requirement or "")
        material_formula = m.group(0) if m else (user_requirement or "")
        executor.execute_mandatory_tool_calls(material_formula)
    except Exception:
        pass


def run_autonomous_workflow(user_requirement, llm):
    """运行智能体自主调度模式 / Run agent autonomous scheduling mode
    
    基于 TOA 意图识别的全新架构，直接使用 intent 对象控制流程
    New architecture based on TOA intent recognition, directly using intent object to control workflow
    """
    print("启动智能体自主调度模式... / Starting autonomous scheduling mode...")
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    from src.config.config import Config
    from src.agents.task_organizing_agent import TaskOrganizingAgent
    from src.agents.task_allocator import TaskAllocator
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
    
    # 创建任务分配器并注册所有智能体 / Create task allocator and register all agents
    task_allocator = TaskAllocator(llm)
    task_allocator.register_agent("TaskOrganizingAgent", coordinator_agent)
    task_allocator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    task_allocator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    task_allocator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    task_allocator.register_agent("ExtractingAgent", agents['literature_processor'])
    task_allocator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    task_allocator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    task_allocator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # ============================================================
    # ✨ TOA 意图驱动流程 / TOA Intent-Driven Workflow
    # ============================================================
    print("\n🧠 TOA 正在分析用户意图... / TOA analyzing user intent...")
    intent = coordinator.analyze_user_intent(user_requirement)
    print(f"✅ 意图分析完成 / Intent analysis complete: {intent['reasoning']}")
    
    # 打印意图详情 / Print intent details
    print(f"\n📊 意图详情 / Intent Details:")
    print(f"   • 需要设计 / Needs Design: {intent.get('needs_design', False)}")
    print(f"   • 需要评估 / Needs Evaluation: {intent.get('needs_evaluation', False)}")
    print(f"   • 评估模式 / Evaluation Mode: {intent.get('evaluation_mode', None)}")
    print(f"   • 需要机理分析 / Needs Mechanism: {intent.get('needs_mechanism', False)}")
    print(f"   • 需要合成方法 / Needs Synthesis: {intent.get('needs_synthesis', False)}")
    print(f"   • 需要操作指导 / Needs Operation: {intent.get('needs_operation', False)}")
    print(f"   • 提供的材料 / Material Provided: {intent.get('material_provided', None)}")
    
    # 初始化任务和智能体列表 / Initialize task and agent lists
    required_tasks = []
    required_agents = []
    seen_roles = set()
    design_task = None
    final_validation_task = None
    
    # ============================================================
    # Step 1: 处理材料设计 / Handle Material Design
    # ============================================================
    if intent.get('needs_design', False):
        print("\n🛠️ 创建材料设计任务 / Creating material design task...")
        design_agent = task_allocator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
        
        # 预执行工具调用 / Pre-execute tool calls
        _execute_material_tools(user_requirement, project_root)
        
    elif intent.get('needs_evaluation', False) or intent.get('needs_mechanism', False) or intent.get('needs_synthesis', False) or intent.get('needs_operation', False):
        # 用户提供了材料，创建虚拟上下文任务（不实际执行）
        # User provided material, create virtual context task (not executed)
        material_info = intent.get('material_provided') or user_requirement
        print(f"\n📝 使用用户提供的材料信息 / Using user-provided material info: {material_info[:50]}...")
        
        # 创建虚拟上下文任务，仅用于传递材料信息，不添加到任务列表
        # Create virtual context task, only for passing material info, not added to task list
        design_task = Task(
            description=f"Existing material provided by user:\n{user_requirement}",
            expected_output="Material information for downstream tasks",
            agent=coordinator_agent  # 使用协调员作为占位符 / Use coordinator as placeholder
        )
        # 注意：虚拟任务不添加到 required_tasks / Note: Virtual task NOT added to required_tasks
        
        _execute_material_tools(user_requirement, project_root)
    
    # ============================================================
    # Step 2: 处理评估任务 / Handle Evaluation Tasks
    # ============================================================
    if intent.get('needs_evaluation', False):
        evaluation_mode = intent.get('evaluation_mode', 'with_summary')
        
        # 获取评估智能体 / Get evaluation agents
        evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
        evaluation_tasks = []
        
        for agent in evaluation_agents:
            if agent.role not in seen_roles:
                required_agents.append(agent)
                seen_roles.add(agent.role)
            task = EvaluationTask(llm).create_task(agent, design_task, user_requirement)
            evaluation_tasks.append(task)
        
        required_tasks.extend(evaluation_tasks)
        
        if evaluation_mode == 'experts_only':
            # 仅专家评分模式 / Experts-only mode
            print(f"\n✅ 仅评估模式：三个 ASA 专家评分，不进行最终总结")
            print(f"   Experts-only mode: 3 ASA experts scoring, no final summary")
        else:
            # 完整评估模式（包含最终总结） / Full evaluation mode (with summary)
            print(f"\n📊 完整评估模式：三个 ASA 专家评分 + 最终总结")
            print(f"   Full evaluation mode: 3 ASA experts + final summary")
            
            final_validation_agent = task_allocator.get_agent_for_task("final_validation")
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
    # Step 3: 处理机理分析任务 / Handle Mechanism Analysis Task
    # ============================================================
    if intent.get('needs_mechanism', False):
        print(f"\n🔬 创建机理分析任务 / Creating mechanism analysis task...")
        mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
        if mechanism_agent and mechanism_agent.role not in seen_roles:
            required_agents.append(mechanism_agent)
            seen_roles.add(mechanism_agent.role)
        
        context_task = final_validation_task or design_task
        mechanism_task = MechanismAnalysisTask(llm).create_task(
            mechanism_agent, context_task, user_requirement=user_requirement
        )
        required_tasks.append(mechanism_task)
    
    # ============================================================
    # Step 4: 处理合成方法任务 / Handle Synthesis Method Task
    # ============================================================
    if intent.get('needs_synthesis', False):
        print(f"\n🧪 创建合成方法任务 / Creating synthesis method task...")
        synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
        if synthesis_agent and synthesis_agent.role not in seen_roles:
            required_agents.append(synthesis_agent)
            seen_roles.add(synthesis_agent.role)
        
        context_task = final_validation_task or design_task
        synthesis_task = SynthesisMethodTask(llm).create_task(
            synthesis_agent, context_task, user_requirement=user_requirement
        )
        required_tasks.append(synthesis_task)
    
    # ============================================================
    # Step 5: 处理操作指导任务 / Handle Operation Guidance Task
    # ============================================================
    if intent.get('needs_operation', False):
        print(f"\n📖 创建操作指导任务 / Creating operation guidance task...")
        operation_agent = task_allocator.get_agent_for_task("operation_suggestion")
        if operation_agent and operation_agent.role not in seen_roles:
            required_agents.append(operation_agent)
            seen_roles.add(operation_agent.role)
        
        context_task = final_validation_task or design_task
        operation_task = OperationSuggestingTask(llm).create_task(
            operation_agent, context_task, user_requirement=user_requirement
        )
        required_tasks.append(operation_task)
    
    # ============================================================
    # 检查是否有任务 / Check if there are any tasks
    # ============================================================
    if not required_tasks:
        print("\n⚠️ 未识别出任何任务，默认执行材料设计 / No tasks identified, defaulting to material design")
        design_agent = task_allocator.get_agent_for_task("material_design")
        if design_agent and design_agent.role not in seen_roles:
            required_agents.append(design_agent)
            seen_roles.add(design_agent.role)
        design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
        required_tasks.append(design_task)
    
    # ============================================================
    # 打印任务摘要 / Print task summary
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
    
    # 定义任务回调函数，用于保存整体流程结果
    # 生成全局时间戳，确保所有任务使用相同的流程结果文件
    import datetime
    global_workflow_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def task_callback(task_output):
        import json
        import os
        
        # 确保outputs目录存在
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        # 生成流程结果文件名
        workflow_result_filename = f"workflow_result_{global_workflow_timestamp}.txt"
        workflow_result_filepath = os.path.join(outputs_dir, workflow_result_filename)
        
        # 获取任务名称
        task_name = getattr(task_output, 'name', 'unknown_task')
        if not task_name:
            task_name = 'unknown_task'
        
        # 将任务输出追加到流程结果文件
        with open(workflow_result_filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"任务名称: {task_name}\n")
            f.write(f"执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"任务描述: {getattr(task_output, 'description', 'N/A')}\n")
            f.write(f"预期输出: {getattr(task_output, 'expected_output', 'N/A')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"实际输出:\n{str(task_output)}\n")
            
            # 如果有JSON输出，也保存
            if hasattr(task_output, 'json_dict') and task_output.json_dict:
                f.write("\n" + "=" * 60 + "\n")
                f.write("JSON输出:\n")
                json.dump(task_output.json_dict, f, ensure_ascii=False, indent=2)
            f.write(f"\n{'='*60}\n")
    
    # 创建Crew / Create Crew
    # 基于 intent 判断是否需要设计任务 / Based on intent to determine if design task is needed
    all_tasks = required_tasks
    if design_task and intent.get('needs_design', False):
        # 如果需要设计，将设计任务放在最前面 / If design needed, put design task first
        # 注意：design_task 已经在 Step 1 中添加到 required_tasks，无需重复添加
        all_tasks = required_tasks
    elif design_task:
        # 如果是虚拟上下文任务（用户提供材料），不将其添加到任务列表中
        # If virtual context task (user provided material), don't add to task list
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
        return result
    except Exception:
        return run_tool_only_summary(user_requirement)

def main():
    print("基于CrewAI的ecomats多智能体系统 / ECOMATS Multi-Agent System Based on CrewAI")
    print("=" * 50)
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    # 强制从项目根目录加载 .env 并覆盖，确保与独立测试一致
    from dotenv import load_dotenv, dotenv_values
    import os as _os
    _dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(_dotenv_path, override=True)
    # 再次将 .env 的值写入环境，避免IDE/任务运行器覆盖
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

    # 获取用户自定义输入 / Get user custom input
    user_requirement = get_user_input()
    
    # 获取用户选择的工作模式 / Get user-selected workflow mode
    workflow_mode = get_workflow_mode()
    
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    # 显式设置 OPENAI 兼容环境，确保底层Provider不读取旧变量
    import os as _os
    _os.environ["OPENAI_API_KEY"] = Config.QWEN_API_KEY or ""
    _os.environ["OPENAI_API_BASE"] = Config.QWEN_API_BASE or ""
    _os.environ["OPENAI_BASE_URL"] = Config.QWEN_API_BASE or ""
    
    from src.utils.llm_config import create_llm
    llm = create_llm()
    print("成功创建Qwen3 LLM实例用于主程序")
    
    # 根据用户选择的工作模式执行相应的流程 / Execute corresponding process based on user-selected workflow mode
    if workflow_mode == "preset":
        run_design_iteration(user_requirement, llm)
    else:
        run_autonomous_workflow(user_requirement, llm)
    
    # 工作流结果已经通过task_callback保存到workflow_result文件中
    # 不再生成单独的result文件
    print("工作流执行完成，结果已保存到workflow_result文件中")

def run_tool_only_summary(user_requirement):
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

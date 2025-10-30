#!/usr/bin/env python3
"""
ECOMATS - 基于CrewAI的水处理材料设计多智能体系统
"""

import sys
import os

# 添加项目根目录到Python路径，使src模块可以被正确导入 / Add project root directory to Python path so src modules can be imported correctly
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

import json

# 确保环境变量已加载 / Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from src.config.config import Config
import dashscope

# 智能体导入 / Agent imports
from src.agents.base_agent import BaseAgent
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
from src.agents.task_allocator import TaskAllocator

# 任务导入 / Task imports
from src.tasks.design_task import DesignTask
from src.tasks.evaluation_task import EvaluationTask
from src.tasks.final_validation_task import FinalValidationTask
from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
from src.tasks.synthesis_method_task import SynthesisMethodTask
from src.tasks.operation_suggesting_task import OperationSuggestingTask

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
    
    # 创建所有智能体 / Create all agents
    agents = create_all_agents(llm)
    
    # 创建任务，将用户需求传递给任务 / Create tasks and pass user requirements to tasks
    # 1. 首先创建材料设计任务 / First create material design task
    design_task = DesignTask(llm).create_task(agents['material_designer'], user_requirement=user_requirement)
    
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
    result = ecomats_crew.kickoff()
    return result

def run_autonomous_workflow(user_requirement, llm):
    """运行智能体自主调度模式 / Run agent autonomous scheduling mode"""
    print("启动智能体自主调度模式...")
    
    # 创建所有智能体 / Create all agents
    agents = create_all_agents(llm)
    
    # 创建任务组织代理实例（注意：这里创建的是TaskOrganizingAgent类的实例，而不是Agent实例）
    # Create task organizing agent instance (note: this creates an instance of the TaskOrganizingAgent class, not an Agent instance)
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
    
    # 根据用户需求动态决定需要哪些任务 / Dynamically decide which tasks are needed based on user requirements
    required_task_types = task_allocator.determine_required_task_types(user_requirement)
    
    # 初始化任务和智能体列表
    required_tasks = []
    required_agents = [coordinator_agent]
    seen_roles = {coordinator_agent.role}
    task_mapping = {}
    design_task = None  # 初始化design_task变量
    
    # 特殊处理：如果只运行独立任务
    independent_tasks = ["mechanism_analysis", "synthesis_method", "operation_suggestion"]
    if len(required_task_types) == 1 and required_task_types[0] in independent_tasks:
        # 只运行独立任务
        task_type = required_task_types[0]
        agent = task_allocator.get_agent_for_task(task_type)
        if agent and agent.role not in seen_roles:
            required_agents.append(agent)
            seen_roles.add(agent.role)
        
        # 创建相应的任务，使用用户需求作为输入
        if task_type == "mechanism_analysis":
            mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(agent, user_requirement=user_requirement)
            task_mapping["mechanism_analysis"] = mechanism_analysis_task
            required_tasks.append(mechanism_analysis_task)
        elif task_type == "synthesis_method":
            synthesis_method_task = SynthesisMethodTask(llm).create_task(agent, user_requirement=user_requirement)
            task_mapping["synthesis_method"] = synthesis_method_task
            required_tasks.append(synthesis_method_task)
        elif task_type == "operation_suggestion":
            operation_suggesting_task = OperationSuggestingTask(llm).create_task(agent, user_requirement=user_requirement)
            task_mapping["operation_suggestion"] = operation_suggesting_task
            required_tasks.append(operation_suggesting_task)
    else:
        # 检查是否需要材料设计任务
        if "material_design" in required_task_types:
            # 正常处理流程，需要材料设计任务
            # 任务组织代理根据任务需求自主委派任务 / Task organizing agent autonomously delegates tasks based on task requirements
            # 1. 委派材料设计任务 / Delegate material design task
            design_agent = coordinator.delegate_task("material_design", task_allocator, user_requirement)
            
            # 2. 创建材料设计任务 / Create material design task
            design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
            
            # 3. 添加材料设计智能体到所需智能体列表
            if design_agent and design_agent.role not in seen_roles:
                required_agents.append(design_agent)
                seen_roles.add(design_agent.role)
            
            # 根据任务类型创建相应的任务 / Create tasks based on task types
            # 首先处理材料设计任务 / First handle material design task
            task_mapping["material_design"] = design_task
        elif "evaluation" in required_task_types or "final_validation" in required_task_types:
            # 如果需要评估但不需要设计，则创建一个虚拟的设计任务来传递材料信息
            # 这样评估任务可以依赖于这个虚拟任务获取材料信息
            from crewai import Task
            design_task = Task(
                description=f"Existing material design information provided by user:\n{user_requirement}",
                expected_output="Material information for evaluation",
                agent=agents['material_designer']  # 使用材料设计智能体作为占位符
            )
            task_mapping["material_design"] = design_task
        
        # 然后处理其他任务 / Then handle other tasks
        # 处理评估任务链 / Handle evaluation task chain
        evaluation_tasks = []
        final_validation_task = None
        
        if "evaluation" in required_task_types:
            # 委派评估任务给所有评估专家 / Delegate evaluation tasks to all evaluation experts
            evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
            for agent in evaluation_agents:
                if agent.role not in seen_roles:
                    required_agents.append(agent)
                    seen_roles.add(agent.role)
                task = EvaluationTask(llm).create_task(agent, design_task, user_requirement)
                evaluation_tasks.append(task)
            
            # 委派最终验证任务 / Delegate final validation task
            final_validation_agent = task_allocator.get_agent_for_task("final_validation")
            if final_validation_agent and final_validation_agent.role not in seen_roles:
                required_agents.append(final_validation_agent)
                seen_roles.add(final_validation_agent.role)
            final_validation_task = FinalValidationTask(llm).create_task(final_validation_agent, 
                                                                   [design_task] + evaluation_tasks, user_requirement=user_requirement)
            
            task_mapping["evaluation"] = evaluation_tasks
            task_mapping["final_validation"] = final_validation_task
            required_tasks.extend(evaluation_tasks)
            required_tasks.append(final_validation_task)
        
        # 处理独立任务（不依赖于评估任务） / Handle independent tasks (not dependent on evaluation tasks)
        # 机理分析任务 / Mechanism analysis task
        if "mechanism_analysis" in required_task_types:
            mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
            if mechanism_agent and mechanism_agent.role not in seen_roles:
                required_agents.append(mechanism_agent)
                seen_roles.add(mechanism_agent.role)
            # 对于独立任务，可以使用用户需求作为输入，或者如果已有最终验证任务则依赖于它
            context_task = final_validation_task if final_validation_task else None
            mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(mechanism_agent, context_task, user_requirement=user_requirement)
            task_mapping["mechanism_analysis"] = mechanism_analysis_task
            required_tasks.append(mechanism_analysis_task)
        
        # 合成方法任务 / Synthesis method task
        if "synthesis_method" in required_task_types:
            synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
            if synthesis_agent and synthesis_agent.role not in seen_roles:
                required_agents.append(synthesis_agent)
                seen_roles.add(synthesis_agent.role)
            # 对于独立任务，可以使用用户需求作为输入，或者如果已有最终验证任务则依赖于它
            context_task = final_validation_task if final_validation_task else None
            synthesis_method_task = SynthesisMethodTask(llm).create_task(synthesis_agent, context_task, user_requirement=user_requirement)
            task_mapping["synthesis_method"] = synthesis_method_task
            required_tasks.append(synthesis_method_task)
            
        # 操作建议任务 / Operation suggestion task
        if "operation_suggestion" in required_task_types:
            operation_suggesting_agent = task_allocator.get_agent_for_task("operation_suggestion")
            if operation_suggesting_agent and operation_suggesting_agent.role not in seen_roles:
                required_agents.append(operation_suggesting_agent)
                seen_roles.add(operation_suggesting_agent.role)
            # 对于独立任务，可以使用用户需求作为输入，或者如果已有最终验证任务则依赖于它
            context_task = final_validation_task if final_validation_task else None
            operation_suggesting_task = OperationSuggestingTask(llm).create_task(operation_suggesting_agent, context_task, user_requirement=user_requirement)
            task_mapping["operation_suggestion"] = operation_suggesting_task
            required_tasks.append(operation_suggesting_task)
    
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
    # 只有在真正需要设计任务时才将其添加到任务列表中
    all_tasks = required_tasks
    if design_task and "material_design" in required_task_types:
        all_tasks = [design_task] + required_tasks
    elif design_task:
        # 如果是虚拟设计任务，不将其添加到任务列表中，但确保评估任务可以获取材料信息
        # 评估任务已经依赖于design_task，所以不需要将其添加到任务列表中
        all_tasks = required_tasks
    
    ecomats_crew = Crew(
        agents=required_agents,
        tasks=all_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE,
        task_callback=task_callback  # 添加任务回调函数
    )
    
    # 执行 / Execute
    result = ecomats_crew.kickoff()
    return result

def main():
    print("基于CrewAI的ecomats多智能体系统 / ECOMATS Multi-Agent System Based on CrewAI")
    print("=" * 50)
    
    # 检查必要的环境变量
    if not check_environment_variables():
        return
    
    # 获取用户自定义输入 / Get user custom input
    user_requirement = get_user_input()
    
    # 获取用户选择的工作模式 / Get user-selected workflow mode
    workflow_mode = get_workflow_mode()
    
    # 验证API密钥是否存在
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型，使用Qwen3模型配置
    from src.utils.llm_config import create_llm
    try:
        llm = create_llm()
        print("成功创建Qwen3 LLM实例用于主程序")
    except Exception as e:
        print(f"创建Qwen3模型实例失败: {e}")
        return
    
    # 根据用户选择的工作模式执行相应的流程 / Execute corresponding process based on user-selected workflow mode
    if workflow_mode == "preset":
        # 使用迭代设计机制 / Use iterative design mechanism
        result = run_design_iteration(user_requirement, llm)
    else:
        result = run_autonomous_workflow(user_requirement, llm)
    
    # 工作流结果已经通过task_callback保存到workflow_result文件中
    # 不再生成单独的result文件
    print("工作流执行完成，结果已保存到workflow_result文件中")

if __name__ == "__main__":
    main()
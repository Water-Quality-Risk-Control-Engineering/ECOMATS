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
            print(f"改进建议: {feedback}")
            # 进行下一轮迭代 / Proceed to next iteration
            return run_design_iteration(updated_requirement, llm, iteration_count + 1)
        else:
            return result
    else:
        print("设计方案已达到要求，无需进一步迭代。")
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
    evaluation_task_a = EvaluationTask(llm).create_task(agents['expert_a'], design_task)
    evaluation_task_b = EvaluationTask(llm).create_task(agents['expert_b'], design_task)
    evaluation_task_c = EvaluationTask(llm).create_task(agents['expert_c'], design_task)
    
    # 3. 创建最终验证任务，依赖于所有评估任务 / Create final validation task, dependent on all evaluation tasks
    final_validation_task = FinalValidationTask(llm).create_task(agents['final_validator'], 
                                                           [design_task, evaluation_task_a, evaluation_task_b, evaluation_task_c])
    
    # 4. 创建合成方法任务，依赖于最终验证任务 / Create synthesis method task, dependent on final validation task
    synthesis_method_task = SynthesisMethodTask(llm).create_task(agents['synthesis_expert'], final_validation_task)
    
    # 5. 创建机理分析任务，依赖于最终验证任务 / Create mechanism analysis task, dependent on final validation task
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(agents['mechanism_expert'], final_validation_task)
    
    # 6. 创建操作建议任务，依赖于最终验证任务 / Create operation suggestion task, dependent on final validation task
    operation_suggesting_task = OperationSuggestingTask(llm).create_task(agents['operation_suggesting'], final_validation_task)
    
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
            mechanism_analysis_task,
            synthesis_method_task,
            operation_suggesting_task
        ],  # 任务按顺序执行 / Tasks executed in order
        process=Process.sequential,  # 使用顺序流程执行任务 / Use sequential process to execute tasks
        verbose=Config.VERBOSE
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
    task_allocator = TaskAllocator()
    task_allocator.register_agent("TaskOrganizingAgent", coordinator_agent)
    task_allocator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    task_allocator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    task_allocator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    task_allocator.register_agent("ExtractingAgent", agents['literature_processor'])
    task_allocator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    task_allocator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    task_allocator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # 任务组织代理根据任务需求自主委派任务 / Task organizing agent autonomously delegates tasks based on task requirements
    # 1. 委派材料设计任务 / Delegate material design task
    design_agent = coordinator.delegate_task("material_design", task_allocator, user_requirement)
    
    # 2. 创建材料设计任务 / Create material design task
    design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
    
    # 3. 委派评估任务给所有评估专家 / Delegate evaluation tasks to all evaluation experts
    evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
    evaluation_tasks = []
    for i, agent in enumerate(evaluation_agents):
        task = EvaluationTask(llm).create_task(agent, design_task)
        evaluation_tasks.append(task)
    
    # 4. 委派最终验证任务 / Delegate final validation task
    final_validation_agent = task_allocator.get_agent_for_task("final_validation")
    final_validation_task = FinalValidationTask(llm).create_task(final_validation_agent, 
                                                           [design_task] + evaluation_tasks)
    
    # 5. 委派机理分析任务 / Delegate mechanism analysis task
    mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(mechanism_agent, final_validation_task)
    
    # 6. 委派合成方法任务 / Delegate synthesis method task
    synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
    synthesis_method_task = SynthesisMethodTask(llm).create_task(synthesis_agent, final_validation_task)
    
    # 7. 委派操作建议任务 / Delegate operation suggestion task
    operation_suggesting_agent = task_allocator.get_agent_for_task("operation_suggestion")
    operation_suggesting_task = OperationSuggestingTask(llm).create_task(operation_suggesting_agent, final_validation_task)
    
    # 创建Crew，包含所有参与任务的智能体 / Create Crew including all agents participating in tasks
    all_agents = [
        coordinator_agent,
        design_agent,
        *evaluation_agents,
        final_validation_agent,
        mechanism_agent,
        synthesis_agent
    ]
    
    # 确保不会重复添加智能体 / Ensure no duplicate agents are added
    unique_agents = []
    seen_roles = set()
    for agent in all_agents:
        if agent.role not in seen_roles:
            unique_agents.append(agent)
            seen_roles.add(agent.role)
    
    # 创建任务列表 / Create task list
    all_tasks = [
        design_task,
        *evaluation_tasks,
        final_validation_task,
        mechanism_analysis_task,
        synthesis_method_task,
        operation_suggesting_task
    ]
    
    # 创建Crew / Create Crew
    ecomats_crew = Crew(
        agents=unique_agents,
        tasks=all_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE
    )
    
    # 执行 / Execute
    result = ecomats_crew.kickoff()
    return result

def main():
    print("基于CrewAI的ecomats多智能体系统 / ECOMATS Multi-Agent System Based on CrewAI")
    print("=" * 50)
    
    # 获取用户自定义输入 / Get user custom input
    user_requirement = get_user_input()
    
    # 获取用户选择的工作模式 / Get user-selected workflow mode
    workflow_mode = get_workflow_mode()
    
    # 验证API密钥是否存在 / Verify if API key exists
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("错误：API密钥未正确设置 / Error: API key not properly configured")
        return
    
    # 设置dashscope的API密钥 / Set dashscope API key
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型，优先使用EAS模型配置 / Initialize LLM model, prioritize EAS model configuration
    from src.utils.llm_config import create_eas_llm
    try:
        llm = create_eas_llm()
        print("成功创建EAS LLM实例用于主程序 / Successfully created EAS LLM instance for main program")
    except Exception as e:
        print(f"创建EAS模型实例失败，使用默认配置: {e} / Failed to create EAS model instance, using default configuration: {e}")
        # 如果EAS配置失败，回退到默认配置 / If EAS configuration fails, fall back to default configuration
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,  # 使用原始API密钥 / Use original API key
            model="openai/" + Config.QWEN_MODEL_NAME,  # 使用配置的模型名称，加上提供商前缀 / Use configured model name with provider prefix
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
    
    # 根据用户选择的工作模式执行相应的流程 / Execute corresponding process based on user-selected workflow mode
    if workflow_mode == "preset":
        # 使用迭代设计机制 / Use iterative design mechanism
        result = run_design_iteration(user_requirement, llm)
    else:
        result = run_autonomous_workflow(user_requirement, llm)
    
    print(result)

if __name__ == "__main__":
    main()
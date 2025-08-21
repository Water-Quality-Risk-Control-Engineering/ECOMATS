#!/usr/bin/env python3
"""
基于CrewAI的ecomats多智能体系统框架
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from config.config import Config
import dashscope

# 智能体导入
from agents.base_agent import BaseAgent
from agents.coordinator import Coordinator
from agents.material_designer import MaterialDesigner
from agents.expert_a import ExpertA
from agents.expert_b import ExpertB
from agents.expert_c import ExpertC
from agents.final_validator import FinalValidator
from agents.literature_processor import LiteratureProcessor
from agents.mechanism_expert import MechanismExpert
from agents.synthesis_expert import SynthesisExpert
from agents.task_allocator import TaskAllocator

# 任务导入
from tasks.design_task import DesignTask
from tasks.evaluation_task import EvaluationTask
from tasks.mechanism_analysis_task import MechanismAnalysisTask
from tasks.synthesis_method_task import SynthesisMethodTask

def get_user_input():
    """获取用户自定义的材料设计需求"""
    print("请输入您的材料设计需求:")
    print("例如: 设计一种用于处理含重金属镉废水的高效催化剂")
    user_input = input("材料设计需求: ")
    return user_input

def get_workflow_mode():
    """获取用户选择的工作模式"""
    print("\n请选择工作模式:")
    print("1. 预设工作流模式 (按固定顺序执行所有任务)")
    print("2. 智能体自主调度模式 (由协调者动态分配任务)")
    while True:
        choice = input("请输入选项 (1 或 2): ").strip()
        if choice == "1":
            return "preset"
        elif choice == "2":
            return "autonomous"
        else:
            print("无效选项，请输入 1 或 2")

def create_all_agents(llm):
    """创建所有智能体的公共函数"""
    coordinator_agent = Coordinator(llm).create_agent()
    material_designer_agent = MaterialDesigner(llm).create_agent()
    expert_a_agent = ExpertA(llm).create_agent()
    expert_b_agent = ExpertB(llm).create_agent()
    expert_c_agent = ExpertC(llm).create_agent()
    final_validator_agent = FinalValidator(llm).create_agent()
    literature_processor_agent = LiteratureProcessor(llm).create_agent()
    mechanism_expert_agent = MechanismExpert(llm).create_agent()
    synthesis_expert_agent = SynthesisExpert(llm).create_agent()
    
    return {
        'coordinator': coordinator_agent,
        'material_designer': material_designer_agent,
        'expert_a': expert_a_agent,
        'expert_b': expert_b_agent,
        'expert_c': expert_c_agent,
        'final_validator': final_validator_agent,
        'literature_processor': literature_processor_agent,
        'mechanism_expert': mechanism_expert_agent,
        'synthesis_expert': synthesis_expert_agent
    }

def run_preset_workflow(user_requirement, llm):
    """运行预设工作流模式"""
    print("启动预设工作流模式...")
    
    # 创建所有智能体
    agents = create_all_agents(llm)
    
    # 创建任务，将用户需求传递给任务
    # 1. 首先创建材料设计任务
    design_task = DesignTask(llm).create_task(agents['material_designer'], user_requirement=user_requirement)
    
    # 2. 为每个评估专家创建评估任务，都依赖于设计任务
    evaluation_task_a = EvaluationTask(llm).create_task(agents['expert_a'], design_task)
    evaluation_task_b = EvaluationTask(llm).create_task(agents['expert_b'], design_task)
    evaluation_task_c = EvaluationTask(llm).create_task(agents['expert_c'], design_task)
    
    # 3. 创建最终验证任务，依赖于所有评估任务
    final_validation_task = EvaluationTask(llm).create_task(agents['final_validator'], 
                                                           [design_task, evaluation_task_a, evaluation_task_b, evaluation_task_c])
    
    # 4. 创建机理分析任务，依赖于最终验证任务
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(agents['mechanism_expert'], final_validation_task)
    
    # 5. 创建合成方法任务，依赖于最终验证任务
    synthesis_method_task = SynthesisMethodTask(llm).create_task(agents['synthesis_expert'], final_validation_task)
    
    # 创建Crew
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
            agents['synthesis_expert']
        ],
        tasks=[
            design_task, 
            evaluation_task_a, 
            evaluation_task_b, 
            evaluation_task_c, 
            final_validation_task,
            mechanism_analysis_task,
            synthesis_method_task
        ],  # 任务按顺序执行
        process=Process.sequential,  # 使用顺序流程执行任务
        verbose=Config.VERBOSE
    )
    
    # 执行
    result = ecomats_crew.kickoff()
    return result

def run_autonomous_workflow(user_requirement, llm):
    """运行智能体自主调度模式"""
    print("启动智能体自主调度模式...")
    
    # 创建所有智能体
    agents = create_all_agents(llm)
    
    # 创建协调者实例（注意：这里创建的是Coordinator类的实例，而不是Agent实例）
    coordinator = Coordinator(llm)
    coordinator_agent = coordinator.create_agent()
    
    # 创建任务分配器并注册所有智能体
    task_allocator = TaskAllocator()
    task_allocator.register_agent("Coordinator", coordinator_agent)
    task_allocator.register_agent("MaterialDesigner", agents['material_designer'])
    task_allocator.register_agent("Expert", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    task_allocator.register_agent("FinalValidator", agents['final_validator'])
    task_allocator.register_agent("LiteratureProcessor", agents['literature_processor'])
    task_allocator.register_agent("MechanismExpert", agents['mechanism_expert'])
    task_allocator.register_agent("SynthesisExpert", agents['synthesis_expert'])
    
    # 协调者根据任务需求自主委派任务
    # 1. 委派材料设计任务
    design_agent = coordinator.delegate_task("material_design", task_allocator, user_requirement)
    
    # 2. 创建材料设计任务
    design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
    
    # 3. 委派评估任务给所有评估专家
    evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
    evaluation_tasks = []
    for i, agent in enumerate(evaluation_agents):
        task = EvaluationTask(llm).create_task(agent, design_task)
        evaluation_tasks.append(task)
    
    # 4. 委派最终验证任务
    final_validation_agent = task_allocator.get_agent_for_task("final_validation")
    final_validation_task = EvaluationTask(llm).create_task(final_validation_agent, 
                                                           [design_task] + evaluation_tasks)
    
    # 5. 委派机理分析任务
    mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(mechanism_agent, final_validation_task)
    
    # 6. 委派合成方法任务
    synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
    synthesis_method_task = SynthesisMethodTask(llm).create_task(synthesis_agent, final_validation_task)
    
    # 创建Crew，包含所有参与任务的智能体
    all_agents = [
        coordinator_agent,
        design_agent,
        *evaluation_agents,
        final_validation_agent,
        mechanism_agent,
        synthesis_agent
    ]
    
    # 确保不会重复添加智能体
    unique_agents = []
    seen_roles = set()
    for agent in all_agents:
        if agent.role not in seen_roles:
            unique_agents.append(agent)
            seen_roles.add(agent.role)
    
    # 创建任务列表
    all_tasks = [
        design_task,
        *evaluation_tasks,
        final_validation_task,
        mechanism_analysis_task,
        synthesis_method_task
    ]
    
    # 创建Crew
    ecomats_crew = Crew(
        agents=unique_agents,
        tasks=all_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE
    )
    
    # 执行
    result = ecomats_crew.kickoff()
    return result

def main():
    print("基于CrewAI的ecomats多智能体系统")
    print("=" * 50)
    
    # 获取用户自定义输入
    user_requirement = get_user_input()
    
    # 获取用户选择的工作模式
    workflow_mode = get_workflow_mode()
    
    # 验证API密钥是否存在
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型，使用DashScope专用方式
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,  # 使用原始API密钥
        model="openai/" + Config.QWEN_MODEL_NAME,  # 使用配置的模型名称，加上提供商前缀
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 根据用户选择的工作模式执行相应的流程
    if workflow_mode == "preset":
        result = run_preset_workflow(user_requirement, llm)
    else:
        result = run_autonomous_workflow(user_requirement, llm)
    
    print(result)

if __name__ == "__main__":
    main()
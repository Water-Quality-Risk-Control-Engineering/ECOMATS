#!/usr/bin/env python3
"""
运行自主调度模式测试
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from src.config.config import Config
import dashscope

# 智能体导入
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

# 任务导入
from src.tasks.design_task import DesignTask
from src.tasks.evaluation_task import EvaluationTask
from src.tasks.final_validation_task import FinalValidationTask
from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
from src.tasks.synthesis_method_task import SynthesisMethodTask
from src.tasks.operation_suggesting_task import OperationSuggestingTask

def create_test_llm():
    """创建测试用的LLM实例"""
    # 使用默认配置创建LLM实例
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/" + Config.QWEN_MODEL_NAME,
        temperature=0.3,  # 使用较低的温度以获得更一致的结果
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    return llm

def create_all_agents(llm):
    """创建所有智能体的公共函数"""
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

def run_autonomous_workflow(user_requirement, llm):
    """运行智能体自主调度模式"""
    print(f"启动智能体自主调度模式处理: {user_requirement}")
    
    # 创建所有智能体
    agents = create_all_agents(llm)
    
    # 创建任务组织代理实例
    coordinator = TaskOrganizingAgent(llm)
    coordinator_agent = coordinator.create_agent()
    
    # 创建任务分配器并注册所有智能体
    task_allocator = TaskAllocator()
    task_allocator.register_agent("TaskOrganizingAgent", coordinator_agent)
    task_allocator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    task_allocator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    task_allocator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    task_allocator.register_agent("ExtractingAgent", agents['literature_processor'])
    task_allocator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    task_allocator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    task_allocator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # 任务组织代理根据任务需求自主委派任务
    # 1. 委派材料设计任务
    design_agent = coordinator.delegate_task("material_design", task_allocator, user_requirement)
    
    # 2. 创建材料设计任务
    design_task = DesignTask(llm).create_task(design_agent, user_requirement=user_requirement)
    
    # 3. 根据用户需求动态决定需要哪些任务
    required_tasks = []
    required_agents = [coordinator_agent, design_agent]
    seen_roles = {coordinator_agent.role, design_agent.role}
    
    # 使用任务分配器来确定需要哪些任务类型
    required_task_types = task_allocator.determine_required_task_types(user_requirement)
    
    # 获取需要的智能体
    required_agent_mapping = {}
    for task_type in required_task_types:
        if task_type == "material_design":
            # 材料设计任务已经创建了
            required_agent_mapping[task_type] = design_agent
        else:
            agent = task_allocator.get_agent_for_task(task_type)
            if agent and agent.role not in seen_roles:
                required_agent_mapping[task_type] = agent
                required_agents.append(agent)
                seen_roles.add(agent.role)
    
    # 根据任务类型创建相应的任务
    task_mapping = {}
    
    # 首先处理材料设计任务
    task_mapping["material_design"] = design_task
    
    # 然后处理其他任务
    if "evaluation" in required_task_types:
        # 委派评估任务给所有评估专家
        evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
        evaluation_tasks = []
        for agent in evaluation_agents:
            task = EvaluationTask(llm).create_task(agent, design_task)
            evaluation_tasks.append(task)
        
        # 委派最终验证任务
        final_validation_agent = task_allocator.get_agent_for_task("final_validation")
        final_validation_task = FinalValidationTask(llm).create_task(final_validation_agent, 
                                                               [design_task] + evaluation_tasks)
        
        task_mapping["evaluation"] = evaluation_tasks
        task_mapping["final_validation"] = final_validation_task
        required_tasks.extend(evaluation_tasks)
        required_tasks.append(final_validation_task)
        
        # 处理依赖于最终验证任务的任务
        if "mechanism_analysis" in required_task_types:
            mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
            mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(mechanism_agent, final_validation_task)
            task_mapping["mechanism_analysis"] = mechanism_analysis_task
            required_tasks.append(mechanism_analysis_task)
            
        if "synthesis_method" in required_task_types:
            synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
            synthesis_method_task = SynthesisMethodTask(llm).create_task(synthesis_agent, final_validation_task)
            task_mapping["synthesis_method"] = synthesis_method_task
            required_tasks.append(synthesis_method_task)
            
        if "operation_suggestion" in required_task_types:
            operation_suggesting_agent = task_allocator.get_agent_for_task("operation_suggestion")
            operation_suggesting_task = OperationSuggestingTask(llm).create_task(operation_suggesting_agent, final_validation_task)
            task_mapping["operation_suggestion"] = operation_suggesting_task
            required_tasks.append(operation_suggesting_task)
    else:
        # 如果不需要评估任务，则其他任务直接依赖于设计任务
        if "synthesis_method" in required_task_types:
            synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
            synthesis_method_task = SynthesisMethodTask(llm).create_task(synthesis_agent, design_task)
            task_mapping["synthesis_method"] = synthesis_method_task
            required_tasks.append(synthesis_method_task)
            
        if "operation_suggestion" in required_task_types:
            operation_suggesting_agent = task_allocator.get_agent_for_task("operation_suggestion")
            operation_suggesting_task = OperationSuggestingTask(llm).create_task(operation_suggesting_agent, design_task)
            task_mapping["operation_suggestion"] = operation_suggesting_task
            required_tasks.append(operation_suggesting_task)
    
    # 输出任务分配情况
    print(f"需要的任务类型: {required_task_types}")
    print(f"创建的任务数量: {len(required_tasks) + 1}")
    print(f"使用的智能体数量: {len(required_agents)}")
    
    # 创建Crew
    ecomats_crew = Crew(
        agents=required_agents,
        tasks=[design_task] + required_tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE
    )
    
    # 执行
    try:
        result = ecomats_crew.kickoff()
        return {
            "success": True,
            "result": result,
            "task_types": required_task_types,
            "agent_count": len(required_agents),
            "task_count": len(required_tasks) + 1
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "task_types": required_task_types,
            "agent_count": len(required_agents),
            "task_count": len(required_tasks) + 1
        }

def main():
    print("运行自主调度模式测试")
    print("=" * 60)
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 创建测试LLM实例
    try:
        llm = create_test_llm()
        print("成功创建LLM实例")
    except Exception as e:
        print(f"创建LLM实例失败: {e}")
        return
    
    # 测试用例列表
    test_cases = [
        # 基础设计任务
        "设计一种用于处理含重金属镉废水的高效催化剂",
        
        # 设计+合成方法
        "设计一种用于处理含重金属镉废水的高效催化剂，并提供合成方法",
        
        # 设计+操作建议
        "设计一种用于处理含重金属镉废水的高效催化剂，并提供操作建议",
        
        # 设计+评估（简化测试，避免复杂评估）
        "设计一种用于处理含重金属镉废水的高效催化剂，进行性能评估",
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}/{len(test_cases)}: {test_case}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        result = run_autonomous_workflow(test_case, llm)
        end_time = datetime.now()
        
        result["test_case"] = test_case
        result["duration"] = (end_time - start_time).total_seconds()
        results.append(result)
        
        if result["success"]:
            print(f"✓ 测试成功")
            print(f"  任务类型: {result['task_types']}")
            print(f"  任务数量: {result['task_count']}")
            print(f"  智能体数量: {result['agent_count']}")
            print(f"  执行时间: {result['duration']:.2f}秒")
        else:
            print(f"✗ 测试失败")
            print(f"  错误信息: {result['error']}")
            print(f"  任务类型: {result['task_types']}")
            print(f"  任务数量: {result['task_count']}")
            print(f"  智能体数量: {result['agent_count']}")
            print(f"  执行时间: {result['duration']:.2f}秒")
    
    # 输出汇总报告
    print(f"\n{'='*60}")
    print("测试结果汇总报告")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    for i, result in enumerate(results, 1):
        status = "✓" if result["success"] else "✗"
        print(f"\n{i}. {status} {result['test_case']}")
        print(f"   任务类型: {result['task_types']}")
        print(f"   任务数量: {result['task_count']}")
        print(f"   执行时间: {result['duration']:.2f}秒")
        if not result["success"]:
            print(f"   错误: {result['error']}")

if __name__ == "__main__":
    main()
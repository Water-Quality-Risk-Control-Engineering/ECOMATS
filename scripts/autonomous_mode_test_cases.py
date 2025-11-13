#!/usr/bin/env python3
"""
自主调度模式测试用例
"""

import sys
import os
from dotenv import load_dotenv

def create_test_llm(create_llm_func):
    return create_llm_func()

def analyze_task_allocation(user_requirement, llm, agents_cls, tasks_cls):
    print(f"\n{'='*60}")
    print(f"测试用例: {user_requirement}")
    print(f"{'='*60}")

    coordinator_agent = agents_cls['TaskOrganizingAgent'](llm).create_agent()
    material_designer_agent = agents_cls['CreativeDesigningAgent'](llm).create_agent()
    expert_a_agent = agents_cls['AssessmentScreeningAgentA'](llm).create_agent()
    expert_b_agent = agents_cls['AssessmentScreeningAgentB'](llm).create_agent()
    expert_c_agent = agents_cls['AssessmentScreeningAgentC'](llm).create_agent()
    final_validator_agent = agents_cls['AssessmentScreeningAgentOverall'](llm).create_agent()
    literature_processor_agent = agents_cls['ExtractingAgent'](llm).create_agent()
    mechanism_expert_agent = agents_cls['MechanismMiningAgent'](llm).create_agent()
    synthesis_expert_agent = agents_cls['SynthesisGuidingAgent'](llm).create_agent()
    operation_suggesting_agent = agents_cls['OperationSuggestingAgent'](llm).create_agent()

    agents = {
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

    from src.agents.task_allocator import TaskAllocator
    task_allocator = TaskAllocator()
    task_allocator.register_agent("TaskOrganizingAgent", coordinator_agent)
    task_allocator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    task_allocator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    task_allocator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    task_allocator.register_agent("ExtractingAgent", agents['literature_processor'])
    task_allocator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    task_allocator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    task_allocator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])

    required_task_types = task_allocator.determine_required_task_types(user_requirement)

    print(f"需要的任务类型: {required_task_types}")

    agent_mapping = {}
    for task_type in required_task_types:
        agent = task_allocator.get_agent_for_task(task_type)
        if agent:
            agent_mapping[task_type] = agent.role
        else:
            agent_mapping[task_type] = "未找到智能体"

    print("\n任务类型与智能体映射:")
    for task_type, agent_role in agent_mapping.items():
        print(f"  {task_type} -> {agent_role}")

    return required_task_types, agent_mapping

def main():
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, os.path.abspath(project_root))
    load_dotenv()

    from src.utils.llm_config import create_llm
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
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask

    llm = create_test_llm(create_llm)

    test_cases = [
        "设计一种用于处理含重金属镉废水的高效催化剂",
        "设计一种用于处理含重金属镉废水的高效催化剂，并提供合成方法",
        "设计一种用于处理含重金属镉废水的高效催化剂，并提供操作建议",
        "设计一种用于处理含重金属镉废水的高效催化剂，并提供合成方法和操作建议",
        "设计一种用于处理含重金属镉废水的高效催化剂，并进行性能评估",
        "设计一种用于处理含重金属镉废水的高效催化剂，进行性能评估并分析催化机理",
        "设计一种用于处理含重金属镉废水的高效催化剂，进行性能评估并提供合成方法",
        "设计一种用于处理含重金属镉废水的高效催化剂，进行性能评估并提供操作建议",
        "设计一种用于处理含重金属镉废水的高效催化剂，进行性能评估，分析催化机理，提供合成方法和操作建议",
        "Design a novel catalyst for activating peroxymonosulfate and provide synthesis method",
    ]

    agents_cls = {
        'TaskOrganizingAgent': TaskOrganizingAgent,
        'CreativeDesigningAgent': CreativeDesigningAgent,
        'AssessmentScreeningAgentA': AssessmentScreeningAgentA,
        'AssessmentScreeningAgentB': AssessmentScreeningAgentB,
        'AssessmentScreeningAgentC': AssessmentScreeningAgentC,
        'AssessmentScreeningAgentOverall': AssessmentScreeningAgentOverall,
        'ExtractingAgent': ExtractingAgent,
        'MechanismMiningAgent': MechanismMiningAgent,
        'SynthesisGuidingAgent': SynthesisGuidingAgent,
        'OperationSuggestingAgent': OperationSuggestingAgent,
    }

    tasks_cls = {
        'DesignTask': DesignTask,
        'EvaluationTask': EvaluationTask,
        'FinalValidationTask': FinalValidationTask,
        'MechanismAnalysisTask': MechanismAnalysisTask,
        'SynthesisMethodTask': SynthesisMethodTask,
        'OperationSuggestingTask': OperationSuggestingTask,
    }

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}/{len(test_cases)}")
        task_types, agent_mapping = analyze_task_allocation(test_case, llm, agents_cls, tasks_cls)
        results.append({
            'test_case': test_case,
            'task_types': task_types,
            'agent_mapping': agent_mapping
        })

    print(f"\n{'='*60}")
    print("测试结果汇总报告")
    print(f"{'='*60}")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. 测试用例: {result['test_case']}")
        print(f"   需要的任务类型: {result['task_types']}")
        print(f"   任务数量: {len(result['task_types'])}")

if __name__ == "__main__":
    main()
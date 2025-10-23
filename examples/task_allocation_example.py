#!/usr/bin/env python3
"""
任务分配示例脚本
展示如何使用任务分配器进行智能体的自主选择
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from src.config.config import Config

# 智能体导入
from src.agents.coordinator import Coordinator
from src.agents.Creative_Designing_agent import CreativeDesigningAgent
from src.agents.Assessment_Screening_agent_A import AssessmentScreeningAgentA
from src.agents.Assessment_Screening_agent_B import AssessmentScreeningAgentB
from src.agents.Assessment_Screening_agent_C import AssessmentScreeningAgentC
from src.agents.Assessment_Screening_agent_Overall import AssessmentScreeningAgentOverall
from src.agents.Mechanism_Mining_agent import MechanismMiningAgent
from src.agents.Synthesis_Guiding_agent import SynthesisGuidingAgent
from src.agents.Operation_Suggesting_agent import OperationSuggestingAgent
from src.agents.task_allocator import TaskAllocator

def main():
    print("任务分配示例")
    print("=" * 30)
    
    # 初始化LLM模型
    # 注意：在示例中使用占位符而不是真实的API密钥
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key="sk-***",  # 隐藏真实的API密钥
        model="openai/" + Config.QWEN_MODEL_NAME,
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建智能体
    coordinator_agent = Coordinator(llm).create_agent()
    material_designer_agent = CreativeDesigningAgent(llm).create_agent()
    expert_a_agent = AssessmentScreeningAgentA(llm).create_agent()
    expert_b_agent = AssessmentScreeningAgentB(llm).create_agent()
    expert_c_agent = AssessmentScreeningAgentC(llm).create_agent()
    final_validator_agent = AssessmentScreeningAgentOverall(llm).create_agent()
    mechanism_expert_agent = MechanismMiningAgent(llm).create_agent()
    synthesis_expert_agent = SynthesisGuidingAgent(llm).create_agent()
    operation_suggesting_agent = OperationSuggestingAgent(llm).create_agent()
    
    # 创建任务分配器并注册所有智能体
    task_allocator = TaskAllocator()
    task_allocator.register_agent("Coordinator", coordinator_agent)
    task_allocator.register_agent("CreativeDesigningAgent", material_designer_agent)
    task_allocator.register_agent("AssessmentScreeningAgent", [expert_a_agent, expert_b_agent, expert_c_agent])
    task_allocator.register_agent("AssessmentScreeningAgentOverall", final_validator_agent)
    task_allocator.register_agent("MechanismMiningAgent", mechanism_expert_agent)
    task_allocator.register_agent("SynthesisGuidingAgent", synthesis_expert_agent)
    task_allocator.register_agent("OperationSuggestingAgent", operation_suggesting_agent)
    
    # 演示任务分配
    print("演示任务分配:")
    print("-" * 20)
    
    # 为材料设计任务分配智能体
    design_agent = task_allocator.get_agent_for_task("material_design")
    if design_agent:
        print(f"材料设计任务分配给: {design_agent.role}")
    else:
        print("未找到适合材料设计任务的智能体")
    
    # 为评估任务分配智能体
    evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
    if evaluation_agents:
        print(f"评估任务分配给 {len(evaluation_agents)} 个智能体:")
        for i, agent in enumerate(evaluation_agents, 1):
            print(f"  {i}. {agent.role}")
    else:
        print("未找到适合评估任务的智能体")
    
    # 为机理分析任务分配智能体
    mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
    if mechanism_agent:
        print(f"机理分析任务分配给: {mechanism_agent.role}")
    else:
        print("未找到适合机理分析任务的智能体")
    
    # 为合成方法任务分配智能体
    synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
    if synthesis_agent:
        print(f"合成方法任务分配给: {synthesis_agent.role}")
    else:
        print("未找到适合合成方法任务的智能体")
    
    # 为操作建议任务分配智能体
    operation_suggesting_agent = task_allocator.get_agent_for_task("operation_suggestion")
    if operation_suggesting_agent:
        print(f"操作建议任务分配给: {operation_suggesting_agent.role}")
    else:
        print("未找到适合操作建议任务的智能体")
    
    # 根据名称查找特定智能体
    specific_agent = task_allocator.get_agent_by_name("最终验证专家")
    if specific_agent:
        print(f"通过名称查找智能体: {specific_agent.role}")
    else:
        print("未找到指定名称的智能体")
    
    # 演示协调者委派任务
    print("\n演示协调者委派任务:")
    print("-" * 20)
    coordinator = Coordinator(llm)
    
    # 协调者委派材料设计任务
    delegated_agent = coordinator.delegate_task("material_design", task_allocator, "设计一种新型催化剂")
    if delegated_agent:
        print(f"协调者委派材料设计任务给: {delegated_agent.role}")
    else:
        print("协调者未能委派材料设计任务")

if __name__ == "__main__":
    main()
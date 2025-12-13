#!/usr/bin/env python3
"""
任务分配示例脚本
展示如何使用 TOA 进行意图识别和智能体调度

Task allocation example script
Demonstrates how to use TOA for intent recognition and agent scheduling
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

def _load_env():
    from dotenv import load_dotenv
    load_dotenv()

def _imports():
    from src.utils.llm_config import create_llm, create_eas_llm
    from src.config.config import Config
    import dashscope
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
    return {
        'create_llm': create_llm,
        'create_eas_llm': create_eas_llm,
        'Config': Config,
        'dashscope': dashscope,
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

# 任务导入

def create_all_agents(llm):
    """创建所有智能体 / Create all agents"""
    _i = _imports()
    coordinator_agent = _i['TaskOrganizingAgent'](llm).create_agent()
    material_designer_agent = _i['CreativeDesigningAgent'](llm).create_agent()
    expert_a_agent = _i['AssessmentScreeningAgentA'](llm).create_agent()
    expert_b_agent = _i['AssessmentScreeningAgentB'](llm).create_agent()
    expert_c_agent = _i['AssessmentScreeningAgentC'](llm).create_agent()
    final_validator_agent = _i['AssessmentScreeningAgentOverall'](llm).create_agent()
    literature_processor_agent = _i['ExtractingAgent'](llm).create_agent()
    mechanism_expert_agent = _i['MechanismMiningAgent'](llm).create_agent()
    synthesis_expert_agent = _i['SynthesisGuidingAgent'](llm).create_agent()
    operation_suggesting_agent = _i['OperationSuggestingAgent'](llm).create_agent()
    
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

def main():
    _load_env()
    _i = _imports()
    # 验证API密钥是否存在
    if not _i['Config'].is_api_key_valid(_i['Config'].QWEN_API_KEY):
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    _i['dashscope'].api_key = _i['Config'].QWEN_API_KEY
    
    # 初始化LLM模型，优先使用EAS模型配置
    try:
        llm = _i['create_eas_llm']()
        print("成功创建EAS LLM实例用于测试")
    except Exception as e:
        print(f"创建EAS模型实例失败，使用默认配置: {e}")
        # 如果EAS配置失败，回退到默认配置（CrewAI原生LLM）
        llm = _i['create_llm']()
    
    print("基于CrewAI的ecomats多智能体系统 TOA 意图驱动示例")
    print("=" * 50)
    
    # 创建所有智能体
    agents = create_all_agents(llm)
    
    # 创建 TOA 并注册所有智能体 / Create TOA and register all agents
    coordinator = _i['TaskOrganizingAgent'](llm)
    coordinator_agent = coordinator.create_agent()
    
    coordinator.register_agent("TaskOrganizingAgent", coordinator_agent)
    coordinator.register_agent("CreativeDesigningAgent", agents['material_designer'])
    coordinator.register_agent("AssessmentScreeningAgent", [agents['expert_a'], agents['expert_b'], agents['expert_c']])
    coordinator.register_agent("AssessmentScreeningAgentOverall", agents['final_validator'])
    coordinator.register_agent("ExtractingAgent", agents['literature_processor'])
    coordinator.register_agent("MechanismMiningAgent", agents['mechanism_expert'])
    coordinator.register_agent("SynthesisGuidingAgent", agents['synthesis_expert'])
    coordinator.register_agent("OperationSuggestingAgent", agents['operation_suggesting'])
    
    # 示例 1: 意图识别 / Example 1: Intent Recognition
    print("\n🧠 意图识别示例:")
    print("-" * 30)
    
    test_queries = [
        "Design a catalyst for PMS activation and evaluate it",
        "Please evaluate CuNi-C2N2 only",
        "Explain the mechanism of TiO2 photocatalysis"
    ]
    
    for query in test_queries:
        intent = coordinator.analyze_user_intent(query)
        print(f"\n问句: {query[:40]}...")
        print(f"  → needs_design: {intent.get('needs_design')}")
        print(f"  → needs_evaluation: {intent.get('needs_evaluation')}")
        print(f"  → evaluation_mode: {intent.get('evaluation_mode')}")
        print(f"  → needs_mechanism: {intent.get('needs_mechanism')}")
    
    # 示例 2: 智能体获取 / Example 2: Agent Retrieval
    print("\n👥 智能体获取示例:")
    print("-" * 30)
    
    # 获取设计智能体
    design_agent = coordinator.get_agent_for_task("material_design")
    print(f"材料设计智能体: {design_agent.role}")
    
    # 获取评估智能体
    evaluation_agents = coordinator.get_all_agents_for_task("evaluation")
    print(f"评估智能体: {[agent.role for agent in evaluation_agents]}")
    
    # 获取最终验证智能体
    final_validation_agent = coordinator.get_agent_for_task("final_validation")
    print(f"最终验证智能体: {final_validation_agent.role}")
    
    # 获取机理分析智能体
    mechanism_agent = coordinator.get_agent_for_task("mechanism_analysis")
    print(f"机理分析智能体: {mechanism_agent.role}")
    
    # 获取合成方法智能体
    synthesis_agent = coordinator.get_agent_for_task("synthesis_method")
    print(f"合成方法智能体: {synthesis_agent.role}")
    
    # 获取操作建议智能体
    operation_agent = coordinator.get_agent_for_task("operation_suggestion")
    print(f"操作建议智能体: {operation_agent.role}")
    
    print("\n✅ 示例完成!")

if __name__ == "__main__":
    main()

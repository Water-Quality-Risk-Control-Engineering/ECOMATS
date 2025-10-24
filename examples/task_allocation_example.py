#!/usr/bin/env python3
"""
任务分配示例脚本
展示如何使用任务分配器进行智能体的自主选择
"""

import sys
import os
import json

# 添加项目根目录到Python路径，使src模块可以被正确导入
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

def create_all_agents(llm):
    """创建所有智能体 / Create all agents"""
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

def main():
    # 验证API密钥是否存在
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("错误：API密钥未正确设置")
        return
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型，优先使用EAS模型配置
    from src.utils.llm_config import create_eas_llm
    try:
        llm = create_eas_llm()
        print("成功创建EAS LLM实例用于测试")
    except Exception as e:
        print(f"创建EAS模型实例失败，使用默认配置: {e}")
        # 如果EAS配置失败，回退到默认配置
        llm = ChatOpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY,  # 使用原始API密钥
            model="openai/" + Config.QWEN_MODEL_NAME,  # 使用配置的模型名称，加上提供商前缀
            temperature=Config.MODEL_TEMPERATURE,
            streaming=False,
            max_tokens=Config.MODEL_MAX_TOKENS
        )
    
    print("基于CrewAI的ecomats多智能体系统任务分配示例")
    print("=" * 50)
    
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
    print("\n任务委派示例:")
    print("-" * 30)
    
    # 委派材料设计任务
    design_agent = coordinator.delegate_task("material_design", task_allocator, "设计一种新型催化剂")
    print(f"材料设计任务委派给: {design_agent.role}")
    
    # 委派评估任务
    evaluation_agents = task_allocator.get_all_agents_for_task("evaluation")
    print(f"评估任务委派给: {[agent.role for agent in evaluation_agents]}")
    
    # 委派最终验证任务
    final_validation_agent = task_allocator.get_agent_for_task("final_validation")
    print(f"最终验证任务委派给: {final_validation_agent.role}")
    
    # 委派机理分析任务
    mechanism_agent = task_allocator.get_agent_for_task("mechanism_analysis")
    print(f"机理分析任务委派给: {mechanism_agent.role}")
    
    # 委派合成方法任务
    synthesis_agent = task_allocator.get_agent_for_task("synthesis_method")
    print(f"合成方法任务委派给: {synthesis_agent.role}")
    
    # 委派操作建议任务
    operation_suggesting_agent = task_allocator.get_agent_for_task("operation_suggestion")
    print(f"操作建议任务委派给: {operation_suggesting_agent.role}")

if __name__ == "__main__":
    main()
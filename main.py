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
from agents.coordinator import Coordinator
from agents.material_designer import MaterialDesigner
from agents.expert_a import ExpertA
from agents.expert_b import ExpertB
from agents.expert_c import ExpertC
from agents.final_validator import FinalValidator
from agents.literature_processor import LiteratureProcessor
from agents.mechanism_expert import MechanismExpert
from agents.synthesis_expert import SynthesisExpert

# 任务导入
from tasks.design_task import DesignTask
from tasks.evaluation_task import EvaluationTask

def main():
    print("基于CrewAI的ecomats多智能体系统")
    print("=" * 50)
    
    # 打印配置信息用于调试
    print(f"QWEN_API_BASE: {Config.QWEN_API_BASE}")
    print(f"QWEN_API_KEY: {Config.QWEN_API_KEY}")
    print(f"QWEN_MODEL_NAME: {Config.QWEN_MODEL_NAME}")
    print(f"OPENAI_API_BASE: {Config.OPENAI_API_BASE}")
    print(f"OPENAI_API_KEY: {Config.OPENAI_API_KEY}")
    
    # 验证API密钥是否存在
    if not Config.QWEN_API_KEY or Config.QWEN_API_KEY == "YOUR_API_KEY":
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
    
    # 创建智能体
    coordinator_agent = Coordinator(llm).create_agent()
    material_designer_agent = MaterialDesigner(llm).create_agent()
    expert_a_agent = ExpertA(llm).create_agent()
    expert_b_agent = ExpertB(llm).create_agent()
    expert_c_agent = ExpertC(llm).create_agent()
    final_validator_agent = FinalValidator(llm).create_agent()
    literature_processor_agent = LiteratureProcessor(llm).create_agent()
    mechanism_expert_agent = MechanismExpert(llm).create_agent()
    synthesis_expert_agent = SynthesisExpert(llm).create_agent()
    
    # 创建任务
    # 首先创建材料设计任务
    design_task = DesignTask(llm).create_task(material_designer_agent)
    
    # 创建评价任务，依赖于设计任务
    evaluation_task = EvaluationTask(llm).create_task(expert_a_agent, design_task)
    
    # 定义基于评价结果的条件处理逻辑说明
    """
    实现评价流程的条件判断逻辑：
    1. 系统会自动执行设计任务和评价任务
    2. 评价专家会基于五个维度评估材料性能
    3. 如果核心标准不达标，任务会标记为需要重新设计
    4. 协调专家会根据评价结果决定是否需要重新设计
    
    在实际应用中，可以通过以下方式实现循环优化：
    - 使用CrewAI的hierarchical流程，让协调专家动态决定下一步
    - 或者通过自定义工具实现评价结果的解析和条件判断
    """
    
    # 创建Crew
    ecomats_crew = Crew(
        agents=[
            coordinator_agent, 
            material_designer_agent,
            expert_a_agent, 
            expert_b_agent, 
            expert_c_agent,
            final_validator_agent,
            literature_processor_agent,
            mechanism_expert_agent,
            synthesis_expert_agent
        ],
        tasks=[design_task, evaluation_task],  # 任务按顺序执行
        process=Process.sequential,  # 使用顺序流程执行任务
        verbose=Config.VERBOSE
    )
    
    # 执行
    result = ecomats_crew.kickoff()
    print(result)

if __name__ == "__main__":
    main()
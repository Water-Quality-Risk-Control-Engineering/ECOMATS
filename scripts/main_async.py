#!/usr/bin/env python3
"""
ECOMATS - CrewAI 1.7.0异步版本
支持异步Crew执行,显著提升性能
"""

import sys
import os
import json
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# 关键:在导入CrewAI之前设置环境变量!
load_dotenv()  # 先加载.env
os.environ['OPENAI_API_KEY'] = os.getenv('QWEN_API_KEY') or 'dummy'
os.environ['OPENAI_API_BASE'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

# Monkey patch: 修复CrewAI异步memory的bug
# CrewAI 1.7.0的memory在异步模式下会调用asearch(),但ChromaDB客户端是同步的
# 这个patch直接使用同步搜索,避免异步错误
import crewai.memory.storage.rag_storage as rag_storage_module
original_RAGStorage = rag_storage_module.RAGStorage

class PatchedRAGStorage(original_RAGStorage):
    """修复异步搜索的RAGStorage - 直接使用同步方法"""
    async def asearch(self, query: str, limit: int = 5, filter = None, score_threshold: float = 0.6):
        """异步搜索直接使用同步search()"""
        # 直接调用同步方法,跳过异步调用
        return self.search(query, limit, filter, score_threshold)

rag_storage_module.RAGStorage = PatchedRAGStorage

from crewai import Crew, Process

# 配置日志,抑制EAS相关的ERROR提示
logging.basicConfig(level=logging.WARNING)
# 将src.agents的日志级别设为CRITICAL,避免EAS错误提示
for logger_name in ['src.agents.Creative_Designing_agent',
                     'src.agents.Assessment_Screening_agent_A',
                     'src.agents.Assessment_Screening_agent_B', 
                     'src.agents.Assessment_Screening_agent_C',
                     'src.agents.Assessment_Screening_agent_Overall',
                     'src.agents.Mechanism_Mining_agent',
                     'src.agents.Synthesis_Guiding_agent',
                     'src.agents.Operation_Suggesting_agent']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# 添加项目路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

from src.config.config import Config
from src.utils.llm_config import create_llm


def create_dashscope_embedder():
    """创建DashScope Embedding类 - 用于CrewAI记忆系统
    
    关键点:
    1. 必须同时继承ChromaDB和CrewAI的EmbeddingFunction
    2. 返回类型必须是list[np.ndarray]
    """
    # 导入两个基类
    from chromadb.api.types import EmbeddingFunction as ChromaEmbeddingFunction
    from crewai.rag.embeddings.providers.custom.embedding_callable import CustomEmbeddingFunction
    from crewai.rag.core.types import Documents, Embeddings
    from openai import OpenAI
    import numpy as np
    import os
    
    class DashScopeEmbeddingFunction(CustomEmbeddingFunction, ChromaEmbeddingFunction):
        """使用OpenAI SDK调用DashScope Embedding API
        
        同时继承ChromaDB和CrewAI的基类以满足Pydantic验证
        """
        
        def __init__(self):
            self.client = OpenAI(
                api_key=os.getenv('QWEN_API_KEY'),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            self.model = "text-embedding-v2"
            
        def __call__(self, input: Documents) -> Embeddings:
            """
            将文本转换为嵌入向量
            
            Args:
                input: 字符串列表 (Documents = list[str])
                
            Returns:
                Embeddings: numpy数组列表 (list[np.ndarray])
            """
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=input
                )
                # 关键: 返回numpy数组列表!
                embeddings = [
                    np.array(item.embedding, dtype=np.float32) 
                    for item in response.data
                ]
                return embeddings
            except Exception as e:
                print(f"⚠️ DashScope Embedding错误: {e}")
                # 返回空向量作为默认值(维度1536,与v2一致)
                return [np.zeros(1536, dtype=np.float32) for _ in range(len(input))]
    
    return DashScopeEmbeddingFunction  # 返回类而不是实例!


def get_ui_text(key):
    """获取UI文本 / Get UI text"""
    try:
        from src.locales.texts import TEXTS
        lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
        return TEXTS.get(lang, TEXTS['zh'])['ui'].get(key, key)
    except Exception:
        return key


def select_language():
    """选择语言 / Select language"""
    from src.locales import set_language
    
    print("\n" + "="*70)
    print("🌐 Select Language / 选择语言")
    print("="*70)
    print("1. 中文 (Chinese)")
    print("2. English")
    
    while True:
        choice = input("\n请选择/Please select (1-2): ").strip()
        if choice == "1":
            set_language("zh")
            # 更新Config中的语言设置
            Config.LANGUAGE = "zh"
            print("✅ 已选择中文")
            return "zh"
        elif choice == "2":
            set_language("en")
            Config.LANGUAGE = "en"
            print("✅ English selected")
            return "en"
        print("无效选项/Invalid option")


def get_user_input():
    """获取用户材料设计需求 / Get user material design requirements"""
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    print("\n" + "="*70)
    if lang == 'en':
        print("ECOMATS - Multi-Agent System for Water Treatment Material Design (Async)")
        print("="*70)
        print("\nPlease enter your material design requirements:")
        print("Example: Design an efficient catalyst for treating wastewater containing heavy metal cadmium")
        user_input = input("\nMaterial design requirement: ")
    else:
        print("ECOMATS - 水处理材料设计多智能体系统 (异步增强版)")
        print("="*70)
        print("\n请输入您的材料设计需求:")
        print("例如: 设计一种用于处理含重金属镉废水的高效催化剂")
        user_input = input("\n材料设计需求: ")
    return user_input


def get_workflow_mode():
    """获取工作模式 / Get workflow mode"""
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    if lang == 'en':
        print("\nPlease select workflow mode:")
        print("1. Preset Workflow (Sync)")
        print("2. Preset Workflow (Async) ⚡ Recommended!")
        print("3. Autonomous Agent Scheduling (Sync)")
        print("4. Autonomous Agent Scheduling (Async) ⚡ Recommended!")
        prompt = "\nEnter option (1-4): "
        invalid_msg = "Invalid option, please enter 1-4"
    else:
        print("\n请选择工作模式:")
        print("1. 预设工作流 (同步)")
        print("2. 预设工作流 (异步) ⚡ 推荐!")
        print("3. 智能体自主调度 (同步)")
        print("4. 智能体自主调度 (异步) ⚡ 推荐!")
        prompt = "\n请输入选项 (1-4): "
        invalid_msg = "无效选项,请输入1-4"
    
    while True:
        choice = input(prompt).strip()
        if choice in ["1", "2", "3", "4"]:
            return {
                "1": ("preset", False),
                "2": ("preset", True),
                "3": ("autonomous", False),
                "4": ("autonomous", True)
            }[choice]
        print(invalid_msg)


def create_all_agents(llm):
    """创建所有智能体"""
    from src.agents.task_organizing_agent import TaskOrganizingAgent
    from src.agents.Creative_Designing_agent import CreativeDesigningAgent
    from src.agents.Assessment_Screening_agent_A import AssessmentScreeningAgentA
    from src.agents.Assessment_Screening_agent_B import AssessmentScreeningAgentB
    from src.agents.Assessment_Screening_agent_C import AssessmentScreeningAgentC
    from src.agents.Assessment_Screening_agent_Overall import AssessmentScreeningAgentOverall
    from src.agents.Mechanism_Mining_agent import MechanismMiningAgent
    from src.agents.Synthesis_Guiding_agent import SynthesisGuidingAgent
    from src.agents.Operation_Suggesting_agent import OperationSuggestingAgent
    
    return {
        'coordinator': TaskOrganizingAgent(llm).create_agent(),
        'material_designer': CreativeDesigningAgent(llm).create_agent(),
        'expert_a': AssessmentScreeningAgentA(llm).create_agent(),
        'expert_b': AssessmentScreeningAgentB(llm).create_agent(),
        'expert_c': AssessmentScreeningAgentC(llm).create_agent(),
        'final_validator': AssessmentScreeningAgentOverall(llm).create_agent(),
        'mechanism_expert': MechanismMiningAgent(llm).create_agent(),
        'synthesis_expert': SynthesisGuidingAgent(llm).create_agent(),
        'operation_suggesting': OperationSuggestingAgent(llm).create_agent()
    }


async def run_preset_workflow_async(user_requirement, llm):
    """异步预设工作流 - 使用CrewAI 1.7.0异步功能"""
    print("\n🚀 启动异步预设工作流...")
    print("-" * 70)
    
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask  
    from src.tasks.final_validation_task import FinalValidationTask
    from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
    from src.tasks.synthesis_method_task import SynthesisMethodTask
    from src.tasks.operation_suggesting_task import OperationSuggestingTask
    
    # 创建所有agent
    agents = create_all_agents(llm)
    
    # 1. 材料设计任务
    design_task = DesignTask(
        agent=agents['material_designer']
    ).create_task(
        agent=agents['material_designer'],
        user_requirement=user_requirement
    )
    
    # 2. 三个评估任务(可并行)
    eval_a_task = EvaluationTask(
        agent=agents['expert_a']
    ).create_task(
        agent=agents['expert_a'],
        context_task=design_task
    )
    eval_a_task.async_execution = True  # 启用异步!
    
    eval_b_task = EvaluationTask(
        agent=agents['expert_b']
    ).create_task(
        agent=agents['expert_b'],
        context_task=design_task
    )
    eval_b_task.async_execution = True  # 启用异步!
    
    eval_c_task = EvaluationTask(
        agent=agents['expert_c']
    ).create_task(
        agent=agents['expert_c'],
        context_task=design_task
    )
    eval_c_task.async_execution = True  # 启用异步!
    
    # 3. 最终验证
    final_validation_task = FinalValidationTask(
        agent=agents['final_validator']
    ).create_task(
        agent=agents['final_validator'],
        context_task=[eval_a_task, eval_b_task, eval_c_task]
    )
    
    # 4. 机制分析(可与合成并行)
    mechanism_task = MechanismAnalysisTask(
        agent=agents['mechanism_expert']
    ).create_task(
        agent=agents['mechanism_expert'],
        context_task=final_validation_task
    )
    mechanism_task.async_execution = True  # 启用异步!
    
    # 5. 合成方法
    synthesis_task = SynthesisMethodTask(
        agent=agents['synthesis_expert']
    ).create_task(
        agent=agents['synthesis_expert'],
        context_task=final_validation_task
    )
    synthesis_task.async_execution = True  # 启用异步!
    
    # 6. 操作建议
    operation_task = OperationSuggestingTask(
        agent=agents['operation_suggesting']
    ).create_task(
        agent=agents['operation_suggesting'],
        context_task=[mechanism_task, synthesis_task]
    )
    
    # 创建Crew (使用自定义DashScope Embedding)
    # 注意: 传入类而不是实例!
    DashScopeEmbedder = create_dashscope_embedder()
    
    crew = Crew(
        agents=list(agents.values()),
        tasks=[
            design_task,
            eval_a_task, eval_b_task, eval_c_task,  # 并行评估
            final_validation_task,
            mechanism_task, synthesis_task,  # 并行分析
            operation_task
        ],
        process=Process.sequential,
        verbose=True,
        memory=True,  # 启用记忆系统
        embedder={
            "provider": "custom",
            "config": {
                "embedding_callable": DashScopeEmbedder  # 传入类
            }
        }
    )
    
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    if lang == 'en':
        print("⚡ Using async execution mode...")
        print("  - 3 evaluation tasks will run in parallel")
        print("  - Mechanism analysis and synthesis will run in parallel")
        print("  - Expected 2-3x performance improvement")
        print("\n🧠 Memory system enabled (using DashScope text-embedding-v2)")
        print("  - Short-term memory: Store current conversation context")
        print("  - Long-term memory: Learn from historical tasks")
        print("  - Entity memory: Extract key entity information")
        print("  - Storage location: ./.crewai/memory/\n")
    else:
        print("⚡ 使用异步执行模式...")
        print("  - 3个评估任务将并行执行")
        print("  - 机制分析和合成方法将并行执行")
        print("  - 预计性能提升2-3倍")
        print("\n🧠 记忆系统已启用 (使用DashScope text-embedding-v2)")
        print("  - 短期记忆: 存储当前对话上下文")
        print("  - 长期记忆: 学习历史任务经验")
        print("  - 实体记忆: 提取关键实体信息")
        print("  - 存储位置: ./.crewai/memory/\n")
    
    # 异步执行Crew!
    result = await crew.akickoff(inputs={'requirement': user_requirement})
    
    return result


def run_preset_workflow_sync(user_requirement, llm):
    """同步预设工作流 - 保持向后兼容"""
    print("\n📌 启动同步预设工作流...")
    print("-" * 70)
    
    # 导入原始main.py的run_preset_workflow
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from main import run_preset_workflow
    
    return run_preset_workflow(user_requirement, llm)


async def main_async():
    """异步主函数 / Async main function"""
    load_dotenv()
    
    # 再次确保EAS日志被抑制
    logging.getLogger('src.agents').setLevel(logging.CRITICAL)
    
    # 检查环境变量
    if not Config.QWEN_API_KEY:
        print("❌ 错误: 未设置QWEN_API_KEY / Error: QWEN_API_KEY not set")
        return
    
    # 选择语言 / Select language
    select_language()
    
    # 创建LLM
    llm = create_llm()
    
    # 获取用户输入
    user_requirement = get_user_input()
    
    # 获取工作模式
    mode, use_async = get_workflow_mode()
    
    if mode == "preset":
        if use_async:
            # 异步预设工作流
            result = await run_preset_workflow_async(user_requirement, llm)
        else:
            # 同步预设工作流
            result = run_preset_workflow_sync(user_requirement, llm)
    else:
        # 自主调度模式(暂时使用同步)
        print("\n⚠️ 自主调度模式暂时使用同步执行")
        from main import run_autonomous_workflow
        result = run_autonomous_workflow(user_requirement, llm)
    
    # 输出结果 / Output result
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    print("\n" + "="*70)
    if lang == 'en':
        print("Execution Complete!")
    else:
        print("执行完成!")
    print("="*70)
    
    # 保存结果到outputs目录（不在终端打印完整结果）
    # Save result to outputs directory (without printing full result to terminal)
    save_result(result, user_requirement, mode, use_async)
    
    return result


def save_result(result, user_requirement, mode, use_async):
    """保存执行结果到outputs目录 / Save execution result to outputs directory"""
    lang = Config.LANGUAGE if hasattr(Config, 'LANGUAGE') else 'zh'
    
    # 确保outputs目录存在 / Ensure outputs directory exists
    outputs_dir = os.path.join(project_root, 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    
    # 生成文件名 / Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    mode_str = f"{mode}_{'async' if use_async else 'sync'}"
    filename = f"workflow_result_{timestamp}_{mode_str}.txt"
    filepath = os.path.join(outputs_dir, filename)
    
    # 写入结果 / Write result
    with open(filepath, 'w', encoding='utf-8') as f:
        if lang == 'en':
            f.write(f"ECOMATS Execution Result\n")
            f.write(f"{'='*70}\n")
            f.write(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution Mode: {mode_str}\n")
            f.write(f"User Requirement: {user_requirement}\n")
        else:
            f.write(f"ECOMATS 执行结果\n")
            f.write(f"{'='*70}\n")
            f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"执行模式: {mode_str}\n")
            f.write(f"用户需求: {user_requirement}\n")
        f.write(f"{'='*70}\n\n")
        f.write(str(result))
    
    if lang == 'en':
        print(f"\n📁 Result saved to: {filepath}")
    else:
        print(f"\n📁 结果已保存到: {filepath}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ECOMATS - CrewAI 1.7.0 异步增强版")
    print("="*70)
    print("\n🚀 新特性:")
    print("  - 异步Crew执行 (akickoff)")
    print("  - 并行Task执行 (async_execution=True)")
    print("  - 性能提升2-3倍")
    print("  - 完全向后兼容")
    print("\n" + "="*70)
    
    # 运行异步主函数
    asyncio.run(main_async())

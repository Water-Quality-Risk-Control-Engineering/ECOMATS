#!/usr/bin/env python3
"""
CDA (Creative_Designing_agent) 性能测试脚本
单独测试材料设计智能体的运行时间
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

from dotenv import load_dotenv
load_dotenv()

# 设置 OpenAI 兼容环境变量
_api_key = os.getenv('QWEN_API_KEY') or 'dummy'
_api_base = os.getenv('QWEN_API_BASE') or 'https://dashscope.aliyuncs.com/compatible-mode/v1'
os.environ['OPENAI_API_KEY'] = _api_key
os.environ['OPENAI_API_BASE'] = _api_base
os.environ['OPENAI_BASE_URL'] = _api_base

from src.utils.llm_config import create_llm
from src.agents.Creative_Designing_agent import CreativeDesigningAgent
from src.tasks.design_task import DesignTask


def test_cda_performance():
    """测试 CDA 单独运行的性能"""
    print("=" * 70)
    print("CDA (Creative_Designing_agent) 性能测试")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    # 测试需求
    user_requirement = """Design 3 novel diatomic catalysts for activating peroxymonosulfate to generate sulfate radicals, which will be used for water pollution control in advanced oxidation processes."""
    
    print(f"测试需求: {user_requirement[:100]}...")
    print("-" * 70)
    
    # 创建 LLM
    llm = create_llm()
    
    # 创建 CDA Agent
    print("\n📝 创建 Creative_Designing_agent...")
    cda_instance = CreativeDesigningAgent(llm)
    agent = cda_instance.create_agent()
    
    # 显示工具配置
    print(f"✅ Agent 创建完成")
    print(f"   - 配置的工具数量: {len(agent.tools)}")
    print(f"   - 工具列表: {[tool.name for tool in agent.tools]}")
    print(f"   - Max iterations: {agent.max_iter}")
    print(f"   - Temperature: {cda_instance.temperature}")
    print("-" * 70)
    
    # 创建任务
    design_task = DesignTask(agent=agent).create_task(
        agent=agent,
        user_requirement=user_requirement
    )
    
    # 开始计时
    start_time = time.time()
    print(f"\n🚀 开始执行任务...")
    print(f"   开始时间: {datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}")
    
    # 执行任务
    try:
        from crewai import Crew, Process
        crew = Crew(
            agents=[agent],
            tasks=[design_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        # 结束计时
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("✅ 测试完成")
        print("=" * 70)
        print(f"结束时间: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}")
        print(f"总耗时: {duration:.2f} 秒 ({duration/60:.2f} 分钟)")
        print("-" * 70)
        
        # 保存结果
        output_dir = os.path.join(project_root, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'cda_performance_test_{timestamp}.txt')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("CDA 性能测试报告\n")
            f.write("=" * 70 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总耗时: {duration:.2f} 秒 ({duration/60:.2f} 分钟)\n")
            f.write(f"工具配置: {[tool.name for tool in agent.tools]}\n")
            f.write(f"Max iterations: {agent.max_iter}\n")
            f.write(f"Temperature: {cda_instance.temperature}\n")
            f.write("-" * 70 + "\n\n")
            f.write("设计结果:\n")
            f.write("-" * 70 + "\n")
            f.write(str(result))
        
        print(f"\n📁 结果已保存到: {output_file}")
        
        return duration
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("❌ 测试失败")
        print("=" * 70)
        print(f"错误信息: {str(e)}")
        print(f"已运行时间: {duration:.2f} 秒")
        print("-" * 70)
        
        raise


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ECOMATS - CDA 性能测试工具")
    print("=" * 70)
    print("\n⚙️  测试配置:")
    print("  - 仅使用 Materials Project 和 PubChem 工具")
    print("  - 其他工具已注释（可恢复）")
    print("  - 测试 3 个双原子催化剂设计任务")
    print("\n" + "=" * 70)
    
    try:
        duration = test_cda_performance()
        
        print("\n" + "=" * 70)
        print("📊 性能摘要")
        print("=" * 70)
        print(f"总耗时: {duration:.2f} 秒")
        
        if duration < 20:
            print("✅ 优秀！运行时间 < 20 秒")
        elif duration < 30:
            print("✅ 良好！运行时间 < 30 秒")
        elif duration < 60:
            print("⚠️  可接受，运行时间 < 1 分钟")
        else:
            print("⚠️  较慢，运行时间 > 1 分钟")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

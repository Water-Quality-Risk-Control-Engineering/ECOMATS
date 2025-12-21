#!/usr/bin/env python3
"""
CDA (Creative Designing Agent) Thinking Process Demo
用于论文展示：展示材料设计专家的内部推理过程

使用 Qwen3 的 thinking 模式，捕获模型的 <think>...</think> 内容
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv(project_root / ".env")

# ============================================================
# 配置
# ============================================================
API_KEY = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# 使用支持 thinking 的模型
MODEL_NAME = os.getenv("QWEN_THINKING_MODEL", "qwen3-235b-a22b")

# CDA 系统提示词（精简版，用于演示）
CDA_SYSTEM_PROMPT = """You are Creative_Designing_agent, a specialized expert for water treatment material design.

## Core Responsibilities:
1. Design new water treatment materials based on user requirements
2. Predict key properties and performance metrics
3. Ensure designed materials are scientifically feasible

## Material Classification (必须严格遵守):
- Metal-based materials: Pure metals, metal oxides, metal sulfides
- Carbon-based materials: Graphene, carbon nanotubes, activated carbon
- MOF/COF materials: Metal-organic frameworks
- Composite materials: Combinations of above

## Design Process:
1. Analyze user requirements and target pollutants
2. Select material type, design structure and morphology
3. Predict physical and chemical properties
4. Analyze expected performance

Please provide your design with detailed reasoning."""


def demo_cda_thinking(user_requirement: str, show_full_output: bool = True):
    """
    演示 CDA 的 thinking 过程
    
    Args:
        user_requirement: 用户的材料设计需求
        show_full_output: 是否显示完整输出（包括最终答案）
    """
    if not API_KEY:
        print("❌ 错误: 未找到 API_KEY，请在 .env 中设置 QWEN_API_KEY")
        return
    
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    print("=" * 70)
    print("🧪 CDA (Creative Designing Agent) Thinking Process Demo")
    print("=" * 70)
    print(f"\n📝 User Requirement:\n{user_requirement}\n")
    print("-" * 70)
    
    try:
        # 调用 API，启用 thinking 模式
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": CDA_SYSTEM_PROMPT},
                {"role": "user", "content": user_requirement}
            ],
            extra_body={"enable_thinking": True},  # 启用 thinking 模式
            stream=True  # 流式输出
        )
        
        thinking_content = ""
        answer_content = ""
        current_mode = None
        
        print("\n🧠 [CDA Internal Thinking Process]\n")
        
        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            
            # 处理 thinking 内容
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                if current_mode != "thinking":
                    current_mode = "thinking"
                thinking_content += delta.reasoning_content
                print(delta.reasoning_content, end="", flush=True)
            
            # 处理最终答案
            if hasattr(delta, 'content') and delta.content:
                if current_mode != "answer":
                    if current_mode == "thinking":
                        print("\n\n" + "-" * 70)
                        print("\n📋 [CDA Final Output]\n")
                    current_mode = "answer"
                answer_content += delta.content
                if show_full_output:
                    print(delta.content, end="", flush=True)
        
        print("\n\n" + "=" * 70)
        
        # 统计信息
        thinking_chars = len(thinking_content)
        answer_chars = len(answer_content)
        print(f"\n📊 Statistics:")
        print(f"   - Thinking length: {thinking_chars} chars")
        print(f"   - Answer length: {answer_chars} chars")
        print(f"   - Thinking ratio: {thinking_chars / (thinking_chars + answer_chars) * 100:.1f}%")
        
        return {
            "thinking": thinking_content,
            "answer": answer_content
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def main():
    # 示例需求（用于论文展示）
    example_requirements = [
        # 示例 1: 双原子催化剂设计（论文展示）
        "Design 5 new dual-atom catalysts for peroxymonosulfate activating, which have not been reported before, and explain why.",
    ]
    
    # 运行演示
    for i, req in enumerate(example_requirements, 1):
        print(f"\n{'#' * 70}")
        print(f"# Example {i}")
        print(f"{'#' * 70}")
        result = demo_cda_thinking(req, show_full_output=False)
        
        if result:
            # 保存结果到文件（用于论文）
            output_file = project_root / f"outputs/cda_thinking_demo_{i}.txt"
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"User Requirement:\n{req}\n\n")
                f.write("=" * 70 + "\n")
                f.write("THINKING PROCESS:\n")
                f.write("=" * 70 + "\n")
                f.write(result["thinking"])
                f.write("\n\n" + "=" * 70 + "\n")
                f.write("FINAL OUTPUT:\n")
                f.write("=" * 70 + "\n")
                f.write(result["answer"])
            print(f"\n💾 Saved to: {output_file}")


if __name__ == "__main__":
    main()

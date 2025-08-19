#!/usr/bin/env python3
"""
测试修复后的代码功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 测试llm_config模块
def test_llm_config():
    print("测试llm_config模块...")
    try:
        from utils.llm_config import create_eas_llm
        print("✓ llm_config模块导入成功")
    except Exception as e:
        print(f"✗ llm_config模块导入失败: {e}")

# 测试evaluation_tool模块
def test_evaluation_tool():
    print("测试evaluation_tool模块...")
    try:
        from tools.evaluation_tool import EvaluationTool
        print("✓ evaluation_tool模块导入成功")
        
        # 测试分析功能
        test_report = '''
        {
            "results": [
                {
                    "scores": [8, 7, 9, 7, 8]
                }
            ]
        }
        '''
        
        result = EvaluationTool.analyze_evaluation_result(test_report)
        print(f"✓ 评价分析功能正常: {result}")
    except Exception as e:
        print(f"✗ evaluation_tool模块测试失败: {e}")

# 测试expert_c模块
def test_expert_c():
    print("测试expert_c模块...")
    try:
        from agents.expert_c import expert_c
        print("✓ expert_c模块导入成功")
    except Exception as e:
        print(f"✗ expert_c模块导入失败: {e}")

# 测试所有模块
def test_all_modules():
    print("开始测试所有修复后的模块...")
    print("=" * 50)
    
    test_llm_config()
    test_evaluation_tool()
    test_expert_c()
    
    print("=" * 50)
    print("模块测试完成")

if __name__ == "__main__":
    test_all_modules()
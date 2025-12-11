#!/usr/bin/env python3
"""
测试仅评估模式（不总结）功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(project_root))

from src.agents.task_allocator import TaskAllocator

def test_evaluation_only_mode():
    """测试仅评估模式的识别"""
    print("="*70)
    print("测试仅评估模式（不总结）功能")
    print("="*70)
    
    task_allocator = TaskAllocator()
    
    # 测试用例
    test_cases = [
        # 仅评估模式（应该识别为evaluation_only）
        ("设计催化剂并仅评估，不总结", ["material_design", "evaluation_only"]),
        ("设计催化剂并只评估，不要总结", ["material_design", "evaluation_only"]),
        ("设计催化剂，只要三个ASA评分，不需要总结", ["material_design", "evaluation_only"]),
        ("Design catalyst and evaluation only without summary", ["material_design", "evaluation_only"]),
        ("设计并仅评分", ["material_design", "evaluation_only"]),
        
        # 完整评估模式（应该识别为evaluation + final_validation）
        ("设计催化剂并评估", ["material_design", "evaluation", "final_validation"]),
        ("设计并进行性能评估", ["material_design", "evaluation", "final_validation"]),
        
        # 其他模式
        ("设计一种催化剂", ["material_design"]),
        ("只分析机理", ["mechanism_analysis"]),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (user_input, expected_tasks) in enumerate(test_cases, 1):
        actual_tasks = task_allocator.determine_required_task_types(user_input)
        
        print(f"\n测试用例 {i}: {user_input}")
        print(f"  期望任务: {expected_tasks}")
        print(f"  实际任务: {actual_tasks}")
        
        if actual_tasks == expected_tasks:
            print("  ✓ 测试通过")
            success_count += 1
        else:
            print("  ✗ 测试失败")
    
    print(f"\n{'='*70}")
    print(f"测试结果: {success_count}/{total_count} 通过")
    print(f"{'='*70}")
    
    return success_count == total_count

def explain_feature():
    """解释新功能"""
    print("\n" + "="*70)
    print("新功能说明：仅评估模式（不总结）")
    print("="*70)
    
    print("\n【功能描述】")
    print("  当用户只想要三个ASA（评估专家A/B/C）的独立评分，")
    print("  不需要ASA-Overall进行最终总结和排名时，可以使用此模式。")
    
    print("\n【触发关键词】")
    print("  中文：仅评估、只评估、不总结、不要总结、不需要总结、只要评分、仅评分")
    print("  英文：only evaluation、no summary、evaluation only、without summary")
    
    print("\n【使用示例】")
    print("  ✓ \"设计催化剂并仅评估，不总结\"")
    print("  ✓ \"设计催化剂并只评估，不要总结\"")
    print("  ✓ \"设计催化剂，只要三个ASA评分，不需要总结\"")
    print("  ✓ \"Design catalyst and evaluation only without summary\"")
    
    print("\n【执行流程对比】")
    print("\n  传统评估模式（带总结）：")
    print("    设计任务 → ASA-A评估 → ASA-B评估 → ASA-C评估 → ASA-Overall总结")
    print("                                                    ↑")
    print("                                          会进行加权计算、排名、总结")
    
    print("\n  仅评估模式（不总结）：")
    print("    设计任务 → ASA-A评估 → ASA-B评估 → ASA-C评估")
    print("                                      ↑")
    print("                            三个独立评分，互不影响")
    
    print("\n【优势】")
    print("  1. 更快：省去最终总结步骤，执行时间减少约25%")
    print("  2. 更便宜：减少一个智能体的API调用，成本降低约25%")
    print("  3. 更独立：三个专家的评分完全独立，不受总结影响")
    print("  4. 更灵活：用户可以自行分析三个专家的评分")
    
    print("\n【适用场景】")
    print("  ✓ 需要多角度独立评估意见")
    print("  ✓ 用户想自己分析多个专家意见")
    print("  ✓ 快速获取初步评估结果")
    print("  ✓ 预算有限，想节省成本")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    # 先解释功能
    explain_feature()
    
    # 然后运行测试
    success = test_evaluation_only_mode()
    
    if success:
        print("\n✅ 所有测试通过！仅评估模式已成功实现。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败！请检查实现。")
        sys.exit(1)

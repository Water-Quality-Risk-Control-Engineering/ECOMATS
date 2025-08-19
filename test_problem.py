#!/usr/bin/env python3
"""
测试顺序执行模式的示例问题
"""

test_problem = """
设计一种用于处理工业废水中有机污染物的新型催化剂材料。

目标污染物：苯酚（C6H5OH）
处理要求：
1. 能够在温和条件下（常温常压）有效降解苯酚
2. 具有良好的催化稳定性和重复使用性能
3. 成本合理，环境友好
4. 易于规模化生产和应用

请基于以上要求设计一种新型催化剂材料，并进行全面评估。
"""

# 模拟一个简化版的主程序来测试系统
def test_main():
    print("测试问题：")
    print(test_problem)
    print("\n注意：要运行完整的系统，请配置API密钥后执行 'python main.py'")
    
    # 检查依赖是否安装
    try:
        import crewai
        import langchain
        import dotenv
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"✗ 依赖缺失: {e}")
        print("请运行 'pip install -r requirements.txt' 安装依赖")

if __name__ == "__main__":
    test_main()
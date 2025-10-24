#!/usr/bin/env python3
"""
检查Materials Project API支持的字段
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

# 确保环境变量已加载
from dotenv import load_dotenv
load_dotenv()

try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    MP_API_AVAILABLE = False
    print("mp-api客户端未安装")

def check_available_fields():
    """检查API支持的字段"""
    if not MP_API_AVAILABLE:
        print("无法检查字段，mp-api客户端未安装")
        return
        
    try:
        # 获取API密钥
        api_key = os.getenv('MATERIALS_PROJECT_API_KEY')
        if not api_key:
            print("Materials Project API密钥未设置")
            return
            
        # 初始化MPRester客户端
        mpr = MPRester(api_key)
        
        # 获取可用字段
        available_fields = mpr.materials.available_fields
        print("Materials Project API支持的字段:")
        for field in sorted(available_fields):
            print(f"  {field}")
            
        # 特别检查我们感兴趣的字段
        fields_of_interest = [
            "band_gap",
            "formation_energy_per_atom",
            "energy_above_hull",
            "elasticity",
            "magnetic_ordering",
            "total_magnetization"
        ]
        
        print("\n我们感兴趣的字段检查结果:")
        for field in fields_of_interest:
            if field in available_fields:
                print(f"  ✓ {field} - 可用")
            else:
                print(f"  ✗ {field} - 不可用")
                
    except Exception as e:
        print(f"检查字段时出错: {e}")

def main():
    """主函数"""
    print("检查Materials Project API支持的字段...")
    check_available_fields()
    print("\n检查完成。")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
材料设计智能体工具调用验证脚本
用于验证智能体正确注册和使用工具
"""

import sys
import os
import json

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.abspath(project_root))

def analyze_agent_tool_registration():
    """分析智能体工具注册情况"""
    try:
        print("材料设计智能体工具注册分析")
        print("=" * 50)
        
        # 导入必要的模块
        from src.utils.llm_config import create_llm
        from src.agents.Creative_Designing_agent import CreativeDesigningAgent
        
        # 创建LLM实例
        llm = create_llm()
        
        # 创建材料设计智能体
        designer_agent = CreativeDesigningAgent(llm)
        agent = designer_agent.create_agent()
        
        # 显示智能体信息
        print(f"智能体角色: {agent.role}")
        print(f"智能体目标: {agent.goal}")
        
        # 显示智能体注册的工具
        print("\n智能体注册的工具:")
        if hasattr(agent, 'tools') and agent.tools:
            for i, tool in enumerate(agent.tools, 1):
                print(f"  {i}. {type(tool).__name__}")
                # 显示工具的一些基本信息
                if hasattr(tool, 'name'):
                    print(f"     名称: {tool.name}")
                if hasattr(tool, 'description'):
                    print(f"     描述: {tool.description}")
        else:
            print("  未找到注册的工具")
            
        # 分析工具的功能
        print("\n工具功能分析:")
        tools_info = {
            "CrewAIMaterialsProjectTool": "查询无机材料数据库，获取材料结构和性质数据",
            "CrewAIPubChemTool": "查询有机化合物数据库，获取化合物结构和性质数据",
            "CrewAIName2CASTool": "将化合物名称转换为CAS号",
            "CrewAIName2PropertiesTool": "通过名称查询化合物性质",
            "CrewAICID2PropertiesTool": "通过CID查询化合物性质",
            "CrewAIFormula2PropertiesTool": "通过化学式查询化合物性质",
            "CrewAIMaterialSearchTool": "搜索相似材料的性能数据",
            "CrewAIPNECTool": "查询化学物质的环境安全数据",
            "CrewAIStructureValidatorTool": "验证材料结构是否真实存在"
        }
        
        for tool_name, description in tools_info.items():
            print(f"  {tool_name}: {description}")
            
        return True
        
    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_tool_calls():
    """测试单个工具的实际调用"""
    try:
        print("\n\n单个工具实际调用测试")
        print("=" * 50)
        
        # 测试Materials Project工具调用
        print("1. 测试Materials Project工具调用:")
        try:
            from src.tools.materials_project_tool import get_materials_project_tool
            mp_tool = get_materials_project_tool()
            if mp_tool:
                print("  ✓ Materials Project工具初始化成功")
                # 实际调用测试
                try:
                    result = mp_tool.search_materials(formula="Fe2O3", limit=2)
                    print(f"  ✓ 搜索调用成功")
                    if 'data' in result and len(result['data']) > 0:
                        print(f"    返回 {len(result['data'])} 个材料:")
                        for material in result['data'][:2]:  # 只显示前2个
                            print(f"      - {material.get('formula', 'N/A')} ({material.get('material_id', 'N/A')})")
                    else:
                        print("    未找到匹配的材料")
                except Exception as e:
                    print(f"  ✗ 搜索调用失败: {e}")
            else:
                print("  ✗ Materials Project工具初始化失败")
        except Exception as e:
            print(f"  ✗ Materials Project工具不可用: {e}")
        
        # 测试PubChem工具调用
        print("\n2. 测试PubChem工具调用:")
        try:
            from src.tools.pubchem_tool import get_pubchem_tool
            pubchem_tool = get_pubchem_tool()
            if pubchem_tool:
                print("  ✓ PubChem工具初始化成功")
                # 实际调用测试
                try:
                    result = pubchem_tool.search_compound("lead ion", search_type="name")
                    print(f"  ✓ 搜索调用成功")
                    if 'compounds' in result and len(result['compounds']) > 0:
                        print(f"    找到 {len(result['compounds'])} 个化合物")
                    else:
                        print("    未找到匹配的化合物")
                except Exception as e:
                    print(f"  ✗ 搜索调用失败: {e}")
            else:
                print("  ✗ PubChem工具初始化失败")
        except Exception as e:
            print(f"  ✗ PubChem工具不可用: {e}")
        
        # 测试Structure Validator工具调用
        print("\n3. 测试Structure Validator工具调用:")
        try:
            from src.tools.structure_validator_tool import get_structure_validator_tool
            validator_tool = get_structure_validator_tool()
            if validator_tool:
                print("  ✓ Structure Validator工具初始化成功")
                # 实际调用测试
                try:
                    result = validator_tool.validate_structure_exists("Fe2O3")
                    print(f"  ✓ 验证调用成功")
                    print(f"    验证结果: {result.get('valid', 'N/A')}")
                    print(f"    材料类型: {result.get('type', 'N/A')}")
                except Exception as e:
                    print(f"  ✗ 验证调用失败: {e}")
            else:
                print("  ✗ Structure Validator工具初始化失败")
        except Exception as e:
            print(f"  ✗ Structure Validator工具不可用: {e}")
            
        return True
        
    except Exception as e:
        print(f"工具调用测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_task_description():
    """分析任务描述中对工具使用的要求"""
    try:
        print("\n\n任务描述工具使用要求分析")
        print("=" * 50)
        
        from src.utils.llm_config import create_llm
        from src.tasks.design_task import DesignTask
        from src.agents.Creative_Designing_agent import CreativeDesigningAgent
        
        # 创建实例
        llm = create_llm()
        designer_agent = CreativeDesigningAgent(llm)
        agent = designer_agent.create_agent()
        
        # 创建任务
        design_task_instance = DesignTask(llm)
        task = design_task_instance.create_task(agent, user_requirement="测试任务")
        
        # 分析任务描述
        description = task.description
        print("任务描述中的工具使用要求:")
        
        # 查找强制使用工具的指示
        if "强制使用Materials Project工具" in description:
            print("  ✓ 强制要求使用Materials Project工具")
            
        if "强制使用PubChem工具" in description:
            print("  ✓ 强制要求使用PubChem工具")
            
        if "强制使用Structure Validator工具" in description:
            print("  ✓ 强制要求使用Structure Validator工具")
            
        if "必须验证设计的材料结构在现实中是否存在" in description:
            print("  ✓ 要求验证材料结构存在性")
            
        if "必须使用Materials Project和PubChem工具获取数据支持设计" in description:
            print("  ✓ 要求使用工具获取数据支持")
            
        # 查找工具使用说明
        print("\n工具使用说明:")
        lines = description.split('\n')
        for line in lines:
            if "工具" in line and ("使用" in line or "查询" in line):
                print(f"  {line.strip()}")
                
        return True
        
    except Exception as e:
        print(f"任务描述分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始材料设计智能体工具调用验证...")
    
    # 分析智能体工具注册
    analyze_agent_tool_registration()
    
    # 测试单个工具的实际调用
    test_individual_tool_calls()
    
    # 分析任务描述中的工具使用要求
    analyze_task_description()
    
    print("\n验证完成!")
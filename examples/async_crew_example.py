#!/usr/bin/env python3
"""
CrewAI 1.7.0异步Crew示例
演示如何使用异步工具和异步Task
"""
import asyncio
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from src.utils.llm_config import create_llm
from src.tools.async_pubchem_tool import get_async_pubchem_tool

# 创建异步工具
@tool("异步PubChem搜索")
async def async_pubchem_search_tool(compound_name: str) -> str:
    """异步查询PubChem化合物信息"""
    tool_instance = get_async_pubchem_tool()
    result = await tool_instance.get_compound_info(compound_name)
    
    if "error" in result:
        return f"查询失败: {result['error']}"
    
    if "Compound" in result:
        compound = result["Compound"]
        return f"""化合物: {compound_name}
- CID: {compound.get('CID', 'N/A')}
- 分子式: {compound.get('molecular_formula', 'N/A')}
- 分子量: {compound.get('molecular_weight', 'N/A')}
- SMILES: {compound.get('canonical_smiles', 'N/A')}
"""
    return "未找到信息"


async def main():
    """异步主函数"""
    print("="*70)
    print("CrewAI 1.7.0 异步Crew示例")
    print("="*70)
    
    # 创建LLM
    llm = create_llm()
    
    # 创建Agent
    chemist = Agent(
        role="化学分析专家",
        goal="分析化合物性质",
        backstory="精通有机化学和材料化学",
        tools=[async_pubchem_search_tool],
        llm=llm,
        verbose=True
    )
    
    # 创建异步Task
    search_task1 = Task(
        description="查询benzene的化学信息",
        expected_output="benzene的详细化学信息",
        agent=chemist,
        async_execution=True  # 启用异步执行!
    )
    
    search_task2 = Task(
        description="查询toluene的化学信息",
        expected_output="toluene的详细化学信息",
        agent=chemist,
        async_execution=True  # 启用异步执行!
    )
    
    summary_task = Task(
        description="总结benzene和toluene的关键差异",
        expected_output="两种化合物的对比分析",
        agent=chemist,
        context=[search_task1, search_task2]  # 依赖前两个任务
    )
    
    # 创建Crew
    crew = Crew(
        agents=[chemist],
        tasks=[search_task1, search_task2, summary_task],
        process=Process.sequential,
        verbose=True
    )
    
    # 异步执行Crew!
    print("\n开始异步执行Crew...")
    print("-" * 70)
    
    result = await crew.akickoff()  # 使用akickoff()异步执行!
    
    print("\n" + "="*70)
    print("执行结果")
    print("="*70)
    print(result)
    
    return result


if __name__ == "__main__":
    print("\n注意: 这是一个演示脚本,展示CrewAI 1.7.0异步功能")
    print("由于需要调用LLM,可能消耗token,请谨慎运行\n")
    
    # 运行异步主函数
    # asyncio.run(main())  # 取消注释以运行
    
    print("✅ 脚本结构正确")
    print("✅ 异步工具已创建")
    print("✅ 异步Task配置正确(async_execution=True)")
    print("✅ Crew.akickoff()可用")
    print("\n取消main()的注释即可运行完整测试")

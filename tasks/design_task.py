#!/usr/bin/env python3
"""
材料设计任务
负责设计和优化水处理材料方案
"""

from tasks.base_task import BaseTask

class DesignTask(BaseTask):
    def __init__(self, llm):
        super().__init__(llm)

    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        description = """
        根据用户需求设计水处理材料方案。
        
        设计步骤：
        1. 分析目标污染物特性和处理要求
        2. 选择合适的材料类型（如单原子催化剂、双原子催化剂、MOF材料等）
        3. 优化材料结构参数以确保催化性能和稳定性
        4. 考虑材料多样性、结构稳定性、催化性能的平衡
        
        设计要点：
        - 确保材料具有良好的催化性能和结构稳定性
        - 优化材料的活性位点和反应路径
        - 满足目标污染物的降解需求
        """
        
        # 添加用户自定义需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        提供完整的材料设计方案，包括：
        1. 材料组成（材料类型和关键结构参数）
        2. 设计原理说明
        3. 稳定性保障措施
        4. 预期的催化性能
        """
        
        return super().create_task(agent, description, expected_output, context_task)
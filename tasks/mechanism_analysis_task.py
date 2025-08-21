#!/usr/bin/env python3
"""
机理分析任务
负责分析材料的催化机理和作用机制
"""

from tasks.base_task import BaseTask

class MechanismAnalysisTask(BaseTask):
    def __init__(self, llm):
        super().__init__(llm)

    def create_task(self, agent, context_task=None):
        description = """
        请基于最终验证通过的材料方案，进行深入的机理分析，包括：
        
        分析步骤：
        1. 微观结构机理：分析材料的原子级结构和电子特性
        2. 作用机理分析：解释材料如何催化降解目标污染物
        3. 构效关系：阐述材料结构与其性能之间的关系
        4. 界面作用机理：分析材料与污染物之间的界面相互作用
        5. 传质机理：分析反应过程中的质量和热量传递机制
        6. 稳定性机理：解释材料的稳定性和持久性机制
        7. 优化机理分析：提出材料性能优化的可能途径
        
        分析要点：
        - 重点关注材料的催化机制和反应路径
        - 详细解释材料结构如何影响其催化性能
        - 分析材料在实际应用中的表现机理
        """
        
        expected_output = """
        提供详细的机理分析报告，包括：
        1. 材料的微观结构机理
        2. 催化作用机理和反应路径
        3. 材料结构与性能的关系
        4. 界面作用和传质机制
        5. 稳定性机制分析
        6. 性能优化建议
        """
        
        return super().create_task(agent, description, expected_output, context_task)
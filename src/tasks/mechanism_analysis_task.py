#!/usr/bin/env python3
"""
机理分析任务
负责分析材料的催化机理和作用机制
"""

from .base_task import BaseTask

class MechanismAnalysisTask(BaseTask):
    """机理分析任务类 / Mechanism analysis task class"""
    
    def __init__(self, agent, material_info=""):
        """
        初始化机理分析任务 / Initialize mechanism analysis task
        
        Args:
            agent: 机理分析智能体 / Mechanism analysis agent
            material_info: 材料信息 / Material information
        """
        super().__init__(
            agent=agent,
            expected_output="污染物降解的反应机理和动力学特性分析报告",  # 污染物降解的反应机理和动力学特性分析报告 / Analysis report on reaction mechanisms and kinetic characteristics of pollutant degradation
            description=f"""分析目标污染物在催化剂作用下的降解机理和动力学特性。
            要求详细描述反应路径和关键中间体。
            {material_info}
            / Analyze the degradation mechanisms and kinetic characteristics of target pollutants under the action of catalysts.
            Describe the reaction pathways and key intermediates in detail.
            {material_info}"""
        )

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
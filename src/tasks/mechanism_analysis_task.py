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
        请基于最终验证通过的材料方案，进行深入的机理分析，必须包含以下所有分析维度：
        
        分析步骤：
        1. 微观结构机理：
           - 原子/分子结构：分析材料的原子排列、晶体结构和分子几何
           - 关键结构特征：识别活性位点、配位环境和结构基序
           - 配体作用：考察配体对电子结构和催化活性的影响
           - 金属-配体协同：分析金属中心与配体之间的协同效应
           
        2. 作用机理分析：
           - PMS活化催化过程：详细描述过氧单硫酸盐活化途径
           - 吸附：分析污染物在材料表面的吸附机制
           - 电子转移：阐述电子转移路径和氧化还原过程
           - 自由基介导：说明自由基物种在降解机制中的作用
           - 配体参与：分析配体在催化循环中的参与情况
           
        3. 构效关系：
           - 结构与催化性能的定量关系
           - 电子结构-活性相关性
           - 几何效应对反应性的影响
           
        4. 界面作用机理：
           - 固-液界面相互作用
           - 表面反应机制
           - 界面电子转移过程
           
        5. 传质和热传导机理：
           - 扩散过程和传输限制
           - 反应中的热量产生和耗散
           - 温度对反应动力学的影响
           
        6. 稳定性机理：
           - 反应条件下的结构稳定性
           - 抗浸出性和耐久性
           - 长期性能维持机制
           
        7. 优化机理分析：
           - 基于结构的优化策略
           - 性能增强机制
           - 合理设计原理
           
        8. 多尺度建模：
           - 量子、分子和介观尺度模型的整合
           - 跨尺度机制分析方法
           
        9. 关键影响因素：
           - pH、温度和离子强度的影响
           - 竞争离子和有机物的影响
           - 反应介质的影响
           
        10. 机理验证方案：
            - 计算验证方法
            - 实验验证方法
            - 与数据库信息的交叉验证
        
        分析要点：
        - 必须覆盖所有10个分析维度，不能遗漏
        - 重点关注材料的催化机制和反应路径
        - 详细解释材料结构如何影响其催化性能
        - 分析材料在实际应用中的表现机理
        - 结合Materials Project和PubChem工具数据进行验证
        """
        
        expected_output = """
        提供详细的机理分析报告，必须包含以下所有维度：

        1. 微观结构机理
           * 原子/分子结构
           * 关键结构特征
           * 配体作用
           * 金属-配体协同

        2. 作用机理分析
           * PMS活化催化过程
           * 吸附机制
           * 电子转移
           * 自由基介导
           * 配体参与

        3. 构效关系

        4. 界面作用机理

        5. 传质和热传导机理

        6. 稳定性机理

        7. 优化机理分析

        8. 多尺度建模

        9. 关键影响因素

        10. 机理验证方案

        并提供性能预测和基于工具数据的验证结果。
        """
        
        # 创建新的任务实例而不是调用父类方法
        from crewai import Task
        task = Task(
            agent=agent,
            expected_output=expected_output,
            description=description
        )
        
        # 如果有上下文任务，添加依赖关系
        if context_task:
            task.context = [context_task]
            
        return task
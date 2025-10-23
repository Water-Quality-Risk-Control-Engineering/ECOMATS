#!/usr/bin/env python3
"""
合成方法任务
负责设计材料的合成方法和工艺流程
"""

from src.tasks.base_task import BaseTask

class SynthesisMethodTask(BaseTask):
    def __init__(self, llm):
        super().__init__(llm)

    def create_task(self, agent, context_task=None):
        description = """
        请基于最终验证通过的材料方案，设计详细的合成方法和工艺流程：
        
        设计步骤：
        1. 合成策略设计：根据材料的结构参数设计合成路线
        2. 合成步骤细化：明确每个合成步骤的具体操作
        3. 工艺参数优化：确定关键工艺参数的数值范围
        4. 设备和安全要求：列出所需的设备和安全措施
        5. 质量控制指标：确定关键质量控制点和表征方法
        
        设计要点：
        - 确保合成方法的可行性和可重复性
        - 优化工艺参数以获得最佳材料性能
        - 考虑工业化生产的可行性和成本控制
        """
        
        expected_output = """
        提供完整的合成方法方案，包括：
        1. 详细的合成策略和路线设计
        2. 具体的合成步骤和操作条件
        3. 关键工艺参数及其控制范围
        4. 所需设备和安全要求
        5. 质量控制指标和表征方法
        """
        
        return super().create_task(agent, description, expected_output, context_task)
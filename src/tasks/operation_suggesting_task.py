#!/usr/bin/env python3
"""
操作建议任务
负责提供材料合成、生产和应用的详细操作建议
"""

from .base_task import BaseTask

class OperationSuggestingTask(BaseTask):
    """运行建议任务类 / Operation suggestion task class"""
    
    def __init__(self, agent, material_info=""):
        """
        初始化运行建议任务 / Initialize operation suggestion task
        
        Args:
            agent: 运行建议智能体 / Operation suggestion agent
            material_info: 材料信息 / Material information
        """
        super().__init__(
            agent=agent,
            expected_output="水处理工艺的运行参数建议和优化策略",  # 水处理工艺的运行参数建议和优化策略 / Operational parameter recommendations and optimization strategies for water treatment processes
            description=f"""为基于催化剂的水处理工艺提供运行参数建议和优化策略。
            包括pH值、温度、催化剂投加量等关键参数。
            {material_info}
            / Provide operational parameter recommendations and optimization strategies for catalyst-based water treatment processes.
            Include key parameters such as pH, temperature, and catalyst dosage.
            {material_info}"""
        )

    def create_task(self, agent, context_task=None):
        description = """
        请基于最终验证通过的材料方案和合成方法，提供详细的操作建议：
        
        建议内容：
        1. 合成操作指导：提供详细的分步合成操作指导
        2. 工艺参数控制：明确关键工艺参数的控制方法和范围
        3. 质量控制措施：制定详细的质量控制和检测方案
        4. 安全操作规范：列出安全操作要点和应急处理措施
        5. 设备维护建议：提供设备使用和维护建议
        
        建议要点：
        - 确保操作建议的实用性和可操作性
        - 详细说明每个步骤的关键控制点
        - 提供常见问题的解决方案
        - 考虑工业化生产的实际条件
        """
        
        expected_output = """
        提供完整的操作建议方案，包括：
        1. 详细的分步操作指导
        2. 关键工艺参数控制方法
        3. 质量控制和检测方案
        4. 安全操作规范和应急措施
        5. 设备使用和维护建议
        """
        
        return super().create_task(agent, description, expected_output, context_task)
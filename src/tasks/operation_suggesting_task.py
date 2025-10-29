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
        请基于最终验证通过的材料方案，提供详细的操作建议，重点分为实验室初试和中试级别两个部分：
        
        1. 实验室初试操作建议
        1.1 实验安全性：
            - 评估实验使用设备是否包含高压、高温、蒸汽等危险条件
            - 评估材料毒性及环境危害，使用工具查询化学品安全数据
        1.2 实验参数：
            - 确定反应器体积，活性物质用量，pH值，温度等关键参数
            - 确定搅拌环境（传质）要求
            - 明确催化剂的使用量及使用方式（直接投加/合成电极/合成膜材料等）
        1.3 污染物检测：
            - 如有污染物，给出推荐的多种检测方法（根据不同仪器的检测限给出推荐）
            - 给出降解实验预计的时间（尽量谨慎）
        
        2. 中试级别操作建议
        2.1 经济性分析：
            - 分析材料、反应的应用经济性
            - 评估能耗情况
        2.2 环境影响：
            - 如果环境影响高，给出降低环境影响的具体建议
        2.3 基质影响：
            - 考虑基质对材料性能和稳定性的影响
        
        要求：
        - 重点关注操作安全性和可行性
        - 使用工具验证所有化学品信息
        - 提供具体的参数范围和控制方法
        - 考虑实际应用中的各种影响因素
        """
        
        expected_output = """
        提供完整的操作建议方案，按照以下结构组织：
        
        1. 实验室初试操作建议
        1.1 实验安全性评估（设备危险性、材料毒性、环境危害）
        1.2 实验参数确定（反应器体积、活性物质用量、pH、温度、搅拌环境、催化剂使用方式等）
        1.3 污染物检测方案（检测方法推荐、降解实验时间预估）
        
        2. 中试级别操作建议
        2.1 应用经济性分析（材料成本、反应经济性、能耗评估）
        2.2 环境影响评估及降低建议
        2.3 基质影响考虑
        
        要求：
        - 使用工具验证所有化学品信息
        - 提供具体的数据支持和参数范围
        - 给出明确的操作指导和注意事项
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
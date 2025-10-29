#!/usr/bin/env python3
"""
材料设计任务
负责设计和优化水处理材料方案
"""

from .base_task import BaseTask

class DesignTask(BaseTask):
    """材料设计任务类 / Material design task class"""
    
    def __init__(self, agent):
        """
        初始化材料设计任务 / Initialize material design task
        
        Args:
            agent: 材料设计智能体 / Material design agent
        """
        super().__init__(
            agent=agent,
            expected_output="设计出的10种催化剂材料的详细信息，包括材料结构、合成方法等",  # 设计出的10种催化剂材料的详细信息，包括材料结构、合成方法等 / Detailed information of the 10 designed catalyst materials, including material structure, synthesis methods, etc.
            description="""基于用户需求和污染物特性，设计10种催化PMS活化的催化剂材料。
            要求给出每种材料的详细结构信息和具体的合成方法。
            / Based on user requirements and pollutant characteristics, design 10 catalyst materials for PMS activation.
            Provide detailed structural information and specific synthesis methods for each material."""
        )
    
    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        description = """
        根据用户需求设计水处理材料方案。
        
        设计步骤：
        1. 分析目标污染物特性和处理要求
        2. 选择合适的材料类型（如单原子催化剂、双原子催化剂、MOF材料等）
        3. 设计材料结构
        4. **强制使用Structure Validator工具验证设计的材料结构是否真实存在**
        5. 如果验证失败，需要重新设计
        6. 优化材料结构参数以确保催化性能和稳定性
        7. 考虑材料多样性、结构稳定性、催化性能的平衡
        
        设计要点：
        - 确保材料具有良好的催化性能和结构稳定性
        - 优化材料的活性位点和反应路径
        - 满足目标污染物的降解需求
        - **必须验证设计的材料结构在现实中是否存在**
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
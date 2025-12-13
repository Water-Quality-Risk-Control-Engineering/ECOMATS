#!/usr/bin/env python3
"""
增强型最终验证任务 / Enhanced Final Validation Task
综合各专家评估结果，进行加权计算并形成最终材料评估报告，同时提供改进建议
"""

from .base_task import BaseTask, load_task_text


class EnhancedFinalValidationTask(BaseTask):
    """增强型最终验证任务类 / Enhanced final validation task class"""
    
    def __init__(self, agent, evaluation_results=""):
        """
        初始化增强型最终验证任务 / Initialize enhanced final validation task
        
        Args:
            agent: 增强型最终验证智能体 / Enhanced final validation agent
            evaluation_results: 各专家的评估结果 / Evaluation results from various experts
        """
        # 加载任务文本 / Load task text
        task_text = load_task_text('enhanced_final_validation_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '')
        )

    def create_task(self, agent, context_task=None):
        # 加载任务文本 / Load task text from file
        task_text = load_task_text('enhanced_final_validation_task')
        
        description = task_text.get('description', '')
        expected_output = task_text.get('expected_output', '')
        
        # 创建任务实例 / Create task instance
        from crewai import Task
        task = Task(
            agent=agent,
            expected_output=expected_output,
            description=description
        )
        
        # 如果有上下文任务，添加依赖关系 / Add context dependency
        if context_task:
            if isinstance(context_task, list):
                task.context = context_task
            else:
                task.context = [context_task]
            
        return task
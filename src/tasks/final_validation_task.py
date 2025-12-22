#!/usr/bin/env python3
"""
最终验证任务 / Final Validation Task
"""

from .base_task import BaseTask, load_task_text


class FinalValidationTask(BaseTask):
    """最终验证任务类 / Final validation task class"""
    
    def __init__(self, agent, evaluation_results=""):
        """
        初始化最终验证任务 / Initialize final validation task
        
        Args:
            agent: 最终验证智能体 / Final validation agent
            evaluation_results: 各专家的评估结果 / Evaluation results from various experts
        """
        # 加载任务文本 / Load task text
        task_text = load_task_text('final_validation_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '')
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
        # 加载任务文本 / Load task text from file
        task_text = load_task_text('final_validation_task')
        
        description = task_text.get('description', '')
        expected_output = task_text.get('expected_output', '')
        user_req_prefix = task_text.get('user_requirement_prefix', '\n\nUser Requirement: ')
        
        # 添加用户自定义需求到描述中 / Add user requirement to description
        if user_requirement:
            description += f"{user_req_prefix}{user_requirement}"
        
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

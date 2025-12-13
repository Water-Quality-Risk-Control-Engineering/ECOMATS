#!/usr/bin/env python3
"""
材料设计任务 / Material Design Task
负责设计和优化水处理材料方案
"""

from .base_task import BaseTask, load_task_text


class DesignTask(BaseTask):
    """材料设计任务类 / Material design task class"""
    
    def __init__(self, agent):
        """
        初始化材料设计任务 / Initialize material design task
        
        Args:
            agent: 材料设计智能体 / Material design agent
        """
        # 加载任务文本 / Load task text
        task_text = load_task_text('design_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '')
        )
    
    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        # 加载任务文本 / Load task text from file
        task_text = load_task_text('design_task')
        
        description = task_text.get('description', '')
        expected_output = task_text.get('expected_output', '')
        user_req_prefix = task_text.get('user_requirement_prefix', '\n\nUser Requirement: ')
        feedback_prefix = task_text.get('feedback_prefix', '\n\nFeedback:\n')
        
        # 添加用户自定义需求到描述中 / Add user requirement to description
        if user_requirement:
            description += f"{user_req_prefix}{user_requirement}"
        
        if feedback:
            description += f"{feedback_prefix}{feedback}"
        
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

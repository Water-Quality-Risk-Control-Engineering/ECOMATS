#!/usr/bin/env python3
"""
操作建议任务 / Operation Suggesting Task
负责提供材料合成、生产和应用的详细操作建议
"""

from .base_task import BaseTask, load_task_text


class OperationSuggestingTask(BaseTask):
    """运行建议任务类 / Operation suggestion task class"""
    
    def __init__(self, agent, material_info=""):
        """
        初始化运行建议任务 / Initialize operation suggestion task
        
        Args:
            agent: 运行建议智能体 / Operation suggestion agent
            material_info: 材料信息 / Material information
        """
        # 加载任务文本 / Load task text
        task_text = load_task_text('operation_suggesting_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '')
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
        # 加载任务文本 / Load task text from file
        task_text = load_task_text('operation_suggesting_task')
        
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
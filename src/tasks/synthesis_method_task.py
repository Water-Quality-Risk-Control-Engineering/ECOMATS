#!/usr/bin/env python3
"""
合成方法任务 / Synthesis Method Task
负责设计材料的合成方法和工艺流程
"""

from .base_task import BaseTask, load_task_text


class SynthesisMethodTask(BaseTask):
    """合成方法任务类 / Synthesis method task class"""
    
    def __init__(self, agent, material_info=""):
        """
        初始化合成方法任务 / Initialize synthesis method task
        
        Args:
            agent: 合成方法智能体 / Synthesis method agent
            material_info: 材料信息 / Material information
        """
        # 加载任务文本 / Load task text
        task_text = load_task_text('synthesis_method_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '') + f"\n{material_info}" if material_info else task_text.get('description', '')
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
        # 加载任务文本 / Load task text from file
        task_text = load_task_text('synthesis_method_task')
        
        description = task_text.get('description', '')
        expected_output = task_text.get('expected_output', '')
        user_req_prefix = task_text.get('user_requirement_prefix', '\n\nUser Requirement: ')
        
        # 添加用户需求到描述中 / Add user requirement to description
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

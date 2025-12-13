#!/usr/bin/env python3
"""
材料评价任务 / Material Evaluation Task
基于催化性能、经济可行性、环境友好性、技术可行性和结构合理性五个维度进行评价
"""

from .base_task import BaseTask, load_task_text


class EvaluationTask(BaseTask):
    """材料评估任务类 / Material evaluation task class"""
    
    def __init__(self, agent, material_info=""):
        """
        初始化材料评估任务 / Initialize material evaluation task
        
        Args:
            agent: 材料评估智能体 / Material evaluation agent
            material_info: 待评估的材料信息 / Material information to be evaluated
        """
        # 加载任务文本 / Load task text
        task_text = load_task_text('evaluation_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '') + f"\n{material_info}" if material_info else task_text.get('description', '')
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
        # 加载任务文本 / Load task text from file
        task_text = load_task_text('evaluation_task')
        
        description = task_text.get('description', '')
        expected_output = task_text.get('expected_output', '')
        user_req_prefix = task_text.get('user_requirement_prefix', '\n\nUser Requirement: ')
        
        # 如果有用户需求，添加到描述中 / Add user requirement to description
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

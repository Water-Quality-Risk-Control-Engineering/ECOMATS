#!/usr/bin/env python3
"""
Material Evaluation Task
"""

from .base_task import BaseTask, load_task_text


class EvaluationTask(BaseTask):
    """ Material evaluation task class"""
    
    def __init__(self, agent, material_info=""):
        """
        Initialize material evaluation task
        
        Args:
            agent: Material evaluation agent
            material_info: Material information to be evaluated
        """
        # Load task text
        task_text = load_task_text('evaluation_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '') + f"\n{material_info}" if material_info else task_text.get('description', '')
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
        # Load task text from file
        task_text = load_task_text('evaluation_task')
        
        description = task_text.get('description', '')
        expected_output = task_text.get('expected_output', '')
        user_req_prefix = task_text.get('user_requirement_prefix', '\n\nUser Requirement: ')
        
        # Add user requirement to description
        if user_requirement:
            description += f"{user_req_prefix}{user_requirement}"
        
        # Create task instance
        from crewai import Task
        task = Task(
            agent=agent,
            expected_output=expected_output,
            description=description
        )
        
        # Add context dependency
        if context_task:
            if isinstance(context_task, list):
                task.context = context_task
            else:
                task.context = [context_task]
            
        return task

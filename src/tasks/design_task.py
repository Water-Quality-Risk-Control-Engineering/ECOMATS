#!/usr/bin/env python3
"""
Material Design Task
Responsible for designing and optimizing water treatment material solutions
"""

from .base_task import BaseTask, load_task_text


class DesignTask(BaseTask):
    """ Material design task class"""
    
    def __init__(self, agent):
        """
         Initialize material design task
        
        Args:
            agent: Material design agent
        """
        # Load task text
        task_text = load_task_text('design_task')
        
        super().__init__(
            agent=agent,
            expected_output=task_text.get('expected_output', ''),
            description=task_text.get('description', '')
        )
    
    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        # Load task text from file
        task_text = load_task_text('design_task')
        
        description = task_text.get('description', '')
        expected_output = task_text.get('expected_output', '')
        user_req_prefix = task_text.get('user_requirement_prefix', '\n\nUser Requirement: ')
        feedback_prefix = task_text.get('feedback_prefix', '\n\nFeedback:\n')
        
        # Add user requirement to description
        if user_requirement:
            description += f"{user_req_prefix}{user_requirement}"
        
        if feedback:
            description += f"{feedback_prefix}{feedback}"
        
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

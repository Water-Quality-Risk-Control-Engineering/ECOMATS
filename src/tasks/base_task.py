#!/usr/bin/env python3
"""
 Base Task Class
"""

import os
import yaml
from crewai import Task


def get_language():
    """ Get current language setting"""
    try:
        from src.config.config import Config
        return getattr(Config, 'LANGUAGE', 'zh')
    except Exception:
        return 'zh'


def is_english():
    """ Check if English mode"""
    return get_language() == 'en'


def load_task_text(task_name):
    """
     Load task text from file
    
    Args:
        task_name:  ( Examples 'design_task', 'evaluation_task')
    
    Returns:
        dict: contains description, expected_output, user_requirement_prefix 
    """
    lang = get_language()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
   
    yaml_path = os.path.join(current_dir, '..', 'locales', lang, 'tasks', f'{task_name}.yaml')
    
   
    if not os.path.exists(yaml_path):
        yaml_path = os.path.join(current_dir, '..', 'locales', 'zh', 'tasks', f'{task_name}.yaml')
    
    
    if not os.path.exists(yaml_path):
        return {}
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Failed to load task text from {yaml_path}: {e}")
        return {}

class BaseTask:
    """ Base task class"""
    
    def __init__(self, agent, expected_output, description):
        """
         Initialize base task
        
        Args:
            agent: Agent responsible for executing the task
            expected_output: Expected output format
            description: Task description
        """
        self.agent = agent
        self.expected_output = expected_output
        self.description = description
    
    def create_task(self):
        """ Create and return task instance"""
        return Task(
            agent=self.agent,
            expected_output=self.expected_output,
            description=self.description
        )

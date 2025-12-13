#!/usr/bin/env python3
"""
基础任务类 / Base Task Class
提供任务创建的通用功能
"""

import os
import yaml
from crewai import Task


def get_language():
    """获取当前语言设置 / Get current language setting"""
    try:
        from src.config.config import Config
        return getattr(Config, 'LANGUAGE', 'zh')
    except Exception:
        return 'zh'


def is_english():
    """检查是否为英文模式 / Check if English mode"""
    return get_language() == 'en'


def load_task_text(task_name):
    """
    从文件加载任务文本 / Load task text from file
    
    Args:
        task_name: 任务名称 (如 'design_task', 'evaluation_task')
    
    Returns:
        dict: 包含 description, expected_output, user_requirement_prefix 等字段
    """
    lang = get_language()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建文件路径
    yaml_path = os.path.join(current_dir, '..', 'locales', lang, 'tasks', f'{task_name}.yaml')
    
    # 如果当前语言文件不存在，回退到中文
    if not os.path.exists(yaml_path):
        yaml_path = os.path.join(current_dir, '..', 'locales', 'zh', 'tasks', f'{task_name}.yaml')
    
    # 如果文件仍不存在，返回空字典
    if not os.path.exists(yaml_path):
        return {}
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Failed to load task text from {yaml_path}: {e}")
        return {}

class BaseTask:
    """基础任务类 / Base task class"""
    
    def __init__(self, agent, expected_output, description):
        """
        初始化基础任务 / Initialize base task
        
        Args:
            agent: 负责执行任务的智能体 / Agent responsible for executing the task
            expected_output: 期望的输出格式 / Expected output format
            description: 任务描述 / Task description
        """
        self.agent = agent
        self.expected_output = expected_output
        self.description = description
    
    def create_task(self):
        """创建并返回任务实例 / Create and return task instance"""
        return Task(
            agent=self.agent,
            expected_output=self.expected_output,
            description=self.description
        )

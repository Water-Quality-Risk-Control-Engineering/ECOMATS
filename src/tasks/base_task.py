#!/usr/bin/env python3
"""
基础任务类
提供任务创建的通用功能
"""

from crewai import Task

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

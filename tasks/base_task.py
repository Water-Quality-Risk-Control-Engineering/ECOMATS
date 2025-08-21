#!/usr/bin/env python3
"""
基础任务类
提供任务创建的通用功能
"""

from crewai import Task

class BaseTask:
    """基础任务类，提供通用的任务创建功能"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def create_task(self, agent, description, expected_output, context_task=None):
        """
        创建任务的通用方法
        
        Args:
            agent: 执行任务的智能体
            description: 任务描述
            expected_output: 期望的输出
            context_task: 上下文任务（可选）
            
        Returns:
            Task: 创建的任务实例
        """
        task_params = {
            'description': description.strip(),
            'expected_output': expected_output.strip(),
            'agent': agent,
            'verbose': True
        }
        
        # 处理上下文任务
        if context_task:
            if isinstance(context_task, list):
                # 如果是任务列表，直接使用
                task_params['context'] = context_task
            else:
                # 如果是单个任务，放入列表中
                task_params['context'] = [context_task]
        
        return Task(**task_params)
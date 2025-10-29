#!/usr/bin/env python3
"""
增强型最终验证任务
综合各专家评估结果，进行加权计算并形成最终材料评估报告，同时提供改进建议
"""

from .base_task import BaseTask

class EnhancedFinalValidationTask(BaseTask):
    """增强型最终验证任务类 / Enhanced final validation task class"""
    
    def __init__(self, agent, evaluation_results=""):
        """
        初始化增强型最终验证任务 / Initialize enhanced final validation task
        
        Args:
            agent: 增强型最终验证智能体 / Enhanced final validation agent
            evaluation_results: 各专家的评估结果 / Evaluation results from various experts
        """
        super().__init__(
            agent=agent,
            expected_output="综合各专家评估结果的最终材料筛选建议和排序，包含改进建议",  # 综合各专家评估结果的最终材料筛选建议和排序，包含改进建议 / Final material screening recommendations and ranking based on comprehensive evaluation results from various experts, including improvement suggestions
            description=f"""综合各评估专家的结果，给出最终的材料筛选建议和排序。
            要求明确指出最优的几种材料及其优势，并在验证结果不佳时提供具体的改进建议。
            {evaluation_results}
            / Synthesize the results from various evaluation experts and provide final material screening recommendations and rankings.
            Clearly identify the optimal materials and their advantages, and provide specific improvement suggestions when validation results are unsatisfactory.
            {evaluation_results}"""
        )

    def create_task(self, agent, context_task=None):
        description = """
        请综合各专家评估结果，进行加权计算并形成最终材料评估报告：
        
        处理步骤：
        1. 收集并分析专家A、B、C的评估结果
        2. 计算各维度的平均分和标准差
        3. 应用一致性系数调整最终得分
        4. 根据加权公式计算综合得分
        5. 确定材料的最终排名
        6. **使用Structure Validator工具对最终排名靠前的材料进行结构验证**
        
        加权计算公式：
        最终得分 = 0.50×催化性能 + 0.10×经济可行性 + 0.10×环境友好性 + 0.10×技术可行性 + 0.20×结构合理性
        
        一致性分析要求：
        1. 计算每个维度在三个专家评分中的标准差
        2. 识别评分差异较大的维度并分析原因
        3. 计算一致性系数 Cj = 1 - (SD/mean)
        4. 应用一致性系数调整最终得分
        
        排名确定规则：
        - Excellent: 所有维度≥8且综合得分≥8.0
        - Good: 所有维度≥6且综合得分≥6.0
        - Average: 综合得分≥4.0
        - Poor: 综合得分≥2.0
        - Invalid: 任一维度=1或综合得分<2.0
        
        改进建议要求（重要）：
        1. 如果最终排名为Poor或Invalid，必须提供具体的改进建议
        2. 改进建议应针对评分最低的维度
        3. 提供可操作的设计修改指导
        4. 包括材料结构、合成方法或性能优化的具体建议
        
        输出要求：
        1. 显示详细的计算过程
        2. 提供一致性分析结果
        3. 给出最终排名和综合得分
        4. 提供具体的改进建议（如果需要）
        5. **对排名前3的材料使用Structure Validator工具验证其结构真实性**
        """
        
        expected_output = """
        提供完整的最终验证报告，包括：
        1. 各专家评分汇总
        2. 平均分和标准差计算
        3. 一致性分析结果
        4. 加权计算过程和最终得分
        5. 最终排名确定
        6. 具体的改进建议（如果最终排名为Poor或Invalid）
        """
        
        # 创建新的任务实例而不是调用父类方法
        from crewai import Task
        task = Task(
            agent=agent,
            expected_output=expected_output,
            description=description
        )
        
        # 如果有上下文任务，添加依赖关系
        if context_task:
            if isinstance(context_task, list):
                task.context = context_task
            else:
                task.context = [context_task]
            
        return task
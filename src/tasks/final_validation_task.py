#!/usr/bin/env python3
"""
最终验证任务
综合各专家评估结果，进行加权计算并形成最终材料评估报告
"""

from .base_task import BaseTask

class FinalValidationTask(BaseTask):
    """最终验证任务类 / Final validation task class"""
    
    def __init__(self, agent, evaluation_results=""):
        """
        初始化最终验证任务 / Initialize final validation task
        
        Args:
            agent: 最终验证智能体 / Final validation agent
            evaluation_results: 各专家的评估结果 / Evaluation results from various experts
        """
        super().__init__(
            agent=agent,
            expected_output="综合各专家评估结果的最终材料筛选建议和排序",  # 综合各专家评估结果的最终材料筛选建议和排序 / Final material screening recommendations and ranking based on comprehensive evaluation results from various experts
            description=f"""综合各评估专家的结果，给出最终的材料筛选建议和排序。
            要求明确指出最优的几种材料及其优势。
            {evaluation_results}
            / Synthesize the results from various evaluation experts and provide final material screening recommendations and rankings.
            Clearly identify the optimal materials and their advantages.
            {evaluation_results}"""
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
        description = """
        请综合各专家评估结果，进行加权计算并形成最终材料评估报告：
        
        处理步骤：
        1. 收集并分析专家A、B、C的评估结果
        2. 计算各维度的平均分和标准差
        3. 应用一致性系数调整最终得分
        4. 根据加权公式计算综合得分
        5. 确定材料的最终排名
        6. **使用Structure Validator工具对最终排名靠前的材料进行结构验证**
        
        工具使用策略：
        1. **专家数据验证阶段**：
           - 首先验证各专家评估结果中引用的工具数据是否真实存在
           - 检查所有MP-ID、CAS号等数据库标识符的有效性
           - 对于专家提供的工具查询结果，使用相同工具进行独立验证
           - 标记任何无法验证或明显错误的数据
        
        2. **材料结构验证阶段**：
           - 对排名前5的材料，逐一调用Structure Validator Tool验证结构真实性
           - 对于金属材料，同时调用Materials Project工具进行交叉验证
           - 对于有机材料，同时调用PubChem工具进行交叉验证
           - 记录所有验证工具的查询参数和返回结果
           - 对无法验证的材料进行特别标注并影响最终排名
        
        3. **数据一致性分析阶段**：
           - 使用Data Validator Tool验证各专家评分数据的一致性
           - 计算每个维度在三个专家评分中的标准差和变异系数
           - 识别评分差异较大的维度并分析原因
           - 对一致性差的维度进行重点关注和重新评估
        
        4. **综合验证阶段**：
           - 对所有工具验证结果进行综合分析
           - 识别并标记任何编造或不一致的数据
           - 验证材料性能数据的合理性和可信度
           - 确保最终排名基于真实的工具验证数据
        
        5. **改进建议数据支持阶段**：
           - 对于排名较低的材料，调用相关工具获取改进建议的数据支持
           - 查询类似优化材料的性能数据
           - 提供基于工具数据的具体改进方向
           - 确保改进建议的可行性和科学性
        
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
        
        输出要求：
        1. 显示详细的计算过程
        2. 提供一致性分析结果
        3. 给出最终排名和综合得分
        4. 提供具体的改进建议
        5. **对排名前3的材料使用Structure Validator工具验证其结构真实性**
        6. 详细记录所有工具调用的参数和结果
        7. 明确标识任何发现的编造或不一致数据
        8. **如果Materials Project工具未返回有效的material_id，不得进行推断或生成虚假的MP-ID**
        """
        
        # 添加用户需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        expected_output = """
        提供完整的最终验证报告，包括：
        1. 各专家评分汇总
        2. 平均分和标准差计算
        3. 一致性分析结果
        4. 加权计算过程和最终得分
        5. 最终排名确定
        6. 具体的改进建议
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

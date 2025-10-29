#!/usr/bin/env python3
"""
材料评价任务
基于催化性能、经济可行性、环境友好性、技术可行性和结构合理性五个维度进行评价
"""

from .base_task import BaseTask

class EvaluationTask(BaseTask):
    """材料评估任务类 / Material evaluation task class"""
    
    def __init__(self, agent, material_info=""):
        """
        初始化材料评估任务 / Initialize material evaluation task
        
        Args:
            agent: 材料评估智能体 / Material evaluation agent
            material_info: 待评估的材料信息 / Material information to be evaluated
        """
        super().__init__(
            agent=agent,
            expected_output="对材料的评估结果，包括各项性能指标和综合评分",  # 对材料的评估结果，包括各项性能指标和综合评分 / Evaluation results of the material, including various performance indicators and comprehensive scores
            description=f"""对设计的催化剂材料进行专业评估。
            评估内容包括材料的化学稳定性、环境安全性等指标。
            {material_info}
            / Conduct professional evaluation of the designed catalyst materials.
            The evaluation includes indicators such as chemical stability and environmental safety of the materials.
            {material_info}"""
        )

    def create_task(self, agent, context_task=None):
        description = """
        请根据以下五个维度评估材料方案的性能：
        1. 催化性能（权重50%）
        2. 经济可行性（权重10%）
        3. 环境友好性（权重10%）
        4. 技术可行性（权重10%）
        5. 结构合理性（权重20%）
        
        其中，催化性能是核心标准。
        
        评估步骤：
        1. 分析材料方案在上述五个维度的表现
        2. 重点关注催化性能是否达到标准
        3. 如果催化性能不符合标准，请明确指出问题并建议返回材料设计阶段重新设计
        4. 如果催化性能达标，再综合评估其他维度
        
        工具使用要求（必须遵守）：
        - 使用Materials Project工具验证金属材料的物理化学性质（如带隙、密度、形成能等）
        - 使用PubChem工具验证有机污染物或配体的分子结构和性质
        - 使用name2properties_tool或formula2properties_tool验证材料关键组分的性质
        - 使用pnec_tool评估材料的环境安全性
        - **使用Structure Validator工具验证材料结构是否真实存在**
        - 所有工具查询结果必须在评估中引用，并作为评分依据
        
        评估要求：
        - 请独立进行评估，不要参考其他专家的评分
        - 重点关注材料的科学合理性和实际应用潜力
        - 对于明显不合理的材料设计，请在结构合理性维度给出低分
        - 必须使用工具验证材料信息的准确性
        - **必须验证材料结构在现实中是否存在**
        
        评估结果输出格式：
        1. 各维度评分（满分10分）：
           - 催化性能: [评分] (核心标准)
           - 经济可行性: [评分]
           - 环境友好性: [评分]
           - 技术可行性: [评分]
           - 结构合理性: [评分]
        
        2. 核心标准评估：
           - 催化性能: [达标/不达标]
        
        3. 综合评价：
           - 如果核心标准不达标: 返回重新设计，并说明原因
           - 如果核心标准达标: 继续进行其他维度评估并给出总体建议
           
        4. 工具验证结果：
           - Materials Project查询结果：[具体数据]
           - PubChem查询结果：[具体数据]
           - Structure Validator验证结果：[材料是否存在]
           - 其他工具查询结果：[具体数据]
           - 工具数据如何支持评分决定：[说明]
        """
        
        expected_output = """
        提供详细的材料方案评价报告，包括：
        1. 各维度评分和分析
        2. 核心标准评估结果
        3. 明确的决策建议（通过或返回重新设计）
        4. 如果需要重新设计，提供具体的改进建议
        5. 工具验证结果（必须包含具体的数据和查询结果）
        6. 工具数据如何支持评分决定的详细说明
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
            task.context = [context_task]
            
        return task
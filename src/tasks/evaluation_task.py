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
            expected_output="对材料方案的全面评估报告，包含五个维度的评分（1-10分）以及具体的优势和改进建议。评估必须基于上游设计智能体提供的详细信息，不得进行独立数据库查询。",
            description=f"根据以下由设计智能体提供的材料信息进行评估:\n{material_info}\n\n请从催化性能、经济可行性、环境友好性、技术可行性和结构合理性五个维度进行全面评价。"
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
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
        
        工具使用策略：
        1. **数据收集阶段**：
           - 调用Material Identifier Tool确定待评估材料的类型
           - 调用Structure Validator Tool验证材料结构是否存在
           - 记录所有工具调用的参数和初步结果
        
        2. **结构合理性验证阶段**：
           - 对于所有材料：调用Structure Validator Tool验证材料结构是否存在
           - 对于金属材料：调用Materials Project工具查询晶体结构参数、稳定性数据和关键属性
           - 对于有机材料：调用PubChem工具验证分子结构和获取基础化学信息
           - **必须明确记录Materials Project返回的material_id，如果未返回有效material_id，则记录为"未验证"**
           - **不得使用任何未经过Materials Project工具验证的MP-ID**
           - 记录验证结果，对无法验证的材料在结构合理性维度给予低分
        
        3. **催化性能评估阶段**：
           - 调用Material Search Tool查询类似材料的催化性能数据（如TOC去除率、k值等）
           - 调用Name2Properties Tool或Formula2Properties Tool获取材料关键组分的性质参数
           - 结合工具数据定量评估材料的PMS活化效率、反应速率等指标
           - 如果工具调用失败，必须说明对评估的影响
        
        4. **经济可行性评估阶段**：
           - 调用Materials Project工具获取材料成本相关数据（如元素丰度、市场价格趋势）
           - 调用PubChem工具查询原材料的可获得性和价格信息
           - 调用Name2Properties Tool获取关键组分的市场信息
           - 基于工具数据评估材料的经济可行性
        
        5. **环境友好性评估阶段**：
           - 调用PNEC Tool评估材料的环境安全阈值和生态风险
           - 调用PubChem工具查询材料组分的毒性数据和环境危害信息
           - 评估材料的生物降解潜力和环境影响
           - 综合工具数据给出环境友好性评分
        
        6. **技术可行性评估阶段**：
           - 调用Material Search Tool查询材料的合成方法和工艺成熟度
           - 调用PubChem工具验证原材料的可获得性
           - 评估工业化生产和实际应用的可行性
           - 基于工具数据评估技术可行性
        
        7. **数据验证阶段**：
           - 对所有工具查询结果进行交叉验证
           - 识别和标记任何不一致或可疑的数据
           - 确保评分基于真实可靠的工具数据
           - **如果任何工具调用失败或返回错误信息，必须在评估报告中明确说明，并在相应维度给出保守评分**
           - **对于关键工具（如Structure Validator Tool、Materials Project Tool）调用失败的情况，结构合理性维度评分不得超过2分**
        
        评估要求：
        - 请独立进行评估，不要参考其他专家的评分
        - 重点关注材料的科学合理性和实际应用潜力
        - 对于明显不合理的材料设计，请在结构合理性维度给出低分
        - 必须使用工具验证材料信息的准确性
        - **必须验证材料结构在现实中是否存在**
        - **如果Materials Project工具未返回有效的material_id，必须明确说明此情况，并在评估中将其视为未验证的材料**
        - **在没有有效material_id的情况下，不得进行推断或生成虚假的MP-ID，应基于理论分析和已知的材料科学原理进行评估**
        - **对于任何未验证的材料，结构合理性维度评分不得超过3分**
        - 每个工具调用都必须记录具体的参数和返回结果
        - 如果工具调用失败，必须明确说明失败原因和对评估的影响
        - **如果关键工具（如Structure Validator Tool）调用失败或返回否定结果，必须在相应维度给出低分（≤3分）**
        
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
           - Materials Project查询结果：[具体数据，包括查询参数和返回结果]
           - PubChem查询结果：[具体数据，包括化合物CID和关键属性]
           - Structure Validator验证结果：[材料是否存在，验证依据]
           - 其他工具查询结果：[具体数据]
           - 工具数据如何支持评分决定：[详细说明每个工具数据如何影响评分]
        """
        
        expected_output = """
        提供详细的材料方案评价报告，包括：
        1. 各维度评分和分析
        2. 核心标准评估结果
        3. 明确的决策建议（通过或返回重新设计）
        4. 如果需要重新设计，提供具体的改进建议
        5. 工具验证结果（必须包含具体的数据和查询结果）
        6. 工具数据如何支持评分决定的详细说明
        7. **对于任何未验证的材料，必须明确说明验证失败的原因和对评分的影响**
        8. **对于工具调用失败的情况，必须详细说明失败原因和对评估结果的影响**
        """
        
        # 如果有用户需求，添加到描述中
        if user_requirement:
            description += f"\n\n用户提供的材料信息：{user_requirement}"
        
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
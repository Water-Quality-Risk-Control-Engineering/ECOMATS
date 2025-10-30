#!/usr/bin/env python3
"""
合成方法任务
负责设计材料的合成方法和工艺流程
"""

from .base_task import BaseTask

class SynthesisMethodTask(BaseTask):
    """合成方法任务类 / Synthesis method task class"""
    
    def __init__(self, agent, material_info=""):
        """
        初始化合成方法任务 / Initialize synthesis method task
        
        Args:
            agent: 合成方法智能体 / Synthesis method agent
            material_info: 材料信息 / Material information
        """
        super().__init__(
            agent=agent,
            expected_output="材料合成的详细指导和工艺参数",  # 材料合成的详细指导和工艺参数 / Detailed guidance and process parameters for material synthesis
            description=f"""提供材料合成的详细指导和工艺参数。
            包括实验步骤、反应条件、设备要求等。
            {material_info}
            / Provide detailed guidance and process parameters for material synthesis.
            Include experimental steps, reaction conditions, equipment requirements, etc.
            {material_info}"""
        )

    def create_task(self, agent, context_task=None, user_requirement=None):
        description = """
        请基于最终验证通过的材料方案，设计详细的合成方法和工艺流程：
        
        **重要说明**：在开始设计合成方法之前，必须明确最终验证报告中排名最前的具体材料作为合成目标。
        请仔细分析最终验证报告中的材料排名和综合评分，选择排名前1-2位的材料作为主要合成目标。
        
        设计步骤：
        1. 确定合成目标：明确最终验证报告中排名最前的具体材料（包括化学式、结构参数等）
        2. 合成策略设计：根据材料的结构参数设计合成路线
        3. 合成步骤细化：明确每个合成步骤的具体操作
        4. 工艺参数优化：确定关键工艺参数的数值范围
        5. 设备和安全要求：列出所需的设备和安全措施
        6. 质量控制指标：确定关键质量控制点和表征方法
        
        工具使用策略：
        1. **合成目标确认阶段**：
           - 调用Material Identifier Tool确认将要合成的具体材料类型和基本属性
           - 调用Structure Validator Tool验证材料结构的真实性
           - 记录材料的化学式、结构参数等关键信息
           - 对无法验证的材料结构，必须重新选择或设计合成目标
        
        2. **原材料信息收集阶段**：
           - 调用PubChem工具查询所有原材料的化学性质、物理性质和安全性数据
           - 调用Name2CAS Tool获取原材料的CAS号和标准化学名称
           - 调用Materials Project工具（如适用）查询金属原材料的属性
           - 整理原材料的危险性信息和安全处理要求
        
        3. **合成路线设计阶段**：
           - 调用Material Search Tool查询类似材料的合成方法、工艺参数和产率数据
           - 分析不同合成路线的优缺点和适用条件
           - 基于工具数据选择最适合的合成策略
           - 记录参考文献和数据来源
        
        4. **工艺参数优化阶段**：
           - 基于工具查询结果优化关键工艺参数（温度、时间、pH、浓度等）
           - 调用Formula2Properties Tool预测产物的物理化学性质
           - 调用Name2Properties Tool获取关键中间体的性质参数
           - 确定最佳的反应条件和参数范围
        
        5. **安全风险评估阶段**：
           - 调用PubChem工具查询所有涉及化学品的安全数据（SDS）
           - 评估合成过程中的安全风险（毒性、易燃性、腐蚀性等）
           - 识别潜在的危险操作步骤
           - 制定详细的安全措施和应急预案
        
        6. **可行性验证阶段**：
           - 对所有工具查询结果进行交叉验证
           - 确认合成方法的可行性和可重复性
           - 评估工业化生产的潜在挑战
           - 确保所有设计基于可靠的工具数据
        
        设计要点：
        - 确保合成方法的可行性和可重复性
        - 优化工艺参数以获得最佳材料性能
        - 考虑工业化生产的可行性和成本控制
        - **必须在设计开始时明确指出将要合成的具体材料名称和化学式**
        - **如果Materials Project工具未返回有效的material_id，不得进行推断或生成虚假的MP-ID**
        - **在没有有效material_id的情况下，应基于理论分析和已知的材料科学原理进行合成方法设计**
        - 每个工具调用都必须记录具体的参数和返回结果
        - 如果工具调用失败，必须明确说明失败原因和对设计的影响
        """
        
        # 添加用户需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        expected_output = """
        提供完整的合成方法方案，包括：
        1. 明确的合成目标：具体材料名称、化学式和选择理由
        2. 详细的合成策略和路线设计
        3. 具体的合成步骤和操作条件
        4. 关键工艺参数及其控制范围
        5. 所需设备和安全要求
        6. 质量控制指标和表征方法
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
#!/usr/bin/env python3
"""
材料设计任务
负责设计和优化水处理材料方案
"""

from .base_task import BaseTask

class DesignTask(BaseTask):
    """材料设计任务类 / Material design task class"""
    
    def __init__(self, agent):
        """
        初始化材料设计任务 / Initialize material design task
        
        Args:
            agent: 材料设计智能体 / Material design agent
        """
        super().__init__(
            agent=agent,
            expected_output="设计出的10种催化剂材料的详细信息，包括材料结构、合成方法等，按照详细的材料类型分类和结构描述要求进行设计",  # 设计出的10种催化剂材料的详细信息，包括材料结构、合成方法等 / Detailed information of the 10 designed catalyst materials, including material structure, synthesis methods, etc.
            description="""基于用户需求和污染物特性，设计10种催化PMS活化的催化剂材料。
            要求给出每种材料的详细结构信息和具体的合成方法。
            / Based on user requirements and pollutant characteristics, design 10 catalyst materials for PMS activation.
            Provide detailed structural information and specific synthesis methods for each material.
            
            材料类型分类要求：
            1. 纯金属类：单质金属、合金、纳米颗粒
            2. 金属氧化物类：单一氧化物、复合氧化物、层状双金属氢氧化物
            3. 金属硫化物类：过渡金属硫化物及其复合材料
            4. 金属氮化物/碳化物类：各类金属氮化物和碳化物
            5. MOF/COF材料：传统及功能化框架材料
            6. 碳基材料：石墨烯、碳纳米管、多孔碳等
            7. 单原子催化剂：单原子、双原子、多原子簇催化剂
            8. 复合材料：多种材料的复合体系
            9. 生物基材料：酶催化剂和生物聚合物基材料
            
            结构描述要求：
            1. 基本结构信息：化学式、分子量、晶体结构、电子结构
            2. 活性位点描述：中心原子、配位环境、配位结构、几何构型
            3. 基底结构描述：结构形式、化学连接、拓扑结构
            4. 配体信息：配体类型、结构、配位模式
            5. 结构参数：原子位置、空间群、配位数、几何参数"""
        )
    
    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        description = """
        根据用户需求设计水处理材料方案。
        
        设计步骤：
        1. 分析目标污染物特性和处理要求
        2. 选择合适的材料类型（如单原子催化剂、双原子催化剂、MOF材料等）
        3. **强制使用Materials Project工具查询类似材料的性质数据**
        4. **强制使用PubChem工具验证目标污染物的化学信息**
        5. 基于工具数据设计材料结构
        6. **强制使用Structure Validator工具验证设计的材料结构是否真实存在**
        7. 如果验证失败，需要重新设计
        8. 优化材料结构参数以确保催化性能和稳定性
        9. 考虑材料多样性、结构稳定性、催化性能的平衡
        
        材料类型分类要求：
        1. **纯金属类**：单质金属、合金、纳米颗粒
        2. **金属氧化物类**：单一氧化物、复合氧化物、层状双金属氢氧化物
        3. **金属硫化物类**：过渡金属硫化物及其复合材料
        4. **金属氮化物/碳化物类**：各类金属氮化物和碳化物
        5. **MOF/COF材料**：传统及功能化框架材料
        6. **碳基材料**：石墨烯、碳纳米管、多孔碳等
        7. **单原子催化剂**：单原子、双原子、多原子簇催化剂
        8. **复合材料**：多种材料的复合体系
        9. **生物基材料**：酶催化剂和生物聚合物基材料
        
        结构描述要求：
        1. **基本结构信息**：化学式、分子量、晶体结构、电子结构
        2. **活性位点描述**：中心原子、配位环境、配位结构、几何构型
        3. **基底结构描述**：结构形式、化学连接、拓扑结构
        4. **配体信息**：配体类型、结构、配位模式
        5. **结构参数**：原子位置、空间群、配位数、几何参数
        
        设计要点：
        - 确保材料具有良好的催化性能和结构稳定性
        - 优化材料的活性位点和反应路径
        - 满足目标污染物的降解需求
        - **必须验证设计的材料结构在现实中是否存在**
        - **必须使用Materials Project和PubChem工具获取数据支持设计**
        - 遵循材料类型分类和结构描述的详细要求
        """
        
        # 添加用户自定义需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        提供完整的材料设计方案，包括：
        1. 材料组成（材料类型和关键结构参数）
        2. 设计原理说明
        3. 稳定性保障措施
        4. 预期的催化性能
        5. 详细的结构描述（按照材料类型分类和结构描述要求）
        6. 合成可行性评估
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
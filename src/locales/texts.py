"""
ECOMATS 多语言文本定义
Multilingual text definitions for ECOMATS

结构 / Structure:
TEXTS = {
    "zh": { ... },
    "en": { ... }
}
"""

TEXTS = {
    # ==================== 中文 ====================
    "zh": {
        "agents": {
            "material_designer": {
                "role": "材料设计专家",
                "goal": "设计和优化水处理材料方案，严格按照材料类型分类和结构描述规范进行设计",
                "backstory_suffix": """
在输出设计结果时，应尽可能包含以下详细信息：
- Materials Project ID (mp-xxx)（如该材料已在数据库中）
- 化学式和晶体结构描述
- 关键物理性质（如带隙、密度）
- 热力学稳定性（能量凸包上的高度）

工具使用策略（限流与复用）：
- 优先复用已获取的结构验证或材料标识符结果，不重复发起数据库搜索
- 仅当缺失必要信息时再调用Materials Project搜索，并使用最小字段集合
- 元素组合查询限制返回数量，避免大范围拉取
"""
            },
            "expert_a": {
                "role": "高级氧化评估专家A",
                "goal": "从催化活性和反应机理角度评估材料设计方案的可行性和优越性",
            },
            "expert_b": {
                "role": "高级氧化评估专家B", 
                "goal": "从稳定性和耐久性角度评估材料设计方案",
            },
            "expert_c": {
                "role": "高级氧化评估专家C",
                "goal": "从环境安全性和可持续性角度评估材料设计方案",
            },
            "final_validator": {
                "role": "最终验证专家",
                "goal": "综合多位专家的评估意见，对材料设计方案进行最终审核和验证",
            },
            "mechanism_expert": {
                "role": "反应机理分析专家",
                "goal": "深入分析材料在水处理过程中的催化反应机理",
            },
            "synthesis_expert": {
                "role": "合成方法指导专家",
                "goal": "为设计的材料提供详细可行的合成方法和工艺参数",
            },
            "operation_expert": {
                "role": "操作参数建议专家",
                "goal": "根据材料特性和应用场景，提供最优的操作参数和使用建议",
            },
            "coordinator": {
                "role": "任务协调专家",
                "goal": "协调和分配各智能体的任务，确保工作流程高效运行",
            },
        },
        "tasks": {
            "design_task": {
                "description": """根据用户需求设计水处理材料方案。

设计步骤：
1. 分析目标污染物特性和处理要求
2. 选择合适的材料类型（如单原子催化剂、双原子催化剂、MOF材料等）
3. 优先复用已获取的结构验证或标识符结果；仅在缺失必要信息时调用Materials Project最小字段搜索
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

设计要点：
- 确保材料具有良好的催化性能和结构稳定性
- 优化材料的活性位点和反应路径
- 满足目标污染物的降解需求
- **必须验证设计的材料结构在现实中是否存在**
""",
                "expected_output": """提供完整的材料设计方案，包括：
1. 材料组成（材料类型和关键结构参数）
2. 设计原理说明
3. 稳定性保障措施
4. 预期的催化性能
5. 详细的结构描述（按照材料类型分类和结构描述要求）
6. 合成可行性评估
""",
            },
            "evaluation_task": {
                "description": """对材料设计方案进行专业评估。

评估维度：
1. 催化活性和反应效率
2. 结构稳定性和耐久性
3. 环境安全性和可持续性
4. 成本效益分析
5. 工业化可行性

评估要求：
- 给出具体的评分和详细的评估意见
- 指出设计方案的优势和不足
- 提供改进建议
""",
                "expected_output": """专家评估报告，包括：
1. 各评估维度的评分（1-10分）
2. 详细的评估意见
3. 设计方案的优势和不足
4. 具体的改进建议
""",
            },
            "final_validation_task": {
                "description": """综合多位专家的评估意见，对材料设计方案进行最终审核验证。

验证内容：
1. 汇总各专家评估意见
2. 分析评估结果的一致性和分歧
3. 给出最终的验证结论
4. 筛选出最优的设计方案
""",
                "expected_output": """最终验证报告，包括：
1. 专家评估汇总
2. 最终验证结论
3. 推荐的最优设计方案及排名
4. 综合改进建议
""",
            },
            "mechanism_analysis_task": {
                "description": """深入分析材料在水处理过程中的催化反应机理。

分析内容：
1. 反应活性位点分析
2. 反应路径和中间产物
3. 电子转移机制
4. 自由基生成机理
5. 污染物降解路径
""",
                "expected_output": """反应机理分析报告，包括：
1. 活性位点详细描述
2. 完整的反应路径图
3. 关键中间产物分析
4. 电子转移机制说明
5. 降解效率预测
""",
            },
            "synthesis_method_task": {
                "description": """为设计的材料提供详细可行的合成方法。

合成方案要求：
1. 详细的合成步骤
2. 所需原材料和试剂清单
3. 反应条件和参数
4. 关键工艺控制点
5. 质量检测方法
""",
                "expected_output": """合成方法指导书，包括：
1. 完整的合成流程图
2. 详细的操作步骤
3. 原材料和试剂清单
4. 工艺参数表
5. 质量控制标准
""",
            },
            "operation_suggesting_task": {
                "description": """根据材料特性和应用场景，提供最优的操作参数建议。

建议内容：
1. 最佳操作条件（pH、温度、浓度等）
2. 催化剂用量优化
3. 反应时间控制
4. 操作注意事项
5. 安全防护措施
""",
                "expected_output": """操作参数建议书，包括：
1. 最佳操作条件表
2. 参数优化建议
3. 操作规程
4. 安全注意事项
5. 性能维护指南
""",
            },
        },
        "ui": {
            "welcome": "欢迎使用ECOMATS - 水处理材料设计多智能体系统",
            "input_prompt": "请输入您的材料设计需求：",
            "example": "例如：设计一种用于处理含重金属镉废水的高效催化剂",
            "select_mode": "请选择工作模式：",
            "preset_sync": "预设工作流 (同步)",
            "preset_async": "预设工作流 (异步) ⚡ 推荐!",
            "autonomous_sync": "智能体自主调度 (同步)",
            "autonomous_async": "智能体自主调度 (异步) ⚡ 推荐!",
            "execution_complete": "执行完成!",
            "result_saved": "结果已保存到",
        },
    },
    
    # ==================== English ====================
    "en": {
        "agents": {
            "material_designer": {
                "role": "Material Design Expert",
                "goal": "Design and optimize water treatment material solutions, strictly following material type classification and structural description specifications",
                "backstory_suffix": """
When outputting design results, include the following detailed information:
- Materials Project ID (mp-xxx) (if the material exists in the database)
- Chemical formula and crystal structure description
- Key physical properties (e.g., band gap, density)
- Thermodynamic stability (height on energy convex hull)

Tool usage strategy (rate limiting and reuse):
- Prioritize reusing previously obtained structure validation or material identifier results
- Only call Materials Project search when necessary information is missing, using minimal field sets
- Limit element combination queries to avoid large-scale data retrieval
"""
            },
            "expert_a": {
                "role": "Advanced Oxidation Assessment Expert A",
                "goal": "Evaluate the feasibility and superiority of material design solutions from catalytic activity and reaction mechanism perspectives",
            },
            "expert_b": {
                "role": "Advanced Oxidation Assessment Expert B",
                "goal": "Evaluate material design solutions from stability and durability perspectives",
            },
            "expert_c": {
                "role": "Advanced Oxidation Assessment Expert C",
                "goal": "Evaluate material design solutions from environmental safety and sustainability perspectives",
            },
            "final_validator": {
                "role": "Final Validation Expert",
                "goal": "Integrate multiple expert evaluations to conduct final review and validation of material design solutions",
            },
            "mechanism_expert": {
                "role": "Reaction Mechanism Analysis Expert",
                "goal": "Conduct in-depth analysis of catalytic reaction mechanisms in water treatment processes",
            },
            "synthesis_expert": {
                "role": "Synthesis Method Guidance Expert",
                "goal": "Provide detailed and feasible synthesis methods and process parameters for designed materials",
            },
            "operation_expert": {
                "role": "Operation Parameter Suggestion Expert",
                "goal": "Provide optimal operation parameters and usage recommendations based on material properties and application scenarios",
            },
            "coordinator": {
                "role": "Task Coordination Expert",
                "goal": "Coordinate and distribute tasks among agents to ensure efficient workflow",
            },
        },
        "tasks": {
            "design_task": {
                "description": """Design water treatment material solutions based on user requirements.

Design Steps:
1. Analyze target pollutant characteristics and treatment requirements
2. Select appropriate material types (e.g., single-atom catalysts, dual-atom catalysts, MOF materials)
3. Prioritize reusing previously obtained structure validation or identifier results; only call Materials Project minimal field search when necessary
4. **Mandatory: Use PubChem tool to verify target pollutant chemical information**
5. Design material structure based on tool data
6. **Mandatory: Use Structure Validator tool to verify if designed material structures actually exist**
7. Redesign if validation fails
8. Optimize material structure parameters to ensure catalytic performance and stability
9. Balance material diversity, structural stability, and catalytic performance

Material Type Classification Requirements:
1. **Pure Metals**: Elemental metals, alloys, nanoparticles
2. **Metal Oxides**: Single oxides, composite oxides, layered double hydroxides
3. **Metal Sulfides**: Transition metal sulfides and composites
4. **Metal Nitrides/Carbides**: Various metal nitrides and carbides
5. **MOF/COF Materials**: Traditional and functionalized framework materials
6. **Carbon-based Materials**: Graphene, carbon nanotubes, porous carbon, etc.
7. **Single-atom Catalysts**: Single-atom, dual-atom, multi-atom cluster catalysts
8. **Composite Materials**: Multi-material composite systems
9. **Bio-based Materials**: Enzyme catalysts and biopolymer-based materials

Design Key Points:
- Ensure materials have good catalytic performance and structural stability
- Optimize active sites and reaction pathways
- Meet target pollutant degradation requirements
- **Must verify if designed material structures exist in reality**
""",
                "expected_output": """Complete material design solution including:
1. Material composition (material type and key structural parameters)
2. Design principle explanation
3. Stability assurance measures
4. Expected catalytic performance
5. Detailed structure description (following material type and structure requirements)
6. Synthesis feasibility assessment
""",
            },
            "evaluation_task": {
                "description": """Professionally evaluate the material design solution.

Evaluation Dimensions:
1. Catalytic activity and reaction efficiency
2. Structural stability and durability
3. Environmental safety and sustainability
4. Cost-benefit analysis
5. Industrial feasibility

Evaluation Requirements:
- Provide specific scores and detailed evaluation opinions
- Identify advantages and disadvantages of the design
- Provide improvement suggestions
""",
                "expected_output": """Expert evaluation report including:
1. Scores for each evaluation dimension (1-10)
2. Detailed evaluation opinions
3. Advantages and disadvantages of the design
4. Specific improvement suggestions
""",
            },
            "final_validation_task": {
                "description": """Integrate multiple expert evaluations for final validation of the material design solution.

Validation Content:
1. Summarize expert evaluations
2. Analyze consistency and divergence of evaluation results
3. Provide final validation conclusions
4. Select optimal design solutions
""",
                "expected_output": """Final validation report including:
1. Expert evaluation summary
2. Final validation conclusions
3. Recommended optimal design solutions with ranking
4. Comprehensive improvement suggestions
""",
            },
            "mechanism_analysis_task": {
                "description": """Conduct in-depth analysis of catalytic reaction mechanisms in water treatment.

Analysis Content:
1. Reactive site analysis
2. Reaction pathways and intermediates
3. Electron transfer mechanisms
4. Free radical generation mechanisms
5. Pollutant degradation pathways
""",
                "expected_output": """Reaction mechanism analysis report including:
1. Detailed active site description
2. Complete reaction pathway diagram
3. Key intermediate analysis
4. Electron transfer mechanism explanation
5. Degradation efficiency prediction
""",
            },
            "synthesis_method_task": {
                "description": """Provide detailed and feasible synthesis methods for designed materials.

Synthesis Plan Requirements:
1. Detailed synthesis steps
2. Required raw materials and reagent list
3. Reaction conditions and parameters
4. Key process control points
5. Quality testing methods
""",
                "expected_output": """Synthesis method guide including:
1. Complete synthesis flowchart
2. Detailed operation steps
3. Raw materials and reagent list
4. Process parameter table
5. Quality control standards
""",
            },
            "operation_suggesting_task": {
                "description": """Provide optimal operation parameter recommendations based on material properties and application scenarios.

Recommendation Content:
1. Optimal operating conditions (pH, temperature, concentration, etc.)
2. Catalyst dosage optimization
3. Reaction time control
4. Operation precautions
5. Safety protection measures
""",
                "expected_output": """Operation parameter recommendation including:
1. Optimal operating conditions table
2. Parameter optimization suggestions
3. Operating procedures
4. Safety precautions
5. Performance maintenance guide
""",
            },
        },
        "ui": {
            "welcome": "Welcome to ECOMATS - Multi-Agent System for Water Treatment Material Design",
            "input_prompt": "Please enter your material design requirements:",
            "example": "Example: Design an efficient catalyst for treating wastewater containing heavy metal cadmium",
            "select_mode": "Please select workflow mode:",
            "preset_sync": "Preset Workflow (Sync)",
            "preset_async": "Preset Workflow (Async) ⚡ Recommended!",
            "autonomous_sync": "Autonomous Agent Scheduling (Sync)",
            "autonomous_async": "Autonomous Agent Scheduling (Async) ⚡ Recommended!",
            "execution_complete": "Execution Complete!",
            "result_saved": "Result saved to",
        },
    },
}

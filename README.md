# ECOMATS - 基于CrewAI的水处理材料设计多智能体系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-Powered-green)](#)

这是一个使用CrewAI框架构建的多智能体系统，专门用于水处理材料的设计、评估和优化。系统集成了Materials Project和PubChem等化学数据库工具，能够基于真实的材料数据进行智能化材料设计。

## 项目特色

- 基于CrewAI框架构建的多智能体协作系统
- 专门针对水处理材料设计领域优化
- 支持材料设计、评估和优化的完整工作流
- 模块化设计，易于扩展和定制
- 采用全面评估模式，每个专家评估所有维度
- 使用详细的Prompt文件定义专家行为
- 支持智能体任务分配机制，根据任务类型自动选择合适的智能体
- 支持阿里云EAS自部署模型集成
- 集成化学数据库工具验证材料设计合理性
- 实现三重盲评和一致性分析机制
- 支持迭代设计优化机制
- 实现5个专用AI工具，增强材料属性查询能力

## 项目结构

```
ECOMATS/
├── src/                       # 源代码目录
│   ├── agents/                # 智能体实现
│   │   ├── Assessment_Screening_agent_A.py
│   │   ├── Assessment_Screening_agent_B.py
│   │   ├── Assessment_Screening_agent_C.py
│   │   ├── Assessment_Screening_agent_Overall.py
│   │   ├── Creative_Designing_agent.py
│   │   ├── Extracting_agent.py
│   │   ├── Mechanism_Mining_agent.py
│   │   ├── Operation_Suggesting_agent.py
│   │   ├── Synthesis_Guiding_agent.py
│   │   ├── base_agent.py
│   │   ├── coordinator.py
│   │   └── task_allocator.py
│   ├── config/                # 配置文件
│   │   └── config.py
│   ├── prompts/               # Prompt文件
│   │   ├── coordinator_prompt.md
│   │   ├── expert_a_prompt.md
│   │   ├── expert_b_prompt.md
│   │   ├── expert_c_prompt.md
│   │   ├── final_validator_prompt.md
│   │   ├── literature_processor_prompt.md
│   │   ├── material_designer_prompt.md
│   │   ├── mechanism_expert_prompt.md
│   │   ├── operation_suggesting_prompt.md
│   │   └── synthesis_expert_prompt.md
│   ├── tasks/                 # 任务定义
│   │   ├── base_task.py
│   │   ├── design_task.py
│   │   ├── evaluation_task.py
│   │   ├── final_validation_task.py
│   │   ├── mechanism_analysis_task.py
│   │   ├── operation_suggesting_task.py
│   │   └── synthesis_method_task.py
│   ├── tools/                 # 工具实现
│   │   ├── __init__.py
│   │   ├── crewai_materials_project_tool.py
│   │   ├── crewai_pubchem_tool.py
│   │   ├── crewai_name2cas_tool.py
│   │   ├── crewai_name2properties_tool.py
│   │   ├── crewai_cid2properties_tool.py
│   │   ├── crewai_formula2properties_tool.py
│   │   ├── crewai_material_search_tool.py
│   │   ├── crewai_pnec_tool.py
│   │   ├── evaluation_tool.py
│   │   ├── materials_project_tool.py
│   │   ├── pubchem_tool.py
│   │   ├── name2cas_tool.py
│   │   ├── name2properties_tool.py
│   │   ├── cid2properties_tool.py
│   │   ├── formula2properties_tool.py
│   │   ├── material_search_tool.py
│   │   └── pnec_tool.py
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── llm_config.py
│       └── prompt_loader.py
├── scripts/                   # 脚本文件
│   ├── main.py                # 主程序入口
│   ├── generate_catalysts.py  # 催化剂生成脚本
│   └── generate_catalysts_advanced.py # 高级催化剂生成脚本
├── examples/                  # 示例文件
├── tests/                     # 测试文件
├── .env.example               # 环境变量示例
├── requirements.txt           # 依赖列表
└── README.md                 # 项目说明文件
```

## 核心智能体

系统包含以下核心智能体：

1. **协调者** - 负责协调各专家工作，确保任务高效完成
2. **材料设计专家** - 设计和优化水处理材料方案
3. **专家A** - 全面评估材料方案的各个方面
4. **专家B** - 全面评估材料方案的各个方面
5. **专家C** - 全面评估材料方案的各个方面
6. **最终验证专家** - 综合各专家评估结果，进行加权计算并形成最终材料评估报告
7. **文献处理专家** - 处理和分析相关技术文献
8. **机理分析专家** - 分析材料的催化机理和作用机制
9. **合成方法专家** - 设计材料的合成方法和工艺流程
10. **操作建议专家** - 提供材料合成、生产和应用的详细操作建议

## 工作模式

系统支持两种工作模式：

### 1. 预设工作流模式（默认）
任务按照预定义顺序执行，包括材料设计、评估、验证、机理分析和合成方法设计等阶段。

工作流程：
1. 材料设计专家设计材料方案
2. 评估专家A、B、C并行评估材料方案
3. 最终验证专家综合评估结果并生成最终报告
4. 机理分析专家分析材料的催化机理
5. 合成方法专家设计材料的合成方法
6. 操作建议专家提供详细的操作指导

### 2. 智能体自主调度模式
由协调专家动态决定任务执行顺序，实现更灵活的任务调度。

## 评估维度及权重

- 催化性能（权重50%）
- 经济可行性（权重10%）
- 环境友好性（权重10%）
- 技术可行性（权重10%）
- 结构合理性（权重20%）

## 使用说明

1. 复制 `.env.example` 文件为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 在 `.env` 文件中配置你的API密钥:
   ```env
   QWEN_API_KEY=你的Qwen API密钥
   MATERIALS_PROJECT_API_KEY=你的Materials Project API密钥（可选）
   ```

3. （可选）配置阿里云EAS自部署模型:
   ```env
   EAS_ENDPOINT=你的EAS模型端点URL
   EAS_TOKEN=你的EAS模型Token
   EAS_MODEL_NAME=你的EAS模型名称
   ```

4. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

5. 运行系统:
   ```bash
   python scripts/main.py
   ```

## 智能体工具集成

系统集成了以下数据库查询工具，智能体可根据需要自动调用：

1. **Materials Project工具** - 访问材料科学数据库获取材料属性，包括带隙、形成能、晶体结构等
2. **PubChem工具** - 查询化学化合物信息，包括CAS号、分子量、SMILES等
3. **Name2CAS工具** - 将材料名称转换为CAS号
4. **Name2Properties工具** - 根据材料名称查询理化性质
5. **CID2Properties工具** - 根据PubChem CID查询性质
6. **Formula2Properties工具** - 根据化学式预测性质
7. **MaterialSearch工具** - 检索相似材料的性能数据
8. **PNEC工具** - 查询化学物质的预测无效应浓度数据，用于环境风险评估

## 迭代设计机制

系统实现了智能迭代设计机制：

1. **评估驱动优化** - 根据专家评估结果自动识别设计不足
2. **反馈循环** - 将评估反馈整合到下一轮设计中
3. **多轮优化** - 支持最多3轮设计迭代优化
4. **质量控制** - 设置最低可接受评分阈值(7.0分)

## 一致性分析机制

系统实现了三重盲评和一致性分析机制：

1. **三重盲评** - 三个评估专家独立评分
2. **标准差计算** - 计算各维度评分的标准差
3. **一致性系数** - 计算一致性系数Cj = 1 - (SD/mean)
4. **融合评分** - 使用一致性系数调整最终得分

## 开发指南

### 添加新智能体

1. 在 `agents/` 目录下创建新的智能体文件，继承`BaseAgent`基类
2. 在 `prompt/` 目录下创建对应的Prompt文件
3. 在智能体文件中使用`PromptLoader`加载Prompt文件
4. 在 `main.py` 中导入并使用新智能体
5. 在任务分配器中注册新智能体类型

### 扩展评价维度

1. 修改各专家的提示词文件，添加新的评价维度
2. 更新评价维度和权重分配
3. 调整评价标准和输出格式以适应新的维度

### 添加新任务类型

1. 在 `tasks/` 目录下创建新的任务文件，继承`BaseTask`基类
2. 在任务分配器中添加任务类型与智能体类型的映射关系
3. 在主程序中创建并执行新任务

### 集成新工具

1. 在 `tools/` 目录下创建新的工具文件
2. 实现工具的具体功能
3. 在智能体中通过CrewAI的工具机制集成新工具
4. 更新相关智能体的Prompt文件，指导其如何使用新工具

## [English Version](README_en.md)

## 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。
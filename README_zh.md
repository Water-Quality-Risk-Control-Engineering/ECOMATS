# ECOMATS - 基于CrewAI的水处理材料设计多智能体系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-Powered-green)](#)

这是一个基于CrewAI框架构建的多智能体系统，专门用于水处理材料的设计、评估和优化。该系统集成了Materials Project和PubChem等化学数据库工具，能够基于真实材料数据实现智能化材料设计。

## 项目特性

- 基于CrewAI框架构建的多智能体协作系统
- 专门针对水处理材料设计进行优化
- 支持从材料设计到评估优化的完整工作流程
- 模块化设计，易于扩展和定制
- 全面评估模式，每个专家评估所有维度
- 详细的Prompt文件定义专家行为
- 代理任务分配机制，根据任务类型自动选择合适的代理
- 支持阿里云EAS自部署模型集成
- 集成化学数据库工具以验证材料设计
- 实现三盲评审和一致性分析机制
- 支持迭代设计优化
- 集成5个专业AI工具以增强材料属性查询能力

## 项目结构

```
ECOMATS/
├── src/                       # 源代码目录
│   ├── agents/                # 代理实现
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
│   │   ├── crewai_cid2properties_tool.py
│   │   ├── crewai_formula2properties_tool.py
│   │   ├── crewai_material_search_tool.py
│   │   ├── crewai_materials_project_tool.py
│   │   ├── crewai_name2cas_tool.py
│   │   ├── crewai_name2properties_tool.py
│   │   ├── crewai_pnec_tool.py
│   │   ├── crewai_pubchem_tool.py
│   │   ├── cid2properties_tool.py
│   │   ├── evaluation_tool.py
│   │   ├── formula2properties_tool.py
│   │   ├── material_search_tool.py
│   │   ├── materials_project_tool.py
│   │   ├── name2cas_tool.py
│   │   ├── name2properties_tool.py
│   │   ├── pnec_tool.py
│   │   └── pubchem_tool.py
│   └── utils/                 # 工具函数
│       ├── llm_config.py
│       └── prompt_loader.py
├── scripts/                   # 脚本文件
│   ├── main.py                # 主程序入口
│   ├── generate_catalysts.py  # 催化剂生成脚本
│   ├── generate_catalysts_advanced.py # 高级催化剂生成脚本
│   ├── run_test.py            # 测试运行脚本
│   └── test_new_tools.py      # 新工具测试脚本
├── examples/                  # 示例文件
│   └── task_allocation_example.py
├── .env.example               # 环境变量示例
├── requirements.txt           # 依赖列表
├── README.md                  # 项目文档 (英文)
└── README_zh.md               # 项目文档 (中文)
```

## 核心代理

系统包括以下核心代理：

1. **Coordinator** - 协调专家工作，确保任务高效完成
2. **Material Designer** - 设计和优化水处理材料解决方案 (Creative_Designing_agent.py)
3. **Expert A** - 全面评估材料解决方案的各个方面 (Assessment_Screening_agent_A.py)
4. **Expert B** - 全面评估材料解决方案的各个方面 (Assessment_Screening_agent_B.py)
5. **Expert C** - 全面评估材料解决方案的各个方面 (Assessment_Screening_agent_C.py)
6. **Final Validator** - 综合所有专家的评估结果，进行加权计算，生成最终材料评估报告 (Assessment_Screening_agent_Overall.py)
7. **Literature Processor** - 处理和分析相关技术文献 (Extracting_agent.py)
8. **Mechanism Expert** - 分析材料的催化机制和作用原理 (Mechanism_Mining_agent.py)
9. **Synthesis Method Expert** - 设计材料的合成方法和工艺 (Synthesis_Guiding_agent.py)
10. **Operation Suggesting Agent** - 提供材料合成、生产和应用的详细操作指导 (Operation_Suggesting_agent.py)

## 工作模式

系统支持两种工作模式：

### 1. 预设工作流模式（默认）
任务按照预定义的顺序执行，包括材料设计、评估、验证、机理分析和合成方法设计。

工作流程：
1. Material Designer创建材料解决方案
2. Experts A、B、C并行评估材料解决方案
3. Final Validator综合评估结果并生成最终报告
4. Mechanism Expert分析材料的催化机制
5. Synthesis Method Expert设计材料的合成方法
6. Operation Suggesting Agent提供详细的操作指导

### 2. 代理自主调度模式
协调器动态确定任务执行顺序，实现更灵活的任务调度。

## 评估维度和权重

- 催化性能（50%权重）
- 经济可行性（10%权重）
- 环境友好性（10%权重）
- 技术可行性（10%权重）
- 结构合理性（20%权重）

## 使用说明

1. 复制`.env.example`文件为`.env`：
   ```bash
   cp .env.example .env
   ```

2. 在`.env`文件中配置您的API密钥：
   ```env
   QWEN_API_KEY=您的Qwen API密钥
   MATERIALS_PROJECT_API_KEY=您的Materials Project API密钥（可选）
   ```

3. （可选）配置阿里云EAS自部署模型：
   ```env
   EAS_ENDPOINT=您的EAS模型端点URL
   EAS_TOKEN=您的EAS模型令牌
   EAS_MODEL_NAME=您的EAS模型名称
   ```

4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

5. 运行系统：
   ```bash
   python scripts/main.py
   ```

## 代理工具集成

系统集成了以下数据库查询工具，代理可以根据需要自动调用：

1. **Materials Project Tool** - 访问材料科学数据库，获取材料属性，包括带隙、形成能、晶体结构等 (materials_project_tool.py)
2. **PubChem Tool** - 查询化学化合物信息，包括CAS号、分子量、SMILES等 (pubchem_tool.py)
3. **Name2CAS Tool** - 将材料名称转换为CAS号 (name2cas_tool.py)
4. **Name2Properties Tool** - 根据材料名称查询理化性质 (name2properties_tool.py)
5. **CID2Properties Tool** - 根据PubChem CID查询性质 (cid2properties_tool.py)
6. **Formula2Properties Tool** - 根据化学式预测性质 (formula2properties_tool.py)
7. **MaterialSearch Tool** - 检索相似材料的性能数据 (material_search_tool.py)
8. **PNEC Tool** - 查询化学物质的预测无效应浓度数据，用于环境风险评估 (pnec_tool.py)

## 迭代设计机制

系统实现了智能化迭代设计机制：

1. **评估驱动优化** - 基于专家评估自动识别设计不足
2. **反馈循环** - 将评估反馈整合到下一轮设计中
3. **多轮优化** - 支持最多3轮设计迭代优化
4. **质量控制** - 设置最低可接受分数阈值（7.0分）

## 一致性分析机制

系统实现三盲评审和一致性分析机制：

1. **三盲评审** - 三位评估专家独立评分
2. **标准差计算** - 计算各维度分数的标准差
3. **一致性系数** - 计算一致性系数Cj = 1 - (SD/mean)
4. **融合评分** - 使用一致性系数调整最终分数

## 开发指南

### 添加新代理

1. 在`agents/`目录中创建新的代理文件，继承自`BaseAgent`类
2. 在`prompt/`目录中创建相应的Prompt文件
3. 在代理文件中使用`PromptLoader`加载Prompt文件
4. 在`main.py`中导入并使用新代理
5. 在任务分配器中注册新的代理类型

### 扩展评估维度

1. 修改各专家的prompt文件以添加新的评估维度
2. 更新评估维度和权重分配
3. 调整评估标准和输出格式以适应新维度

### 添加新任务类型

1. 在`tasks/`目录中创建新的任务文件，继承自`BaseTask`类
2. 在任务分配器中添加任务类型到代理类型的映射
3. 在主程序中创建并执行新任务

### 集成新工具

1. 在`tools/`目录中创建新的工具文件
2. 实现工具的具体功能
3. 通过CrewAI的工具机制将新工具集成到代理中
4. 更新相关代理的prompt文件以指导其使用新工具

## 许可证

本项目采用MIT许可证。详情请见[LICENSE](LICENSE)文件。
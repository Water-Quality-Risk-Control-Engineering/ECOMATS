# ECOMATS - 基于CrewAI的水处理材料设计多智能体系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.7.0-green)](#)
[![Async](https://img.shields.io/badge/Async-Enabled-orange)](#)

这是一个基于 **CrewAI 1.7.0** 框架构建的高性能多智能体系统，支持**异步执行**，专门用于水处理材料的设计、评估和优化。该系统集成了Materials Project和PubChem等化学数据库工具，能够基于真实材料数据实现智能化材料设计。

**⚡ 性能**: 通过异步执行和并行任务处理，速度提升高达 **7.5 倍**。

## 项目特性

### 🚀 性能与架构
- **CrewAI 1.7.0** 完整异步支持（性能提升 2-10 倍）
- **并行任务执行** - 3 位评估专家并行运行（快 2.6 倍）
- **异步工具** - 非阻塞 API 调用（PubChem、Materials Project）
- **批量处理** 支持多材料设计
- 多智能体协作系统，智能任务调度
- 模块化设计，易于扩展和定制

### 🎯 核心能力
- 专门针对水处理材料设计进行优化
- 支持从材料设计到评估优化的完整工作流程
- 全面评估模式，每个专家评估所有维度
- 三盲评审和一致性分析机制
- 迭代设计优化与反馈循环
- 代理任务分配机制，支持自动模式检测

### 🛠️ 工具与集成
- 13+ 专业 AI 工具用于材料属性查询
- 异步 PubChem 和 Materials Project 工具
- MolPort API 用于商业可用性评估
- 全面的数据验证和结构校验
- 支持阿里云 EAS 自部署模型集成
- 详细的 Prompt 文件定义专家行为

## 项目结构

```
ECOMATS/
├── src/                       # 源代码目录
│   ├── agents/                # 代理实现（10个专业代理）
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
│   │   └── task_organizing_agent.py   # 任务协调器，支持意图识别和智能体调度
│   ├── config/                # 配置文件
│   │   └── config.py
│   ├── prompts/               # Prompt文件
│   │   ├── coordinator_prompt.md
│   │   ├── expert_template_prompt.md      # A/B/C 专家参数化模板
│   │   ├── literature_processor_prompt.md
│   │   ├── material_designer_prompt.md
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
│   │   ├── factory.py                          # 工具工厂，集中管理
│   │   ├── async_pubchem_tool.py               # ⚡ 异步 PubChem（快 3 倍）
│   │   ├── async_materials_project_tool.py     # ⚡ 异步 Materials Project
│   │   ├── pubchem_tool.py                     # PubChem API 集成
│   │   ├── materials_project_tool.py           # Materials Project API 集成
│   │   ├── molport_tool.py                     # MolPort API 商业可用性
│   │   ├── name2cas_tool.py                    # 名称转 CAS 号
│   │   ├── cid2properties_tool.py              # CID 转属性查询
│   │   ├── name2properties_tool.py             # 名称转属性查询
│   │   ├── formula2properties_tool.py          # 分子式转属性查询
│   │   ├── material_search_tool.py             # 材料数据库搜索
│   │   ├── pnec_tool.py                        # PNEC 环境毒性工具
│   │   ├── material_identifier_tool.py         # 材料类型识别
│   │   ├── data_validator_tool.py              # 数据验证工具
│   │   ├── structure_validator_tool.py         # 化学结构验证
│   │   ├── crewai_materials_project_tool.py    # CrewAI 封装
│   │   ├── crewai_pubchem_tool.py              # CrewAI 封装
│   │   ├── crewai_molport_tool.py              # CrewAI 封装（3个工具）
│   │   ├── crewai_name2cas_tool.py             # CrewAI 封装
│   │   ├── crewai_cid2properties_tool.py       # CrewAI 封装
│   │   ├── crewai_name2properties_tool.py      # CrewAI 封装
│   │   ├── crewai_formula2properties_tool.py   # CrewAI 封装
│   │   ├── crewai_material_search_tool.py      # CrewAI 封装
│   │   ├── crewai_pnec_tool.py                 # CrewAI 封装
│   │   ├── crewai_material_identifier_tool.py  # CrewAI 封装
│   │   ├── crewai_data_validator_tool.py       # CrewAI 封装
│   │   ├── crewai_structure_validator_tool.py  # CrewAI 封装
│   │   ├── pg_vector_tool.py                   # PostgreSQL 向量数据库工具
│   │   ├── crewai_pg_vector_tool.py            # PGVector CrewAI 封装
│   │   ├── gdb_tool.py                         # 图数据库（阿里云 GDB）工具
│   │   └── crewai_gdb_tool.py                  # GDB CrewAI 封装
│   └── utils/                 # 工具函数
│       ├── llm_config.py
│       ├── prompt_loader.py
│       ├── context_store.py              # 工具缓存的上下文存储
│       ├── workflow_monitor.py           # 工作流监控与报告
│       ├── assessment_tool_executor.py   # 评估工具执行逻辑
│       └── assessment_scoring_logic.py   # 评估评分计算
├── scripts/                   # 脚本文件
│   ├── main.py                # 主程序入口（同步模式）
│   ├── main_async.py          # ⚡ 异步主程序（推荐，快 2-3 倍）
│   ├── test_molport_tool.py   # MolPort API 连接测试
│   └── (其他脚本)
├── tests/                     # 统一测试目录
│   ├── integration/           # 集成测试
│   ├── tools/                 # 工具特定测试
│   ├── test_crewai_1.7.0.py  # CrewAI 1.7.0 特性测试
│   ├── test_async_tools.py   # 异步工具性能测试
│   └── (60+ 测试文件)
├── examples/                  # 示例文件
│   ├── async_crew_example.py  # ⚡ 异步 Crew 使用示例
│   └── task_allocation_example.py
├── docs/                      # 文档目录
│   ├── README.md              # 文档索引
│   ├── CrewAI升级完成报告.md   # ⚡ CrewAI 1.7.0 升级总结
│   ├── sft/                   # SFT 生成指南
│   ├── archives/              # 归档文档
│   │   └── crewai-upgrade/    # CrewAI 升级详情
│   ├── molport_integration_guide.md
│   ├── tool_redundancy_analysis.md
│   └── API_Key配置检查报告.md
├── .env.example               # 环境变量示例
├── requirements.txt           # 依赖列表
└── README.md                  # 项目文档（英文）
```

## 核心代理

系统包括以下核心代理：

1. **Task_Organizing_Agent** - 组织和协调专家工作，确保任务高效完成
2. **Creative_Designing_agent** - 设计和优化水处理材料解决方案
3. **Assessment_Screening_agent_A** - 全面评估材料解决方案的各个方面
4. **Assessment_Screening_agent_B** - 全面评估材料解决方案的各个方面
5. **Assessment_Screening_agent_C** - 全面评估材料解决方案的各个方面
6. **Assessment_Screening_agent_Overall** - 综合所有专家的评估结果，进行加权计算，生成最终材料评估报告，并提供改进建议
7. **Extracting_agent** - 处理和分析相关技术文献
8. **Mechanism_Mining_agent** - 分析材料的催化机制和作用原理
9. **Synthesis_Guiding_agent** - 设计材料的合成方法和工艺
10. **Operation_Suggesting_agent** - 提供材料合成、生产和应用的详细操作指导

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

### 平台兼容性

**推荐**: Linux / macOS / WSL2  
**Windows 用户**: 请查看 [Windows 兼容性指南](docs/Windows_Compatibility_Guide.md) 了解 `signal.SIGHUP` 兼容性问题和解决方案。

### 配置步骤

1. 复制`.env.example`文件为`.env`：
   ```bash
   cp .env.example .env
   ```

2. 在`.env`文件中配置您的API密钥：
   ```env
   # 必需：Qwen LLM API
   QWEN_API_KEY=您的Qwen API密钥
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_MODEL_NAME=qwen-plus
   
   # 必需：Materials Project API
   MATERIALS_PROJECT_API_KEY=您的Materials Project API密钥
   
   # 可选：MolPort API（用于商业可用性查询）
   MOLPORT_API_KEY=您的MolPort API密钥
   
   # 可选：PubChem API（公开API，不需要密钥但建议配置）
   PUBCHEM_API_KEY=您的PubChem API密钥
   
   # 可选：PostgreSQL 向量数据库（用于 SFT 向量检索）
   PG_HOST=your_host
   PG_PORT=5432
   PG_DATABASE=your_database
   PG_USER=your_username
   PG_PASSWORD=your_password
   
   # 可选：图数据库（用于阿里云 GDB 图谱查询）
   GDB_HOST=your_host
   GDB_PORT=3734
   GDB_USERNAME=your_username
   GDB_PASSWORD=your_password
   
   # 系统配置
   ENABLE_TOOLS=true
   VERBOSE=True
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
   
   **选项 A：异步模式（⚡ 推荐，快 2-3 倍）**
   ```bash
   python scripts/main_async.py
   ```
   
   **选项 B：同步模式（原始版，向后兼容）**
   ```bash
   python scripts/main.py
   ```
   
   **性能对比**：
   - 异步模式：完整工作流约 21 秒
   - 同步模式：完整工作流约 33 秒
   - 批量设计（10个材料）：43秒 vs 326秒（快 7.5 倍）

## 代理工具集成

系统集成了以下数据库查询工具，代理可以根据需要自动调用：

### 核心数据库工具

1. **Materials Project Tool** - 访问材料科学数据库，获取材料属性，包括带隙、形成能、晶体结构等。已优化字段选择和分块以提高查询性能。(materials_project_tool.py)
2. **PubChem Tool** - 查询化学化合物信息，包括CAS号、分子量、SMILES、InChI等详细属性。增强了 InChIKey 搜索能力和分子式验证。(pubchem_tool.py)
3. **MolPort Tool** - 新增！商业可用性评估工具，包含三个专业功能：
   - **化合物可用性检查器** - 检查化合物是否可商业获取
   - **化学结构搜索** - 搜索相似化合物（精确、相似度、子结构）
   - **分子信息加载器** - 获取详细的供应商、价格和库存信息

### 专业查询工具

4. **Name2CAS Tool** - 将材料名称转换为CAS号 (name2cas_tool.py)
5. **Name2Properties Tool** - 根据材料名称查询理化性质 (name2properties_tool.py)
6. **CID2Properties Tool** - 根据PubChem CID查询性质 (cid2properties_tool.py)
7. **Formula2Properties Tool** - 根据化学式预测性质 (formula2properties_tool.py)
8. **MaterialSearch Tool** - 检索相似材料的性能数据 (material_search_tool.py)

### 验证与分析工具

9. **PNEC Tool** - 查询化学物质的预测无效应浓度数据，用于环境风险评估 (pnec_tool.py)
10. **Material Identifier Tool** - 识别材料类型（MOF、无机物、有机物等）(material_identifier_tool.py)
11. **Data Validator Tool** - 验证数据完整性和一致性 (data_validator_tool.py)
12. **Structure Validator Tool** - 验证化学结构和SMILES格式 (structure_validator_tool.py)

### 数据库查询工具

13. **PGVector Tool** - PostgreSQL 向量数据库查询，用于 SFT 问答对检索 (pg_vector_tool.py)
14. **GDB Tool** - 阿里云图数据库查询，支持催化剂-污染物关系探索 (gdb_tool.py)

### 工具工厂模式

所有工具通过 **ToolFactory** 类（`src/tools/factory.py`）管理，为不同类型的代理提供专业工具集：
- **材料设计工具**（5个工具） - Materials Project、PubChem、Material Identifier、Structure Validator、Material Search
- **材料评估工具**（6个工具） - 包含 MolPort 用于商业可用性评估
- **材料搜索工具**（3个工具） - 用于合成方法探索
- **机理分析工具**（2个工具） - Materials Project 和 PubChem 用于机理研究
- **操作指导工具**（3个工具） - 安全与环境评估
- **文献提取工具**（5个工具） - 化学信息提取与验证

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



## 最近更新 (2025-12-13)

### 🚀 重大升级：CrewAI 1.7.0
- ✅ **异步执行** - 完整 async/await 支持，使用 `crew.akickoff()`
- ✅ **并行任务** - 3 位评估专家并行运行（快 2.6 倍）
- ✅ **异步工具** - 非阻塞 PubChem 和 Materials Project 工具
- ✅ **性能提升** - 根据工作负载快 2-10 倍
- ✅ **向后兼容** - 原始同步模式仍然支持

### 新功能
- ✅ **异步主程序** - `main_async.py` 支持 4 种执行模式
- ✅ **批量处理** - 10 个材料 43 秒完成（vs 同步 326 秒）
- ✅ **MolPort 集成** - 商业可用性评估
- ✅ **增强测试** - 60+ 测试文件，结构整齐
- ✅ **整洁架构** - 移除冗余文件，优化结构

### 性能指标
```
单个工作流:    33秒 → 21秒  (快 1.57 倍)
批量 10 设计:   326秒 → 43秒 (快 7.5 倍)
3 个评估:       12秒 → 4.6秒 (快 2.6 倍)
5 个 API 查询: 12秒 → 4.2秒 (快 3.0 倍)
```

### 文档
- 📚 **[CrewAI 升级报告](docs/CrewAI升级完成报告.md)** - 完整升级指南
- 📚 **[异步 Crew 示例](examples/async_crew_example.py)** - 学习异步用法
- 📚 **[文档中心](docs/README.md)** - 所有文档
- 📚 **[项目状态](docs/项目状态总览.md)** - 当前状态概览
- 📚 **[MolPort 集成](docs/molport_integration_guide.md)** - MolPort 指南

### 异步模式快速开始
```bash
# 运行异步版本（推荐）
python scripts/main_async.py

# 选择模式:
# 1. 预设工作流（同步）
# 2. 预设工作流（异步）⚡ - 快 2 倍
# 3. 自主模式（同步）
# 4. 自主模式（异步）⚡ - 推荐
```

## [英文版本](README.md)


## 许可证

本项目采用MIT许可证。详情请见[LICENSE](LICENSE)文件。
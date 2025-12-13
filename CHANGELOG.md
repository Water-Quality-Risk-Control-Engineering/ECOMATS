# ECOMATS 更新日志

本文档记录ECOMATS项目的重要更新和变更。

---

## [Unreleased]

### 待优化
- 考虑执行工具冗余优化(详见[工具冗余分析报告](docs/工具冗余分析报告.md))
- (可选)配置PubChem API Key以提高请求速率

---

## [v1.5.0] - 2025-12-13

### 新增 ✨

#### MolPort API集成
- 🎉 **新工具**: MolPort商业可获得性查询工具
  - `molport_availability_tool` - 检查化合物是否可商业购买
  - `molport_search_tool` - 化学结构搜索(精确、相似性、子结构等)
  - `molport_molecule_info_tool` - 获取供应商、价格、库存详细信息
- 📚 创建[MolPort集成指南](docs/molport_integration_guide.md)
- ✅ 完整测试通过(3/3测试用例)

#### 增强的任务分配
- 🔍 优化仅评估模式(evaluation_only)识别逻辑
  - 新增关键词: "三位专家"、"分别打分"、"ABC评估"、"三个ASA"等
  - 添加化学式自动检测(如Fe2O3, TiO2)
  - 修复逻辑优先级问题
- ✅ 测试通过率从1/5提升到5/5

#### 测试和验证
- 🧪 创建`test_api_connectivity.py` - API连接性测试
  - 测试Qwen API ✅
  - 测试Materials Project API ✅
  - 测试PubChem API ✅
  - 测试MolPort API ✅
- 🧪 创建`test_evaluation_only_autonomous.py` - 仅评估功能测试
  - 5个测试用例全部通过 ✅

#### 文档完善
- 📖 创建[项目状态总览](docs/项目状态总览.md)
- 📖 创建[工具冗余分析报告](docs/工具冗余分析报告.md)
- 📖 创建[API Key配置检查报告](docs/API_Key配置检查报告.md)
- 📖 创建[工具连接性测试报告](docs/测试报告-工具连接性.md)
- 📖 创建[自主调度仅评估功能测试报告](docs/测试报告-自主调度仅评估功能.md)
- 📖 创建[文档中心索引](docs/README.md)
- 📖 更新主README.md,反映最新项目状态

### 修复 🐛

#### API配置
- 🔧 修复Qwen模型名称: `qwen3-max` → `qwen-plus`
- 🔧 清理.env中的重复配置项(ENABLE_TOOLS)
- 🔧 补充MolPort API Key配置

#### 代码优化
- 🧹 删除主程序(`scripts/main.py`)中的LLM连通性测试代码(第615-628行)
- 🧹 删除`src/utils/llm_config.py`中的LLM配置日志输出(第70-72行)
- 🧹 优化`src/tools/pubchem_tool.py`:
  - 移除`requests.Session()`对象(避免挂起)
  - 减少超时时间: 30s → 10s
  - 减少请求间隔: 2s → 1s

#### Bug修复
- ✅ 修复qwen3-max模型不支持导致的API调用失败
- ✅ 修复PubChem工具导入挂起问题
- ✅ 修复仅评估模式识别失败(关键词不完整)
- ✅ 修复测试脚本未加载.env环境变量问题

### 变更 🔄

#### 工具架构
- 📦 工具总数: 13个基础工具 + 14个CrewAI包装器
- 📦 新增MolPort工具后,工具集更加完善
- ⚠️ 识别工具冗余问题(详见冗余分析报告)

#### 配置优化
- ⚙️ 统一API Key配置方式
- ⚙️ 完善.env.example配置说明
- ⚙️ 所有必需API Key已配置并验证

---

## [v1.4.0] - 2025-12-09

### 新增
- 📚 创建[MolPort集成指南](docs/molport_integration_guide.md)(初版)
- 📚 创建[Tool Redundancy Analysis](docs/tool_redundancy_analysis.md)(英文版)

---

## [v1.3.0] - 2025-12-08

### 新增
- 📚 创建[SFT与GraphRAG混合系统实施方案](docs/实施方案_SFT与GraphRAG混合系统.md)
- 🎯 规划系统高级功能实施路线

---

## [v1.2.0] - 2025-10-31

### 新增
- 📚 创建[Materials Project工具使用指南](docs/materials_project_tool_usage.md)
- 🔧 优化Materials Project API调用性能

---

## [v1.1.0] - 2025-10-29

### 新增
- 📚 创建[改进的工具调用逻辑](docs/improved_tool_calling_logic.md)
- 🔧 优化CrewAI工具调用机制

---

## [v1.0.0] - 2025-10 (初始发布)

### 核心功能
- 🎉 基于CrewAI的多智能体系统
- 🤖 10个专业智能体(材料设计、评估、合成等)
- 🔧 8个数据库查询工具
- 📊 完整的评估体系(5个维度,加权评分)
- 🔄 迭代设计优化机制
- 📈 三盲审查和一致性分析
- 🎯 任务分配机制(自主调度+预设流程)

### 技术栈
- CrewAI框架
- Qwen LLM
- Materials Project API
- PubChem API

---

## 版本规范

本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)规范:

- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 更新类型标识

- ✨ **新增** - 新功能、新工具、新智能体
- 🐛 **修复** - Bug修复、问题解决
- 🔄 **变更** - 功能变更、API调整
- 🧹 **优化** - 代码优化、性能提升
- 📚 **文档** - 文档更新、说明完善
- 🧪 **测试** - 测试添加、测试优化
- ⚙️ **配置** - 配置调整、环境变更
- 🔧 **工具** - 工具更新、工具优化

---

## 链接

- [项目README](README.md)
- [文档中心](docs/README.md)
- [项目状态总览](docs/项目状态总览.md)

---

**维护者**: ECOMATS开发团队  
**最后更新**: 2025-12-13

# ECOMATS - 基于CrewAI的水处理材料设计多智能体系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-Powered-green)](#)

这是一个使用CrewAI框架构建的多智能体系统，专门用于水处理材料的设计和优化。

## 项目特色

- 基于CrewAI框架构建的多智能体协作系统
- 专门针对水处理材料设计领域优化
- 支持材料设计、评估和优化的完整工作流
- 模块化设计，易于扩展和定制
- 采用全面评估模式，每个专家评估所有维度
- 使用详细的Prompt文件定义专家行为
- 支持智能体任务分配机制，根据任务类型自动选择合适的智能体

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

## 工作模式

系统支持两种工作模式：

### 1. 顺序执行模式（默认）
任务按照预定义顺序执行，当前包括材料设计和评估两个主要阶段。

工作流程：
1. 材料设计专家设计材料方案
2. 评估专家A、B、C并行评估材料方案
3. 最终验证专家综合评估结果并生成最终报告
4. 机理分析专家分析材料的催化机理
5. 合成方法专家设计材料的合成方法

### 2. 分层执行模式
由协调专家动态决定任务执行顺序，实现更灵活的任务调度。

评估维度及权重：
- 催化性能（权重50%）
- 经济可行性（权重10%）
- 环境友好性（权重10%）
- 技术可行性（权重10%）
- 结构合理性（权重20%）

## 智能体任务分配机制

系统实现了智能体任务分配机制，可以根据任务类型自动选择合适的智能体：

1. **任务类型映射** - 系统定义了任务类型与智能体类型的映射关系
2. **智能体注册** - 所有可用智能体都会注册到任务分配器中
3. **自动分配** - 根据任务类型自动选择合适的智能体执行任务
4. **灵活扩展** - 可以轻松添加新的任务类型和智能体类型

## Prompt文件

每个专家都有对应的Prompt文件，定义了专家的详细行为和评估标准：
- [coordinator_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/coordinator_prompt.md) - 协调者Prompt
- [material_designer_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/material_designer_prompt.md) - 材料设计专家Prompt
- [expert_a_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/expert_a_prompt.md) - 专家A Prompt
- [expert_b_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/expert_b_prompt.md) - 专家B Prompt
- [expert_c_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/expert_c_prompt.md) - 专家C Prompt
- [final_validator_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/final_validator_prompt.md) - 最终验证专家Prompt
- [literature_processor_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/literature_processor_prompt.md) - 文献处理专家Prompt
- [mechanism_expert_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/mechanism_expert_prompt.md) - 机理分析专家Prompt
- [synthesis_expert_prompt.md](file:///home/axlhuang/crewai_ecomats/prompt/synthesis_expert_prompt.md) - 合成方法专家Prompt

这些Prompt文件现在统一存放在[prompt](file:///home/axlhuang/crewai_ecomats/prompt)目录中，与[agents](file:///home/axlhuang/crewai_ecomats/agents)目录同级，在系统运行时会被自动加载，作为各专家的详细行为指导。

## 使用说明

1. 复制 `.env.example` 文件为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 在 `.env` 文件中配置你的API密钥:
   ```env
   QWEN_API_KEY=你的Qwen API密钥
   ```

3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

4. 运行系统:
   ```bash
   python main.py
   ```

5. 测试顺序执行模式:
   ```bash
   python test_problem.py
   ```

## 开发指南

### 添加新智能体

1. 在 `agents/` 目录下创建新的智能体文件
2. 在 `prompt/` 目录下创建对应的Prompt文件
3. 在智能体文件中实现Prompt文件加载功能
4. 在 `main.py` 中导入并使用新智能体
5. 在任务分配器中注册新智能体类型

### 扩展评价维度

1. 修改各专家的提示词文件
2. 更新评价维度和权重分配
3. 调整评价标准和输出格式

### 添加新任务类型

1. 在 `tasks/` 目录下创建新的任务文件
2. 在任务分配器中添加任务类型与智能体类型的映射关系
3. 在主程序中创建并执行新任务

## 致谢

本项目使用了以下优秀框架和工具：

- [CrewAI](https://www.crewai.com/) - 多智能体协作框架
- [DashScope](https://dashscope.aliyuncs.com/) - 阿里云模型服务
- [LangChain](https://www.langchain.com/) - 大语言模型应用开发框架

## 最近优化

### 代码结构优化
- 创建了基础智能体类(`BaseAgent`)，减少代码重复
- 重构了所有专家类以继承基础类
- 删除了冗余的测试文件`test_sequential_execution.py`
- 删除了空的`models`目录

### 功能改进
- 保持了所有现有功能的完整性
- 提高了代码的可维护性和扩展性
- 简化了智能体的实现方式

## 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。
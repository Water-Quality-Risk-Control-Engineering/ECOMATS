# ECOMATS

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.7.0-green)](#)

**ECOMATS** — 基于 CrewAI 1.7.0 的水处理材料设计多智能体系统。

## 特性

- 🤖 **10 个专业智能体** — 设计、评估、合成和操作指导
- 🔬 **14 个集成工具** — Materials Project、PubChem、MolPort、PNEC 等
- ⚡ **异步执行** — 基于 CrewAI 异步支持的并行任务处理
- 🌐 **多语言支持** — 中英文提示词系统

## 快速开始

```bash
# 1. 克隆并配置
cp .env.example .env
# 编辑 .env 填入 API 密钥 (QWEN_API_KEY, MATERIALS_PROJECT_API_KEY)

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python scripts/main_async.py
```

## 智能体

| 智能体 | 职责 |
|--------|------|
| Task Organizing | 协调智能体（仅自主调度模式） |
| Creative Designing | 设计材料方案 |
| Assessment Screening A/B/C | 并行评估专家 |
| Assessment Screening Overall | 综合评估结果 |
| Mechanism Mining | 分析催化机理 |
| Synthesis Guiding | 设计合成方法 |
| Operation Suggesting | 提供操作指导 |
| Extracting | 处理技术文献 |

## 评估维度

| 维度 | 权重 |
|------|------|
| 催化性能 | 50% |
| 结构合理性 | 20% |
| 经济可行性 | 10% |
| 环境友好性 | 10% |
| 技术可行性 | 10% |

## 配置

`.env` 必需的 API 密钥：
- `QWEN_API_KEY` — 阿里云通义千问 LLM
- `MATERIALS_PROJECT_API_KEY` — Materials Project 数据库

可选：
- `MOLPORT_API_KEY` — 商业可用性查询
- `EAS_ENDPOINT` / `EAS_TOKEN` — 自部署模型

## 项目结构

```
ECOMATS/
├── src/
│   ├── agents/          # 10 个智能体实现
│   ├── tasks/           # 任务定义
│   ├── tools/           # 14 个数据库查询工具
│   ├── locales/         # 中英文提示词和任务
│   └── utils/           # 工具函数（日志、错误码、LLM配置）
├── scripts/
│   ├── main.py          # 同步模式入口
│   ├── main_async.py    # 异步模式入口（推荐）
│   └── workflow/        # 模块化工作流组件
│       ├── patches.py       # CrewAI异步兼容补丁
│       ├── embeddings.py    # DashScope嵌入向量
│       └── callback_factory.py
└── .env.example         # 环境变量模板
```

## 环境要求

- Python 3.11 或 3.12
- Linux / macOS / WSL2（Windows 用户请参阅[兼容性指南](docs/Windows_Compatibility_Guide.md)）

## [English Version](README.md)

## 许可证

MIT 许可证 — 详见 [LICENSE](LICENSE) 文件。

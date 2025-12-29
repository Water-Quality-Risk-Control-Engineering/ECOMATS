# ECOMATS

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.7.0-green)](#)

**ECOMATS** — A multi-agent system for water treatment material design, built with CrewAI 1.7.0.

## Features

- 🤖 **10 Specialized Agents** — Design, evaluation, synthesis, and operation guidance
- 🔬 **14 Integrated Tools** — Materials Project, PubChem, MolPort, PNEC, and more
- ⚡ **Async Execution** — Parallel task processing with CrewAI async support
- 🌐 **Multi-language** — English and Chinese prompt system

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your API keys (QWEN_API_KEY, MATERIALS_PROJECT_API_KEY)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python scripts/main_async.py
```

## Agents

| Agent | Role |
|-------|------|
| Task Organizing | Coordinates agents (autonomous mode only) |
| Creative Designing | Designs material solutions |
| Assessment Screening A/B/C | Parallel evaluation experts |
| Assessment Screening Overall | Synthesizes evaluation results |
| Mechanism Mining | Analyzes catalytic mechanisms |
| Synthesis Guiding | Designs synthesis methods |
| Operation Suggesting | Provides operational guidance |
| Extracting | Processes technical literature |

## Evaluation Dimensions

| Dimension | Weight |
|-----------|--------|
| Catalytic Performance | 50% |
| Structural Rationality | 20% |
| Economic Feasibility | 10% |
| Environmental Friendliness | 10% |
| Technical Feasibility | 10% |

## Configuration

Required API keys in `.env`:
- `QWEN_API_KEY` — Alibaba Cloud Qwen LLM
- `MATERIALS_PROJECT_API_KEY` — Materials Project database

Optional:
- `MOLPORT_API_KEY` — Commercial availability queries
- `EAS_ENDPOINT` / `EAS_TOKEN` — Self-deployed model

## Project Structure

```
ECOMATS/
├── src/
│   ├── agents/          # 10 agent implementations
│   ├── tasks/           # Task definitions
│   ├── tools/           # 14 database query tools
│   ├── locales/         # EN/ZH prompts and tasks
│   └── utils/           # Utilities (logging, error codes, LLM config)
├── scripts/
│   ├── main.py          # Sync mode entry
│   ├── main_async.py    # Async mode entry (recommended)
│   └── workflow/        # Modular workflow components
│       ├── patches.py       # CrewAI async compatibility
│       ├── embeddings.py    # DashScope embedding
│       └── callback_factory.py
└── .env.example         # Environment template
```

## Requirements

- Python 3.11 or 3.12
- Linux / macOS / WSL2 (Windows: see [compatibility guide](docs/Windows_Compatibility_Guide.md))

## [中文版本](README_zh.md)

## License

MIT License — see [LICENSE](LICENSE) for details.

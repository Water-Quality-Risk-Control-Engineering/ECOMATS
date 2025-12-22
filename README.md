# ECOMATS - Multi-Agent System for Water Treatment Material Design Based on CrewAI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.7.0-green)](#)
[![Async](https://img.shields.io/badge/Async-Enabled-orange)](#)

This is a high-performance multi-agent system built using the **CrewAI 1.7.0** framework with **async support**, specifically designed for the design, evaluation, and optimization of water treatment materials. The system integrates chemical database tools such as Materials Project and PubChem, enabling intelligent material design based on real material data.

**⚡ Performance**: Up to **7.5x faster** with async execution and parallel task processing.

## Project Features

### 🚀 Performance & Architecture
- **CrewAI 1.7.0** with full async support (2-10x performance boost)
- **Parallel task execution** for 3 evaluation experts (2.6x faster)
- **Async tools** for non-blocking API calls (PubChem, Materials Project)
- **Batch processing** support for multiple material designs
- Multi-agent collaboration system with intelligent task scheduling
- Modular design for easy expansion and customization

### 🎯 Core Capabilities
- Specifically optimized for water treatment material design
- Complete workflow from material design to evaluation and optimization
- Comprehensive evaluation mode where each expert evaluates all dimensions
- Triple-blind review and consistency analysis mechanisms
- Iterative design optimization with feedback loops
- Agent task allocation mechanism with automatic mode detection

### 🛠️ Tools & Integration
- 13+ specialized AI tools for material property querying
- Async PubChem and Materials Project tools
- MolPort API for commercial availability assessment
- Comprehensive data validation and structure verification
- Supports Alibaba Cloud EAS self-deployed model integration
- Detailed Prompt files define expert behaviors

## Project Structure

```
ECOMATS/
├── src/                       # Source code directory
│   ├── agents/                # Agent implementations (10 specialized agents)
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
│   │   └── task_organizing_agent.py   # Task organizing agent with intent recognition & agent registry
│   ├── config/                # Configuration files
│   │   └── config.py
│   ├── prompts/               # Prompt files
│   │   ├── coordinator_prompt.md
│   │   ├── enhanced_final_validator_prompt.md  # ASA Overall synthesis prompt
│   │   ├── expert_template_prompt.md           # Parameterized template for A/B/C experts
│   │   ├── intent_recognition_prompt.md        # User intent recognition
│   │   ├── literature_processor_prompt.md
│   │   ├── material_designer_prompt.md
│   │   ├── mechanism_expert_prompt.md          # Mechanism analysis expert
│   │   ├── operation_suggesting_prompt.md
│   │   └── synthesis_expert_prompt.md
│   ├── tasks/                 # Task definitions
│   │   ├── base_task.py
│   │   ├── design_task.py
│   │   ├── evaluation_task.py
│   │   ├── final_validation_task.py
│   │   ├── mechanism_analysis_task.py
│   │   ├── operation_suggesting_task.py
│   │   └── synthesis_method_task.py
│   ├── tools/                 # Tool implementations
│   │   ├── __init__.py
│   │   ├── factory.py                          # Tool factory for centralized management
│   │   ├── async_pubchem_tool.py               # ⚡ Async PubChem (3x faster)
│   │   ├── async_materials_project_tool.py     # ⚡ Async Materials Project
│   │   ├── pubchem_tool.py                     # PubChem API integration
│   │   ├── materials_project_tool.py           # Materials Project API integration
│   │   ├── molport_tool.py                     # MolPort API for commercial availability
│   │   ├── name2cas_tool.py                    # Name to CAS number conversion
│   │   ├── cid2properties_tool.py              # CID to properties query
│   │   ├── name2properties_tool.py             # Name to properties query
│   │   ├── formula2properties_tool.py          # Formula to properties query
│   │   ├── material_search_tool.py             # Material database search
│   │   ├── pnec_tool.py                        # PNEC environmental toxicity tool
│   │   ├── material_identifier_tool.py         # Material type identification
│   │   ├── data_validator_tool.py              # Data validation tool
│   │   ├── structure_validator_tool.py         # Chemical structure validation
│   │   ├── crewai_materials_project_tool.py    # CrewAI wrapper
│   │   ├── crewai_pubchem_tool.py              # CrewAI wrapper
│   │   ├── crewai_molport_tool.py              # CrewAI wrapper (3 tools)
│   │   ├── crewai_name2cas_tool.py             # CrewAI wrapper
│   │   ├── crewai_cid2properties_tool.py       # CrewAI wrapper
│   │   ├── crewai_name2properties_tool.py      # CrewAI wrapper
│   │   ├── crewai_formula2properties_tool.py   # CrewAI wrapper
│   │   ├── crewai_material_search_tool.py      # CrewAI wrapper
│   │   ├── crewai_pnec_tool.py                 # CrewAI wrapper
│   │   ├── crewai_material_identifier_tool.py  # CrewAI wrapper
│   │   ├── crewai_data_validator_tool.py       # CrewAI wrapper
│   │   ├── crewai_structure_validator_tool.py  # CrewAI wrapper
│   │   ├── pg_vector_tool.py                   # PostgreSQL vector database tool
│   │   ├── crewai_pg_vector_tool.py            # CrewAI wrapper for PGVector
│   │   ├── gdb_tool.py                         # Graph database (Aliyun GDB) tool
│   │   └── crewai_gdb_tool.py                  # CrewAI wrapper for GDB
│   └── utils/                 # Utility functions
│       ├── llm_config.py
│       ├── prompt_loader.py
│       ├── context_store.py              # Context storage for tool caching
│       ├── workflow_monitor.py           # Workflow monitoring and reporting
│       ├── tool_call_spec.py             # Tool call specifications
│       ├── assessment_tool_executor.py   # Assessment tool execution logic
│       └── assessment_scoring_logic.py   # Assessment scoring calculations
├── scripts/                   # Script files
│   ├── main.py                # Main program entry (sync mode)
│   ├── main_async.py          # ⚡ Async main program (recommended, 2-3x faster)
│   ├── test_molport_tool.py   # MolPort API connectivity test
│   └── (other scripts)
├── tests/                     # Unified test directory
│   ├── integration/           # Integration tests
│   ├── tools/                 # Tool-specific tests
│   ├── test_crewai_1.7.0.py  # CrewAI 1.7.0 feature tests
│   ├── test_async_tools.py   # Async tools performance tests
│   └── (60+ test files)
├── examples/                  # Example files
│   ├── async_crew_example.py  # ⚡ Async Crew usage example
│   └── task_allocation_example.py
├── docs/                      # Documentation directory
│   ├── README.md              # Documentation index
│   ├── CrewAI升级完成报告.md   # ⚡ CrewAI 1.7.0 upgrade summary
│   ├── sft/                   # SFT generation guides
│   ├── archives/              # Archived documentation
│   │   └── crewai-upgrade/    # CrewAI upgrade details
│   ├── molport_integration_guide.md
│   ├── tool_redundancy_analysis.md
│   └── API_Key配置检查报告.md
├── .env.example               # Environment variable example
├── requirements.txt           # Dependency list
└── README.md                 # Project documentation (Chinese)
```

## Core Agents

The system includes the following core agents:

1. **Task_Organizing_agent** - Organizes and coordinates the work of experts to ensure efficient task completion
2. **Creative_Designing_agent** - Designs and optimizes water treatment material solutions
3. **Assessment_Screening_agent_A** - Comprehensively evaluates all aspects of material solutions
4. **Assessment_Screening_agent_B** - Comprehensively evaluates all aspects of material solutions
5. **Assessment_Screening_agent_C** - Comprehensively evaluates all aspects of material solutions
6. **Assessment_Screening_agent_Overall** - Synthesizes evaluation results from all experts, performs weighted calculations, generates final material evaluation reports, and provides improvement suggestions
7. **Extracting_agent** - Processes and analyzes relevant technical literature
8. **Mechanism_Mining_agent** - Analyzes the catalytic mechanisms and action principles of materials
9. **Synthesis_Guiding_agent** - Designs synthesis methods and processes for materials
10. **Operation_Suggesting_agent** - Provides detailed operational guidance for material synthesis, production, and application

## Working Modes

The system supports two working modes:

### 1. Preset Workflow Mode (Default)
Tasks are executed in a predefined order, including material design, evaluation, validation, mechanism analysis, and synthesis method design.

Workflow:
1. Material Designer creates material solutions
2. Experts A, B, and C evaluate material solutions in parallel
3. Final Validator synthesizes evaluation results and generates final reports
4. Mechanism Expert analyzes the catalytic mechanisms of materials
5. Synthesis Method Expert designs synthesis methods for materials
6. Operation Suggesting Agent provides detailed operational guidance

### 2. Agent Autonomous Scheduling Mode
The coordinator dynamically determines task execution order for more flexible task scheduling.

## Evaluation Dimensions and Weights

- Catalytic Performance (50% weight)
- Economic Feasibility (10% weight)
- Environmental Friendliness (10% weight)
- Technical Feasibility (10% weight)
- Structural Rationality (20% weight)

## Usage Instructions

### Requirements

- **Python 3.11 or 3.12** (Recommended)
  - ⚠️ Python 3.13 has known compatibility issues with `chromadb` on Windows
  - Python 3.10 may work but is not tested

### Platform Compatibility

**Recommended**: Linux / macOS / WSL2
**Windows Users**: See [Windows Compatibility Guide](docs/Windows_Compatibility_Guide.md) for `signal.SIGHUP` compatibility issues and solutions.

### Setup Steps

1. Copy `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure your API keys in the `.env` file:
   ```env
   # Required: Qwen LLM API
   QWEN_API_KEY=Your Qwen API key
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_MODEL_NAME=qwen-plus
   
   # Required: Materials Project API
   MATERIALS_PROJECT_API_KEY=Your Materials Project API key
   
   # Optional: MolPort API (for commercial availability queries)
   MOLPORT_API_KEY=Your MolPort API key
   
   # Optional: PubChem API (public API, key not required but recommended)
   PUBCHEM_API_KEY=Your PubChem API key
   
   # Optional: PostgreSQL Vector DB (for SFT vector search)
   PG_HOST=your_host
   PG_PORT=5432
   PG_DATABASE=your_database
   PG_USER=your_username
   PG_PASSWORD=your_password
   
   # Optional: Graph DB (for Aliyun GDB graph queries)
   GDB_HOST=your_host
   GDB_PORT=3734
   GDB_USERNAME=your_username
   GDB_PASSWORD=your_password
   
   # System configuration
   ENABLE_TOOLS=true
   VERBOSE=True
   ```

3. (Optional) Configure Alibaba Cloud EAS self-deployed model:
   ```env
   EAS_ENDPOINT=Your EAS model endpoint URL
   EAS_TOKEN=Your EAS model token
   EAS_MODEL_NAME=Your EAS model name
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the system:
   
   **Option A: Async Mode (⚡ Recommended, 2-3x faster)**
   ```bash
   python scripts/main_async.py
   ```
   
   **Option B: Sync Mode (Original, backward compatible)**
   ```bash
   python scripts/main.py
   ```
   
   **Performance Comparison**:
   - Async Mode: ~21 seconds for full workflow
   - Sync Mode: ~33 seconds for full workflow
   - Batch Design (10 materials): 43s vs 326s (7.5x faster)

## Agent Tool Integration

The system integrates the following database query tools that agents can automatically invoke as needed:

### Core Database Tools

1. **Materials Project Tool** - Accesses materials science database to obtain material properties, including band gap, formation energy, crystal structure, etc. Optimized with field selection and chunking to improve query performance. (materials_project_tool.py)
2. **PubChem Tool** - Queries chemical compound information, including CAS numbers, molecular weights, SMILES, InChI, and other detailed properties. Enhanced with InChIKey search capability and improved molecular formula validation. (pubchem_tool.py)
3. **MolPort Tool** - NEW! Commercial availability assessment tool with three specialized functions:
   - **Compound Availability Checker** - Check if compounds are commercially available
   - **Chemical Structure Search** - Search for similar compounds (exact, similarity, substructure)
   - **Molecule Info Loader** - Get detailed supplier, pricing, and stock information

### Specialized Query Tools

4. **Name2CAS Tool** - Converts material names to CAS numbers (name2cas_tool.py)
5. **Name2Properties Tool** - Queries physicochemical properties by material name (name2properties_tool.py)
6. **CID2Properties Tool** - Queries properties by PubChem CID (cid2properties_tool.py)
7. **Formula2Properties Tool** - Predicts properties based on chemical formula (formula2properties_tool.py)
8. **MaterialSearch Tool** - Retrieves performance data of similar materials (material_search_tool.py)

### Validation and Analysis Tools

9. **PNEC Tool** - Queries Predicted No Effect Concentration data for chemical substances, used for environmental risk assessment (pnec_tool.py)
10. **Material Identifier Tool** - Identifies material type (MOF, inorganic, organic, etc.) (material_identifier_tool.py)
11. **Data Validator Tool** - Validates data completeness and consistency (data_validator_tool.py)
12. **Structure Validator Tool** - Validates chemical structures and SMILES format (structure_validator_tool.py)

### Database Query Tools

13. **PGVector Tool** - PostgreSQL vector database queries for SFT Q&A pair retrieval (pg_vector_tool.py)
14. **GDB Tool** - Aliyun Graph Database queries for catalyst-pollutant relationship exploration (gdb_tool.py)

### Tool Factory Pattern

All tools are managed through the **ToolFactory** class (`src/tools/factory.py`), which provides specialized tool sets for different agent types:
- **Unified Assessment Tools** (4 tools) - Materials Project, PubChem, PNEC, MolPort (shared by ASA A/B/C)
- **Material Design Tools** (2 tools) - Materials Project, PubChem for design
- **Material Search Tools** (2 tools) - For synthesis method exploration
- **Literature Extraction Tools** (3 tools) - Chemical information extraction and validation

## Iterative Design Mechanism

The system implements an intelligent iterative design mechanism:

1. **Evaluation-Driven Optimization** - Automatically identifies design deficiencies based on expert evaluations
2. **Feedback Loop** - Integrates evaluation feedback into the next round of design
3. **Multi-Round Optimization** - Supports up to 3 rounds of design iteration optimization
4. **Quality Control** - Sets a minimum acceptable score threshold (7.0 points)

## Consistency Analysis Mechanism

The system implements triple-blind review and consistency analysis mechanisms:

1. **Triple-Blind Review** - Three evaluation experts score independently
2. **Standard Deviation Calculation** - Calculates the standard deviation of scores across dimensions
3. **Consistency Coefficient** - Calculates consistency coefficient Cj = 1 - (SD/mean)
4. **Fused Scoring** - Uses consistency coefficient to adjust final scores

## Development Guide

### Adding New Agents

1. Create a new agent file in the `agents/` directory, inheriting from the `BaseAgent` class
2. Create a corresponding Prompt file in the `prompt/` directory
3. Use `PromptLoader` to load the Prompt file in the agent file
4. Import and use the new agent in `main.py`
5. Register the new agent type in the task allocator

### Extending Evaluation Dimensions

1. Modify the prompt files of each expert to add new evaluation dimensions
2. Update evaluation dimensions and weight allocation
3. Adjust evaluation criteria and output format to accommodate new dimensions

### Adding New Task Types

1. Create a new task file in the `tasks/` directory, inheriting from the `BaseTask` class
2. Add task type to agent type mapping in the task allocator
3. Create and execute new tasks in the main program

### Integrating New Tools

1. Create a new tool file in the `tools/` directory
2. Implement the specific functionality of the tool
3. Integrate the new tool into agents through CrewAI's tool mechanism
4. Update the prompt files of relevant agents to guide their use of the new tool



## Recent Updates (2025-12-20)

### 🚀 Major Upgrade: CrewAI 1.7.0
- ✅ **Async Execution** - Full async/await support with `crew.akickoff()`
- ✅ **Parallel Tasks** - 3 evaluation experts run concurrently (2.6x faster)
- ✅ **Async Tools** - Non-blocking PubChem and Materials Project tools
- ✅ **Performance Boost** - 2-10x faster depending on workload
- ✅ **Backward Compatible** - Original sync mode still supported

### New Features
- ✅ **Async Main Program** - `main_async.py` with 4 execution modes
- ✅ **Batch Processing** - Process 10 materials in 43s (vs 326s sync)
- ✅ **MolPort Integration** - Commercial availability assessment
- ✅ **Enhanced Testing** - 60+ test files, organized structure
- ✅ **Clean Architecture** - Removed redundant files, optimized structure

### Performance Metrics
```
Single Workflow:  33s → 21s  (1.57x faster)
Batch 10 designs: 326s → 43s (7.5x faster)
3 Evaluations:    12s → 4.6s (2.6x faster)
5 API Queries:    12s → 4.2s (3.0x faster)
```

### Documentation
- 📚 **[CrewAI Upgrade Report](docs/CrewAI升级完成报告.md)** - Complete upgrade guide
- 📚 **[Async Crew Example](examples/async_crew_example.py)** - Learn async usage
- 📚 **[Documentation Center](docs/README.md)** - All documentation
- 📚 **[Project Status](docs/项目状态总览.md)** - Current status overview
- 📚 **[MolPort Integration](docs/molport_integration_guide.md)** - MolPort guide

### Quick Start with Async
```bash
# Run async version (recommended)
python scripts/main_async.py

# Select mode:
# 1. Preset workflow (sync)
# 2. Preset workflow (async) ⚡ - 2x faster
# 3. Autonomous mode (sync)
# 4. Autonomous mode (async) ⚡ - recommended
```

## [中文版本](README_zh.md)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
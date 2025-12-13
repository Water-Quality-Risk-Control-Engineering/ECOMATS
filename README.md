# ECOMATS - Multi-Agent System for Water Treatment Material Design Based on CrewAI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![CrewAI](https://img.shields.io/badge/CrewAI-Powered-green)](#)

This is a multi-agent system built using the CrewAI framework, specifically designed for the design, evaluation, and optimization of water treatment materials. The system integrates chemical database tools such as Materials Project and PubChem, enabling intelligent material design based on real material data.

## Project Features

- Multi-agent collaboration system built on the CrewAI framework
- Specifically optimized for water treatment material design
- Supports complete workflow from material design to evaluation and optimization
- Modular design for easy expansion and customization
- Comprehensive evaluation mode where each expert evaluates all dimensions
- Detailed Prompt files define expert behaviors
- Agent task allocation mechanism that automatically selects appropriate agents based on task types
- Supports Alibaba Cloud EAS self-deployed model integration
- Integrates chemical database tools to validate material designs
- Implements triple-blind review and consistency analysis mechanisms
- Supports iterative design optimization
- Implements 13+ specialized AI tools to enhance material property querying capabilities
- Integrates MolPort API for commercial availability assessment of chemical compounds
- Comprehensive data validation and structure verification tools

## Project Structure

```
ECOMATS/
├── src/                       # Source code directory
│   ├── agents/                # Agent implementations
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
│   │   ├── task_organizing_agent.py
│   │   └── task_allocator.py         # Enhanced task allocation with evaluation-only mode
│   ├── config/                # Configuration files
│   │   └── config.py
│   ├── prompts/               # Prompt files
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
│   │   ├── materials_project_tool.py           # Materials Project API integration
│   │   ├── pubchem_tool.py                     # PubChem API integration
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
│   │   └── crewai_structure_validator_tool.py  # CrewAI wrapper
│   └── utils/                 # Utility functions
│       ├── llm_config.py
│       ├── prompt_loader.py
│       ├── context_store.py              # Context storage for tool caching
│       ├── assessment_tool_executor.py   # Assessment tool execution logic
│       └── assessment_scoring_logic.py   # Assessment scoring calculations
├── scripts/                   # Script files
│   ├── main.py                # Main program entry
│   ├── test_molport_tool.py   # MolPort API connectivity test
│   └── (other test scripts)
├── tests/                     # Unified test directory
│   ├── test_api_connectivity.py           # API connectivity tests
│   ├── test_evaluation_only_autonomous.py # Evaluation-only mode tests
│   └── (other test files)
├── docs/                      # Documentation directory
│   ├── molport_integration_guide.md       # MolPort integration guide
│   ├── 工具冗余分析报告.md                   # Tool redundancy analysis report
│   └── API_Key配置检查报告.md                # API Key configuration check report
├── examples/                  # Example files
│   └── task_allocation_example.py
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
   ```bash
   python scripts/main.py
   ```

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

### Tool Factory Pattern

All tools are managed through the **ToolFactory** class, which provides specialized tool sets for different agent types:
- Material Design Tools
- Material Assessment Tools (includes MolPort for economic viability)
- Material Search Tools
- Operation Guidance Tools
- Literature Extraction Tools
- Final Validation Tools

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

### Tool Factory Pattern

The system implements a tool factory pattern to manage and provide tools to agents:

1. **ToolFactory Class** - Centralized tool management in `src/tools/factory.py`
2. **Specialized Tool Sets** - Pre-defined tool sets for different agent types:
   - Material Design Tools (5 tools)
   - Material Assessment Tools (7 tools, includes MolPort)
   - Material Search Tools (4 tools)
   - Operation Guidance Tools (4 tools)
   - Literature Extraction Tools (5 tools)
   - Final Validation Tools (1 tool)
3. **Consistent Tool Interface** - All tools follow CrewAI's BaseTool interface
4. **Easy Tool Management** - Simplified tool addition and removal through the factory pattern
5. **Context Caching** - Integrated context storage for improved performance

## Recent Updates (2025-12-13)

### New Features
- ✅ **MolPort API Integration** - Added commercial availability assessment for chemical compounds
- ✅ **Enhanced Task Allocation** - Improved evaluation-only mode recognition with chemical formula detection
- ✅ **Comprehensive Testing** - Added API connectivity tests and evaluation-only mode tests
- ✅ **Tool Analysis** - Created detailed tool redundancy analysis report
- ✅ **API Configuration** - Complete API key configuration and validation

### System Status
- ✅ All API connections tested and verified
- ✅ MolPort tool fully functional (availability, search, pricing)
- ✅ Task allocation supports intelligent mode detection
- ✅ All core tools operational with proper API keys

### Documentation
- 📚 [Project Status Overview](docs/项目状态总览.md) - **Start here for current project status**
- 📚 [Documentation Center](docs/README.md) - Complete documentation index
- 📚 [MolPort Integration Guide](docs/molport_integration_guide.md)
- 📚 [Tool Redundancy Analysis Report](docs/工具冗余分析报告.md)
- 📚 [API Key Configuration Check Report](docs/API_Key配置检查报告.md)

## [中文版本](README_zh.md)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
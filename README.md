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
- Implements 5 specialized AI tools to enhance material property querying capabilities

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
│   │   ├── coordinator.py
│   │   └── task_allocator.py
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
│   └── utils/                 # Utility functions
│       ├── llm_config.py
│       └── prompt_loader.py
├── scripts/                   # Script files
│   ├── main.py                # Main program entry
│   ├── generate_catalysts.py  # Catalyst generation script
│   ├── generate_catalysts_advanced.py # Advanced catalyst generation script
│   ├── run_test.py            # Test running script
│   └── test_new_tools.py      # New tools test script
├── examples/                  # Example files
│   └── task_allocation_example.py
├── .env.example               # Environment variable example
├── requirements.txt           # Dependency list
└── README.md                 # Project documentation (Chinese)
```

## Core Agents

The system includes the following core agents:

1. **coordinator** - Coordinates the work of experts to ensure efficient task completion
2. **Creative_Designing_agent** - Designs and optimizes water treatment material solutions
3. **Assessment_Screening_agent_A** - Comprehensively evaluates all aspects of material solutions
4. **Assessment_Screening_agent_B** - Comprehensively evaluates all aspects of material solutions
5. **Assessment_Screening_agent_C** - Comprehensively evaluates all aspects of material solutions
6. **Assessment_Screening_agent_Overall** - Synthesizes evaluation results from all experts, performs weighted calculations, and generates final material evaluation reports
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
   QWEN_API_KEY=Your Qwen API key
   MATERIALS_PROJECT_API_KEY=Your Materials Project API key (optional)
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

1. **Materials Project Tool** - Accesses materials science database to obtain material properties, including band gap, formation energy, crystal structure, etc. (materials_project_tool.py)
2. **PubChem Tool** - Queries chemical compound information, including CAS numbers, molecular weights, SMILES, etc. (pubchem_tool.py)
3. **Name2CAS Tool** - Converts material names to CAS numbers (name2cas_tool.py)
4. **Name2Properties Tool** - Queries physicochemical properties by material name (name2properties_tool.py)
5. **CID2Properties Tool** - Queries properties by PubChem CID (cid2properties_tool.py)
6. **Formula2Properties Tool** - Predicts properties based on chemical formula (formula2properties_tool.py)
7. **MaterialSearch Tool** - Retrieves performance data of similar materials (material_search_tool.py)
8. **PNEC Tool** - Queries Predicted No Effect Concentration data for chemical substances, used for environmental risk assessment (pnec_tool.py)

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

## [中文版本](README_zh.md)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
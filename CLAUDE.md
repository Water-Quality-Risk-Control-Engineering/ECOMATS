# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ECOMATS is a multi-agent system for water treatment material design built using the CrewAI framework. The system integrates chemical databases like Materials Project and PubChem to enable intelligent material design based on real material data.

Key features:
- Multi-agent collaboration system built on CrewAI
- Specifically optimized for water treatment material design
- Supports complete workflow from material design to evaluation and optimization
- Implements triple-blind review and consistency analysis mechanisms
- Supports iterative design optimization with up to 3 rounds
- Integrates 8 specialized database query tools for material property lookup

## Architecture

The system follows a modular architecture with these core components:

1. **Agents** (`src/agents/`) - Specialized AI agents for different roles:
   - Creative Designing Agent - Designs water treatment materials
   - Assessment Screening Agents (A, B, C) - Evaluate materials from different perspectives
   - Assessment Screening Agent Overall - Synthesizes evaluation results
   - Mechanism Mining Agent - Analyzes catalytic mechanisms
   - Synthesis Guiding Agent - Designs synthesis methods
   - Operation Suggesting Agent - Provides operational guidance
   - Task Organizing Agent - Coordinates workflow
   - Task Allocator - Dynamically assigns tasks

2. **Tasks** (`src/tasks/`) - Defines specific work units:
   - Design Task - Creates material solutions
   - Evaluation Task - Assesses material properties
   - Final Validation Task - Generates comprehensive reports
   - Mechanism Analysis Task - Analyzes reaction mechanisms
   - Synthesis Method Task - Designs preparation processes
   - Operation Suggesting Task - Provides implementation guidance

3. **Tools** (`src/tools/`) - Database integration tools:
   - Materials Project Tool - Accesses materials science database
   - PubChem Tool - Queries chemical compound information
   - Name2CAS Tool - Converts material names to CAS numbers
   - Name2Properties Tool - Queries properties by material name
   - CID2Properties Tool - Queries properties by PubChem CID
   - Formula2Properties Tool - Predicts properties from formulas
   - MaterialSearch Tool - Retrieves performance data of similar materials
   - PNEC Tool - Queries environmental risk assessment data

4. **Configuration** (`src/config/`) - System configuration:
   - API keys and model settings
   - Temperature configurations for different agents
   - Iterative design and consistency analysis parameters

5. **Utilities** (`src/utils/`) - Helper functions:
   - LLM configuration management
   - Prompt loading utilities

## Common Development Commands

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the system:
```bash
python scripts/main.py
```

Run tests:
```bash
python scripts/run_test.py
```

Test PubChem connection:
```bash
python scripts/test_pubchem_connection.py
```

Test material tools:
```bash
python scripts/test_material_tools.py
```

## Development Guidelines

### Adding New Agents
1. Create a new agent file in `src/agents/` inheriting from `BaseAgent`
2. Create a corresponding prompt file in `src/prompts/`
3. Use `PromptLoader` to load the prompt in the agent file
4. Import and register the new agent in `scripts/main.py` and `src/agents/task_allocator.py`

### Adding New Tasks
1. Create a new task file in `src/tasks/` inheriting from `BaseTask`
2. Add task type to agent type mapping in the task allocator
3. Create and execute new tasks in the main program

### Integrating New Tools
1. Create a new tool file in `src/tools/`
2. Implement the tool functionality
3. Integrate the tool into agents through CrewAI's tool mechanism
4. Update relevant agent prompts to guide tool usage
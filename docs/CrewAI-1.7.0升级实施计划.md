# CrewAI 1.7.0 升级实施计划

**项目**: ECOMATS - 水处理材料设计多智能体系统  
**当前版本**: CrewAI 1.2.1  
**目标版本**: CrewAI 1.7.0  
**制定日期**: 2025-12-13  
**预计工期**: 5-7个工作日

---

## 📋 目录

1. [升级概述](#一升级概述)
2. [升级前准备](#二升级前准备)
3. [核心功能适配矩阵](#三核心功能适配矩阵)
4. [详细实施步骤](#四详细实施步骤)
5. [测试验证计划](#五测试验证计划)
6. [回滚预案](#六回滚预案)
7. [优化机会](#七优化机会)

---

## 一、升级概述

### 1.1 升级理由

根据用户需求,ECOMATS项目的以下特性与1.7.0新功能高度匹配:

| ECOMATS需求 | 1.7.0新特性 | 匹配度 |
|-----------|------------|--------|
| **多材料并发评估** | Async Crew并发执行 | ⭐⭐⭐⭐⭐ |
| **多数据库并发查询** | Async Tools | ⭐⭐⭐⭐⭐ |
| **实时反馈** | Async Streaming | ⭐⭐⭐⭐ |
| **批量材料设计** | akickoff_for_each | ⭐⭐⭐⭐⭐ |
| **上下文记忆** | Async Memory | ⭐⭐⭐⭐ |
| **知识库检索** | Async Knowledge | ⭐⭐⭐⭐ |

**核心优势**:
1. **性能提升**: 10种材料并发评估,预计时间节省60-70%
2. **用户体验**: 流式输出,实时查看设计进度
3. **资源效率**: 异步I/O,提升CPU和网络利用率8倍
4. **可扩展性**: 支持更大规模的材料筛选任务

### 1.2 风险评估

| 风险类型 | 风险等级 | 缓解措施 |
|---------|---------|---------|
| API不兼容 | 🟢 低 | 同步API保留,渐进迁移 |
| 依赖冲突 | 🟡 中 | 创建虚拟环境测试 |
| 功能破坏 | 🟢 低 | 完整回归测试 |
| 性能回退 | 🟢 低 | 性能基准对比 |
| 学习成本 | 🟡 中 | 详细文档和示例 |

**总体风险**: 🟢 **可控**

---

## 二、升级前准备

### 2.1 环境备份

#### 步骤1: 创建升级分支
```bash
cd /home/axlhuang/ECOMATS
git checkout -b upgrade-crewai-1.7.0
git add -A
git commit -m "Checkpoint: Pre-upgrade state (CrewAI 1.2.1)"
```

#### 步骤2: 备份当前环境
```bash
# 备份依赖
pip freeze > requirements-backup-1.2.1.txt

# 备份配置
cp .env .env.backup

# 备份关键文件
mkdir -p backups/pre-upgrade
cp -r src/ backups/pre-upgrade/
cp -r scripts/ backups/pre-upgrade/
```

#### 步骤3: 创建测试环境
```bash
# 创建独立虚拟环境(可选)
python -m venv venv-1.7.0-test
source venv-1.7.0-test/bin/activate

# 或使用conda
conda create -n ecomats-1.7.0 python=3.10
conda activate ecomats-1.7.0
```

### 2.2 依赖检查

**当前依赖状态**:
```
crewai==1.2.1
crewai-tools==1.2.1
openai>=1.100.0
dashscope>=1.25.0
python-dotenv>=1.0.0
requests>=2.32.0
mp-api>=0.45.0
```

**需要检查的第三方库兼容性**:
- [ ] httpx (异步HTTP库)
- [ ] asyncio (Python标准库,3.8+)
- [ ] aiofiles (异步文件I/O,可选)

---

## 三、核心功能适配矩阵

### 3.1 ECOMATS架构组件清单

| 组件类别 | 文件/模块 | 当前使用方式 | 需要升级 | 优先级 |
|---------|----------|------------|---------|--------|
| **Agents** | | | | |
| - BaseAgent | `src/agents/base_agent.py` | 同步创建 | ✅ 是 | P0 |
| - CreativeDesigningAgent | `src/agents/Creative_Designing_agent.py` | 同步执行 | ✅ 是 | P0 |
| - AssessmentAgents (A/B/C) | `src/agents/Assessment_Screening_agent_*.py` | 同步执行 | ✅ 是 | P0 |
| - TaskOrganizingAgent | `src/agents/task_organizing_agent.py` | 同步协调 | ✅ 是 | P0 |
| **Tasks** | | | | |
| - DesignTask | `src/tasks/design_task.py` | 同步任务 | ✅ 是 | P0 |
| - EvaluationTask | `src/tasks/evaluation_task.py` | 同步任务 | ✅ 是 | P0 |
| - FinalValidationTask | `src/tasks/final_validation_task.py` | 同步任务 | ✅ 是 | P0 |
| - MechanismAnalysisTask | `src/tasks/mechanism_analysis_task.py` | 同步任务 | ✅ 是 | P1 |
| - SynthesisMethodTask | `src/tasks/synthesis_method_task.py` | 同步任务 | ✅ 是 | P1 |
| **Tools** | | | | |
| - PubChem Tools | `src/tools/*pubchem*.py` | 同步API调用 | ✅ 是 | P0 |
| - Materials Project Tools | `src/tools/*mp*.py` | 同步API调用 | ✅ 是 | P0 |
| - MolPort Tools | `src/tools/*molport*.py` | 同步API调用 | ✅ 是 | P1 |
| **Workflows** | | | | |
| - Preset Workflow | `scripts/main.py:run_preset_workflow` | 同步Crew执行 | ✅ 是 | P0 |
| - Autonomous Mode | `scripts/main.py:run_autonomous_workflow` | 同步Crew执行 | ✅ 是 | P0 |
| **Memory** | | | | |
| - Crew Memory | 未显式配置 | 未使用 | ⚠️ 新增 | P2 |
| **Knowledge** | | | | |
| - Knowledge Base | 未配置 | 未使用 | ⚠️ 新增 | P2 |

**优先级说明**:
- **P0**: 核心功能,必须升级和测试
- **P1**: 重要功能,建议升级
- **P2**: 增强功能,可选升级

### 3.2 功能适配对照表

#### 3.2.1 Crew执行方式

| 功能 | 当前代码 | 1.7.0升级方案 | 性能提升 |
|-----|---------|--------------|---------|
| **单Crew执行** | `crew.kickoff()` | `await crew.akickoff()` | 持平 |
| **多材料并发** | 顺序执行 | `asyncio.gather()` | 5-10倍 ⭐⭐⭐ |
| **批量设计** | for循环 | `akickoff_for_each()` | 8-10倍 ⭐⭐⭐ |
| **实时反馈** | 无 | `stream=True` | 体验提升 ⭐⭐⭐⭐ |

**代码示例对比**:

**当前(1.2.1)**:
```python
# scripts/main.py
def run_preset_workflow(user_requirement, llm):
    # 创建Crew
    crew = Crew(
        agents=[...],
        tasks=[...],
        process=Process.sequential
    )
    
    # 同步执行
    result = crew.kickoff(inputs={'requirement': user_requirement})
    return result
```

**升级后(1.7.0)**:
```python
# scripts/main.py
async def run_preset_workflow_async(user_requirement, llm):
    # 创建Crew
    crew = Crew(
        agents=[...],
        tasks=[...],
        process=Process.sequential,
        stream=True  # ⭐ 新增: 启用流式输出
    )
    
    # 异步执行
    result = await crew.akickoff(inputs={'requirement': user_requirement})
    return result
```

#### 3.2.2 Task异步执行

| 场景 | 当前方式 | 升级方案 | 适用情况 |
|-----|---------|---------|---------|
| **独立评估任务** | 顺序执行 | `async_execution=True` | 3个评估专家并发 ⭐⭐⭐ |
| **数据收集** | 顺序调用工具 | 异步工具调用 | 多数据库查询 ⭐⭐⭐ |
| **依赖任务** | 同步等待 | `context=[task]` | 设计→评估→验证 |

**优化示例**:

**当前**: 3个评估专家顺序执行
```
Expert A (30s) → Expert B (30s) → Expert C (30s) = 90秒
```

**升级后**: 3个评估专家并发执行
```
Expert A (30s) ↘
Expert B (30s) → 并发执行 = 35秒
Expert C (30s) ↗
```

**时间节省**: 60% ⭐⭐⭐

#### 3.2.3 Tools异步化

| 工具类型 | 文件 | 当前实现 | 升级方案 | 性能提升 |
|---------|-----|---------|---------|---------|
| **PubChem查询** | `pubchem_tool.py` | `requests.get()` | `httpx.AsyncClient()` | 8-10倍 ⭐⭐⭐ |
| **Materials Project** | `mp_tools.py` | 同步API | 异步包装 | 5-8倍 ⭐⭐⭐ |
| **MolPort** | `molport_tool.py` | `requests` | `httpx.AsyncClient` | 8-10倍 ⭐⭐⭐ |
| **结构验证** | `structure_validator.py` | 同步 | 异步 | 5倍 ⭐⭐ |

**异步工具模板**:
```python
# 当前同步工具
def sync_pubchem_search(compound: str) -> dict:
    response = requests.get(f"https://pubchem.../search?query={compound}")
    return response.json()

# 升级后异步工具
@tool("异步PubChem搜索")
async def async_pubchem_search(compound: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"https://pubchem.../search?query={compound}")
        return response.json()
```

#### 3.2.4 Memory和Knowledge

| 功能 | 当前状态 | 升级方案 | 价值 |
|-----|---------|---------|------|
| **Crew Memory** | 未启用 | `memory=True` | 记住设计历史 ⭐⭐⭐ |
| **Knowledge Base** | 未配置 | 添加材料知识库 | 提升设计质量 ⭐⭐⭐⭐ |
| **异步记忆** | - | 自动启用 | 性能提升8倍 ⭐⭐⭐ |

---

## 四、详细实施步骤

### 阶段1: 基础升级 (第1-2天)

#### 步骤1.1: 升级CrewAI包
```bash
# 1. 升级crewai
pip install crewai==1.7.0 --upgrade

# 2. 升级crewai-tools
pip install crewai-tools==1.7.0 --upgrade

# 3. 检查依赖
pip check

# 4. 更新requirements.txt
cat > requirements.txt << EOF
# CrewAI框架
crewai==1.7.0
crewai-tools==1.7.0

# LLM API
openai>=1.100.0
dashscope>=1.25.0

# 异步HTTP
httpx>=0.27.0

# 工具和数据库
python-dotenv>=1.0.0
requests>=2.32.0
mp-api>=0.45.0
EOF

# 5. 安装新依赖
pip install httpx>=0.27.0
```

**验证点**:
- [ ] `pip list | grep crewai` 显示1.7.0
- [ ] `pip check` 无冲突
- [ ] Python版本 >= 3.8

#### 步骤1.2: 创建异步工具基类

**新建文件**: `src/tools/async_base_tool.py`

```python
"""异步工具基类"""
import httpx
from typing import Optional
from crewai.tools import BaseTool

class AsyncHTTPTool(BaseTool):
    """异步HTTP工具基类"""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """获取或创建异步HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                limits=httpx.Limits(max_connections=100)
            )
        return self._client
    
    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
```

**清单**:
- [ ] 创建`async_base_tool.py`
- [ ] 测试基类功能
- [ ] 更新`__init__.py`

#### 步骤1.3: 适配BaseAgent支持异步

**修改文件**: `src/agents/base_agent.py`

```python
# 保持向后兼容,添加异步支持
class BaseAgent:
    def __init__(self, llm, role, goal, prompt_file, temperature=None, enable_async=False):
        self.llm = llm
        self.role = role
        self.goal = goal
        self.prompt_file = prompt_file
        self.temperature = temperature
        self.enable_async = enable_async  # ⭐ 新增
    
    def create_agent(self):
        # 现有代码保持不变
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=load_prompt(self.prompt_file),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
```

**清单**:
- [ ] 修改`base_agent.py`
- [ ] 保持向后兼容
- [ ] 添加`enable_async`参数

---

### 阶段2: 工具异步化 (第2-3天)

#### 步骤2.1: 异步化PubChem工具

**修改文件**: `src/tools/pubchem_tool.py`

**优先级**: P0 (核心工具)

**改造方案**:
```python
from crewai.tools import tool
import httpx

# 保留同步版本(向后兼容)
@tool("PubChem搜索")
def pubchem_search(compound: str) -> dict:
    """同步版本PubChem搜索(兼容)"""
    import requests
    response = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound}/JSON")
    return response.json()

# 新增异步版本
@tool("异步PubChem搜索")
async def async_pubchem_search(compound: str) -> dict:
    """异步版本PubChem搜索(推荐)"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound}/JSON"
        )
        return response.json()

# 批量异步查询(新功能)
async def batch_pubchem_search(compounds: list[str]) -> dict:
    """批量异步查询多个化合物"""
    import asyncio
    
    async def search_one(compound):
        return await async_pubchem_search.arun(compound)
    
    tasks = [search_one(c) for c in compounds]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return dict(zip(compounds, results))
```

**测试脚本**: `scripts/test_async_pubchem.py`

```python
import asyncio
from src.tools.pubchem_tool import async_pubchem_search, batch_pubchem_search

async def test_async_pubchem():
    # 测试1: 单个查询
    result = await async_pubchem_search.arun("benzene")
    print(f"单个查询结果: {result}")
    
    # 测试2: 批量查询
    compounds = ["benzene", "toluene", "phenol", "aniline"]
    results = await batch_pubchem_search(compounds)
    print(f"批量查询完成: {len(results)}个化合物")

if __name__ == "__main__":
    asyncio.run(test_async_pubchem())
```

**清单**:
- [ ] 创建异步PubChem工具
- [ ] 保留同步版本
- [ ] 创建批量查询函数
- [ ] 编写测试脚本
- [ ] 验证功能正常

#### 步骤2.2: 异步化Materials Project工具

**修改文件**: `src/tools/mp_*.py`

**优先级**: P0

**改造策略**:
1. Materials Project API本身可能不支持异步,使用线程池包装
2. 或使用`asyncio.to_thread()`包装同步调用

```python
import asyncio
from mp_api.client import MPRester

@tool("异步MP查询")
async def async_mp_search(formula: str, api_key: str) -> dict:
    """异步Materials Project搜索"""
    # 使用to_thread包装同步API
    def sync_search():
        with MPRester(api_key) as mpr:
            docs = mpr.materials.summary.search(formula=formula)
            return [doc.dict() for doc in docs]
    
    result = await asyncio.to_thread(sync_search)
    return result
```

**清单**:
- [ ] 异步化MP工具
- [ ] 测试查询功能
- [ ] 性能基准测试

#### 步骤2.3: 异步化MolPort工具

**修改文件**: `src/tools/molport_tool.py`

**优先级**: P1

**改造方案**:
```python
@tool("异步MolPort搜索")
async def async_molport_search(smiles: str, api_key: str) -> dict:
    """异步MolPort搜索"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"https://api.molport.com/api/search",
            params={"smiles": smiles},
            headers={"X-API-KEY": api_key}
        )
        return response.json()
```

**清单**:
- [ ] 异步化MolPort工具
- [ ] 测试API调用
- [ ] 验证结果正确性

---

### 阶段3: Task和Crew适配 (第3-4天)

#### 步骤3.1: 适配DesignTask支持异步

**修改文件**: `src/tasks/design_task.py`

**改造点**:
1. 添加`async_execution`参数支持
2. 更新工具调用说明

```python
class DesignTask(BaseTask):
    def create_task(self, agent, context_task=None, feedback=None, 
                   user_requirement=None, async_mode=False):
        # ... 现有代码 ...
        
        description = """
        # ... 现有描述 ...
        
        工具使用策略(异步模式):
        1. **并发查询阶段**:
           - 同时查询PubChem和Materials Project
           - 使用异步工具提升查询速度
        
        2. **批量验证阶段**:
           - 批量验证多个材料结构
           - 并发执行结构验证
        """
        
        task = Task(
            agent=agent,
            expected_output=expected_output,
            description=description,
            async_execution=async_mode  # ⭐ 支持异步
        )
        
        return task
```

**清单**:
- [ ] 添加`async_mode`参数
- [ ] 更新工具使用说明
- [ ] 测试异步任务创建

#### 步骤3.2: 适配EvaluationTask支持并发

**修改文件**: `src/tasks/evaluation_task.py`

**关键优化**: 3个评估专家并发执行

```python
class EvaluationTask(BaseTask):
    def create_tasks(self, agents, context_task, enable_async=True):
        """创建多个评估任务,支持并发执行"""
        tasks = []
        
        for agent, expert_name in zip(agents, ['A', 'B', 'C']):
            task = Task(
                agent=agent,
                description=self._get_description(expert_name),
                expected_output=self.expected_output,
                context=[context_task],
                async_execution=enable_async  # ⭐ 启用异步
            )
            tasks.append(task)
        
        return tasks
```

**清单**:
- [ ] 修改`create_tasks`方法
- [ ] 添加`enable_async`参数
- [ ] 测试并发评估

#### 步骤3.3: 升级主工作流

**修改文件**: `scripts/main.py`

**核心改造**: 添加异步工作流函数

```python
# ===== 新增: 异步预设工作流 =====
async def run_preset_workflow_async(user_requirement, llm):
    """异步预设工作流模式"""
    print("启动异步预设工作流模式...")
    
    # 创建所有agents
    agents = create_all_agents(llm)
    
    # 创建tasks
    from src.tasks.design_task import DesignTask
    from src.tasks.evaluation_task import EvaluationTask
    from src.tasks.final_validation_task import FinalValidationTask
    
    # 设计任务
    design_task = DesignTask(agents['material_designer']).create_task(
        agent=agents['material_designer'],
        user_requirement=user_requirement,
        async_mode=False  # 设计任务同步
    )
    
    # 评估任务(并发)
    eval_tasks = EvaluationTask(agents['expert_a']).create_tasks(
        agents=[agents['expert_a'], agents['expert_b'], agents['expert_c']],
        context_task=design_task,
        enable_async=True  # ⭐ 启用并发评估
    )
    
    # 最终验证任务
    final_task = FinalValidationTask(agents['final_validator']).create_task(
        agent=agents['final_validator'],
        context_task=eval_tasks
    )
    
    # 创建Crew
    crew = Crew(
        agents=list(agents.values()),
        tasks=[design_task] + eval_tasks + [final_task],
        process=Process.sequential,
        memory=True,  # ⭐ 启用记忆
        stream=True,  # ⭐ 启用流式输出
        verbose=True
    )
    
    # 异步执行
    result = await crew.akickoff(
        inputs={'requirement': user_requirement}
    )
    
    return result

# ===== 新增: 批量材料设计 =====
async def batch_material_design(requirements: list[str], llm):
    """批量异步设计多个材料"""
    print(f"开始批量设计 {len(requirements)} 个材料...")
    
    # 并发执行多个设计任务
    tasks = [
        run_preset_workflow_async(req, llm) 
        for req in requirements
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"批量设计完成! 成功: {sum(1 for r in results if not isinstance(r, Exception))}")
    
    return results

# ===== 修改main函数支持异步 =====
def main():
    # ... 现有代码 ...
    
    mode = get_workflow_mode()
    
    if mode == "preset":
        # 询问是否使用异步模式
        print("\n是否启用异步加速模式? (y/n)")
        use_async = input().strip().lower() == 'y'
        
        if use_async:
            # 使用异步模式
            result = asyncio.run(run_preset_workflow_async(user_input, llm))
        else:
            # 使用同步模式(向后兼容)
            result = run_preset_workflow(user_input, llm)
    # ... 其他代码 ...
```

**清单**:
- [ ] 创建`run_preset_workflow_async`
- [ ] 创建`batch_material_design`
- [ ] 修改`main`函数
- [ ] 保持向后兼容
- [ ] 添加用户选择界面

---

### 阶段4: 高级功能集成 (第4-5天)

#### 步骤4.1: 集成Crew Memory

**目标**: 记住设计历史,避免重复设计

```python
# scripts/main.py

# 启用Memory的Crew
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # ⭐ 启用记忆
    memory_config={
        "provider": "local",  # 本地存储
        "storage_path": "./memory_store"
    },
    verbose=True
)

# Memory会自动记住:
# 1. 设计过的材料
# 2. 评估结果
# 3. 用户反馈
# 4. 失败的设计方案
```

**清单**:
- [ ] 配置Memory
- [ ] 测试记忆功能
- [ ] 验证历史查询

#### 步骤4.2: 添加Knowledge Base

**目标**: 添加材料知识库,提升设计质量

**新建文件**: `src/knowledge/materials_knowledge.py`

```python
from crewai.knowledge.source import TextSource, FileSource

# 创建材料知识源
materials_knowledge = TextSource(
    content="""
    # 水处理催化剂设计知识库
    
    ## 常见污染物及对应催化剂
    1. 重金属镉: Fe3O4/C, MnO2, CeO2基催化剂
    2. 有机染料: TiO2, ZnO, BiOBr光催化剂
    3. 抗生素: 单原子催化剂, MOF材料
    
    ## 催化机理
    1. PMS活化: 过渡金属活化过硫酸盐
    2. 自由基生成: SO4•−, •OH
    3. 降解路径: 氧化分解
    
    ## 设计原则
    1. 高活性位点密度
    2. 良好的结构稳定性
    3. 易于分离回收
    """
)

# 在Agent中使用
material_designer = Agent(
    role="材料设计专家",
    goal="设计高效催化剂",
    knowledge_sources=[materials_knowledge],  # ⭐ 添加知识源
    backstory=load_prompt("creative_designing_agent.txt")
)
```

**清单**:
- [ ] 创建知识库文件
- [ ] 集成到Agent
- [ ] 测试知识检索
- [ ] 评估设计质量提升

#### 步骤4.3: 实现流式输出

**目标**: 实时显示设计进度

```python
async def run_with_streaming(user_requirement, llm):
    """流式输出执行"""
    crew = Crew(
        agents=[...],
        tasks=[...],
        stream=True  # ⭐ 启用流式
    )
    
    print("🚀 开始材料设计,实时输出:")
    print("="*60)
    
    streaming_output = await crew.akickoff(
        inputs={'requirement': user_requirement}
    )
    
    # 异步迭代流式输出
    async for chunk in streaming_output:
        print(f"[实时] {chunk.content}", end="", flush=True)
    
    # 获取最终结果
    final_result = streaming_output.result
    
    print("\n" + "="*60)
    print("✅ 设计完成!")
    print(f"最终结果: {final_result.raw}")
    
    return final_result
```

**清单**:
- [ ] 实现流式输出函数
- [ ] 测试实时反馈
- [ ] 优化输出格式

---

### 阶段5: 性能优化 (第5-6天)

#### 步骤5.1: 并发控制

**目标**: 避免过度并发导致API限流

```python
import asyncio

class ConcurrencyController:
    """并发控制器"""
    def __init__(self, max_concurrent=5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, coro):
        """控制并发执行"""
        async with self.semaphore:
            return await coro

# 使用示例
controller = ConcurrencyController(max_concurrent=5)

async def controlled_batch_design(requirements, llm):
    """受控的批量设计"""
    tasks = [
        controller.execute(run_preset_workflow_async(req, llm))
        for req in requirements
    ]
    results = await asyncio.gather(*tasks)
    return results
```

**清单**:
- [ ] 实现并发控制器
- [ ] 集成到批量操作
- [ ] 测试并发限制

#### 步骤5.2: 超时和重试

**目标**: 处理网络异常和超时

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def reliable_api_call(func, *args, **kwargs):
    """可靠的API调用(自动重试)"""
    try:
        result = await asyncio.wait_for(
            func(*args, **kwargs),
            timeout=30.0
        )
        return result
    except asyncio.TimeoutError:
        print(f"API调用超时,重试...")
        raise
    except Exception as e:
        print(f"API调用失败: {e},重试...")
        raise
```

**清单**:
- [ ] 添加超时控制
- [ ] 实现自动重试
- [ ] 测试异常处理

#### 步骤5.3: 连接池优化

**目标**: 复用HTTP连接,提升性能

```python
# 全局HTTP客户端
class GlobalHTTPClient:
    _instance = None
    _client = None
    
    @classmethod
    async def get_client(cls):
        """获取单例客户端"""
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100
                )
            )
        return cls._client
    
    @classmethod
    async def close(cls):
        """关闭客户端"""
        if cls._client:
            await cls._client.aclose()
            cls._client = None
```

**清单**:
- [ ] 实现全局客户端
- [ ] 更新工具使用客户端
- [ ] 测试性能提升

---

## 五、测试验证计划

### 5.1 单元测试

**测试文件**: `tests/test_async_components.py`

```python
import pytest
import asyncio

# 测试异步工具
@pytest.mark.asyncio
async def test_async_pubchem_tool():
    """测试异步PubChem工具"""
    from src.tools.pubchem_tool import async_pubchem_search
    result = await async_pubchem_search.arun("benzene")
    assert result is not None
    assert "PC_Compounds" in result

# 测试异步Task
@pytest.mark.asyncio
async def test_async_evaluation_tasks():
    """测试并发评估任务"""
    # ... 测试代码 ...
    pass

# 测试异步Crew
@pytest.mark.asyncio
async def test_async_crew_execution():
    """测试异步Crew执行"""
    # ... 测试代码 ...
    pass
```

**清单**:
- [ ] 编写异步工具测试
- [ ] 编写异步Task测试
- [ ] 编写异步Crew测试
- [ ] 执行所有测试
- [ ] 覆盖率>80%

### 5.2 集成测试

**测试脚本**: `scripts/test_async_workflow.py`

```python
import asyncio
import time

async def integration_test():
    """完整异步工作流集成测试"""
    from scripts.main import run_preset_workflow_async
    from src.config.config import Config
    from src.utils.llm_config import create_llm
    
    llm = create_llm()
    
    # 测试需求
    test_requirement = "设计一种用于处理含镉废水的催化剂"
    
    print("开始集成测试...")
    start_time = time.time()
    
    result = await run_preset_workflow_async(test_requirement, llm)
    
    end_time = time.time()
    
    print(f"✅ 测试完成")
    print(f"耗时: {end_time - start_time:.2f}秒")
    print(f"结果: {result.raw[:200]}...")
    
    return result

if __name__ == "__main__":
    asyncio.run(integration_test())
```

**清单**:
- [ ] 创建集成测试脚本
- [ ] 测试完整工作流
- [ ] 验证输出正确性
- [ ] 记录性能数据

### 5.3 性能基准测试

**测试脚本**: `scripts/benchmark_async_vs_sync.py`

```python
import asyncio
import time

async def benchmark():
    """性能对比测试"""
    
    test_cases = [
        "设计催化剂1",
        "设计催化剂2",
        "设计催化剂3",
        "设计催化剂4",
        "设计催化剂5"
    ]
    
    # 同步执行
    print("同步执行测试...")
    sync_start = time.time()
    for req in test_cases:
        result = run_preset_workflow(req, llm)
    sync_time = time.time() - sync_start
    
    # 异步执行
    print("异步执行测试...")
    async_start = time.time()
    tasks = [run_preset_workflow_async(req, llm) for req in test_cases]
    results = await asyncio.gather(*tasks)
    async_time = time.time() - async_start
    
    # 结果
    print(f"\n{'='*60}")
    print(f"同步执行: {sync_time:.2f}秒")
    print(f"异步执行: {async_time:.2f}秒")
    print(f"性能提升: {(sync_time/async_time):.2f}倍")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(benchmark())
```

**预期结果**:
- 5个任务并发: 性能提升 **3-5倍**
- 10个任务并发: 性能提升 **5-8倍**

**清单**:
- [ ] 创建基准测试
- [ ] 执行对比测试
- [ ] 记录性能数据
- [ ] 生成性能报告

### 5.4 回归测试

**目标**: 确保升级不破坏现有功能

**测试清单**:
- [ ] 预设工作流模式(同步)
- [ ] 自主调度模式(同步)
- [ ] 所有Agent正常工作
- [ ] 所有Tool正常调用
- [ ] 所有Task正常执行
- [ ] 输出格式一致
- [ ] 评分逻辑正确

**测试脚本**: 复用现有测试
```bash
# 运行现有测试
python scripts/test_molport_tool.py
python scripts/run_autonomous_tests.py
python scripts/simple_verification_test.py
```

---

## 六、回滚预案

### 6.1 快速回滚

如果升级后出现严重问题,执行快速回滚:

```bash
# 1. 切换回主分支
git checkout main

# 2. 恢复依赖
pip install -r requirements-backup-1.2.1.txt

# 3. 恢复环境变量
cp .env.backup .env

# 4. 验证功能
python scripts/main.py
```

### 6.2 部分回滚

如果只有部分功能有问题:

```bash
# 保留异步代码,但默认使用同步模式
# 在main.py中设置默认值
use_async = False  # 默认关闭异步

# 或通过环境变量控制
export ECOMATS_ENABLE_ASYNC=false
```

### 6.3 数据恢复

```bash
# 恢复备份的代码
cp -r backups/pre-upgrade/src/* src/
cp -r backups/pre-upgrade/scripts/* scripts/
```

---

## 七、优化机会

### 7.1 短期优化 (升级后立即实施)

| 优化项 | 预期收益 | 实施难度 | 优先级 |
|-------|---------|---------|--------|
| **并发评估** | 60%时间节省 | 低 | P0 |
| **批量API调用** | 8-10倍性能 | 低 | P0 |
| **流式输出** | 用户体验提升 | 低 | P1 |
| **连接池复用** | 30%性能提升 | 中 | P1 |

### 7.2 中期优化 (1-2周后)

| 优化项 | 预期收益 | 实施难度 | 优先级 |
|-------|---------|---------|--------|
| **Memory集成** | 避免重复设计 | 中 | P1 |
| **Knowledge Base** | 设计质量提升 | 中 | P1 |
| **缓存机制** | 50%API调用减少 | 中 | P2 |
| **并发控制优化** | 稳定性提升 | 中 | P2 |

### 7.3 长期优化 (1个月后)

| 优化项 | 预期收益 | 实施难度 | 优先级 |
|-------|---------|---------|--------|
| **分布式任务** | 无限扩展 | 高 | P3 |
| **GPU加速** | 计算性能提升 | 高 | P3 |
| **实时协作** | 多用户支持 | 高 | P3 |

---

## 八、里程碑和时间表

### 第1天: 基础升级
- ✅ 升级CrewAI包
- ✅ 创建异步工具基类
- ✅ 适配BaseAgent
- 🎯 里程碑: 环境升级完成

### 第2天: 工具异步化
- ✅ 异步化PubChem工具
- ✅ 异步化Materials Project工具
- ✅ 异步化MolPort工具
- 🎯 里程碑: 所有工具支持异步

### 第3天: Task和Crew适配
- ✅ 适配DesignTask
- ✅ 适配EvaluationTask
- ✅ 升级主工作流
- 🎯 里程碑: 异步工作流可用

### 第4天: 高级功能
- ✅ 集成Crew Memory
- ✅ 添加Knowledge Base
- ✅ 实现流式输出
- 🎯 里程碑: 所有新特性集成

### 第5天: 性能优化
- ✅ 并发控制
- ✅ 超时和重试
- ✅ 连接池优化
- 🎯 里程碑: 性能优化完成

### 第6-7天: 测试验证
- ✅ 单元测试
- ✅ 集成测试
- ✅ 性能测试
- ✅ 回归测试
- 🎯 里程碑: 升级验证通过

---

## 九、成功指标

### 9.1 功能指标
- [ ] 所有现有功能正常工作
- [ ] 异步工作流成功执行
- [ ] 批量设计功能可用
- [ ] 流式输出正常显示

### 9.2 性能指标
- [ ] 5个材料并发: ≥3倍性能提升
- [ ] 10个材料并发: ≥5倍性能提升
- [ ] API调用成功率: ≥98%
- [ ] 平均响应时间: 降低50%

### 9.3 质量指标
- [ ] 测试覆盖率: ≥80%
- [ ] 所有测试通过
- [ ] 无严重Bug
- [ ] 代码审查通过

---

## 十、风险缓解

### 10.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| API不兼容 | 高 | 低 | 保留同步版本,渐进迁移 |
| 性能回退 | 中 | 低 | 性能基准测试 |
| 内存泄漏 | 高 | 中 | 压力测试,资源监控 |
| 并发Bug | 高 | 中 | 充分测试,并发控制 |

### 10.2 项目风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| 工期延误 | 中 | 中 | 每日进度检查,优先级管理 |
| 资源不足 | 中 | 低 | 弹性调整计划 |
| 依赖问题 | 高 | 低 | 提前检查兼容性 |

---

## 十一、总结

### 11.1 升级价值

**性能提升**:
- 并发执行: **5-10倍** ⭐⭐⭐⭐⭐
- API调用: **8-10倍** ⭐⭐⭐⭐⭐
- 用户体验: 显著提升 ⭐⭐⭐⭐⭐

**新功能**:
- 批量材料设计 ⭐⭐⭐⭐⭐
- 实时进度反馈 ⭐⭐⭐⭐
- 设计历史记忆 ⭐⭐⭐⭐
- 知识库集成 ⭐⭐⭐⭐

**技术优势**:
- 紧跟CrewAI发展 ⭐⭐⭐⭐
- 提升代码质量 ⭐⭐⭐⭐
- 增强可扩展性 ⭐⭐⭐⭐⭐

### 11.2 下一步行动

1. **立即开始**: 创建升级分支
2. **第1天**: 升级CrewAI包
3. **持续沟通**: 每日进度汇报
4. **灵活调整**: 根据实际情况优化计划

---

**文档维护**: 升级过程中持续更新  
**责任人**: AI助手  
**审核**: 项目负责人  
**版本**: v1.0

---

## 附录A: 快速参考

### 异步API速查

```python
# Crew执行
result = await crew.akickoff(inputs={...})

# 批量执行
results = await crew.akickoff_for_each(datasets)

# 并发执行
results = await asyncio.gather(
    crew1.akickoff(...),
    crew2.akickoff(...)
)

# 流式输出
async for chunk in streaming_output:
    print(chunk.content)
```

### 常见问题

**Q: 升级后原有代码还能用吗?**
A: 能!同步API完全保留,可以渐进式迁移。

**Q: 如何判断是否需要异步?**
A: 如果有多个独立任务或I/O密集型操作,建议使用异步。

**Q: 异步会增加复杂度吗?**
A: 会,但收益远大于成本。我们提供详细文档和示例。

---

**准备就绪,开始升级!** 🚀

# CrewAI 1.8.x 新特性使用指南

> ECOMATS 项目已升级至 CrewAI 1.8.1，本文档介绍新版本的核心特性及使用方法。

## 目录

- [版本概览](#版本概览)
- [1. Production-ready Flows](#1-production-ready-flows)
- [2. HITL (Human-in-the-Loop)](#2-hitl-human-in-the-loop)
- [3. A2A (Agent-to-Agent) 协议](#3-a2a-agent-to-agent-协议)
- [4. 原生异步支持](#4-原生异步支持)
- [5. Streaming Events](#5-streaming-events)
- [6. Bug 修复收益](#6-bug-修复收益)
- [迁移注意事项](#迁移注意事项)

---

## 版本概览

| 版本 | 发布日期 | 关键特性 |
|------|----------|---------|
| 1.8.1 | 2025-01-15 | A2A 任务执行、Agent Card 生成、错误处理改进 |
| 1.8.0 | 2025-01-08 | Production Flows、HITL、Streaming events |
| 1.7.x | 2024-12 | 全链路原生异步支持 |

---

## 1. Production-ready Flows

### 概述

Flows 是 CrewAI 1.8.0 引入的生产级工作流编排架构，支持复杂的多 Crew 协作场景。

### 基础用法

```python
from crewai import Flow, Crew, Agent, Task
from crewai.flow.flow import listen, start

class ECOMATSFlow(Flow):
    """ECOMATS 材料设计工作流"""
    
    @start()
    def design_phase(self):
        """启动设计阶段"""
        design_crew = Crew(
            agents=[self.designer_agent],
            tasks=[self.design_task],
        )
        return design_crew.kickoff()
    
    @listen(design_phase)
    def evaluation_phase(self, design_result):
        """设计完成后触发评估阶段"""
        eval_crew = Crew(
            agents=[self.eval_agent_a, self.eval_agent_b, self.eval_agent_c],
            tasks=[self.eval_task_a, self.eval_task_b, self.eval_task_c],
        )
        return eval_crew.kickoff(inputs={"design": design_result})
    
    @listen(evaluation_phase)
    def synthesis_phase(self, eval_result):
        """评估完成后触发合成方法设计"""
        synthesis_crew = Crew(
            agents=[self.synthesis_agent],
            tasks=[self.synthesis_task],
        )
        return synthesis_crew.kickoff(inputs={"evaluation": eval_result})

# 运行 Flow
flow = ECOMATSFlow()
result = flow.kickoff()
```

### 条件分支

```python
from crewai.flow.flow import listen, router

class ConditionalFlow(Flow):
    
    @start()
    def analyze_requirement(self):
        # 分析用户需求
        return {"needs_synthesis": True, "score": 85}
    
    @router(analyze_requirement)
    def route_next_step(self, analysis):
        """根据评估分数决定下一步"""
        if analysis["score"] >= 80:
            return "high_quality_path"
        else:
            return "refinement_path"
    
    @listen("high_quality_path")
    def proceed_to_synthesis(self):
        """高分材料直接进入合成阶段"""
        pass
    
    @listen("refinement_path")
    def refine_design(self):
        """低分材料重新设计"""
        pass
```

---

## 2. HITL (Human-in-the-Loop)

### 概述

HITL 允许在工作流执行过程中暂停并等待人工确认，适用于需要人工审核的关键决策点。

### 基础用法

```python
from crewai import Flow
from crewai.flow.flow import listen, start

class HITLFlow(Flow):
    
    @start()
    def design_material(self):
        """设计材料"""
        return {"material": "TiO2/g-C3N4 复合光催化剂", "score": 78}
    
    @listen(design_material)
    def human_review(self, design):
        """
        人工审核节点
        
        工作流会在此暂停，等待用户通过 API 或 UI 确认
        """
        if design["score"] < 80:
            # 触发人工审核
            self.pause_for_human_input(
                prompt=f"材料 {design['material']} 评分为 {design['score']}，是否继续？",
                options=["继续", "重新设计", "终止"]
            )
        return design
```

### Webhook 集成

```python
# 配置 HITL Webhook
from crewai import Flow

class WebhookHITLFlow(Flow):
    def __init__(self):
        super().__init__(
            hitl_config={
                "webhook_url": "https://your-api.com/hitl/callback",
                "timeout_seconds": 3600,  # 1小时超时
            }
        )
```

---

## 3. A2A (Agent-to-Agent) 协议

### 概述

A2A 协议允许不同系统中的 Agent 相互通信和协作，实现跨项目的智能体协作。

### Agent Card 生成

```python
from crewai import Agent
from crewai.a2a import AgentCard

# 创建 Agent
designer = Agent(
    role="材料设计专家",
    goal="设计高效水处理材料",
    backstory="资深材料科学研究员",
)

# 生成 Agent Card（用于 A2A 通信）
card = AgentCard.from_agent(
    agent=designer,
    name="ECOMATS-Designer",
    description="ECOMATS 系统的材料设计智能体",
    capabilities=["material_design", "structure_optimization"],
)

# 导出 Agent Card
card.to_json("agent_cards/designer.json")
```

### A2A 服务器配置

```python
from crewai.a2a import A2AServer

# 启动 A2A 服务器
server = A2AServer(
    agents=[designer, evaluator, synthesizer],
    port=8080,
)

# 其他系统可通过 A2A 协议调用这些 Agent
server.start()
```

### 跨系统调用

```python
from crewai.a2a import A2AClient

# 连接远程 A2A 服务器（例如 BioCrew）
client = A2AClient("http://biocrew-server:8080")

# 获取远程 Agent 能力
capabilities = client.get_capabilities()

# 请求远程 Agent 执行任务
result = await client.execute_task(
    agent_name="BioCrew-Identifier",
    task="识别可降解 DBP 的微生物",
    inputs={"pollutant": "邻苯二甲酸二丁酯"}
)
```

---

## 4. 原生异步支持

### 概述

CrewAI 1.7.0+ 提供全链路原生异步支持，包括 Crew、Task、Agent、Tools、Memory、Knowledge。

### 异步 Crew 执行

```python
import asyncio
from crewai import Crew

async def run_async_workflow():
    crew = Crew(
        agents=[agent1, agent2, agent3],
        tasks=[task1, task2, task3],
    )
    
    # 异步执行
    result = await crew.akickoff(inputs={"requirement": "设计光催化剂"})
    return result

# 运行
result = asyncio.run(run_async_workflow())
```

### 并行任务执行

```python
from crewai import Task

# 标记任务为异步执行
eval_task_a = Task(
    description="评估催化性能",
    agent=expert_a,
    async_execution=True,  # 启用异步
)

eval_task_b = Task(
    description="评估结构合理性",
    agent=expert_b,
    async_execution=True,  # 启用异步
)

eval_task_c = Task(
    description="评估经济可行性",
    agent=expert_c,
    async_execution=True,  # 启用异步
)

# 这三个任务会并行执行，而非顺序执行
```

### 异步工具

```python
from crewai.tools import BaseTool

class AsyncMaterialsProjectTool(BaseTool):
    name: str = "Materials Project Query"
    description: str = "查询 Materials Project 数据库"
    
    async def _arun(self, query: str) -> str:
        """异步执行查询"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.materialsproject.org/...", params={"q": query})
            return response.json()
```

---

## 5. Streaming Events

### 概述

Streaming Events 允许实时监控工具调用和任务执行进度。

### 基础用法

```python
from crewai import Crew
from crewai.events import EventListener

class ToolCallListener(EventListener):
    """监听工具调用事件"""
    
    def on_tool_start(self, tool_name: str, inputs: dict):
        print(f"🔧 开始调用工具: {tool_name}")
        print(f"   输入: {inputs}")
    
    def on_tool_end(self, tool_name: str, output: str):
        print(f"✅ 工具完成: {tool_name}")
        print(f"   输出: {output[:100]}...")
    
    def on_agent_action(self, agent: str, action: str):
        print(f"🤖 [{agent}] {action}")

# 注册监听器
crew = Crew(
    agents=[...],
    tasks=[...],
    event_listeners=[ToolCallListener()],
)
```

---

## 6. Bug 修复收益

升级到 1.8.1 后，以下问题已修复：

| 问题 | 修复版本 | 影响 |
|------|----------|------|
| 连接问题 (#4129) | 1.7.2 | API 调用更稳定 |
| 异步任务优雅终止 | 1.7.1 | 任务中断时不再挂起 |
| RPM 控制器计时器挂起 | 1.7.1 | 长时间运行不再卡死 |
| 任务排序问题 | 1.7.1 | 任务执行顺序正确 |
| Windows 信号兼容 | 1.7.1 | Windows 下运行正常 |
| HumanFeedbackPending 错误处理 | 1.8.1 | HITL 场景更健壮 |

---

## 迁移注意事项

### Patches 不再需要

ECOMATS 中的 `patches.py` 已更新为自动检测版本：

```python
# 现在会自动跳过不必要的补丁
from scripts.workflow.patches import apply_crewai_patches
apply_crewai_patches()
# 输出: ✅ CrewAI 1.8.1 detected - patches not needed (native async support)
```

### 兼容性

- Python 3.11 / 3.12 推荐
- Python 3.13 可能存在 chromadb 兼容问题（Windows）
- 所有原有代码无需修改即可运行

---

---

## ECOMATS 新模块一览

升级后新增的模块位于 `scripts/workflow/`:

| 文件 | 功能 | 替代 |
|------|------|------|
| `event_listener.py` | 标准化事件监听 | callback_factory.py |
| `ecomats_flow.py` | 声明式 Flow 编排 | 手动 Crew 构建 |
| `hitl.py` | 人工审核节点 | 新增 |
| `a2a.py` | 跨项目协作协议 | 新增 |

### 使用示例

```python
# EventListener
from scripts.workflow.event_listener import ECOMATSEventListener
listener = ECOMATSEventListener(monitor=monitor, verbose=True)
crew = Crew(..., step_callback=listener)

# HITL
from scripts.workflow.hitl import create_hitl_manager
hitl = create_hitl_manager(enabled=True, auto_approve_threshold=75.0)
decision = await hitl.request_decision(
    prompt="评分 70，是否继续？",
    options=["继续", "重新设计", "终止"],
    context={"score": 70}
)

# A2A (BioCrew 协作)
from scripts.workflow.a2a import BioCrewClient
client = BioCrewClient("http://biocrew-server:8081")
microbes = await client.identify_microorganisms(pollutant="DBP")
```

---

## 参考资料

- [CrewAI 官方文档](https://docs.crewai.com/)
- [CrewAI GitHub Releases](https://github.com/crewAIInc/crewAI/releases)
- [A2A 协议规范](https://docs.crewai.com/a2a)

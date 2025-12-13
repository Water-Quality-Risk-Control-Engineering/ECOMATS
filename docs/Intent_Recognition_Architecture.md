# Intent Recognition Architecture / 意图识别架构

## Overview / 概述

ECOMATS 系统采用 **TOA (Task Organizing Agent) 主导的意图识别架构**，取代了之前的硬编码关键词匹配方式。

The ECOMATS system adopts a **TOA (Task Organizing Agent)-driven intent recognition architecture**, replacing the previous hard-coded keyword matching approach.

---

## Architecture / 架构

### Before (Old) / 之前（旧）

```
用户输入 → 硬编码关键词匹配
          ↓ (70+ 硬编码关键词)
          ↓
         任务类型列表 → main.py 创建任务
```

**Problems / 问题**:
- ❌ 硬编码 70+ 关键词，维护困难
- ❌ 无法覆盖所有表达方式
- ❌ TOA 未参与意图理解

### After (New) / 之后（新）

```
用户输入 → TOA.analyze_user_intent()
          ↓ (LLM 语义理解)
          ↓
         意图 JSON → TOA.intent_to_task_types()
                    ↓
                   任务类型列表 → main.py 创建任务
```

**Benefits / 优势**:
- ✅ LLM 语义理解，支持任意表达方式
- ✅ 无需维护关键词列表
- ✅ TOA 主导意图识别，职责清晰
- ✅ 易于扩展新任务类型

---

## Implementation / 实现

### 1. Intent Recognition Prompt / 意图识别 Prompt

**File**: [src/prompts/intent_recognition_prompt.md](../src/prompts/intent_recognition_prompt.md)

Defines the intent recognition task with:
- Available tasks (material_design, evaluation, mechanism_analysis, etc.)
- Decision criteria for each task
- Output JSON format
- Examples for common scenarios

定义了意图识别任务，包括：
- 可用任务（材料设计、评估、机理分析等）
- 各任务的判断标准
- 输出 JSON 格式
- 常见场景示例

### 2. TOA Intent Analysis / TOA 意图分析

**File**: [src/agents/task_organizing_agent.py](../src/agents/task_organizing_agent.py#L61-L133)

```python
def analyze_user_intent(self, user_requirement: str) -> dict:
    """
    使用 LLM 分析用户意图，确定需要执行的任务
    """
    intent_prompt = load_prompt("intent_recognition_prompt.md")
    full_prompt = f"{intent_prompt}\n\nUser requirement:\n{user_requirement}"
    response = self.llm.call([{"role": "user", "content": full_prompt}])
    # 解析 JSON
    intent = json.loads(response_text)
    return intent
```

**Returns / 返回**:
```json
{
  "needs_design": boolean,
  "needs_evaluation": boolean,
  "evaluation_mode": "experts_only" | "with_summary" | null,
  "needs_mechanism": boolean,
  "needs_synthesis": boolean,
  "needs_operation": boolean,
  "material_provided": string | null,
  "reasoning": string
}
```

### 3. Intent to Task Types / 意图转任务类型

**File**: [src/agents/task_organizing_agent.py](../src/agents/task_organizing_agent.py#L135-L173)

```python
def intent_to_task_types(self, intent: dict) -> list:
    """
    将意图分析结果转换为任务类型列表
    """
    result = []
    
    if intent.get("needs_design", False):
        result.append("material_design")
    
    if intent.get("needs_evaluation", False):
        evaluation_mode = intent.get("evaluation_mode", "with_summary")
        if evaluation_mode == "experts_only":
            result.append("evaluation_only")
        else:
            result.extend(["evaluation", "final_validation"])
    
    # ... 其他任务
    
    return result
```

### 4. Integration in main.py / 在 main.py 中的集成

**File**: [scripts/main.py](../scripts/main.py#L346-L354)

```python
# ✨ 新的意图驱动流程：由 TOA 分析用户意图
print("\n🧠 TOA 正在分析用户意图...")
intent = coordinator.analyze_user_intent(user_requirement)
print(f"✅ 意图分析完成: {intent['reasoning']}")

# 将意图转换为任务类型
required_task_types = coordinator.intent_to_task_types(intent)
print(f"📝 需要执行的任务: {required_task_types}")
```

---

## Test Results / 测试结果

### Test Case 1: Evaluate Only / 仅评估

**Input**:
> "A PMS activation catalyst, CuNi-C2N2 Bimetallic Layered Catalyst, where Cu and Ni atoms are embedded in a 2D carbon-nitride (C2N2) matrix, forming a dual-atom active site with mixed coordination. Please evaluate it only."

**Output**:
```json
{
  "needs_design": false,
  "needs_evaluation": true,
  "evaluation_mode": "experts_only",
  "material_provided": "CuNi-C2N2 Bimetallic Layered Catalyst",
  "reasoning": "User provided specific material description, explicitly requests 'evaluate it only' indicating experts-only mode"
}
```

**Task Types**: `['evaluation_only']` ✅

---

### Test Case 2: Design + Evaluation / 设计+评估

**Input**:
> "设计一个去除重金属的材料，并评估其性能"

**Output**:
```json
{
  "needs_design": true,
  "needs_evaluation": true,
  "evaluation_mode": "with_summary",
  "material_provided": null,
  "reasoning": "用户要求设计新材料并进行常规评估，包含最终总结"
}
```

**Task Types**: `['material_design', 'evaluation', 'final_validation']` ✅

---

### Test Case 3: Mechanism Analysis Only / 仅机理分析

**Input**:
> "请分析TiO2的催化机理"

**Output**:
```json
{
  "needs_design": false,
  "needs_evaluation": false,
  "evaluation_mode": null,
  "needs_mechanism": true,
  "material_provided": "TiO2",
  "reasoning": "用户提供了具体材料TiO2，仅要求分析催化机理"
}
```

**Task Types**: `['mechanism_analysis']` ✅

---

### Test Case 4: Experts Only (Chinese) / 仅专家评分（中文）

**Input**:
> "请对Fe3O4材料仅进行三位专家评估，不需要总结"

**Output**:
```json
{
  "needs_design": false,
  "needs_evaluation": true,
  "evaluation_mode": "experts_only",
  "material_provided": "Fe3O4",
  "reasoning": "用户提供了具体材料Fe3O4，明确要求仅进行三位专家评估，不需要总结"
}
```

**Task Types**: `['evaluation_only']` ✅

---

## Fallback Mechanism / 回退机制

If LLM intent analysis fails (JSON parse error, API error, etc.), the system falls back to default behavior:

如果 LLM 意图分析失败（JSON 解析错误、API 错误等），系统会回退到默认行为：

```python
{
  "needs_design": True,
  "needs_evaluation": True,
  "evaluation_mode": "with_summary",
  "needs_mechanism": False,
  "needs_synthesis": False,
  "needs_operation": False,
  "material_provided": None,
  "reasoning": "Fallback to default due to error"
}
```

This ensures the system continues to function even if intent recognition fails.

这确保即使意图识别失败，系统也能继续运行。

---

## Future Enhancements / 未来增强

1. **Intent Caching** / **意图缓存**
   - Cache common queries to reduce API calls
   - 缓存常见问句以减少 API 调用

2. **Multi-turn Conversation** / **多轮对话**
   - Support follow-up questions with context
   - 支持带上下文的后续问题

3. **Intent Confidence** / **意图置信度**
   - Add confidence scores to intent analysis
   - 为意图分析添加置信度评分

4. **User Feedback Loop** / **用户反馈循环**
   - Learn from user corrections to improve accuracy
   - 从用户纠正中学习以提高准确性

---

## Related Files / 相关文件

- [src/prompts/intent_recognition_prompt.md](../src/prompts/intent_recognition_prompt.md) - Intent recognition prompt
- [src/agents/task_organizing_agent.py](../src/agents/task_organizing_agent.py) - TOA implementation
- [scripts/main.py](../scripts/main.py) - Integration in autonomous mode
- [test_toa_intent.py](../test_toa_intent.py) - Test script

---

**Last Updated**: 2025-12-13  
**Status**: ✅ Implemented and Tested

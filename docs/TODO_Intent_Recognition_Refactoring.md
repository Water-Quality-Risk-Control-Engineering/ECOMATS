# TODO: 任务意图识别重构 / Task Intent Recognition Refactoring

## 问题描述 / Problem Description

### 当前实现 / Current Implementation
[task_allocator.py](../src/agents/task_allocator.py) 中的 `determine_required_task_types()` 方法使用**硬编码关键词匹配**来识别用户意图：

```python
# 硬编码关键词列表
only_evaluation_keywords = ["仅评估", "只评估", "evaluate only", "it only", ...]
no_design_keywords = ["不需要设计", "this material", "the catalyst", ...]
```

### 存在的问题 / Issues

1. **覆盖不全**：无法识别所有可能的表达方式
   - 例如："Please evaluate it only" 虽然包含 "it only"，但仍可能被其他规则误判
   - 用户可以用无数种方式表达同一意图

2. **维护成本高**：每次发现新表达都要手动添加关键词

3. **语义理解弱**：无法理解上下文和隐含意图
   - 例如："A PMS activation catalyst, CuNi-C2N2... Please evaluate it only"
   - 明确提供了材料描述 + "evaluate it only"，意图很清晰，但硬编码规则可能失败

4. **与项目架构不符**：
   - 项目有专门的 **TOA (Task Organizing Agent)** 负责任务组织和调度
   - TOA 应该承担意图识别的职责，而不是依赖硬编码规则

---

## 改进方案 / Proposed Solution

### 方案：让 TOA 进行意图感知 / Use TOA for Intent Recognition

#### 1. 设计思路 / Design Concept

```
用户输入 (User Input)
      ↓
TOA + LLM 分析意图 (TOA analyzes intent with LLM)
      ↓
结构化意图输出 (Structured intent output)
{
  "needs_design": false,
  "needs_evaluation": true,
  "evaluation_mode": "experts_only",  // "experts_only" 或 "with_summary"
  "needs_mechanism": false,
  "needs_synthesis": false,
  "needs_operation": false,
  "material_provided": "CuNi-C2N2 Bimetallic Layered Catalyst",
  "reasoning": "User provided specific material and requested evaluation only"
}
      ↓
TaskAllocator 根据意图分配任务 (TaskAllocator assigns tasks)
```

#### 2. 实现步骤 / Implementation Steps

##### Step 1: 创建意图识别 Prompt
在 `src/prompts/` 创建 `intent_recognition_prompt.md`（中英双语）

```markdown
# Task Intent Recognition / 任务意图识别

## Your Role / 你的角色
You are a task intent analyzer for a water treatment material design system.
你是水处理材料设计系统的任务意图分析器。

## Task / 任务
Analyze user's requirement and determine what tasks are needed.
分析用户需求，确定需要执行哪些任务。

## Analysis Criteria / 分析标准

1. **Material Design / 材料设计**
   - If user asks to "design" or "create" a new material → needs_design: true
   - If user provides specific material description → needs_design: false
   
2. **Evaluation Mode / 评估模式**
   - "only evaluation", "evaluate only", "no summary" → evaluation_mode: "experts_only"
   - Normal evaluation request → evaluation_mode: "with_summary"

3. **Other Tasks / 其他任务**
   - "mechanism", "catalytic principle" → needs_mechanism: true
   - "synthesis", "preparation method" → needs_synthesis: true
   - "operation", "guidance" → needs_operation: true

## Output Format / 输出格式
Return JSON only, no explanation.
仅返回JSON，不要解释。

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

##### Step 2: 修改 TaskAllocator
在 `src/agents/task_allocator.py` 添加 LLM 意图识别方法：

```python
def determine_required_task_types_with_llm(self, task_description: str) -> List[str]:
    """
    使用 LLM 分析用户意图，动态决定需要哪些任务类型
    Use LLM to analyze user intent and determine required task types
    """
    if not self.llm:
        # 如果没有 LLM，回退到硬编码方法
        return self.determine_required_task_types(task_description)
    
    # 加载 Prompt
    prompt = PromptLoader.load_prompt("intent_recognition_prompt.md")
    
    # 调用 LLM
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"User requirement: {task_description}"}
    ]
    
    response = self.llm.invoke(messages)
    intent = json.loads(response.content)
    
    # 根据意图构建任务列表
    result = []
    
    if intent["needs_design"]:
        result.append("material_design")
    
    if intent["needs_evaluation"]:
        if intent["evaluation_mode"] == "experts_only":
            result.append("evaluation_only")
        else:
            result.extend(["evaluation", "final_validation"])
    
    if intent["needs_mechanism"]:
        result.append("mechanism_analysis")
    
    if intent["needs_synthesis"]:
        result.append("synthesis_method")
    
    if intent["needs_operation"]:
        result.append("operation_suggestion")
    
    return result if result else ["material_design"]
```

##### Step 3: 在 main.py 中启用
```python
# 使用 LLM 意图识别（推荐）
required_task_types = task_allocator.determine_required_task_types_with_llm(user_requirement)

# 或保留硬编码作为备选（向后兼容）
# required_task_types = task_allocator.determine_required_task_types(user_requirement)
```

---

## 优势 / Benefits

1. ✅ **语义理解强**：LLM 可以理解各种表达方式
2. ✅ **无需维护关键词**：不需要手动添加关键词列表
3. ✅ **符合架构设计**：TOA 负责意图理解，职责清晰
4. ✅ **可扩展性强**：新增任务类型只需调整 Prompt
5. ✅ **更好的用户体验**：准确识别用户真实意图

---

## 注意事项 / Considerations

1. **性能**：增加一次 LLM 调用（约 1-2 秒）
   - 可以缓存常见问句的意图识别结果
   
2. **成本**：每次运行增加一次 API 调用
   - 但相比整个工作流的调用次数，影响很小

3. **向后兼容**：保留硬编码方法作为 fallback
   - 如果 LLM 不可用，自动回退

4. **测试**：需要充分测试各种表达方式
   - 建议创建测试用例集

---

## 优先级 / Priority
**中等 / Medium**

- 当前硬编码方法基本可用，但覆盖不全
- 建议在下一个迭代中实现
- 可以先在自主调度模式中试点

---

## 相关文件 / Related Files

- [src/agents/task_allocator.py](../src/agents/task_allocator.py) - 需要修改
- [src/agents/task_organizing_agent.py](../src/agents/task_organizing_agent.py) - TOA 实现
- [scripts/main.py](../scripts/main.py) - 调用入口
- [scripts/main_async.py](../scripts/main_async.py) - 异步版本

---

## 记录时间 / Record Time
2025-12-13

## 提出者 / Proposed By
User feedback during testing

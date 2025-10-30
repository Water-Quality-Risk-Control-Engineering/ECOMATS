# Materials Project 工具使用说明

## 概述

本工具提供对Materials Project材料数据库的访问功能，使用官方的`mp-api`客户端库。

## 可用字段

当前版本的Materials Project API支持以下字段：

- `builder_meta`
- `calc_types`
- `chemsys`
- `composition`
- `composition_reduced`
- `created_at`
- `density`
- `density_atomic`
- `deprecated`
- `deprecated_tasks`
- `deprecation_reasons`
- `elements`
- `entries`
- `formula_anonymous`
- `formula_pretty`
- `initial_structures`
- `last_updated`
- `material_id`
- `nelements`
- `nsites`
- `origins`
- `run_types`
- `structure`
- `symmetry`
- `task_ids`
- `task_types`
- `volume`
- `warnings`

## 不可用字段

以下字段在当前版本的API中不可用：

- `elasticity`
- `magnetic_ordering`
- `total_magnetization`

## 工具方法

### search_materials

搜索材料，支持以下参数：

- `formula`: 化学式
- `elements`: 必须包含的元素列表
- `exclude_elements`: 要排除的元素列表
- `crystal_system`: 晶体系统
- `limit`: 返回结果的最大数量（默认100）
- `skip`: 跳过的结果数量（默认0）

### get_material_by_id

通过材料ID获取特定材料的详细信息。

### get_materials_summary

获取材料摘要信息，支持以下参数：

- `elements`: 元素列表
- `limit`: 返回结果的最大数量（默认100）

## 使用示例

### Python直接调用

```python
from src.tools.materials_project_tool import get_materials_project_tool

# 获取工具实例
tool = get_materials_project_tool()

# 按化学式搜索
result = tool.search_materials(formula="Fe2O3", limit=5)

# 按元素搜索
result = tool.search_materials(elements=["Fe", "O"], limit=5)

# 获取特定材料详情
result = tool.get_material_by_id("mp-19770")

# 获取材料摘要
result = tool.get_materials_summary(elements=["Fe"], limit=5)
```

### 通过CrewAI工具调用

```python
from src.tools.crewai_materials_project_tool import materials_project_tool

# 搜索材料
result = materials_project_tool._run(action="search", formula="Fe2O3")

# 获取特定材料详情
result = materials_project_tool._run(action="get_material", material_id="mp-19770")
```

## 注意事项

1. 确保已在环境变量中设置`MATERIALS_PROJECT_API_KEY`
2. 使用`fields`参数时，必须确保字段是API支持的字段
3. 使用`fields`参数时，必须确保字段是API支持的字段
4. 查询大量数据时可能需要较长时间，请设置合适的超时时间
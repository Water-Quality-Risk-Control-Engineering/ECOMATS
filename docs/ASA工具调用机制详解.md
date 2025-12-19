# ASA 工具调用机制详解

本文档详细说明 ASA (Assessment Screening Agent) 如何通过 CrewAI 的 Function Calling 机制调用各种数据库工具。

---

## 📋 目录

1. [Agent 创建与工具绑定](#1-agent-创建与工具绑定)
2. [工具工厂模式](#2-工具工厂模式)
3. [工具实现示例](#3-工具实现示例)
4. [完整调用流程](#4-完整调用流程)
5. [缓存机制](#5-缓存机制)

---

## 1. Agent 创建与工具绑定

### 文件位置
- **文件**: `src/agents/Assessment_Screening_agent_A.py`
- **行号**: L1-L68

### 核心代码

```python
# src/agents/Assessment_Screening_agent_A.py:L12-L29
class AssessmentScreeningAgentA(BaseAgent):
    def __init__(self, llm):
        """
        初始化 ASA A 智能体
        
        参数：
            llm: 语言模型实例
        """
        from src.config.config import Config
        super().__init__(
            llm, 
            "Assessment_Screening_agent_A",  # L24: Agent 角色名称
            "全面评估材料方案的各个方面",      # L25: Agent 目标
            "expert_a_prompt.md",            # L26: Prompt 文件
            temperature=Config.EXPERT_A_TEMPERATURE,  # L27: 温度设置
            max_iter=15  # L28: 最大迭代次数（允许多次工具调用）
        )
```

### 工具绑定逻辑

```python
# src/agents/Assessment_Screening_agent_A.py:L31-L67
def create_agent(self):
    """
    创建并配置 Agent，绑定工具
    
    返回：
        配置好的 Agent 实例（包含工具列表）
    """
    # L40-L52: 尝试创建 EAS 模型实例
    try:
        from src.utils.llm_config import create_eas_llm
        eas_llm = create_eas_llm()
        logger.info("成功创建EAS LLM实例")
        self.llm = eas_llm
    except Exception as e:
        logger.error(f"创建EAS模型实例失败: {e}")
        # 回退到传入的 LLM
    
    # L55: 调用父类创建 Agent
    agent = super().create_agent()
    
    # L56-L65: ⭐ 关键 - 绑定工具到 Agent
    try:
        from src.utils.llm_config import tools_enabled
        if tools_enabled():
            # L60: 绑定统一的评估工具集
            agent.tools = ToolFactory.create_catalytic_assessment_tools()
        else:
            agent.tools = []
    except Exception:
        # L64-L65: 回退方案
        agent.tools = ToolFactory.create_catalytic_assessment_tools()
    
    return agent
```

**说明**：
- L60 调用 `create_catalytic_assessment_tools()` 实际上调用的是 `create_unified_assessment_tools()`（别名）
- 参考: `src/tools/factory.py:L206-L208`

---

## 2. 工具工厂模式

### 文件位置
- **文件**: `src/tools/factory.py`
- **行号**: L177-L202

### 统一工具集创建

```python
# src/tools/factory.py:L177-L202
@staticmethod
def create_unified_assessment_tools():
    """
    创建统一的 ASA 评估工具集 (Expert A/B/C 共用)
    Create unified ASA assessment tools (shared by Expert A/B/C)
    
    根据 Prompt 要求，每个 ASA 都需要从 5 个维度进行全面评估：
    According to Prompt requirements, each ASA needs to evaluate from 5 dimensions:
    - 催化性能 (50%) - 需要 materials_project           # L185
    - 经济可行性 (10%) - 需要 pubchem, molport          # L186
    - 环境友好性 (10%) - 需要 pubchem, PNEC            # L187
    - 技术可行性 (10%) - 需要 materials_project, structure_validator  # L188
    - 结构合理性 (20%) - 需要 structure_validator, material_identifier  # L189
    
    Returns:
        list: 统一的评估工具实例列表 / Unified assessment tools list
    """
    tools = [
        materials_project_tool,          # L195: 材料结构和电子结构
        pubchem_tool,                    # L196: 化学品性质和毒性
        CrewAIMaterialIdentifierTool(),  # L197: 材料识别
        CrewAIStructureValidatorTool(),  # L198: 结构验证
        CrewAIPNECTool(),                # L199: 环境风险评估 (PNEC)
        CrewAIDataValidatorTool()        # L200: 数据验证
    ]
    return tools
```

### 工具实例导入

```python
# src/tools/factory.py:L1-L23
#!/usr/bin/env python3
"""
工具工厂
用于创建和管理各种数据库查询工具
"""

# CrewAI工具包装器
from src.tools.crewai_materials_project_tool import materials_project_tool  # L8
from src.tools.crewai_pubchem_tool import pubchem_tool                      # L9
from src.tools.crewai_name2cas_tool import CrewAIName2CASTool               # L10
from src.tools.crewai_name2properties_tool import CrewAIName2PropertiesTool # L11
from src.tools.crewai_cid2properties_tool import CrewAICID2PropertiesTool   # L12
from src.tools.crewai_formula2properties_tool import CrewAIFormula2PropertiesTool  # L13
from src.tools.crewai_material_search_tool import CrewAIMaterialSearchTool  # L14
from src.tools.crewai_pnec_tool import CrewAIPNECTool                       # L15
from src.tools.crewai_material_identifier_tool import CrewAIMaterialIdentifierTool  # L16
from src.tools.crewai_data_validator_tool import CrewAIDataValidatorTool    # L17
from src.tools.crewai_structure_validator_tool import CrewAIStructureValidatorTool  # L18
from src.tools.crewai_molport_tool import (                                 # L19-L23
    molport_availability_tool,
    molport_search_tool,
    molport_molecule_info_tool
)
```

---

## 3. 工具实现示例

### 3.1 Materials Project Tool

#### 文件位置
- **文件**: `src/tools/crewai_materials_project_tool.py`
- **行号**: L1-L160

#### 参数定义

```python
# src/tools/crewai_materials_project_tool.py:L6-L18
class MaterialsProjectToolInput(BaseModel):
    """
    Materials Project工具输入参数模型
    CrewAI 会将这个模型转换为 OpenAI Function Schema
    """
    action: str = Field(description="操作类型: 'search', 'get_properties'")  # L11
    material_id: Optional[str] = Field(default=None, description="材料ID（用于获取特定材料信息的操作）")  # L11
    formula: Optional[str] = Field(default=None, description="化学式（用于搜索）")  # L12
    elements: Optional[List[str]] = Field(default=None, description="必须包含的元素列表（用于搜索）")  # L13
    exclude_elements: Optional[List[str]] = Field(default=None, description="必须排除的元素列表（用于搜索）")  # L14
    crystal_system: Optional[str] = Field(default=None, description="晶体系统（用于搜索）")  # L15
    limit: int = Field(default=100, description="返回结果数量限制（用于搜索）")  # L16
    skip: int = Field(default=0, description="跳过的结果数量（用于搜索）")  # L17
    fields: Optional[List[str]] = Field(default=None, description="要包含的数据字段列表")  # L18
```

#### 工具类定义

```python
# src/tools/crewai_materials_project_tool.py:L20-L34
class CrewAIMaterialsProjectTool(BaseTool):
    """CrewAI工具包装器，用于Materials Project API"""
    
    # L23: 工具名称（会出现在 Function Schema 中）
    name: str = "Materials Project Database Access"
    
    # L24-L28: 工具描述（告诉 LLM 什么时候使用这个工具）
    description: str = (
        "访问Materials Project材料科学数据库以搜索材料、获取材料属性等。"
        "可以搜索具有特定化学式、元素组成、晶体结构或物理性质的材料。"
        "使用方法: action='search', formula='C3N4' 来搜索材料"
    )
    
    # L29: 参数模式（CrewAI 自动转换为 Function Schema）
    args_schema: type[BaseModel] = MaterialsProjectToolInput

    def __init__(self):
        super().__init__()
        self._cache: dict = {}      # L33: 本地缓存
        self._ttl_seconds = 600     # L34: 缓存有效期 10 分钟
```

#### 核心执行方法

```python
# src/tools/crewai_materials_project_tool.py:L36-L157
def _run(
    self,
    action: str,
    material_id: Optional[str] = None,
    formula: Optional[str] = None,
    elements: Optional[List[str]] = None,
    exclude_elements: Optional[List[str]] = None,
    crystal_system: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    fields: Optional[List[str]] = None
) -> str:
    """
    执行Materials Project数据库操作
    
    这是 CrewAI 调用的核心方法！
    当 LLM 决定调用这个工具时，CrewAI 会：
    1. 将 LLM 返回的 Function Call 参数传入这个方法
    2. 执行这个方法
    3. 将返回的 JSON 字符串传回给 LLM
    
    Args:
        action: 操作类型 ('search', 'get_properties', 'get_electronic', ...)
        material_id: 材料ID（用于获取特定材料信息的操作）
        formula: 化学式（用于搜索）
        elements: 必须包含的元素列表（用于搜索）
        exclude_elements: 必须排除的元素列表（用于搜索）
        crystal_system: 晶体系统（用于搜索）
        limit: 返回结果数量限制（用于搜索）
        skip: 跳过的结果数量（用于搜索）
        fields: 要包含的数据字段列表（用于获取材料详情，注意：必须是API支持的字段）
        
    Returns:
        JSON格式的API响应结果
    """
    try:
        # L76: 获取底层工具实例
        tool = get_materials_project_tool()
        
        # L77-L89: 生成缓存键
        key = (
            action,
            material_id or "",
            formula or "",
            tuple(elements) if elements else (),
            tuple(exclude_elements) if exclude_elements else (),
            crystal_system or "",
            int(limit or 0),
            int(skip or 0),
            tuple(fields) if fields else ()
        )
        
        import time as _t
        now = _t.time()
        
        # L90-L107: ⭐ 关键 - 检查 ContextStore 全局缓存
        if action == "search":
            cached_ctx = ContextStore.get("materials_project_search")  # L91
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)  # L93
            
            if formula:
                cached_ctx = ContextStore.get(f"materials_project_search:{formula}")  # L95
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)  # L96
        
        elif action == "get_properties":
            if not material_id:
                return json.dumps({"error": "获取材料详情需要提供material_id"})
            cached_ctx = ContextStore.get(f"materials_project_properties:{material_id}")  # L101
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)  # L102
        
        # L108-L110: 检查本地 TTL 缓存
        cached = self._cache.get(key)
        if cached and now - cached[0] < self._ttl_seconds:
            return json.dumps(cached[1], ensure_ascii=False, indent=2)
        
        # L112-L145: 执行不同的操作
        if action == "search":
            # L113-L125: 搜索材料
            result = tool.search_materials(
                formula=formula,
                elements=elements,
                exclude_elements=exclude_elements,
                crystal_system=crystal_system,
                limit=limit,
                skip=skip,
                fields=fields
            )
        elif action == "get_properties":
            # L126-L130: 获取材料详情
            if not material_id:
                return json.dumps({"error": "获取材料详情需要提供material_id"})
            result = tool.get_material_properties(material_id, fields)
        elif action == "get_electronic":
            # L131-L134: 获取电子性质（未实现）
            if not material_id:
                return json.dumps({"error": "获取电子性质需要提供material_id"})
            return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
        elif action == "get_thermo":
            # L135-L138: 获取热力学性质（未实现）
            if not material_id:
                return json.dumps({"error": "获取热力学性质需要提供material_id"})
            return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
        elif action == "get_elastic":
            # L139-L142: 获取弹性性质（未实现）
            if not material_id:
                return json.dumps({"error": "获取弹性性质需要提供material_id"})
            return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
        elif action == "get_summary":
            # L143-L144: 获取摘要（未实现）
            return json.dumps({"error": "此功能尚未实现"}, ensure_ascii=False)
        else:
            # L145-L146: 不支持的操作
            return json.dumps({"error": f"不支持的操作: {action}"})
        
        # L148-L149: 写入本地缓存
        self._cache[key] = (now, result)
        
        # L150-L153: ⭐ 写入 ContextStore 全局缓存（供其他 Agent 复用）
        if action == "search":
            ContextStore.set("materials_project_search", result)  # L151
            if formula:
                ContextStore.set(f"materials_project_search:{formula}", result)  # L153
        
        # L154: 返回 JSON 结果
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # L156-L157: 错误处理
        return json.dumps({"error": f"执行操作时出错: {str(e)}"}, ensure_ascii=False)
```

#### 工具实例创建

```python
# src/tools/crewai_materials_project_tool.py:L159-L160
# 创建工具实例供智能体使用
materials_project_tool = CrewAIMaterialsProjectTool()
```

---

### 3.2 Structure Validator Tool

#### 文件位置
- **文件**: `src/tools/crewai_structure_validator_tool.py`
- **行号**: L1-L63

#### 完整实现

```python
# src/tools/crewai_structure_validator_tool.py:L1-L63
import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.structure_validator_tool import get_structure_validator_tool
from src.utils.context_store import ContextStore

# L7-L9: 参数定义
class StructureValidatorToolInput(BaseModel):
    """结构验证工具输入参数模型"""
    material_formula: str = Field(description="材料化学式")

# L11-L21: 工具类定义
class CrewAIStructureValidatorTool(BaseTool):
    """CrewAI工具包装器，用于材料结构验证，支持全局缓存"""
    
    name: str = "Material Structure Validator"  # L14
    description: str = (  # L15-L20
        "验证材料结构是否真实存在。"
        "支持金属材料（使用Materials Project数据库）和有机化合物（使用PubChem数据库）的结构验证。"
        "当需要确认设计的材料结构在现实中是否存在时使用此工具。"
        "✨ 此工具支持全局缓存，重复查询不会重新调用 API。"
    )
    args_schema: type[BaseModel] = StructureValidatorToolInput  # L21
    
    # L23-L60: 核心执行方法
    def _run(
        self,
        material_formula: str
    ) -> str:
        """
        执行材料结构验证，支持 ContextStore 缓存
        
        Args:
            material_formula: 材料化学式
            
        Returns:
            JSON格式的验证结果
        """
        try:
            # L37-L42: ⭐ 先从全局上下文查询缓存
            cache_key = f"structure_validator:{material_formula}"
            cached = ContextStore.get(cache_key)
            if cached is not None:
                # 返回缓存结果
                return json.dumps(cached, ensure_ascii=False, indent=2)
            
            # L44-L45: 获取工具实例
            tool = get_structure_validator_tool()
            
            # L47-L48: 执行验证
            result = tool.validate_structure_exists(material_formula)
            
            # L50-L54: ⭐ 写入全局缓存（供其他 Agent 复用）
            ContextStore.set(cache_key, result)
            
            # 也写入通用键以供其他 Agent 复用
            ContextStore.set("structure_validator", result)
                
            # L56-L57: 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            # L59-L60: 错误处理
            return json.dumps({"error": f"执行验证时出错: {str(e)}"}, ensure_ascii=False)

# L62-L63: 创建工具实例
structure_validator_tool = CrewAIStructureValidatorTool()
```

---

### 3.3 PNEC Tool (环境风险评估)

#### 文件位置
- **文件**: `src/tools/crewai_pnec_tool.py`
- **行号**: L1-L75

#### 完整实现

```python
# src/tools/crewai_pnec_tool.py:L1-L75
import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.pnec_tool import get_pnec_tool
from src.utils.context_store import ContextStore

# L7-L10: 参数定义
class PNECToolInput(BaseModel):
    """PNEC工具输入参数模型"""
    query: str = Field(description="查询内容（CAS号或化合物名称）")
    query_type: str = Field(default="name", description="查询类型 ('name' 或 'cas')")

# L12-L26: 工具类定义
class CrewAIPNECTool(BaseTool):
    """CrewAI工具包装器，用于查询化学物质的预测无效应浓度(PNEC)数据"""
    
    name: str = "PNEC Database Query"  # L15
    description: str = (  # L16-L20
        "查询化学物质的预测无效应浓度(PNEC)数据，用于环境风险评估。"
        "可以基于CAS号或化合物名称查询PNEC值。"
        "当需要评估化学物质的环境安全性时使用此工具。"
    )
    args_schema: type[BaseModel] = PNECToolInput  # L21
    
    def __init__(self):
        super().__init__()
        self._cache = {}         # L25: 本地缓存
        self._ttl_seconds = 600  # L26: TTL 10分钟
    
    # L28-L75: 核心执行方法
    def _run(self, query: str, query_type: str = "name") -> str:
        """
        执行PNEC数据查询
        
        Args:
            query: 查询内容（CAS号或化合物名称）
            query_type: 查询类型 ("name" 或 "cas")
            
        Returns:
            JSON格式的查询结果
        """
        try:
            # L40-L42: 生成缓存键
            key = (query_type.lower(), query)
            import time as _t
            now = _t.time()

            # L44-L52: ⭐ 先尝试从全局上下文读取
            if query_type.lower() == "cas":
                cached_ctx = ContextStore.get(f"pnec:cas:{query}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            else:
                cached_ctx = ContextStore.get(f"pnec:name:{query}")
                if cached_ctx is not None:
                    return json.dumps(cached_ctx, ensure_ascii=False, indent=2)

            # L54-L57: 再尝试本地TTL缓存
            cached = self._cache.get(key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)

            # L59-L60: 获取工具实例
            tool = get_pnec_tool()
            
            # L62-L68: 根据查询类型执行相应操作
            if query_type.lower() == "cas":
                result = tool.get_pnec_by_cas(query)
                ContextStore.set(f"pnec:cas:{query}", result)  # L65: 写入全局缓存
            else:
                result = tool.get_pnec_by_name(query)
                ContextStore.set(f"pnec:name:{query}", result)  # L68: 写入全局缓存
            
            # L70-L72: 写入本地TTL缓存并返回
            self._cache[key] = (now, result)
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            # L74-L75: 错误处理
            return json.dumps({"error": f"执行查询时出错: {str(e)}"}, ensure_ascii=False)
```

---

### 3.4 PubChem Tool

#### 文件位置
- **文件**: `src/tools/crewai_pubchem_tool.py`
- **行号**: L1-L87

#### 关键代码

```python
# src/tools/crewai_pubchem_tool.py:L7-L12
class PubChemToolInput(BaseModel):
    """PubChem工具输入参数模型"""
    query: str = Field(description="查询内容（化学名称、分子式或InChIKey）")
    search_type: str = Field(default="auto", description="查询类型 ('auto', 'name', 'formula', 'inchikey')")
    get_cas: bool = Field(default=True, description="是否获取CAS号信息")
    get_full_info: bool = Field(default=False, description="是否获取完整化合物信息（包括所有属性）")

# L14-L28: 工具类定义
class CrewAIPubChemTool(BaseTool):
    """CrewAI工具包装器，用于PubChem数据库查询"""
    
    name: str = "PubChem Database Query"
    description: str = (
        "查询PubChem化学数据库以获取化合物信息。"
        "支持通过化学名称、分子式或InChIKey搜索化合物，并获取CAS号、分子量、SMILES、InChI等详细信息。"
        "当需要验证化学信息或获取化合物详细数据时使用此工具。"
    )
    args_schema: type[BaseModel] = PubChemToolInput

# L30-L84: 核心执行方法
def _run(
    self,
    query: str,
    search_type: str = "auto",
    get_cas: bool = True,
    get_full_info: bool = False
) -> str:
    """执行PubChem数据库查询"""
    try:
        # L53-L65: 检查 ContextStore 缓存
        if get_full_info:
            cached_ctx = ContextStore.get(f"pubchem_full:{query}")
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
        # ... 其他缓存检查
        
        # L66-L68: 检查本地 TTL 缓存
        cached = self._cache.get(key)
        if cached and now - cached[0] < self._ttl_seconds:
            return json.dumps(cached[1], ensure_ascii=False, indent=2)

        # L70-L79: 调用底层工具并写入缓存
        tool = get_pubchem_tool()
        if get_full_info:
            result = tool.get_compound_info(query)
            ContextStore.set(f"pubchem_full:{query}", result)  # L73
        elif get_cas:
            result = tool.get_compound_info_with_cas(query)
            ContextStore.set(f"pubchem_cas:{query}", result)  # L76
        else:
            result = tool.search_compound(query, search_type)
            ContextStore.set(f"pubchem_search:{search_type}:{query}", result)  # L79

        # L81-L84: 返回结果
        self._cache[key] = (now, result)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"执行查询时出错: {str(e)}"}, ensure_ascii=False)

# L86-L87: 创建工具实例
pubchem_tool = CrewAIPubChemTool()
```

---

## 4. 完整调用流程

### 流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    ASA Function Call 完整流程                    │
└─────────────────────────────────────────────────────────────────┘

步骤1: Agent 创建时绑定工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 src/agents/Assessment_Screening_agent_A.py:L31-L67

AssessmentScreeningAgentA.create_agent()
├─> 创建 Agent 实例 (L55)
└─> 绑定工具 (L60): agent.tools = ToolFactory.create_unified_assessment_tools()

工具列表:
  1. Materials Project Database Access
  2. PubChem Database Query
  3. Material Identifier Tool
  4. Material Structure Validator
  5. PNEC Database Query
  6. Data Validator Tool

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
步骤2: CrewAI 将工具转换为 Function Schema
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 CrewAI 内部机制（自动执行）

CrewAI 读取每个工具的:
- name (L23)
- description (L24-L28)
- args_schema (L29)

转换为 OpenAI Function Schema:
{
  "name": "Materials Project Database Access",
  "description": "访问Materials Project材料科学数据库...",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "description": "操作类型: 'search', 'get_properties'"
      },
      "formula": {
        "type": "string",
        "description": "化学式（用于搜索）"
      },
      "elements": {
        "type": "array",
        "items": {"type": "string"},
        "description": "必须包含的元素列表（用于搜索）"
      },
      ...
    },
    "required": ["action"]
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
步骤3: LLM 接收任务并决定调用工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 src/locales/zh/tasks/evaluation_task.yaml:L1-L48
📍 src/locales/zh/prompts/expert_a_prompt.md:L1-L70

用户输入:
  材料方案: TiO2/g-C3N4 异质结
  目标: 降解重金属镉

LLM 接收到的 Prompt (CrewAI 自动组装):
┌──────────────────────────────────────────────┐
│ System: 你是高级氧化评估专家A，专注于从    │
│ **催化活性和反应机理**角度评估水处理材料  │
│ 设计方案。                                  │
│                                              │
│ Task: 请根据以下五个维度评估材料方案的性能:│
│ 1. 催化性能（权重50%）                      │
│ 2. 经济可行性（权重10%）                    │
│ 3. 环境友好性（权重10%）                    │
│ 4. 技术可行性（权重10%）                    │
│ 5. 结构合理性（权重20%）                    │
│                                              │
│ 材料方案: TiO2/g-C3N4 异质结                │
│ 目标: 降解重金属镉                          │
│                                              │
│ Tools Available: [Function Schema 列表]     │
└──────────────────────────────────────────────┘

LLM 推理:
  "需要评估 TiO2 的催化性能，我需要:
   1. 查询 TiO2 的晶体结构和带隙 (Materials Project)
   2. 查询 Cd 的毒性数据 (PubChem)
   3. 评估环境风险 (PNEC)"

LLM 返回 Function Call:
{
  "function": "Materials Project Database Access",
  "arguments": {
    "action": "search",
    "formula": "TiO2",
    "fields": ["band_gap", "formation_energy", "energy_above_hull"]
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
步骤4: CrewAI 执行工具调用
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 src/tools/crewai_materials_project_tool.py:L36-L157

CrewAI 调用:
  materials_project_tool._run(
      action="search",
      formula="TiO2",
      fields=["band_gap", "formation_energy", "energy_above_hull"]
  )

执行流程:
  1. L91-L96: 检查 ContextStore 缓存
     cache_key = "materials_project_search:TiO2"
     cached = ContextStore.get(cache_key)
     
  2. 如果缓存命中 → 直接返回缓存结果 (L93)
  
  3. 如果缓存未命中:
     a. L76: 获取底层工具 tool = get_materials_project_tool()
     b. L113-L125: 调用 Materials Project API
        result = tool.search_materials(
            formula="TiO2",
            fields=["band_gap", "formation_energy", "energy_above_hull"]
        )
     c. L151-L153: 写入 ContextStore 全局缓存
        ContextStore.set("materials_project_search", result)
        ContextStore.set("materials_project_search:TiO2", result)
     d. L154: 返回 JSON 结果

返回给 LLM 的结果:
{
  "formula": "TiO2",
  "material_id": "mp-2657",
  "band_gap": 3.2,
  "formation_energy": -9.5,
  "energy_above_hull": 0.0,
  "is_stable": true
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
步骤5: LLM 接收工具结果继续推理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LLM 分析:
  "TiO2 带隙为 3.2 eV，适合紫外光催化。
   能量凸包高度为 0.0，说明热力学稳定。
   现在需要查询 Cd 的毒性数据..."

LLM 发起第二次 Function Call:
{
  "function": "PubChem Database Query",
  "arguments": {
    "query": "Cadmium",
    "search_type": "name",
    "get_cas": true,
    "get_full_info": true
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 src/tools/crewai_pubchem_tool.py:L30-L84

CrewAI 调用:
  pubchem_tool._run(
      query="Cadmium",
      search_type="name",
      get_cas=True,
      get_full_info=True
  )

执行流程:
  1. L53-L56: 检查 ContextStore 缓存
  2. L70-L73: 调用 PubChem API
     result = tool.get_compound_info("Cadmium")
  3. L73: 写入缓存
     ContextStore.set("pubchem_full:Cadmium", result)
  4. L82: 返回结果

返回结果:
{
  "name": "Cadmium",
  "CAS": "7440-43-9",
  "molecular_weight": 112.411,
  "toxicity": "highly toxic",
  "LD50": "225 mg/kg (oral, rat)"
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LLM 继续推理:
  "Cd 是高毒性重金属（LD50=225mg/kg）。
   现在评估环境风险..."

LLM 发起第三次 Function Call:
{
  "function": "PNEC Database Query",
  "arguments": {
    "query": "7440-43-9",
    "query_type": "cas"
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 src/tools/crewai_pnec_tool.py:L28-L75

返回结果:
{
  "CAS": "7440-43-9",
  "PNEC_aquatic": 0.25,  # μg/L
  "risk_level": "high"
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
步骤6: LLM 生成最终评估报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 src/locales/zh/prompts/expert_a_prompt.md:L42-L69

基于工具调用结果，LLM 生成 JSON 输出:

{
  "expert": "高级氧化评估专家A",
  "focus_area": "催化活性和反应机理",
  "evaluation": {
    "catalytic_activity": {
      "score": 8,
      "analysis": "基于 Materials Project 数据，TiO2 带隙为 3.2 eV，适合紫外光催化。异质结构可以促进电荷分离，提高催化效率。",
      "strengths": [
        "TiO2 热力学稳定（energy_above_hull=0.0）",
        "带隙适中，光催化活性高",
        "与 g-C3N4 形成异质结可提升电荷分离效率"
      ],
      "weaknesses": [
        "仅在紫外光下活性高，可见光利用率低"
      ]
    },
    "reaction_mechanism": {
      "score": 7,
      "analysis": "TiO2 光激发产生电子-空穴对，电子转移至 g-C3N4，空穴氧化污染物。",
      "reaction_pathway": "TiO2 + hv → e- + h+ | e- → g-C3N4 | h+ + Cd²⁺ → Cd⁴⁺"
    },
    "selectivity": {
      "score": 6,
      "analysis": "对 Cd²⁺ 有一定选择性，但可能同时氧化其他物质。"
    },
    "efficiency": {
      "score": 7,
      "analysis": "光催化效率中等，需要紫外光激发。"
    }
  },
  "overall_score": 7.5,
  "recommendations": [
    "考虑掺杂以提升可见光响应",
    "优化异质结界面接触",
    "增加活性位点密度"
  ],
  "conclusion": "材料方案在催化活性方面表现良好，但需要进一步优化可见光利用率。基于 Materials Project 和 PubChem 数据分析，建议通过掺杂改性提升性能。"
}
```

---

## 5. 缓存机制

### 5.1 ContextStore 全局缓存

#### 文件位置
- **文件**: `src/utils/context_store.py`
- **说明**: 跨 Agent 共享缓存

#### 使用示例

```python
# 写入缓存
ContextStore.set("materials_project_search:TiO2", result)

# 读取缓存
cached = ContextStore.get("materials_project_search:TiO2")
if cached is not None:
    return cached
```

#### 在工具中的应用

| 工具 | 缓存键格式 | 代码位置 |
|------|-----------|---------|
| **Materials Project** | `materials_project_search:{formula}` | `crewai_materials_project_tool.py:L151-L153` |
| **PubChem** | `pubchem_full:{query}` | `crewai_pubchem_tool.py:L73` |
| **PubChem** | `pubchem_cas:{query}` | `crewai_pubchem_tool.py:L76` |
| **Structure Validator** | `structure_validator:{formula}` | `crewai_structure_validator_tool.py:L38-L51` |
| **PNEC** | `pnec:cas:{query}` | `crewai_pnec_tool.py:L65` |
| **PNEC** | `pnec:name:{query}` | `crewai_pnec_tool.py:L68` |

### 5.2 本地 TTL 缓存

#### 实现位置
- 每个工具内部的 `self._cache` 字典
- TTL: 600 秒（10 分钟）

#### 代码示例

```python
# src/tools/crewai_materials_project_tool.py:L33-L34
def __init__(self):
    super().__init__()
    self._cache: dict = {}      # 本地缓存
    self._ttl_seconds = 600     # 缓存有效期

# L108-L110: 检查缓存
cached = self._cache.get(key)
if cached and now - cached[0] < self._ttl_seconds:
    return json.dumps(cached[1], ensure_ascii=False, indent=2)

# L148-L149: 写入缓存
self._cache[key] = (now, result)
```

### 5.3 双层缓存优势

```
查询流程:
1. 检查 ContextStore 全局缓存（跨 Agent 共享）
   ├─ 命中 → 直接返回
   └─ 未命中 ↓

2. 检查本地 TTL 缓存（单个工具实例内）
   ├─ 命中 → 返回
   └─ 未命中 ↓

3. 调用 API
   ├─ 写入 ContextStore 全局缓存
   ├─ 写入本地 TTL 缓存
   └─ 返回结果

优势:
✅ 全局缓存: 多个 Agent 共享，避免重复 API 调用
✅ 本地缓存: 快速访问，降低缓存查询开销
✅ TTL 机制: 自动过期，确保数据新鲜度
```

---

## 📊 总结

### 关键文件索引

| 组件 | 文件路径 | 关键行号 |
|------|---------|---------|
| **ASA A Agent** | `src/agents/Assessment_Screening_agent_A.py` | L12-L67 |
| **工具工厂** | `src/tools/factory.py` | L177-L202 |
| **Materials Project Tool** | `src/tools/crewai_materials_project_tool.py` | L6-L160 |
| **Structure Validator** | `src/tools/crewai_structure_validator_tool.py` | L7-L63 |
| **PNEC Tool** | `src/tools/crewai_pnec_tool.py` | L7-L75 |
| **PubChem Tool** | `src/tools/crewai_pubchem_tool.py` | L7-L87 |
| **任务描述** | `src/locales/zh/tasks/evaluation_task.yaml` | L1-L48 |
| **Prompt** | `src/locales/zh/prompts/expert_a_prompt.md` | L1-L70 |
| **ContextStore** | `src/utils/context_store.py` | - |

### 工具调用核心要素

1. **参数定义** (`BaseModel` + `Field`) → L7-L18
2. **工具描述** (`name` + `description`) → L23-L28
3. **执行方法** (`_run()`) → L36-L157
4. **缓存机制** (ContextStore + TTL) → L91-L96, L148-L153
5. **错误处理** (JSON 错误返回) → L156-L157

### Function Call 流程总结

```
Agent 创建 → 绑定工具 → CrewAI 转换 Schema → LLM 决策 → 
工具执行 → 缓存结果 → 返回 LLM → 生成报告
```

---

**文档版本**: v1.0  
**最后更新**: 2025-12-19  
**维护者**: ECOMATS 开发团队

# 改进的工具调用逻辑设计

## 1. 当前问题分析

当前工具调用逻辑存在以下问题：
1. 工具在所有智能体中都被无差别地注册，无论是否需要
2. 工具调用缺乏明确的验证和补充信息区分
3. 缺乏结构验证机制，无法确认设计的材料结构是否真实存在
4. 工具调用时机不够精准，有些地方需要验证但没有强制调用

## 2. 改进目标

1. **精准调用**：根据不同任务阶段和需求精准调用相应工具
2. **验证优先**：在关键节点强制进行数据验证
3. **信息补充**：在需要时主动获取补充信息
4. **结构验证**：实现材料结构存在性验证功能

## 3. 改进方案

### 3.1 工具分类与职责划分

#### 验证类工具（必须调用）
- **MaterialsProjectValidator**：验证金属材料结构存在性和性质
- **PubChemValidator**：验证有机化合物结构存在性和性质
- **DataValidator**：验证数据格式和有效性

#### 信息补充类工具（按需调用）
- **MaterialSearcher**：检索相似材料性能数据
- **PropertyLookup**：查询材料/化合物性质
- **IdentifierResolver**：解析材料标识符

### 3.2 任务阶段工具调用策略

#### 设计阶段
```
1. 设计材料结构
2. 调用结构验证工具验证材料是否存在
   - 金属材料 → MaterialsProjectValidator
   - 有机材料 → PubChemValidator
3. 如果验证失败，返回重新设计
```

#### 评估阶段
```
1. 评估材料性能
2. 强制调用验证工具获取准确数据
   - 金属材料 → MaterialsProjectValidator
   - 有机材料 → PubChemValidator
   - 通用性质 → PropertyLookup
3. 使用DataValidator验证数据有效性
```

#### 机理分析阶段
```
1. 分析反应机理
2. 按需调用信息补充工具
   - 需要电子结构数据 → MaterialsProjectValidator
   - 需要分子信息 → PubChemValidator
   - 需要性能对比 → MaterialSearcher
```

#### 最终验证阶段
```
1. 综合所有评估结果
2. 强制调用所有验证工具进行交叉验证
3. 生成最终验证报告
```

### 3.3 工具调用逻辑实现

#### 验证逻辑
```python
class MaterialValidator:
    def __init__(self):
        self.mp_tool = get_materials_project_tool()
        self.pubchem_tool = get_pubchem_tool()
        self.validator = get_data_validator_tool()
    
    def validate_material_structure(self, material_formula, material_type):
        """
        验证材料结构是否存在
        """
        if material_type == "metal":
            # 使用Materials Project验证金属材料
            result = self.mp_tool.search_materials(formula=material_formula, limit=1)
            if result.get("data"):
                return {"valid": True, "data": result["data"][0]}
            else:
                return {"valid": False, "reason": "Materials Project中未找到该材料"}
        elif material_type == "organic":
            # 使用PubChem验证有机材料
            result = self.pubchem_tool.search_compound(material_formula)
            if "error" not in result:
                return {"valid": True, "data": result}
            else:
                return {"valid": False, "reason": "PubChem中未找到该化合物"}
        else:
            # 尝试两种方法
            mp_result = self.mp_tool.search_materials(formula=material_formula, limit=1)
            if mp_result.get("data"):
                return {"valid": True, "data": mp_result["data"][0], "type": "metal"}
            
            pubchem_result = self.pubchem_tool.search_compound(material_formula)
            if "error" not in pubchem_result:
                return {"valid": True, "data": pubchem_result, "type": "organic"}
            
            return {"valid": False, "reason": "Materials Project和PubChem中均未找到该材料"}
    
    def validate_material_properties(self, material_id, material_type):
        """
        验证材料性质数据
        """
        if material_type == "metal":
            result = self.mp_tool.get_material_by_id(material_id)
            validation = self.validator.validate_chemical_data(result)
            return {"data": result, "validation": validation}
        elif material_type == "organic":
            result = self.pubchem_tool.get_properties_by_cid(material_id)
            validation = self.validator.validate_chemical_data(result)
            return {"data": result, "validation": validation}
```

#### 信息补充逻辑
```python
class InformationSupplementer:
    def __init__(self):
        self.search_tool = get_material_search_tool()
        self.property_tool = get_name2properties_tool()
    
    def get_similar_materials(self, query, limit=5):
        """
        获取相似材料信息用于参考
        """
        return self.search_tool.search_similar_materials(query, limit)
    
    def get_material_properties(self, material_name):
        """
        获取材料性质信息
        """
        return self.property_tool.get_properties_by_name(material_name)
```

### 3.4 工具在智能体中的注册策略

#### 设计智能体
```python
class CreativeDesigningAgent(BaseAgent):
    def create_agent(self):
        agent = super().create_agent()
        # 只注册结构验证工具
        agent.tools = [structure_validator_tool]
        return agent
```

#### 评估智能体
```python
class AssessmentScreeningAgent(BaseAgent):
    def create_agent(self):
        agent = super().create_agent()
        # 注册验证工具和数据验证工具
        agent.tools = [
            materials_project_validator_tool,
            pubchem_validator_tool,
            data_validator_tool
        ]
        return agent
```

#### 机理分析智能体
```python
class MechanismMiningAgent(BaseAgent):
    def create_agent(self):
        agent = super().create_agent()
        # 注册验证工具和信息补充工具
        agent.tools = [
            materials_project_validator_tool,
            pubchem_validator_tool,
            material_searcher_tool,
            property_lookup_tool
        ]
        return agent
```

## 4. 结构验证功能实现

### 4.1 结构验证工具设计

```python
class StructureValidator:
    def __init__(self):
        self.identifier_tool = get_material_identifier_tool()
        self.mp_tool = get_materials_project_tool()
        self.pubchem_tool = get_pubchem_tool()
    
    def validate_structure_exists(self, material_formula):
        """
        验证材料结构是否真实存在
        """
        # 首先识别材料类型
        identification = self.identifier_tool.identify_material(material_formula)
        material_type = identification.get("material_type", "unknown")
        
        if material_type == "metal":
            # 金属材料验证
            return self._validate_metal_structure(material_formula)
        elif material_type == "organic":
            # 有机材料验证
            return self._validate_organic_structure(material_formula)
        else:
            # 未知类型，尝试两种方法
            metal_result = self._validate_metal_structure(material_formula)
            if metal_result["valid"]:
                return metal_result
            
            organic_result = self._validate_organic_structure(material_formula)
            return organic_result
    
    def _validate_metal_structure(self, formula):
        """
        验证金属材料结构
        """
        try:
            result = self.mp_tool.search_materials(formula=formula, limit=1)
            if result.get("data") and len(result["data"]) > 0:
                return {
                    "valid": True,
                    "type": "metal",
                    "data": result["data"][0],
                    "source": "Materials Project"
                }
            else:
                return {
                    "valid": False,
                    "type": "metal",
                    "reason": f"Materials Project中未找到化学式为{formula}的材料"
                }
        except Exception as e:
            return {
                "valid": False,
                "type": "metal",
                "reason": f"验证过程中出错: {str(e)}"
            }
    
    def _validate_organic_structure(self, formula):
        """
        验证有机材料结构
        """
        try:
            result = self.pubchem_tool.search_compound(formula)
            if "error" not in result:
                return {
                    "valid": True,
                    "type": "organic",
                    "data": result,
                    "source": "PubChem"
                }
            else:
                return {
                    "valid": False,
                    "type": "organic",
                    "reason": f"PubChem中未找到化学式为{formula}的化合物"
                }
        except Exception as e:
            return {
                "valid": False,
                "type": "organic",
                "reason": f"验证过程中出错: {str(e)}"
            }
```

### 4.2 在设计任务中的应用

```python
class DesignTask(BaseTask):
    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        description = """
        设计步骤：
        1. 分析目标污染物特性和处理要求
        2. 选择合适的材料类型
        3. 设计材料结构
        4. **强制调用结构验证工具验证设计的材料结构是否存在**
        5. 如果验证失败，需要重新设计
        6. 优化材料参数
        """
        
        # 添加结构验证要求
        description += """
        
        重要验证要求：
        - 必须使用StructureValidator工具验证设计的材料结构是否真实存在
        - 如果材料在Materials Project或PubChem中找不到，需要重新设计
        - 验证通过后才能进入下一步
        """
        
        # ... 其他代码
```

## 5. 实施计划

1. **第一阶段**：实现StructureValidator工具和验证逻辑
2. **第二阶段**：修改智能体工具注册策略
3. **第三阶段**：更新任务描述，明确验证要求
4. **第四阶段**：实现信息补充工具和逻辑
5. **第五阶段**：测试和优化

## 6. 预期效果

1. **提高数据准确性**：通过强制验证确保所有材料数据真实可靠
2. **优化工具调用**：减少不必要的工具调用，提高系统效率
3. **增强系统可靠性**：通过结构验证避免设计不存在的材料
4. **改善用户体验**：提供更精准的信息补充服务
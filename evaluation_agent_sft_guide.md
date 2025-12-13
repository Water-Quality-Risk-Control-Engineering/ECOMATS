# 评估智能体 SFT 生成指南

## 📋 目录
- [智能体职责定位](#智能体职责定位)
- [数据格式规范](#数据格式规范)
- [Instruction生成逻辑](#instruction生成逻辑)
- [Output生成逻辑](#output生成逻辑)
- [质量控制标准](#质量控制标准)
- [样本示例](#样本示例)
- [生成脚本集成](#生成脚本集成)

---

## 智能体职责定位

### 核心职责
评估智能体（Assessment Agent）是ECOMATS系统中的**质量把关者**，负责从多个维度对材料方案进行综合评估，确保方案的可行性和有效性。

### 评估维度
1. **催化性能** (50%权重) - Catalytic Performance
   - PMS活化能力
   - 活性位点合理性
   - ROS生成路径
   - 机理一致性

2. **经济可行性** (10%权重) - Economic Viability
   - 成本估算
   - 元素丰度
   - 市场价格
   - 可扩展性

3. **环境友好性** (10%权重) - Environmental Friendliness
   - 毒性评估
   - 金属浸出风险
   - 生态影响
   - PNEC合规性

4. **技术可行性** (10%权重) - Technical Feasibility
   - 合成难度
   - 前驱体可获得性
   - 反应条件
   - 实验室可复现性

5. **结构合理性** (20%权重) - Structural Validity
   - 配位几何
   - 电荷平衡
   - 化学键合
   - 结构稳定性

### 工作模式
- **数据驱动**: 基于数据库查询和工具验证
- **多维度评分**: 1-10分制，每个维度独立评分
- **建设性反馈**: 识别弱点并提供改进建议
- **严格验证**: 禁止虚构数据，仅使用真实工具返回结果

---

## 数据格式规范

### 标准格式
```json
{
  "instruction": "完整的评估问题描述（包含材料信息、评估要求、可用数据等）",
  "output": "详细的评估报告（包含五维度评分、优缺点分析、数据验证、改进建议）"
}
```

### 与其他智能体的区别
| 智能体 | 核心任务 | Output特点 |
|--------|---------|-----------|
| 设计智能体 | 创造新材料方案 | 方案设计 + 参数优化 |
| 合成智能体 | 提供制备方法 | 步骤化流程 + 操作参数 |
| 机理智能体 | 解析反应机理 | 化学方程式 + 机制解释 |
| **评估智能体** | **质量评估与打分** | **量化评分 + 数据验证 + 改进建议** |

---

## Instruction生成逻辑

### 1. 基础结构

Instruction应包含以下完整信息：

```
你是一个水处理材料评估专家（Assessment Agent）。

【待评估材料】
材料名称: [材料化学式或描述]
设计来源: [设计智能体/文献来源/用户提供]
应用场景: [目标污染物类型、废水特征]
设计依据: [设计思路简述]

【材料基本信息】
- 化学组成: [元素组成、配位结构]
- 合成方法: [制备路径概述]
- 预期性能: [降解率、矿化率等]
- 成本估算: [如有]

【评估要求】
1. 从五个维度进行评估：催化性能(50%)、经济可行性(10%)、环境友好性(10%)、技术可行性(10%)、结构合理性(20%)
2. 每个维度给出1-10分的具体评分及详细理由
3. 基于以下可用数据/工具结果进行验证：
   - [Materials Project数据 / PubChem查询结果 / 文献数据等]
4. 识别优缺点并提供改进建议

【可用验证数据】（如有）
- Materials Project ID: [mp-xxxxx]
- PubChem CID: [xxxxxxx]
- 结构验证结果: [已通过/部分通过/未验证]
- 环境安全数据: [PNEC值、毒性等级等]

请进行全面评估并输出标准JSON格式的评估报告。
```

### 2. Instruction变体设计

根据评估场景不同，设计多种Instruction模板：

**场景A: 基于设计智能体输出的评估**
```
你是一个材料评估专家。设计智能体提出了以下催化剂方案，请进行全面评估。

【材料方案】
化学式: Fe₁.₂Co₀.₈-N₄/BC (Fe-Co双金属负载的N掺杂生物炭)
设计目标: 降解印染废水中的亚甲基蓝染料
预期性能: 可见光下1小时降解率>90%，循环使用5次以上

【设计依据】
- Fe-Co双金属协同催化
- N掺杂增强电子转移
- 生物炭提供丰富吸附位点

【评估维度权重】
催化性能(50%) + 经济性(10%) + 环保性(10%) + 技术可行性(10%) + 结构合理性(20%)

【可用验证数据】
- Materials Project中存在类似Fe-Co-N配位结构
- PubChem显示前驱体(FeCl₃、Co(NO₃)₂)市场价格合理
- 生物炭无明显毒性风险

请基于上述信息进行评估，给出五维度评分和详细分析。
```

**场景B: 基于文献材料的复评估**
```
你是一个材料评估专家。以下是从文献中提取的催化剂材料，请对其进行重新评估。

【文献材料】
材料: MnFe₂O₄/LDH复合材料
文献性能: PMS活化降解罗丹明B，60 min去除率92%，TOC矿化85%
制备方法: 水热法(180°C，12 h)
成本: 约350元/kg

【评估重点】
1. 验证催化性能的合理性（基于配位环境和活性位点）
2. 评估经济可行性（Mn、Fe元素丰度和价格）
3. 分析环境风险（Mn²⁺浸出、Fe³⁺释放）
4. 技术可行性（水热法设备要求）
5. 结构稳定性（LDH层状结构、磁性分离）

【已知数据】
- Materials Project中存在MnFe₂O₄相关晶体结构（mp-18759）
- Mn、Fe均为低成本元素
- LDH结构稳定性良好

请进行全面评估。
```

**场景C: 多材料对比评估**
```
你是一个材料评估专家。需要对以下三个催化剂方案进行对比评估，选出最优方案。

【方案1】 Fe-SAC/CN (Fe单原子/g-C₃N₄)
- 金属用量: 1.5 wt%
- 预期降解率: >95%
- 成本: 约800元/kg

【方案2】 Co-Zn/Fe₃O₄ (双金属掺杂磁铁矿)
- 金属用量: Co 5 wt%, Zn 3 wt%
- 预期降解率: >85%
- 成本: 约300元/kg
- 可磁性分离

【方案3】 畜禽粪便衍生Fe/C复合材料
- 金属用量: Fe ~8 wt% (天然含有)
- 预期降解率: >75%
- 成本: <100元/kg
- 废弃物利用

【评估任务】
1. 对每个方案进行五维度评分
2. 分析各方案的优劣势
3. 根据不同应用场景推荐最优方案
4. 提供排序建议及理由

请输出标准格式的对比评估报告。
```

### 3. Instruction关键要素清单

每个Instruction **必须包含**：
- ✅ 角色定义（"你是一个材料评估专家"）
- ✅ 待评估材料的基本信息（化学式、组成、性能）
- ✅ 评估维度和权重（五维度+权重百分比）
- ✅ 可用的验证数据或工具结果（真实数据，非虚构）
- ✅ 具体评估要求（评分、分析、建议等）
- ✅ 输出格式要求（JSON结构化输出）

---

## Output生成逻辑

### 1. 标准Output结构

```json
{
  "evaluator": "评估智能体标识（如Expert-C）",
  "material_info": {
    "formula": "材料化学式",
    "name": "材料名称",
    "application": "应用场景"
  },
  "evaluation_summary": {
    "overall_score": "加权总分（1-10，保留1位小数）",
    "recommendation": "推荐/谨慎推荐/不推荐/需改进后评估"
  },
  "dimensional_scores": {
    "catalytic_performance": {
      "score": 8.5,
      "weight": "50%",
      "justification": "详细评分理由（200-400字）",
      "evidence": [
        "Fe-N₄配位结构与文献中PMS活化催化剂一致",
        "DFT计算显示d带中心位于-2.3 eV，适合PMS吸附",
        "预期生成·OH和SO₄·⁻双自由基"
      ]
    },
    "economic_viability": {
      "score": 7.0,
      "weight": "10%",
      "justification": "详细评分理由",
      "evidence": [
        "Fe元素丰度高，成本低（FeCl₃约50元/kg）",
        "生物炭来自农业废弃物，成本<100元/吨",
        "总体成本估算约400元/kg，可接受"
      ]
    },
    "environmental_friendliness": {
      "score": 9.0,
      "weight": "10%",
      "justification": "详细评分理由",
      "evidence": [
        "Fe毒性低，PubChem显示无严重生态风险",
        "生物炭基底环境友好",
        "预计Fe浸出<2 mg/L（符合EPA标准3 mg/L）"
      ]
    },
    "technical_feasibility": {
      "score": 8.0,
      "weight": "10%",
      "justification": "详细评分理由",
      "evidence": [
        "制备方法为热解+浸渍，常规实验室可完成",
        "反应条件温和（800°C热解，室温浸渍）",
        "前驱体易获取，无特殊设备要求"
      ]
    },
    "structural_validity": {
      "score": 8.5,
      "weight": "20%",
      "justification": "详细评分理由",
      "evidence": [
        "Fe-N₄配位几何与Materials Project中mp-xxxxx一致",
        "电荷平衡合理（Fe²⁺/Fe³⁺混合价态）",
        "结构稳定性经Structure Validator验证通过"
      ]
    }
  },
  "strengths": [
    "具体优势1（基于数据）",
    "具体优势2（基于文献对比）",
    "具体优势3（基于工具验证）"
  ],
  "weaknesses": [
    "具体弱点1（识别问题）",
    "具体弱点2（潜在风险）",
    "具体弱点3（改进空间）"
  ],
  "improvement_suggestions": [
    {
      "issue": "问题描述",
      "suggestion": "改进建议",
      "expected_improvement": "预期改进效果"
    }
  ],
  "data_validation": {
    "materials_project_verified": "是/否/部分",
    "pubchem_verified": "是/否/不适用",
    "structure_validated": "是/否",
    "environmental_risk_assessed": "是/否",
    "validation_notes": "数据验证说明（如有工具调用失败需说明）"
  }
}
```

### 2. Output关键特征

**定量化**
- 每个维度必须有明确的1-10分评分
- 加权总分计算公式透明
- 数值必须有具体依据，不能凭空估算

**证据驱动**
- 每个评分必须有evidence支撑
- 引用具体的数据库查询结果（Materials Project ID、PubChem CID等）
- 如工具调用失败，必须明确说明

**建设性**
- 不仅指出问题，还要提供解决方案
- 改进建议要具体可操作
- 预期改进效果要量化

**格式严格**
- 必须输出合法的JSON格式
- 字段名称严格遵循规范
- 数值类型正确（score为浮点数，weight为字符串等）

### 3. Output内容要求

**评分理由长度**
- 每个维度的justification: 200-400字
- 包含具体数据、对比分析、推理过程
- 避免模板化表述（"该材料性能良好" ❌）

**Evidence要求**
- 每个维度至少3条evidence
- Evidence必须具体（包含数值、来源、对比对象）
- 优先使用数据库验证结果

**改进建议格式**
```json
{
  "issue": "Fe单原子负载量仅1.5 wt%，可能导致活性位点密度不足",
  "suggestion": "通过优化浸渍次数或延长热处理时间，将Fe负载量提升至2.5-3.0 wt%",
  "expected_improvement": "预期催化性能评分从8.5提升至9.0以上，降解率从90%提升至95%"
}
```

---

## 质量控制标准

### 1. 必检项（Mandatory Checks）

| 检查项 | 标准 | 不合格示例 |
|--------|------|-----------|
| 评分合理性 | 所有评分在1-10范围内，与justification一致 | score=9.5但justification指出严重缺陷 |
| 权重正确性 | 五维度权重之和=100% | 权重不符合50%+10%+10%+10%+20% |
| 数据真实性 | 所有Materials Project ID、CAS号等可验证 | 虚构mp-xxxxx编号 |
| 证据充分性 | 每个维度至少3条具体evidence | evidence仅列举"性能良好" |
| JSON格式 | 输出为合法JSON，字段名称正确 | 缺少必需字段或JSON语法错误 |
| 改进建议可操作性 | 建议具体且可量化 | "需要进一步优化"（过于笼统） |

### 2. 优选项（Quality Enhancements）

- ✅ 包含与同类材料的对比分析
- ✅ 引用具体文献或数据库记录
- ✅ 量化改进建议的预期效果
- ✅ 识别多个维度之间的权衡关系
- ✅ 提供不同应用场景下的评估差异

### 3. 禁止项（Forbidden Practices）

- ❌ 虚构任何数据库标识符（mp-ID、CAS号、PubChem CID）
- ❌ 评分与理由矛盾（如score=9但justification全是问题）
- ❌ 模板化评语（"该材料性能优异，值得推荐"）
- ❌ 忽略明显的化学不合理性（如电荷不平衡、配位几何错误）
- ❌ 缺少数据验证环节（data_validation字段为空）

---

## 样本示例

### 示例1: 单原子催化剂评估

**Instruction**:
```
你是一个水处理材料评估专家。设计智能体提出了以下单原子催化剂方案，请进行全面评估。

【待评估材料】
材料名称: Fe-SAC/CN (Fe单原子负载在g-C₃N₄上)
化学式: Fe₁-N₄@g-C₃N₄ (Fe含量1.8 wt%)
应用场景: 印染废水中亚甲基蓝染料降解
设计依据: Fe-N₄单原子位点作为电子陷阱，抑制光生载流子复合，同时催化PMS生成·OH和SO₄·⁻

【材料基本信息】
- 配位结构: Fe-N₄平面四配位
- 合成方法: 热剥离g-C₃N₄ + FeCl₃浸渍 + 800°C热解
- 预期性能: 可见光下60 min降解率95%，循环8次后保持85%活性
- 成本估算: 约800元/kg

【评估要求】
1. 从五个维度评分：催化性能(50%)、经济性(10%)、环保性(10%)、技术可行性(10%)、结构合理性(20%)
2. 每个维度给出1-10分评分及详细理由（200-400字）
3. 识别优缺点并提供至少3条改进建议

【可用验证数据】
- Materials Project中存在类似Fe-N配位结构（mp-762252，FeN₄结构）
- PubChem显示FeCl₃毒性等级2，g-C₃N₄无明显毒性
- 文献报道Fe-N₄单原子催化剂对PMS活化效率高（kobs=0.08 min⁻¹）
- 结构验证: Fe-N₄配位几何合理，电荷平衡符合Fe²⁺/Fe³⁺混合价态

请输出标准JSON格式的评估报告。
```

**Output** (省略部分，完整版见注释):
```json
{
  "evaluator": "Expert-C",
  "material_info": {
    "formula": "Fe₁-N₄@g-C₃N₄",
    "name": "Fe单原子催化剂/g-C₃N₄",
    "application": "印染废水亚甲基蓝染料降解"
  },
  "evaluation_summary": {
    "overall_score": 8.4,
    "recommendation": "推荐，但需优化Fe负载量和成本控制"
  },
  "dimensional_scores": {
    "catalytic_performance": {
      "score": 9.0,
      "weight": "50%",
      "justification": "Fe-N₄单原子位点是已被广泛验证的PMS活化中心。该材料设计合理：(1) Fe-N₄配位结构与Materials Project中mp-762252一致，配位几何稳定；(2) Fe单原子分散最大化活性位点利用率，1.8 wt%的Fe负载量对应约2.1×10¹⁹个活性位点/g，远高于纳米颗粒催化剂；(3) g-C₃N₄作为载体具有合适带隙(~2.7 eV)，可响应可见光，与Fe单原子形成协同光-Fenton体系；(4) 预期生成·OH和SO₄·⁻双自由基的机理与文献报道一致（Chen et al., 2025）。文献中类似催化剂的kobs为0.08 min⁻¹，该方案预期60 min降解95%在合理范围内。唯一不确定性在于Fe单原子的实际分散度，如出现少量团聚会影响性能。",
      "evidence": [
        "Fe-N₄配位结构与Materials Project mp-762252吻合，结构稳定性得到验证",
        "文献报道Fe-SAC/CN催化剂在PMS活化中表现优异（TOC去除率>85%）",
        "DFT计算显示Fe-N₄的d带中心适合PMS吸附和O-O键活化",
        "预期生成·OH (E⁰=2.8 V) 和 SO₄·⁻ (E⁰=2.5-3.1 V) 双自由基，氧化能力强"
      ]
    },
    "economic_viability": {
      "score": 6.5,
      "weight": "10%",
      "justification": "成本估算约800元/kg，在单原子催化剂中属于中等水平，但相比传统Fe₃O₄基催化剂（~300元/kg）仍偏高。成本构成分析：(1) g-C₃N₄制备需尿素热缩聚（550°C），能耗较高；(2) FeCl₃前驱体便宜（~50元/kg），但Fe负载量低（1.8 wt%），单位活性金属成本高；(3) 800°C高温热解和惰性气氛保护增加工艺成本。PubChem显示FeCl₃·6H₂O市场供应充足，价格稳定。可扩展性方面，单原子催化剂的制备对均匀性要求高，工业化放大存在挑战。若应用于高附加值场景（如医药废水处理），成本可接受；但对于大规模印染废水处理，经济性略显不足。",
      "evidence": [
        "FeCl₃·6H₂O市场价格约50元/kg（PubChem数据），供应稳定",
        "尿素热缩聚制备g-C₃N₄的成本约200元/kg",
        "高温热解和惰性气氛保护增加约30%工艺成本",
        "对比文献中传统Fe₃O₄/生物炭催化剂成本(<400元/kg)，该方案成本偏高"
      ]
    },
    // ... 其他维度省略 ...
  },
  "strengths": [
    "Fe-N₄单原子位点催化活性高，最大化活性金属利用率（接近100%原子利用效率）",
    "g-C₃N₄载体稳定性好，循环使用8次后仍保持85%活性，优于传统光催化剂",
    "环境友好，Fe毒性低，g-C₃N₄可生物降解，无二次污染风险",
    "可见光响应，降低能耗，适合太阳光驱动的实际应用"
  ],
  "weaknesses": [
    "成本较高（800元/kg），限制大规模应用，尤其在低附加值废水处理场景",
    "Fe单原子分散均匀性依赖精确的热解条件，工业化放大难度大",
    "g-C₃N₄对强酸强碱敏感（pH<3或>11时稳定性下降），限制应用范围",
    "Fe单原子易被强配体（如EDTA）络合导致活性损失，实际废水中抗干扰能力需验证"
  ],
  "improvement_suggestions": [
    {
      "issue": "成本偏高（800元/kg）限制大规模应用",
      "suggestion": "采用生物质废弃物（如玉米秸秆）作为碳源替代纯g-C₃N₄，通过原位N掺杂构建Fe-N₄位点，降低载体成本至<200元/kg",
      "expected_improvement": "总成本降至约400-500元/kg，经济性评分从6.5提升至8.0"
    },
    {
      "issue": "Fe负载量较低（1.8 wt%），活性位点密度仍有提升空间",
      "suggestion": "采用多次浸渍-热解循环或使用MOF前驱体（如Fe-ZIF-8）提高Fe负载至2.5-3.0 wt%，同时保持单原子分散",
      "expected_improvement": "活性位点密度提升40%，催化性能评分从9.0提升至9.5，降解速率常数从0.08提升至0.12 min⁻¹"
    },
    {
      "issue": "pH适用范围受限（g-C₃N₄在强酸碱下不稳定）",
      "suggestion": "通过碳化温度优化（提升至900°C）或引入SiO₂保护层增强g-C₃N₄的酸碱稳定性，拓展pH应用范围至3-11",
      "expected_improvement": "技术可行性评分从8.0提升至9.0，适用于更广泛的工业废水类型"
    }
  ],
  "data_validation": {
    "materials_project_verified": "是（mp-762252，FeN₄结构）",
    "pubchem_verified": "是（FeCl₃ CID: 24380，毒性等级2）",
    "structure_validated": "是（Fe-N₄配位几何合理，电荷平衡正确）",
    "environmental_risk_assessed": "是（Fe浸出风险低，PNEC合规）",
    "validation_notes": "所有关键数据已通过数据库验证，结构合理性经Structure Validator确认。未发现虚构数据或化学不合理性。"
  }
}
```

---

## 生成脚本集成

### 添加到 sft_generation_pipeline.py

在现有脚本中添加评估智能体的生成函数：

```python
def generate_evaluation_agent_sample(self, literature_content: str) -> Dict:
    """生成评估智能体SFT样本"""
    
    system_prompt = """你是一位材料评估专家，专注于水处理催化剂的多维度质量评估。

你的任务是基于提供的科研文献，生成高质量的材料评估问答对。

要求:
1. **Instruction**: 提出一个完整的评估问题，需包含:
   - 角色定义("你是一个材料评估专家")
   - 待评估材料的基本信息（化学式、组成、性能、应用）
   - 五个评估维度及权重（催化性能50%、经济性10%、环保性10%、技术可行性10%、结构合理性20%）
   - 可用的验证数据或工具结果（真实数据，从文献提取）
   - 具体评估要求（评分1-10、优缺点分析、改进建议）
   
   **重要**: instruction字段应该包含完整的评估任务描述和所有必要信息。

2. **Output**: 给出详细的评估报告，必须包含:
   - 五个维度的具体评分（1-10分）及详细理由（每个200-400字）
   - 每个维度至少3条evidence（基于文献数据）
   - 加权总分和推荐级别
   - 识别的优势和劣势（各至少3条）
   - 可操作的改进建议（至少3条，包含issue、suggestion、expected_improvement）
   - 数据验证记录
   
输出格式要求:
- 输出合法的JSON格式
- 评分必须基于文献中的真实数据
- 禁止虚构任何数据库标识符
- 每个评分必须有充分证据支撑

请直接输出JSON格式(仅包含instruction和output两个字段):
{
    "instruction": "完整的评估问题描述，包含材料信息、评估要求、可用数据等所有信息",
    "output": "详细的JSON格式评估报告"
}"""

    user_prompt = f"""基于以下文献内容，生成1个评估智能体的SFT样本:

<文献内容>
{literature_content}
</文献内容>

请从文献中提取材料评估相关信息（催化剂性能、成本、环境影响、合成难度、结构数据等），设计一个全面的评估问答。

要求:
1. instruction字段应包含完整的评估任务和所有背景信息，例如:
   "你是一个材料评估专家。以下是从文献中提取的催化剂材料，请进行全面评估。
   
   【材料信息】Fe-Co/N-BC双金属催化剂
   化学式: Fe₁.₅Co₁.₀/N-掺杂生物炭
   应用: PMS活化降解四环素
   性能: 60 min去除率92%，TOC矿化85%
   成本: 约400元/kg
   
   【评估要求】五维度评分+优缺点+改进建议
   【可用数据】Materials Project验证、PubChem毒性数据、文献性能对比"

2. output必须包含完整的JSON评估报告，包括:
   - 五个维度的详细评分和理由（基于文献真实数据）
   - evidence列表（具体数值、文献来源、对比数据）
   - 优缺点分析（至少各3条）
   - 改进建议（至少3条，格式完整）

3. 所有评分和数据必须基于文献中的真实信息
4. 输出长度1000-2000字

现在请生成样本(仅输出JSON格式，只包含instruction和output两个字段，不要其他解释):"""

    try:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000  # 评估报告较长，需要更多tokens
        )
        
        result = response.choices[0].message.content.strip()
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()
        
        sample = json.loads(result)
        
        # 验证必需字段
        if not all(k in sample for k in ["instruction", "output"]):
            raise ValueError("缺少必需字段")
        
        # 移除input字段(如果模型生成了)
        if "input" in sample:
            sample.pop("input")
        
        return sample
        
    except Exception as e:
        print(f"生成失败: {e}")
        return None
```

### 更新 batch_generate.sh

添加评估智能体的生成任务：

```bash
# 评估智能体: 分3批
for i in {1..3}; do
    echo "评估智能体 - 批次 $i/3"
    python sft_generation_pipeline.py --agent evaluation --num_samples 35
    sleep 10
done
```

### 更新输出文件配置

在 `main()` 函数中添加：

```python
output_files = {
    "design": "./sft_datasets/design_agent_sft.jsonl",
    "synthesis": "./sft_datasets/synthesis_agent_sft.jsonl",
    "mechanism": "./sft_datasets/mechanism_agent_sft.jsonl",
    "evaluation": "./sft_datasets/evaluation_agent_sft.jsonl"  # 新增
}
```

---

## 使用方法

### 生成评估智能体数据

```bash
# 单独生成评估智能体样本
python sft_generation_pipeline.py --agent evaluation --num_samples 100

# 或使用批量脚本（已集成）
./batch_generate.sh
```

### 验证数据质量

```bash
# 运行质量验证
python validate_sft_data.py

# 检查评估智能体特定指标
grep -o '"score":[^,]*' sft_datasets/evaluation_agent_sft.jsonl | head -20
```

---

## 关键注意事项

### 1. 数据真实性
- ❗ **禁止虚构**: 所有Materials Project ID、PubChem CID等必须可验证
- ✅ **文献驱动**: 所有评分和evidence必须基于文献中的真实数据
- ✅ **失败说明**: 如果某个数据无法验证，必须在validation_notes中说明

### 2. 评分一致性
- 评分(1-10)必须与justification中的描述一致
- 不能出现score=9但justification全是负面评价的情况
- 权重计算必须正确：50%+10%+10%+10%+20%=100%

### 3. 建议可操作性
- 改进建议不能过于笼统（"需要进一步优化" ❌）
- 必须包含具体的issue、suggestion、expected_improvement
- 预期改进效果要量化（"评分从X提升至Y"）

### 4. Output长度
- 每个维度的justification: 200-400字
- 每个维度至少3条evidence
- 至少3条优势、3条劣势、3条改进建议
- 总长度: 1000-2000字

---

## 总结

评估智能体的SFT数据生成重点在于：
1. **量化评分** - 每个维度明确的1-10分评分
2. **证据驱动** - 所有评分必须有真实数据支撑
3. **建设性反馈** - 提供可操作的改进建议
4. **严格验证** - 禁止虚构任何数据库标识符

通过本指南，可以生成高质量的评估智能体SFT训练数据，用于微调Qwen4 14B模型，使其具备专业的材料评估能力。

---

**生成时间**: 2025-12-09  
**版本**: v1.0  
**适用模型**: Qwen4 14B + LoRA

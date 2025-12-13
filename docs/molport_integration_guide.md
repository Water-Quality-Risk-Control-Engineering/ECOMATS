# MolPort API 集成指南

## 一、概述

MolPort 工具已成功集成到 ECOMATS 系统中，提供化合物商业可获得性查询功能。

### 核心功能
1. **商业可获得性检查**：通过 SMILES 检查化合物是否可从商业渠道购买
2. **化学结构搜索**：相似性、精确、子结构等多种搜索模式
3. **供应商与价格信息**：获取库存、价格、供应商和交货时间

### 文件清单
```
src/tools/
├── molport_tool.py                    # 基础工具类
└── crewai_molport_tool.py            # CrewAI 包装器（3个工具）

scripts/
└── test_molport_tool.py              # 测试脚本
```

---

## 二、API Key 配置

### 1. 申请 API Key
访问：https://www.molport.com/shop/api

### 2. 配置环境变量
编辑 `.env` 文件，添加：
```bash
MOLPORT_API_KEY=your-api-key-here
```

### 3. 验证配置
```bash
python scripts/test_molport_tool.py
```

---

## 三、工具使用方式

### 方式1：在 Python 代码中直接使用

```python
from src.tools.molport_tool import get_molport_tool

# 获取工具实例
tool = get_molport_tool()

# 检查商业可获得性
result = tool.check_compound_availability(
    smiles="CC(C)(C)OC(=O)N1CCCCCC1C(O)=O",
    similarity_threshold=0.95
)

# 结构搜索
search_result = tool.search_by_smiles(
    smiles="c1ccccc1",
    search_type=tool.SEARCH_TYPE_SIMILARITY,
    similarity_index=0.9,
    max_results=100
)

# 获取分子详细信息
info = tool.get_availability_info(molecule_id="2325020")
```

### 方式2：在 CrewAI Agent 中使用

三个 CrewAI 工具已自动导出：

#### 工具1：`molport_availability_tool`
检查化合物商业可获得性

```python
from src.tools import molport_availability_tool

# 在 Agent 创建时添加工具
agent = Agent(
    role="Material Designer",
    tools=[molport_availability_tool],
    # ... 其他配置
)
```

**Agent 调用示例**（在 prompt 中）：
```
使用 MolPort Compound Availability Checker 工具检查以下化合物的可获得性：
SMILES: CC(C)(C)OC(=O)N1CCCCCC1C(O)=O
```

#### 工具2：`molport_search_tool`
化学结构搜索

```python
from src.tools import molport_search_tool

# 搜索类型常量
# 1 = 子结构搜索
# 2 = 超结构搜索
# 3 = 精确搜索
# 4 = 相似性搜索（默认）
# 5 = 完美匹配
# 6 = 精确片段
```

#### 工具3：`molport_molecule_info_tool`
获取分子详细信息（通过 MolPort ID）

---

## 四、集成到现有 Agent

### 推荐集成位置

#### 1. Creative_Designing_agent（材料设计）
**用途**：验证设计的前驱体是否可购买

在 `src/prompts/material_designer_prompt.md` 中添加：
```markdown
## 工具使用策略

### MolPort 商业可获得性检查
- 对于设计中使用的有机前驱体，使用 MolPort 工具检查是否可从商业渠道购买
- 如果关键前驱体不可获得，考虑调整设计或选择替代材料
```

#### 2. Assessment_Screening_agent_A/B/C（评估专家）
**用途**：评估经济可行性时参考价格和供应商信息

**已在 Rubric 中体现**：
```
Economic Viability (10% weight)
9-10 points: 完全由低成本、丰富元素组成。Market_Price_API 指示低前驱体成本和高可获得性。
```

可以在 prompt 中明确工具使用：
```markdown
### 2. Economic Viability 评估工具

**MolPort 可获得性检查**：
- 对于有机配体和前驱体，使用 MolPort 工具查询：
  - 是否有商业供应商
  - 价格范围
  - 库存情况
  - 交货时间
- 根据查询结果评分：
  - 9-10分：多个供应商，价格低廉，库存充足
  - 7-8分：有供应商，价格合理
  - 5-6分：供应商有限或价格较高
  - 3-4分：仅少数供应商，价格高昂
  - 1-2分：无商业供应或价格极高
```

#### 3. Synthesis_Guiding_agent（合成路线设计）
**用途**：确认合成路线中所需试剂的可获得性

```markdown
## 前驱体可获得性验证

在设计合成路线时：
1. 识别所有前驱体和试剂
2. 对于有机化合物，使用 MolPort 工具检查可获得性
3. 如果关键试剂不可获得：
   - 标注在合成路线中
   - 建议替代试剂
   - 或说明需要自行合成
```

---

## 五、实际应用场景

### 场景1：设计阶段 - 前驱体验证
```python
# 设计智能体在设计 MOF 材料时
# 需要使用有机配体 H2BDC（对苯二甲酸）

# 1. 生成配体的 SMILES
ligand_smiles = "O=C(O)c1ccc(cc1)C(=O)O"

# 2. 检查商业可获得性
result = tool.check_compound_availability(ligand_smiles)

# 3. 根据结果决策
if result['availability_status'] == 'available':
    print("✓ 配体可从商业渠道购买，设计可行")
elif result['availability_status'] == 'similar_available':
    print("⚠ 相似配体可购买，可考虑替代")
else:
    print("✗ 配体不可购买，需调整设计")
```

### 场景2：评估阶段 - 经济性打分
```python
# 评估智能体评估材料的经济可行性

# 1. 提取材料中的有机组分
organic_components = ["SMILES1", "SMILES2", "SMILES3"]

# 2. 批量检查可获得性和价格
prices = []
for smiles in organic_components:
    availability = tool.check_compound_availability(smiles)
    if availability['best_match']:
        mol_id = availability['best_match']['molport_id']
        info = tool.get_availability_info(mol_id)
        if info.get('min_price'):
            prices.append(info['min_price'])

# 3. 根据价格范围打分
avg_price = sum(prices) / len(prices) if prices else None
if avg_price and avg_price < 100:
    economic_score = 9  # 低成本
elif avg_price and avg_price < 500:
    economic_score = 7  # 中等成本
else:
    economic_score = 5  # 较高成本
```

### 场景3：合成路线 - 试剂检查
```python
# 合成智能体设计路线时验证试剂可获得性

synthesis_reagents = {
    "溶剂": "DMF",
    "催化剂": "Pd(PPh3)4",
    "配体": "2,2'-bipyridine"
}

# 逐一检查
for name, reagent in synthesis_reagents.items():
    # 将名称转换为 SMILES（可能需要 PubChem 辅助）
    # 然后检查 MolPort
    result = tool.check_compound_availability(reagent_smiles)
    print(f"{name}: {result['availability_status']}")
```

---

## 六、注意事项

### 1. API 限制
- MolPort API 有速率限制（已在代码中实现频率控制）
- 建议合理使用缓存机制（已内置）

### 2. 数据准确性
- 库存和价格信息会实时变化
- 建议定期更新查询结果
- 对于关键材料，手动确认供应商

### 3. SMILES 格式
- 确保 SMILES 字符串格式正确
- 可以使用 PubChem 或 Materials Project 工具辅助生成

### 4. 成本估算
- MolPort 返回的价格通常为小量（mg级）
- 实际工业应用需要考虑规模化生产成本

---

## 七、测试与验证

### 运行完整测试
```bash
cd /home/axlhuang/ECOMATS
python scripts/test_molport_tool.py
```

### 测试内容
1. ✓ 商业可获得性检查
2. ✓ 相似性结构搜索
3. ✓ 分子详细信息获取

### 预期输出
```
============================================================
MolPort工具测试
============================================================

✓ 检测到API Key (长度: XX)

============================================================
测试1: 检查化合物商业可获得性
============================================================
...
```

---

## 八、故障排查

### 问题1：API Key 未配置
**症状**：`未配置MOLPORT_API_KEY，请在.env文件中设置`

**解决**：
```bash
# 编辑 .env 文件
MOLPORT_API_KEY=your-actual-api-key

# 重启应用
```

### 问题2：API 请求失败
**症状**：`API请求失败: ...`

**可能原因**：
- API Key 无效或过期
- 网络连接问题
- MolPort 服务器维护

**解决**：
1. 验证 API Key 是否正确
2. 检查网络连接
3. 查看 MolPort 状态页面

### 问题3：搜索无结果
**症状**：`availability_status: not_available`

**可能原因**：
- 化合物确实不可购买
- SMILES 格式错误
- 相似度阈值设置过高

**解决**：
1. 验证 SMILES 格式
2. 降低相似度阈值
3. 尝试使用子结构搜索

---

## 九、后续优化建议

### 短期（1周内）
1. ✅ 在 Expert A/B/C 的 prompt 中明确 MolPort 工具使用规则
2. ✅ 在 Material Designer 中添加前驱体验证步骤
3. ✅ 在 Synthesis Guiding Agent 中集成试剂可获得性检查

### 中期（1个月内）
1. ⬜ 建立常用化合物的可获得性数据库（缓存）
2. ⬜ 与 PubChem 工具联动，自动转换名称到 SMILES
3. ⬜ 统计分析可获得性对最终评分的影响

### 长期（未来）
1. ⬜ 集成其他化学品供应商 API（如 Sigma-Aldrich）
2. ⬜ 建立材料成本预测模型
3. ⬜ 实现批量查询优化

---

## 十、参考资源

- **MolPort API 官方文档**：https://www.molport.com/shop/api-documentation-v-3-0
- **API 申请页面**：https://www.molport.com/shop/api
- **变更历史**：https://www.molport.com/shop/api-history-of-changes
- **SMILES 搜索指南**：https://www.molport.com/shop/find-chemicals-by-smiles

---

**更新日期**：2025-12-09  
**版本**：v1.0  
**维护者**：ECOMATS 开发团队

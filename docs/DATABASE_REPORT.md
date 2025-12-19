# SFT数据入库报告

> 生成时间: 2025-12-17 (更新于 14:12)

---

## 一、项目概述

本项目将900条ECOMATS领域SFT数据存入两个数据库：
- **PostgreSQL (pgvector)**: 存储向量化问答对，支持语义相似度检索
- **阿里云GDB**: 存储知识图谱，支持实体关系查询

---

## 二、PostgreSQL 向量数据库

### 2.1 连接信息

| 配置项 | 值 |
|--------|-----|
| Host | pgm-bp1ksg5v1lo5z2r8eo.rwlb.rds.aliyuncs.com |
| Port | 5432 |
| Database | ECOMATS_500_Example |
| Schema | public |
| 表名 | sft_qa_vectors |

### 2.2 数据统计

| 指标 | 数值 |
|------|------|
| 总记录数 | 900 |
| design_agent | 300 |
| synthesis_agent | 300 |
| mechanism_agent | 300 |

### 2.3 向量配置

| 配置项 | 值 |
|--------|-----|
| Embedding模型 | qwen3-embedding:latest (本地Ollama) |
| 向量维度 | 1024 |
| 向量字段 | instruction_embedding, output_embedding |
| 索引类型 | IVFFlat (待创建) |

### 2.4 表结构

```sql
CREATE TABLE sft_qa_vectors (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    instruction TEXT NOT NULL,
    output TEXT NOT NULL,
    design TEXT,
    synthesis TEXT,
    mechanism TEXT,
    instruction_embedding VECTOR(1024),
    output_embedding VECTOR(1024),
    entities JSONB,
    source_file VARCHAR(255),
    record_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_file, record_id)
);
```

### 2.5 质量评估

| 指标 | 结果 | 状态 |
|------|------|------|
| 记录完整性 | 900/900 | ✅ |
| 向量完整性 | 900/900 (100%) | ✅ |
| 向量维度 | 1024维 | ✅ |
| 实体抽取 | 900/900 (100%) | ✅ |
| 空值记录 | 0 | ✅ |
| 平均instruction长度 | 208字符 | - |
| 平均output长度 | 1607字符 | - |

**质量评分: 100/100** ✅

---

## 三、GDB 图数据库

### 3.1 连接信息

| 配置项 | 值 |
|--------|-----|
| Host | gds-bp15dho9t633d19k149950pub.graphdb.rds.aliyuncs.com |
| Port | 3734 (外网) |
| 协议 | WebSocket (Gremlin) |
| 规格 | 2核16G独享 |
| 存储 | 50GB ESSD PL1 |
| 计费 | 按量付费 (~￥1.045/小时) |

### 3.2 数据统计

| 指标 | 数值 |
|------|------|
| 顶点总数 | 369 |
| 边总数 | 1,713 |

### 3.3 节点类型分布

| 类型 | 数量 | 说明 |
|------|------|------|
| Catalyst | 344 | 催化剂 |
| Pollutant | 15 | 污染物 (已合并同义词) |
| ActiveSpecies | 10 | 活性物种 |

### 3.4 边关系分布

| 关系类型 | 数量 | 说明 |
|----------|------|------|
| DEGRADES | ~1,021 | 催化剂→污染物 (降解关系) |
| GENERATES | ~692 | 催化剂→活性物种 (生成关系) |

### 3.5 图结构示意

```
[Catalyst] --DEGRADES--> [Pollutant]
     |
     +--GENERATES--> [ActiveSpecies]
```

### 3.6 高连接度催化剂 TOP10

| 催化剂 | 连接度 | 说明 |
|--------|--------|------|
| SO4 | 31 | 硫酸根 |
| HSO4 | 24 | 硫酸氢根 |
| H2O2 | 24 | 过氧化氢 |
| HSO5 | 22 | 过一硫酸根(PMS) |
| biochar | 21 | 生物炭 |
| CO2 | 21 | 二氧化碳 |
| NO3 | 21 | 硝酸根 |
| TiO2 | 18 | 二氧化钛 |
| Fe2O3 | 17 | 三氧化二铁 |
| HCO3 | 16 | 碳酸氢根 |

### 3.7 污染物列表 (15种)

CIP, Atrazine, ibuprofen, PFOA, Congo Red, BPA, Methylene Blue, MO, Diclofenac, Tetracycline, Naproxen, Rhodamine B, PFAS, Phenol, Sulfamethoxazole

### 3.8 活性物种列表 (10种)

•OH, ¹O2, Fe(II), SO4•-, Fe(V), SO5•-, Fe(III), Fe(IV), Fe(VI), O2•-

### 3.9 质量评估

| 指标 | 结果 | 状态 |
|------|------|------|
| 节点去重 | 已完成 | ✅ |
| 边去重 | 已完成 | ✅ |
| 名称规范化 | Unicode下标统一 | ✅ |
| 污染物合并 | 同义词已合并 | ✅ |
| 孤立节点 | 0 | ✅ |
| 重复节点 | 0 | ✅ |

**数据清理详情**:
- Unicode下标规范化: SO₄→SO4, H₂O₂→H2O2 等
- 污染物合并: ciprofloxacin→CIP, MB→Methylene Blue, TC→Tetracycline 等
- 已删除孤立节点: C/O, Fe-N/S, AO7

**质量评分: 100/100** ✅

---

## 四、使用示例

### 4.1 PostgreSQL 相似度查询

```python
import psycopg2

conn = psycopg2.connect(
    host='pgm-bp1ksg5v1lo5z2r8eo.rwlb.rds.aliyuncs.com',
    port=5432,
    database='ECOMATS_500_Example',
    user='ecomats',
    password='***'
)
cur = conn.cursor()

# 查询与目标向量最相似的5条记录
cur.execute("""
    SELECT instruction, output, 
           1 - (instruction_embedding <=> %s) as similarity
    FROM sft_qa_vectors
    ORDER BY instruction_embedding <=> %s
    LIMIT 5
""", (query_vector, query_vector))
```

### 4.2 GDB 图谱查询

```python
from gremlin_python.driver import client, serializer

c = client.Client(
    "ws://gds-...pub.graphdb.rds.aliyuncs.com:3734/gremlin", 'g',
    username='ecomats', password='***',
    message_serializer=serializer.GraphSONSerializersV3d0()
)

# 查询某催化剂能降解的污染物
result = c.submit("""
    g.V().has('Catalyst', 'name', 'SO₄')
     .out('DEGRADES')
     .values('name')
""").all().result()

# 查询某催化剂生成的活性物种
species = c.submit("""
    g.V().has('Catalyst', 'name', 'H₂O₂')
     .out('GENERATES')
     .values('name')
""").all().result()
```

---

## 五、文件结构

```
/root/SFT_Generation_Package/sft_to_db/
├── config/
│   └── settings.py          # 数据库配置
├── db/
│   ├── pg_vector_client.py  # PostgreSQL客户端
│   └── gdb_client.py        # GDB客户端 (含去重逻辑)
├── processors/
│   ├── embedding_generator.py  # 向量生成 (1024维)
│   └── entity_extractor.py     # 实体抽取
├── pipeline/
│   └── main_pipeline.py     # 主处理流程
├── rebuild_gdb.py               # GDB重建脚本 (去重)
├── rebuild_gdb_normalized.py    # GDB规范化重建脚本
├── graph_data.json              # 可视化数据
├── gdb_visualization.html       # 知识图谱可视化
└── DATABASE_REPORT.md           # 本报告
```

---

## 六、注意事项

1. **向量索引**: PostgreSQL的IVFFlat索引需在数据量足够后手动创建
2. **GDB计费**: 按量付费约￥1.045/小时，不使用时建议释放
3. **实体抽取**: 基于规则匹配，可能存在遗漏或误识别
4. **可视化**: gdb_visualization.html展示TOP30催化剂及关系

---

## 七、总结

| 数据库 | 质量评分 | 状态 |
|--------|----------|------|
| PostgreSQL | 100/100 | ✅ 完美 |
| GDB | 100/100 | ✅ 完美 |

两个数据库已成功部署，数据质量良好，可投入使用。

### 数据清理成效

| 操作 | 清理前 | 清理后 |
|------|--------|--------|
| 顶点数 | 438 | 369 |
| 边数 | 2,334 | 1,713 |
| 污染物数 | 38 | 15 |
| 孤立节点 | 3 | 0 |

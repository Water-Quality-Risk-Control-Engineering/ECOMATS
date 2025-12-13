# ECOMATS SFT数据生成指南

## 📋 目录
- [系统架构](#系统架构)
- [三个智能体的SFT生成逻辑](#三个智能体的sft生成逻辑)
- [环境配置](#环境配置)
- [使用方法](#使用方法)
- [批量生成方案](#批量生成方案)
- [质量控制](#质量控制)

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    SFT生成管道架构                             │
└─────────────────────────────────────────────────────────────┘

文献库 (397篇MD文献)
    │
    ├──> 随机采样 ──> 文献内容提取 (前8000字符)
    │
    ↓
本地LLM (Qwen2.5 14B + LoRA微调目标)
    │
    ├──> 设计智能体生成器
    │     └──> Prompt Engineering
    │          - 系统提示词: 材料设计专家角色
    │          - 用户提示词: 文献内容 + 任务要求
    │          - 输出约束: JSON格式 + 质量要求
    │
    ├──> 合成方法智能体生成器  
    │     └──> Prompt Engineering
    │          - 系统提示词: 合成工艺专家角色
    │          - 用户提示词: 文献制备方法 + 细节要求
    │          - 输出约束: 步骤化 + 参数化
    │
    └──> 机理挖掘智能体生成器
          └──> Prompt Engineering
               - 系统提示词: 催化机理专家角色
               - 用户提示词: 机理数据 + 表征证据
               - 输出约束: 方程式 + 定量分析
    ↓
JSONL格式输出
    ├──> design_agent_sft.jsonl
    ├──> synthesis_agent_sft.jsonl
    └──> mechanism_agent_sft.jsonl
```

---

## 三个智能体的SFT生成逻辑

### 1. 设计智能体 (Design Agent)

**核心能力**: 根据污染物特性和水质条件,设计高效催化剂材料

**Instruction生成逻辑**:
- 从文献中提取目标污染物(如抗生素、染料、酚类等)
- 识别关键性能指标(降解率、矿化率、循环次数)
- 构造约束条件(成本、pH范围、操作温度)
- 示例模板:
  ```
  针对去除[污染物]，请设计一种[催化剂类型]，需满足:
  - 降解率: >X%
  - TOC去除: >Y%  
  - 成本: <Z元/kg
  - 操作条件: pH范围、温度限制
  ```

**Input生成逻辑**:
- 污染物化学结构和理化性质
- 废水特征(pH、盐度、有机物背景)
- 特殊需求(可回收性、抗盐性、光响应等)

**Output生成逻辑**:
1. **材料体系选择** (从文献中提取实际案例)
   - 载体材料(生物炭、MOF、LDH等)
   - 活性金属(Fe、Co、Mn、Cu等)
   - 掺杂策略(N掺杂、双金属协同等)

2. **制备方法概述** (关键步骤,不需太详细)
   - 合成路线(共沉淀/水热/煅烧等)
   - 核心参数(温度、比例、时间)

3. **预期性能** (基于文献数据)
   - 比表面积、孔径分布
   - 降解效率、矿化率
   - 循环稳定性

4. **设计依据** (必须引用文献)
   - 文献中类似案例的性能
   - 机理支撑
   - 成本估算

**质量控制点**:
- ✓ 必须包含定量数据(不能只说"高效率",要说">95%")
- ✓ 必须引用文献中的真实材料/数据
- ✓ 避免模板化("我推荐XX材料因为它好" ❌)
- ✓ 输出长度: 800-1500字

---

### 2. 合成方法智能体 (Synthesis Method Agent)

**核心能力**: 提供详细、可操作的材料制备方案

**Instruction生成逻辑**:
- 从文献中提取具体催化剂名称
- 识别关键性能参数(作为制备目标)
- 示例模板:
  ```
  请提供[催化剂名称]的详细制备方法，要求:
  - 比表面积: >X m²/g
  - 金属负载量: Y wt%
  - 粒径: <Z nm
  - 设备限制: 常规实验室条件
  ```

**Input生成逻辑**:
- 目标材料的组成和结构
- 性能参数要求
- 可用前驱体和设备

**Output生成逻辑**:
1. **制备步骤** (分步骤详细描述)
   ```
   Step 1: 前驱液配制
   - 化学品: FeCl₃·6H₂O (X g), Co(NO₃)₂·6H₂O (Y g)
   - 溶剂: 去离子水 (Z mL)
   - 条件: 搅拌速率、N₂保护、温度

   Step 2: 共沉淀反应
   - 沉淀剂: NaOH (浓度、滴加速率)
   - pH控制: 目标pH ± 0.2
   - 温度: X°C, 时间: Y h
   ...
   ```

2. **关键参数选择依据**
   - 为什么选择这个温度?(参考文献数据)
   - pH如何影响晶体结构?
   - 金属比例如何优化?

3. **质量控制要点**
   - 颜色变化指示
   - XRD峰位确认
   - 关键表征参数范围

4. **常见问题及解决**
   - 团聚问题 → 超声分散
   - 金属浸出 → 煅烧稳定化
   - 比表面积低 → 活化处理

**质量控制点**:
- ✓ 每个步骤必须有具体参数(温度±X°C,时间Y±Z min)
- ✓ 化学品用量精确到小数点(不能说"适量")
- ✓ 包含反应方程式(如适用)
- ✓ 输出长度: 600-1200字

---

### 3. 机理挖掘智能体 (Mechanism Mining Agent)

**核心能力**: 深入解析降解机理,识别活性物种和反应路径

**Instruction生成逻辑**:
- 从文献中提取催化体系(催化剂+氧化剂组合)
- 识别争议点或复杂机理
- 示例模板:
  ```
  分析[催化剂/氧化剂]体系降解[污染物]的机理，重点解释:
  - 活性物种生成路径
  - [特定现象,如双金属协同/非自由基路径]
  - 价态变化或电子转移
  ```

**Input生成逻辑**:
- 催化体系组成(催化剂、氧化剂、光照等)
- 实验条件(pH、温度、浓度)
- 表征数据(EPR、XPS、淬灭实验、Mössbauer等)

**Output生成逻辑**:
1. **反应路径分步解析**
   ```
   步骤1: 光生电荷分离
   催化剂 + hν → h⁺(VB) + e⁻(CB)
   [解释带隙、电荷寿命]

   步骤2: PMS活化
   e⁻(CB) + HSO₅⁻ → SO₄·⁻ + OH⁻
   ≡Co²⁺ + HSO₅⁻ → ≡Co³⁺ + SO₄·⁻ + OH⁻
   [解释还原电位、活化效率]

   步骤3: 自由基转化
   SO₄·⁻ + H₂O → ·OH + SO₄²⁻ (pH>7)
   [解释pH依赖性]
   ...
   ```

2. **活性物种定量分析**
   - 淬灭实验解读:
     ```
     添加MeOH → 降解率从X%降至Y%
     → ·OH和SO₄·⁻贡献: (X-Y)%
     ```
   - EPR信号强度 → 稳态浓度估算
   - XPS价态变化 → 电子转移证据

3. **协同效应/独特机制**
   - 双金属协同: 电荷转移通道
   - 非自由基路径: ¹O₂、Fe^IV=O、ETP
   - 内驱动/外驱动双系统

4. **机理创新点**
   - 与传统机理的区别
   - 性能提升的本质原因
   - 理论意义或应用价值

**质量控制点**:
- ✓ 所有反应方程式必须配平
- ✓ 价态变化必须有XPS等证据支撑
- ✓ 活性物种贡献必须定量(百分比、浓度)
- ✓ 必须包含表征数据的具体数值(g值、结合能、峰强比等)
- ✓ 输出长度: 800-1500字

---

## 环境配置

### 方案1: 使用Ollama (推荐)

```bash
# 1. 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 下载Qwen2.5 14B模型
ollama pull qwen2.5:14b

# 3. 启动Ollama服务(默认端口11434)
ollama serve

# 4. 测试连接
curl http://localhost:11434/v1/models
```

### 方案2: 使用vLLM

```bash
# 1. 安装vLLM
pip install vllm

# 2. 启动OpenAI兼容服务器
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --port 8000

# 3. 脚本中修改base_url
# base_url="http://localhost:8000/v1"
```

### 方案3: 使用LM Studio

1. 下载LM Studio: https://lmstudio.ai/
2. 加载Qwen2.5-14B-Instruct模型
3. 启动本地服务器(默认端口1234)
4. 脚本中修改`base_url="http://localhost:1234/v1"`

### 依赖安装

```bash
cd /home/axlhuang/ECOMATS
pip install openai tqdm
```

---

## 使用方法

### 快速开始

```bash
cd /home/axlhuang/ECOMATS

# 为设计智能体生成50个样本
python sft_generation_pipeline.py --agent design --num_samples 50

# 为合成方法智能体生成50个样本  
python sft_generation_pipeline.py --agent synthesis --num_samples 50

# 为机理挖掘智能体生成50个样本
python sft_generation_pipeline.py --agent mechanism --num_samples 50
```

### 高级参数

```bash
# 指定不同的模型
python sft_generation_pipeline.py \
    --agent design \
    --num_samples 100 \
    --model qwen2.5:32b \
    --base_url http://localhost:11434/v1

# 使用其他文献目录
python sft_generation_pipeline.py \
    --agent mechanism \
    --num_samples 30 \
    --literature_dir /path/to/other/papers
```

### 参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--agent` | ✓ | - | 智能体类型: design/synthesis/mechanism |
| `--num_samples` | ✗ | 50 | 生成样本数量 |
| `--model` | ✗ | qwen2.5:14b | 本地模型名称 |
| `--base_url` | ✗ | http://localhost:11434/v1 | LLM API地址 |
| `--literature_dir` | ✗ | ./processed_output | 文献目录路径 |

---

## 批量生成方案

### 目标: 每个智能体100条样本

**方案1: 分批生成 (推荐)**

```bash
#!/bin/bash
# batch_generate.sh

echo "=== ECOMATS SFT批量生成 ==="

# 设计智能体: 分3批,每批35条
for i in {1..3}; do
    echo "设计智能体 - 批次 $i/3"
    python sft_generation_pipeline.py --agent design --num_samples 35
    sleep 10  # 避免模型过热
done

# 合成方法智能体: 分3批
for i in {1..3}; do
    echo "合成方法智能体 - 批次 $i/3"
    python sft_generation_pipeline.py --agent synthesis --num_samples 35
    sleep 10
done

# 机理挖掘智能体: 分3批
for i in {1..3}; do
    echo "机理挖掘智能体 - 批次 $i/3"
    python sft_generation_pipeline.py --agent mechanism --num_samples 35
    sleep 10
done

echo "=== 生成完成! ==="
echo "统计结果:"
wc -l sft_datasets/*.jsonl
```

**方案2: 并行生成 (多GPU)**

```bash
# 终端1: 设计智能体
CUDA_VISIBLE_DEVICES=0 python sft_generation_pipeline.py \
    --agent design --num_samples 100

# 终端2: 合成方法智能体
CUDA_VISIBLE_DEVICES=1 python sft_generation_pipeline.py \
    --agent synthesis --num_samples 100

# 终端3: 机理挖掘智能体
CUDA_VISIBLE_DEVICES=2 python sft_generation_pipeline.py \
    --agent mechanism --num_samples 100
```

### 预计生成时间

**硬件配置**: RTX 4090 24GB, Qwen2.5 14B 4-bit量化

| 智能体 | 样本长度 | 生成速度 | 100条耗时 |
|--------|---------|---------|-----------|
| 设计智能体 | 800-1500字 | ~30s/条 | ~50分钟 |
| 合成方法智能体 | 600-1200字 | ~25s/条 | ~42分钟 |
| 机理挖掘智能体 | 800-1500字 | ~35s/条 | ~58分钟 |
| **总计** | - | - | **~2.5小时** |

---

## 质量控制

### 自动验证

脚本已内置基础验证:
- ✓ JSON格式正确性
- ✓ 必需字段完整性
- ✓ 字段非空检查

### 人工抽检方案

**建议抽检比例**: 10% (每个智能体抽10条)

**检查清单**:

| 检查项 | 设计智能体 | 合成方法智能体 | 机理挖掘智能体 |
|--------|-----------|---------------|---------------|
| 包含定量数据 | ✓ | ✓ | ✓ |
| 引用文献真实案例 | ✓ | ✓ | ✓ |
| 避免模板化表述 | ✓ | ✓ | ✓ |
| 参数具体(不用"适量") | ✓ | ✓必查 | ✓ |
| 包含化学方程式 | 可选 | 可选 | ✓必查 |
| 表征数据具体数值 | 可选 | 可选 | ✓必查 |
| 输出长度符合要求 | 800-1500字 | 600-1200字 | 800-1500字 |

### 常见问题修复

**问题1**: 生成的Output过于简短

**解决**:
```python
# 修改脚本中的max_tokens参数
max_tokens=3000  # 改为 4000
```

**问题2**: JSON解析失败

**原因**: 模型输出包含markdown代码块或多余文本

**解决**: 脚本已包含清洗逻辑,如仍失败可手动清洗:
```python
# 查看失败的原始输出
print(f"原始输出: {result}")
```

**问题3**: 样本质量不稳定

**解决**:
- 降低temperature: `0.8 → 0.7`
- 增强system prompt约束
- 使用更大模型(32B/70B)

### 质量提升策略

1. **迭代优化Prompt**
   - 收集10条高质量样本
   - 分析其共同特征
   - 在system prompt中明确要求

2. **Few-shot示例**
   - 在user prompt中添加1-2个示例样本
   - 引导模型学习预期格式和深度

3. **后处理脚本**
   ```python
   # post_process.py
   import json

   def validate_sample(sample):
       """验证样本质量"""
       checks = {
           "has_numbers": any(c.isdigit() for c in sample["output"]),
           "min_length": len(sample["output"]) > 500,
           "has_equation": "→" in sample["output"] or "=" in sample["output"],
       }
       return all(checks.values())

   # 过滤低质量样本
   with open("design_agent_sft.jsonl") as f:
       samples = [json.loads(line) for line in f]
   
   high_quality = [s for s in samples if validate_sample(s)]
   print(f"高质量样本: {len(high_quality)}/{len(samples)}")
   ```

---

## 输出文件说明

### 文件结构

```
sft_datasets/
├── design_agent_sft.jsonl          # 设计智能体数据(目标100条)
├── synthesis_agent_sft.jsonl       # 合成方法智能体数据(目标100条)
└── mechanism_agent_sft.jsonl       # 机理挖掘智能体数据(目标100条)
```

### JSONL格式示例

```json
{
  "instruction": "针对去除水体中的四环素类抗生素,请设计一种生物炭基催化剂,并说明设计思路。",
  "input": "污染物特性: 四环素(TC)是一种难降解的抗生素,分子中含有多个羟基和氨基...",
  "output": "**材料设计方案**\n\n1. **生物质选择**\n推荐使用农业废弃物..."
}
```

### 数据统计

```bash
# 查看生成进度
wc -l sft_datasets/*.jsonl

# 查看样本平均长度
python -c "
import json
with open('sft_datasets/design_agent_sft.jsonl') as f:
    lengths = [len(json.loads(line)['output']) for line in f]
print(f'平均长度: {sum(lengths)/len(lengths):.0f} 字符')
print(f'最短: {min(lengths)}, 最长: {max(lengths)}')
"
```

---

## 下一步: LoRA微调

生成300条高质量样本后,可进行微调:

```bash
# 使用LLaMA-Factory进行LoRA微调
llamafactory-cli train \
    --model_name_or_path Qwen/Qwen2.5-14B-Instruct \
    --dataset design_agent,synthesis_agent,mechanism_agent \
    --finetuning_type lora \
    --lora_rank 64 \
    --lora_alpha 128 \
    --learning_rate 1e-4 \
    --num_train_epochs 3 \
    --output_dir ./ecomats_lora
```

详细微调步骤见: `LoRA微调指南.md` (待创建)

---

## 常见问题

**Q1: 为什么不直接用GPT-4生成?**

A: 因为需要微调Qwen4 14B,用同系列模型(Qwen2.5)生成数据可以更好匹配目标模型的分布。

**Q2: 397篇文献够吗?**

A: 够! 每篇文献可生成多个不同角度的样本,关键是Prompt设计和质量控制。

**Q3: 生成速度慢怎么办?**

A: 
- 使用更小模型(7B)先快速验证流程
- 多GPU并行生成
- 使用量化模型(4-bit)降低显存需求

**Q4: 如何避免样本重复?**

A: 
- 脚本已实现随机采样文献
- Temperature设为0.7-0.8引入随机性
- 每篇文献提取不同角度的信息

---

## 许可证

本生成管道基于MinerU处理后的文献数据,仅用于学术研究。

生成的SFT数据遵循原文献的版权声明。

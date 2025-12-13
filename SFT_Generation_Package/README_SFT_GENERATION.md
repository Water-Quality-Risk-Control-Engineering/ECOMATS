# ECOMATS SFT数据生成 - 快速启动指南

## 🎯 目标

为三个智能体生成高质量SFT训练数据(各100条)，用于Qwen4 14B + LoRA微调

**数据格式**: 标准 `instruction + output` 格式，直接适用于SFT微调，无需额外转换

## 📁 项目结构

```
ECOMATS/
├── processed_output/           # 397篇MinerU处理的文献
├── sft_datasets/              # SFT数据输出目录
│   ├── design_agent_sft.jsonl
│   ├── synthesis_agent_sft.jsonl
│   └── mechanism_agent_sft.jsonl
├── sft_generation_pipeline.py # 核心生成脚本
├── batch_generate.sh          # 批量生成脚本
├── validate_sft_data.py       # 质量验证脚本
└── SFT生成指南.md             # 详细文档
```

## ⚡ 快速开始(3步)

### 1. 启动本地模型(Ollama)

```bash
# 如果还没安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载Qwen2.5 14B模型
ollama pull qwen2.5:14b

# 启动服务(新终端)
ollama serve
```

### 2. 安装Python依赖

```bash
cd /home/axlhuang/ECOMATS
pip install openai tqdm
```

### 3. 一键批量生成

```bash
# 自动生成所有数据(预计2.5小时)
./batch_generate.sh

# 或者手动生成单个智能体
python sft_generation_pipeline.py --agent design --num_samples 100
python sft_generation_pipeline.py --agent synthesis --num_samples 100
python sft_generation_pipeline.py --agent mechanism --num_samples 100
```

## 📊 验证数据质量

```bash
# 运行质量检查
python validate_sft_data.py

# 查看生成进度
wc -l sft_datasets/*.jsonl

# 查看样本示例(仅instruction+output两个字段)
head -1 sft_datasets/design_agent_sft.jsonl | python -m json.tool
```

## 🔍 三个智能体的生成逻辑

### 设计智能体
- **Instruction格式**: 完整的问题描述，包含:
  - 角色定义("你是一个环境催化材料专家")
  - 应用场景(印染废水处理项目)
  - 污染物特性(亚甲基蓝染料，浓度50 mg/L)
  - 性能目标(可见光下1小时内降解率>90%)
  - 约束条件(催化剂可循环5次以上，金属用量<2 wt%)
- **Output**: 材料选择 + 制备概述 + 性能预测 + 设计依据(800-1500字)
- **特点**: 侧重方案设计和参数优化，必须包含定量数据

### 合成方法智能体
- **Instruction格式**: 完整的制备问题，包含:
  - 角色定义("你是一个材料合成工艺专家")
  - 目标材料(Fe/Co双金属负载的N掺杂生物炭)
  - 性能要求(比表面积>800 m²/g，Fe+Co 8 wt%，N 5-8 wt%)
  - 原料和设备(玉米秸秆、FeCl₃、Co(NO₃)₂、尿素，常规实验室)
- **Output**: 分步骤制备流程 + 参数选择依据 + 质量控制(600-1200字)
- **特点**: 侧重操作细节和参数控制，每步骤有具体参数

### 机理挖掘智能体
- **Instruction格式**: 完整的机理分析问题，包含:
  - 角色定义("你是一个催化反应机理专家")
  - 催化体系(Fe₂.₅Co₀.₃Zn₀.₂O₄/UVA/PMS)
  - 实验条件(催化剂 0.2 g/L，PMS 0.4 mM，pH=8，60 min)
  - 表征数据(淬灭实验、EPR、XPS等)
  - 需解释的现象(双金属协同效应)
- **Output**: 反应路径 + 活性物种分析 + 协同效应(800-1500字)
- **特点**: 侧重化学方程式和定量分析，所有方程式必须配平

**格式示例**:
```json
{
  "instruction": "你是一个环境催化材料专家。现有一个印染废水处理项目，废水中含有亚甲基蓝染料(浓度50 mg/L)，要求在可见光下1小时内降解率>90%，催化剂可循环使用5次以上，金属用量<2 wt%。请设计一个单原子催化剂并说明设计思路。",
  "output": "**单原子催化剂设计方案**\n\n**1. 催化剂体系选择: Fe单原子/g-C₃N₄**..."
}
```

详见: [SFT生成指南.md](./SFT生成指南.md)

## ⚙️ 高级配置

### 使用其他模型

```bash
# 使用Qwen2.5 32B(需更多显存)
python sft_generation_pipeline.py \
    --agent design \
    --num_samples 50 \
    --model qwen2.5:32b

# 使用vLLM
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --port 8000

python sft_generation_pipeline.py \
    --agent design \
    --num_samples 50 \
    --base_url http://localhost:8000/v1
```

### 调整生成质量

编辑 `sft_generation_pipeline.py`:

```python
# 提高创造性
temperature=0.9  # 默认0.7-0.8

# 增加输出长度
max_tokens=4000  # 默认2500-3500

# 增加采样文献长度
max_chars=12000  # 默认8000
```

## 📈 预计时间和成本

**硬件**: RTX 4090 24GB, Qwen2.5 14B 4-bit量化

| 任务 | 样本数 | 预计时间 | GPU使用率 |
|------|--------|---------|-----------|
| 设计智能体 | 100条 | ~50分钟 | 60-70% |
| 合成方法智能体 | 100条 | ~42分钟 | 60-70% |
| 机理挖掘智能体 | 100条 | ~58分钟 | 60-70% |
| **总计** | 300条 | **~2.5小时** | - |

**成本**: 本地运行,仅电费成本 (~3-4元电费)

## ✅ 质量控制

### 自动验证指标

- JSON格式正确性
- 必需字段完整性
- 输出长度范围
- 包含定量数据
- 包含化学方程式(机理智能体)
- 避免模板化表述
- 文献引用/证据

### 人工抽检建议

- 抽检比例: 10% (每个智能体10条)
- 重点检查: 数据真实性、逻辑完整性、专业准确性

## 🐛 常见问题

**Q: 生成速度慢?**
```bash
# 方案1: 使用更小模型验证流程
ollama pull qwen2.5:7b
python sft_generation_pipeline.py --model qwen2.5:7b --num_samples 5

# 方案2: 使用量化模型
# 4-bit量化可节省50%显存,略微降低质量
```

**Q: JSON解析失败?**
```bash
# 检查模型输出
# 脚本已内置清洗逻辑,如仍失败,可能是模型问题
# 建议: 使用Qwen系列模型(对JSON格式支持好)
```

**Q: 样本质量不稳定?**
```python
# 调整temperature参数
temperature=0.7  # 降低随机性

# 或增加few-shot示例(修改Prompt)
```

## 📚 相关文档

- [SFT生成指南.md](./SFT生成指南.md) - 详细生成逻辑和Prompt设计
- [sft_generation_plan.md](./sft_generation_plan.md) - 初始方案文档

## 🔄 数据格式说明

生成的数据**默认已是标准 `instruction + output` 格式**，直接适用于大多数SFT微调框架，无需额外转换。

**格式示例**:
```json
{
  "instruction": "你是一个环境催化材料专家。现有一个印染废水处理项目...",
  "output": "**材料设计方案**\n\n1. **生物质选择**..."
}
```

**与医学问诊格式的对比**:
- 医生问诊: `{"instruction": "你是一个心血管科医生...", "output": "高血压的患者可以吃..."}`
- ECOMATS: `{"instruction": "你是一个环境催化材料专家...", "output": "**材料设计方案**..."}`

完全相同的格式，直接可用！

---

**备注**: 如需其他格式，可使用 `convert_sft_format.py` 工具进行转换。

## 📝 下一步

生成300条样本后:

1. **格式转换**: 根据微调框架要求选择转换策略
2. **质量审核**: 人工抽检10%样本
3. **数据清洁**: 删除低质量样本
4. **LoRA微调**: 使用LLaMA-Factory进行微调
5. **效果评估**: 在测试集上评估微调后模型

## 🙏 致谢

本项目基于397篇MinerU处理的科研文献,仅用于学术研究。

---

**快速联系**: 如有问题,请查看 `SFT生成指南.md` 获取详细帮助

╔════════════════════════════════════════════════════════════╗
║        ECOMATS SFT数据生成工具包 - 服务器部署指南            ║
╚════════════════════════════════════════════════════════════╝

📦 文件清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

核心脚本:
  • sft_generation_pipeline.py    - 主生成脚本(支持本地LLM)
  • batch_generate.sh              - 批量生成脚本(一键生成300条)
  • validate_sft_data.py           - 质量验证脚本
  • convert_sft_format.py          - 格式转换工具(备用)

文档:
  • README_SFT_GENERATION.md       - 快速启动指南
  • SFT生成指南.md                  - 详细文档(570行)
  • README.txt                     - 本文件

数据:
  • sft_datasets/                  - 已生成的SFT数据(9条样本)
    ├── design_agent_sft.jsonl
    ├── synthesis_agent_sft.jsonl
    └── mechanism_agent_sft.jsonl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 快速部署(3步)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 上传到服务器并解压
   scp -r SFT_Generation_Package user@server:/path/to/
   cd /path/to/SFT_Generation_Package

2. 启动本地LLM (Ollama推荐)
   # 安装Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   
   # 下载模型
   ollama pull qwen2.5:14b
   
   # 启动服务(新终端)
   ollama serve

3. 安装依赖并运行
   pip install openai tqdm
   
   # 一键批量生成300条样本(约2.5小时)
   chmod +x batch_generate.sh
   ./batch_generate.sh
   
   # 或手动生成
   python sft_generation_pipeline.py --agent design --num_samples 100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 数据格式说明
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

生成的数据为标准 instruction + output 格式,直接适用于SFT微调:

{
  "instruction": "你是一个环境催化材料专家。现有一个印染废水处理项目...",
  "output": "**材料设计方案**\n\n1. **生物质选择**..."
}

无需额外转换,直接可用于Qwen4 14B + LoRA微调!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️ 高级配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

使用其他LLM后端:
  # vLLM
  python -m vllm.entrypoints.openai.api_server \
      --model Qwen/Qwen2.5-14B-Instruct --port 8000
  
  python sft_generation_pipeline.py \
      --base_url http://localhost:8000/v1 --agent design

  # LM Studio
  # 在界面中启动服务器,然后:
  python sft_generation_pipeline.py \
      --base_url http://localhost:1234/v1 --agent design

调整生成参数:
  # 编辑 sft_generation_pipeline.py
  temperature=0.8     # 提高创造性 (默认0.7)
  max_tokens=4000     # 增加输出长度 (默认2500-3500)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 质量验证
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

生成完成后运行质量检查:
  python validate_sft_data.py

检查项目:
  ✓ JSON格式正确性
  ✓ 必需字段完整性
  ✓ 输出长度范围
  ✓ 包含定量数据
  ✓ 包含化学方程式(机理智能体)
  ✓ 避免模板化表述
  ✓ 文献引用/证据

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 预期结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

目标: 每个智能体100条样本,总计300条

硬件需求 (RTX 4090 24GB, Qwen2.5 14B 4-bit):
  • 生成时间: ~2.5小时
  • GPU使用率: 60-70%
  • 显存占用: ~18GB
  • 成功率: >90%

输出文件:
  sft_datasets/design_agent_sft.jsonl      - 100条
  sft_datasets/synthesis_agent_sft.jsonl   - 100条
  sft_datasets/mechanism_agent_sft.jsonl   - 100条

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  重要提示
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 需要准备文献数据:
   将MinerU处理后的Markdown文献放在 processed_output/ 目录
   (当前包含9条样本是基于已有文献生成的)

2. 模型选择建议:
   • 推荐: Qwen2.5 14B/32B (对JSON格式支持好)
   • 可选: Qwen2 14B, DeepSeek-V2等
   • 避免: 小于7B的模型(质量不稳定)

3. 生成策略:
   • 分批生成避免模型过热(batch_generate.sh已配置)
   • 每批35条,批次间休息10秒
   • 失败样本会自动记录,可重新生成

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 故障排查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

问题1: "找不到 processed_output 目录"
解决: 创建该目录并放入文献文件
  mkdir processed_output
  # 上传Markdown文献到此目录

问题2: "连接本地LLM失败"
解决: 检查Ollama服务状态
  curl http://localhost:11434/v1/models
  # 如失败,重启: ollama serve

问题3: "JSON解析失败"
解决: 模型输出不规范,可:
  • 降低temperature至0.6
  • 换用Qwen系列模型
  • 查看原始输出调试

问题4: "生成速度慢"
解决:
  • 使用更小模型验证(qwen2.5:7b)
  • 使用4-bit量化
  • 多GPU并行生成

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 详细文档
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

查看完整文档:
  • README_SFT_GENERATION.md  - 快速指南
  • SFT生成指南.md            - 详细的生成逻辑和Prompt设计

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

生成的数据可直接用于:
  • LLaMA-Factory微调
  • Qwen官方微调脚本
  • Swift微调框架
  • 自定义训练脚本

祝您微调顺利! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
生成时间: 2025-12-09
版本: v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

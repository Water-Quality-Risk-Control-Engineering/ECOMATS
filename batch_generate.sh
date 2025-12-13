#!/bin/bash
# ECOMATS SFT数据批量生成脚本
# 用于自动化生成三个智能体的训练数据

set -e  # 遇到错误立即退出

# ============== 配置区域 ==============
TOTAL_SAMPLES_PER_AGENT=100  # 每个智能体目标样本数
BATCH_SIZE=35                # 每批生成数量
SLEEP_TIME=10                # 批次间休息时间(秒)
MODEL="qwen2.5:14b"          # 本地模型名称
BASE_URL="http://localhost:11434/v1"  # Ollama API地址

# ======================================

echo "╔════════════════════════════════════════════════╗"
echo "║     ECOMATS SFT数据批量生成管道                   ║"
echo "║                                                ║"
echo "║  目标: 每个智能体生成 ${TOTAL_SAMPLES_PER_AGENT} 条样本               ║"
echo "║  批次大小: ${BATCH_SIZE} 条/批                           ║"
echo "║  模型: ${MODEL}                    ║"
echo "╚════════════════════════════════════════════════╝"
echo

# 计算需要的批次数
NUM_BATCHES=$(( (TOTAL_SAMPLES_PER_AGENT + BATCH_SIZE - 1) / BATCH_SIZE ))

# 检查Python脚本是否存在
if [ ! -f "sft_generation_pipeline.py" ]; then
    echo "❌ 错误: 找不到 sft_generation_pipeline.py"
    echo "   请确保在 /home/axlhuang/ECOMATS 目录下运行此脚本"
    exit 1
fi

# 检查文献目录
if [ ! -d "processed_output" ]; then
    echo "❌ 错误: 找不到 processed_output 目录"
    exit 1
fi

LITERATURE_COUNT=$(ls processed_output/*.md 2>/dev/null | wc -l)
if [ "$LITERATURE_COUNT" -eq 0 ]; then
    echo "❌ 错误: processed_output 目录中没有文献文件"
    exit 1
fi

echo "✓ 检测到 ${LITERATURE_COUNT} 篇文献"
echo "✓ 将分 ${NUM_BATCHES} 批次生成"
echo

# 创建输出目录
mkdir -p sft_datasets

# 记录开始时间
START_TIME=$(date +%s)

# ========== 生成函数 ==========
generate_agent_data() {
    local agent_type=$1
    local agent_name=$2
    local output_file="sft_datasets/${agent_type}_agent_sft.jsonl"
    
    echo "════════════════════════════════════════════════"
    echo "  开始生成: ${agent_name}"
    echo "════════════════════════════════════════════════"
    
    # 记录当前文件的初始行数
    local initial_lines=0
    if [ -f "$output_file" ]; then
        initial_lines=$(wc -l < "$output_file")
        echo "已有样本: ${initial_lines} 条"
    fi
    
    local batch_num=1
    local total_generated=0
    
    while [ $total_generated -lt $TOTAL_SAMPLES_PER_AGENT ]; do
        # 计算本批应该生成的数量
        local remaining=$((TOTAL_SAMPLES_PER_AGENT - total_generated))
        local current_batch_size=$BATCH_SIZE
        if [ $remaining -lt $BATCH_SIZE ]; then
            current_batch_size=$remaining
        fi
        
        echo
        echo "━━━ 批次 ${batch_num}/${NUM_BATCHES}: 生成 ${current_batch_size} 条样本 ━━━"
        
        # 执行生成
        if python sft_generation_pipeline.py \
            --agent "$agent_type" \
            --num_samples "$current_batch_size" \
            --model "$MODEL" \
            --base_url "$BASE_URL"; then
            
            # 统计当前文件行数
            local current_lines=$(wc -l < "$output_file")
            local new_samples=$((current_lines - initial_lines - total_generated))
            total_generated=$((total_generated + new_samples))
            
            echo "✓ 批次 ${batch_num} 完成,新增 ${new_samples} 条"
            echo "  累计生成: ${total_generated}/${TOTAL_SAMPLES_PER_AGENT}"
            
            # 批次间休息(最后一批不需要)
            if [ $total_generated -lt $TOTAL_SAMPLES_PER_AGENT ]; then
                echo "  休息 ${SLEEP_TIME} 秒..."
                sleep $SLEEP_TIME
            fi
        else
            echo "❌ 批次 ${batch_num} 生成失败"
            echo "   已成功生成 ${total_generated} 条样本"
            return 1
        fi
        
        batch_num=$((batch_num + 1))
    done
    
    echo
    echo "✓✓✓ ${agent_name} 生成完成! 总计: ${total_generated} 条 ✓✓✓"
    echo
}

# ========== 开始生成 ==========

# 1. 设计智能体
if generate_agent_data "design" "设计智能体"; then
    echo "✓ 设计智能体数据生成成功"
else
    echo "❌ 设计智能体生成失败,退出"
    exit 1
fi

echo
echo "────────────────────────────────────────────────"
echo "  休息 30 秒,让模型冷却..."
echo "────────────────────────────────────────────────"
sleep 30

# 2. 合成方法智能体
if generate_agent_data "synthesis" "合成方法智能体"; then
    echo "✓ 合成方法智能体数据生成成功"
else
    echo "❌ 合成方法智能体生成失败,退出"
    exit 1
fi

echo
echo "────────────────────────────────────────────────"
echo "  休息 30 秒,让模型冷却..."
echo "────────────────────────────────────────────────"
sleep 30

# 3. 机理挖掘智能体
if generate_agent_data "mechanism" "机理挖掘智能体"; then
    echo "✓ 机理挖掘智能体数据生成成功"
else
    echo "❌ 机理挖掘智能体生成失败,退出"
    exit 1
fi

# ========== 生成完成统计 ==========
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
HOURS=$((ELAPSED / 3600))
MINUTES=$(((ELAPSED % 3600) / 60))
SECONDS=$((ELAPSED % 60))

echo
echo "╔════════════════════════════════════════════════╗"
echo "║           🎉 全部生成完成! 🎉                     ║"
echo "╚════════════════════════════════════════════════╝"
echo
echo "总耗时: ${HOURS}小时 ${MINUTES}分钟 ${SECONDS}秒"
echo
echo "生成统计:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 详细统计
for agent in design synthesis mechanism; do
    file="sft_datasets/${agent}_agent_sft.jsonl"
    if [ -f "$file" ]; then
        count=$(wc -l < "$file")
        size=$(du -h "$file" | cut -f1)
        
        # 计算平均长度
        avg_len=$(python3 -c "
import json
try:
    with open('$file', 'r', encoding='utf-8') as f:
        lengths = [len(json.loads(line)['output']) for line in f if line.strip()]
    print(f'{sum(lengths)//len(lengths)} 字符')
except:
    print('N/A')
")
        
        echo "  ${agent}_agent_sft.jsonl"
        echo "    样本数: ${count}"
        echo "    文件大小: ${size}"
        echo "    平均长度: ${avg_len}"
        echo
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "下一步:"
echo "  1. 人工抽检 10% 样本质量"
echo "  2. 运行质量验证: python validate_sft_data.py"
echo "  3. 开始LoRA微调"
echo
echo "数据文件位置: $(pwd)/sft_datasets/"
echo

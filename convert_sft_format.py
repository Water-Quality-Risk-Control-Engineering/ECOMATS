#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFT数据格式转换脚本
将 instruction+input+output 格式转换为标准 instruction+output 格式

支持两种转换策略:
1. 合并模式: 将input合并到instruction中
2. 系统提示词模式: 将instruction作为系统角色,input作为用户问题
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict


class SFTFormatConverter:
    """SFT格式转换器"""
    
    def __init__(self, strategy: str = "merge"):
        """
        初始化转换器
        
        Args:
            strategy: 转换策略
                - "merge": 合并input到instruction
                - "system": 使用系统提示词格式
        """
        self.strategy = strategy
    
    def convert_merge_strategy(self, sample: Dict) -> Dict:
        """
        合并策略: 将input合并到instruction中
        
        原始格式:
        {
            "instruction": "设计一个催化剂用于降解四环素...",
            "input": "污染物特性: TC浓度100 mg/L...",
            "output": "推荐使用Fe-Co双金属..."
        }
        
        转换后:
        {
            "instruction": "设计一个催化剂用于降解四环素...\n\n【背景信息】\n污染物特性: TC浓度100 mg/L...",
            "output": "推荐使用Fe-Co双金属..."
        }
        """
        instruction = sample.get("instruction", "").strip()
        input_text = sample.get("input", "").strip()
        output = sample.get("output", "").strip()
        
        # 合并instruction和input
        if input_text:
            combined_instruction = f"{instruction}\n\n【背景信息】\n{input_text}"
        else:
            combined_instruction = instruction
        
        return {
            "instruction": combined_instruction,
            "output": output
        }
    
    def convert_system_strategy(self, sample: Dict) -> Dict:
        """
        系统提示词策略: 将instruction作为系统角色定义
        
        原始格式:
        {
            "instruction": "请设计一个催化剂...",
            "input": "污染物: TC, 浓度: 100 mg/L",
            "output": "推荐使用Fe-Co双金属..."
        }
        
        转换后:
        {
            "instruction": "你是一位环境催化材料设计专家。用户问题: 污染物: TC, 浓度: 100 mg/L\n\n请设计一个催化剂...",
            "output": "推荐使用Fe-Co双金属..."
        }
        """
        instruction = sample.get("instruction", "").strip()
        input_text = sample.get("input", "").strip()
        output = sample.get("output", "").strip()
        
        # 根据智能体类型确定系统角色
        if "设计" in instruction or "催化剂" in instruction:
            system_role = "你是一位环境催化材料设计专家。"
        elif "制备" in instruction or "合成" in instruction or "方法" in instruction:
            system_role = "你是一位材料合成工艺专家。"
        elif "机理" in instruction or "降解" in instruction or "活化" in instruction:
            system_role = "你是一位催化反应机理研究专家。"
        else:
            system_role = "你是一位水质净化领域的专家。"
        
        # 构造新的instruction
        if input_text:
            combined_instruction = f"{system_role}\n\n【用户问题】\n{input_text}\n\n【具体要求】\n{instruction}"
        else:
            combined_instruction = f"{system_role}\n\n{instruction}"
        
        return {
            "instruction": combined_instruction,
            "output": output
        }
    
    def convert_sample(self, sample: Dict) -> Dict:
        """转换单个样本"""
        if self.strategy == "merge":
            return self.convert_merge_strategy(sample)
        elif self.strategy == "system":
            return self.convert_system_strategy(sample)
        else:
            raise ValueError(f"不支持的转换策略: {self.strategy}")
    
    def convert_file(self, input_file: str, output_file: str):
        """转换整个文件"""
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        print(f"\n转换文件: {input_file}")
        print(f"策略: {self.strategy}")
        print(f"输出: {output_file}")
        
        converted_samples = []
        total = 0
        failed = 0
        
        # 读取并转换
        with open(input_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    sample = json.loads(line)
                    converted = self.convert_sample(sample)
                    converted_samples.append(converted)
                    total += 1
                except Exception as e:
                    print(f"  ⚠️  行{i}转换失败: {e}")
                    failed += 1
        
        # 写入转换后的数据
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for sample in converted_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"✓ 转换完成: {total} 条成功, {failed} 条失败")
        
        # 显示示例
        if converted_samples:
            print("\n示例(转换后):")
            print("-" * 60)
            example = converted_samples[0]
            print(f"Instruction (前200字符):")
            print(f"  {example['instruction'][:200]}...")
            print(f"\nOutput (前200字符):")
            print(f"  {example['output'][:200]}...")
            print("-" * 60)


def convert_all_datasets(strategy: str = "merge", output_dir: str = "sft_datasets_converted"):
    """转换所有数据集"""
    
    datasets = [
        ("sft_datasets/design_agent_sft.jsonl", "design"),
        ("sft_datasets/synthesis_agent_sft.jsonl", "synthesis"),
        ("sft_datasets/mechanism_agent_sft.jsonl", "mechanism"),
    ]
    
    converter = SFTFormatConverter(strategy=strategy)
    
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*16 + "SFT数据格式转换" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    print(f"\n转换策略: {strategy}")
    print(f"输出目录: {output_dir}")
    
    for input_file, agent_type in datasets:
        if not Path(input_file).exists():
            print(f"\n⚠️  跳过 {input_file} (文件不存在)")
            continue
        
        output_file = f"{output_dir}/{agent_type}_agent_sft_converted.jsonl"
        
        try:
            converter.convert_file(input_file, output_file)
        except Exception as e:
            print(f"❌ 转换失败: {e}")
    
    print("\n" + "="*60)
    print("✓ 所有文件转换完成!")
    print(f"\n转换后的文件位置: {output_dir}/")
    print("\n使用方法:")
    print("  # 查看转换后的数据")
    print(f"  head -1 {output_dir}/design_agent_sft_converted.jsonl | python -m json.tool")
    print("\n  # 合并所有数据集")
    print(f"  cat {output_dir}/*_converted.jsonl > {output_dir}/ecomats_sft_all.jsonl")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="SFT数据格式转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 使用合并策略转换所有数据集
  python convert_sft_format.py --strategy merge

  # 使用系统提示词策略
  python convert_sft_format.py --strategy system

  # 转换单个文件
  python convert_sft_format.py \\
      --input sft_datasets/design_agent_sft.jsonl \\
      --output sft_datasets_converted/design_converted.jsonl \\
      --strategy merge
        """
    )
    
    parser.add_argument("--strategy", type=str, default="merge",
                       choices=["merge", "system"],
                       help="转换策略: merge(合并) 或 system(系统提示词)")
    parser.add_argument("--input", type=str,
                       help="输入文件路径(不指定则转换所有数据集)")
    parser.add_argument("--output", type=str,
                       help="输出文件路径(配合--input使用)")
    parser.add_argument("--output_dir", type=str, default="sft_datasets_converted",
                       help="输出目录(批量转换时使用)")
    
    args = parser.parse_args()
    
    if args.input:
        # 转换单个文件
        if not args.output:
            print("❌ 错误: 使用--input时必须指定--output")
            return
        
        converter = SFTFormatConverter(strategy=args.strategy)
        converter.convert_file(args.input, args.output)
    else:
        # 批量转换
        convert_all_datasets(strategy=args.strategy, output_dir=args.output_dir)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFT数据质量验证脚本
检查生成的JSONL文件质量,识别问题样本
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class SFTValidator:
    """SFT数据验证器"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.samples = []
        self.issues = defaultdict(list)
        
    def load_data(self):
        """加载JSONL数据"""
        print(f"\n加载文件: {self.file_path}")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    sample = json.loads(line)
                    sample['_line_num'] = i
                    self.samples.append(sample)
                except json.JSONDecodeError as e:
                    print(f"  ⚠️  行{i}: JSON解析错误 - {e}")
                    self.issues['json_error'].append(i)
        
        print(f"✓ 成功加载 {len(self.samples)} 个样本")
    
    def check_required_fields(self):
        """检查必需字段"""
        print("\n检查必需字段...")
        required = ['instruction', 'input', 'output']
        
        for sample in self.samples:
            line = sample['_line_num']
            for field in required:
                if field not in sample:
                    self.issues['missing_field'].append((line, field))
                elif not sample[field] or not sample[field].strip():
                    self.issues['empty_field'].append((line, field))
    
    def check_output_length(self, min_len: int = 500, max_len: int = 8000):
        """检查输出长度"""
        print(f"\n检查输出长度(期望 {min_len}-{max_len} 字符)...")
        
        lengths = []
        for sample in self.samples:
            line = sample['_line_num']
            output = sample.get('output', '')
            length = len(output)
            lengths.append(length)
            
            if length < min_len:
                self.issues['too_short'].append((line, length))
            elif length > max_len:
                self.issues['too_long'].append((line, length))
        
        if lengths:
            avg = sum(lengths) / len(lengths)
            print(f"  平均长度: {avg:.0f} 字符")
            print(f"  最短: {min(lengths)}, 最长: {max(lengths)}")
    
    def check_numbers_presence(self):
        """检查是否包含数值数据"""
        print("\n检查定量数据...")
        
        for sample in self.samples:
            line = sample['_line_num']
            output = sample.get('output', '')
            
            # 检查是否包含数字
            if not re.search(r'\d', output):
                self.issues['no_numbers'].append(line)
                continue
            
            # 检查是否包含具体数值(带单位)
            has_specific_data = bool(re.search(
                r'\d+\.?\d*\s*(%|°C|℃|g/L|mg/L|m²/g|nm|eV|min|h|mM|wt%|emu/g)',
                output
            ))
            if not has_specific_data:
                self.issues['no_specific_numbers'].append(line)
    
    def check_equations(self, agent_type: str):
        """检查化学方程式(仅机理智能体)"""
        if agent_type != 'mechanism':
            return
        
        print("\n检查化学方程式...")
        
        for sample in self.samples:
            line = sample['_line_num']
            output = sample.get('output', '')
            
            # 检查是否包含反应箭头
            has_equation = bool(re.search(r'[→⇄←↔=]', output))
            if not has_equation:
                self.issues['no_equations'].append(line)
    
    def check_template_phrases(self):
        """检查模板化表述"""
        print("\n检查模板化表述...")
        
        template_patterns = [
            r'我推荐.*因为它.*好',
            r'这是一个.*的.*',
            r'首先.*其次.*最后',
            r'总之.*综上所述',
            r'根据.*可以.*',
        ]
        
        for sample in self.samples:
            line = sample['_line_num']
            output = sample.get('output', '')
            
            for pattern in template_patterns:
                if re.search(pattern, output):
                    self.issues['template_phrase'].append((line, pattern))
    
    def check_citation_evidence(self):
        """检查文献引用或证据"""
        print("\n检查文献证据...")
        
        evidence_keywords = [
            '文献', '研究表明', '报道', '证实', '证明',
            'XPS', 'EPR', 'XRD', 'TEM', 'SEM', 'BET',
            'et al', '等人'
        ]
        
        for sample in self.samples:
            line = sample['_line_num']
            output = sample.get('output', '')
            
            has_evidence = any(kw in output for kw in evidence_keywords)
            if not has_evidence:
                self.issues['no_citation'].append(line)
    
    def generate_report(self, agent_type: str):
        """生成验证报告"""
        total = len(self.samples)
        
        print("\n" + "="*60)
        print(f"  验证报告: {self.file_path.name}")
        print("="*60)
        
        # 总体统计
        print(f"\n总样本数: {total}")
        
        if not self.issues:
            print("\n✓✓✓ 所有样本通过验证! ✓✓✓")
            return
        
        # 问题统计
        print("\n问题汇总:")
        print("-" * 60)
        
        issue_counts = {
            'json_error': 'JSON格式错误',
            'missing_field': '缺少必需字段',
            'empty_field': '字段为空',
            'too_short': '输出过短(<500字符)',
            'too_long': '输出过长(>8000字符)',
            'no_numbers': '缺少数值数据',
            'no_specific_numbers': '缺少具体参数',
            'no_equations': '缺少化学方程式',
            'template_phrase': '模板化表述',
            'no_citation': '缺少文献引用/证据',
        }
        
        for issue_key, issue_name in issue_counts.items():
            if issue_key in self.issues:
                count = len(self.issues[issue_key])
                pct = count / total * 100
                print(f"  {issue_name:20s}: {count:3d} ({pct:5.1f}%)")
        
        # 详细问题列表
        print("\n详细问题列表:")
        print("-" * 60)
        
        for issue_key, issue_name in issue_counts.items():
            if issue_key not in self.issues:
                continue
            
            print(f"\n【{issue_name}】")
            items = self.issues[issue_key]
            
            # 显示前10个问题
            for item in items[:10]:
                if isinstance(item, tuple):
                    print(f"  行 {item[0]}: {item[1]}")
                else:
                    print(f"  行 {item}")
            
            if len(items) > 10:
                print(f"  ... 还有 {len(items)-10} 个")
        
        # 合格率统计
        print("\n合格率分析:")
        print("-" * 60)
        
        # 统计有问题的样本行号
        problematic_lines = set()
        for issues_list in self.issues.values():
            for item in issues_list:
                if isinstance(item, tuple):
                    problematic_lines.add(item[0])
                else:
                    problematic_lines.add(item)
        
        qualified = total - len(problematic_lines)
        qualified_pct = qualified / total * 100
        
        print(f"  合格样本: {qualified}/{total} ({qualified_pct:.1f}%)")
        print(f"  问题样本: {len(problematic_lines)}/{total} ({100-qualified_pct:.1f}%)")
        
        # 建议
        print("\n改进建议:")
        print("-" * 60)
        
        if self.issues.get('too_short'):
            print("  • 增加max_tokens参数至3500-4000")
        if self.issues.get('no_specific_numbers'):
            print("  • 在Prompt中强调\"必须包含具体数值和单位\"")
        if self.issues.get('no_equations'):
            print("  • 机理智能体Prompt中强调\"必须包含配平的化学方程式\"")
        if self.issues.get('template_phrase'):
            print("  • 在System Prompt中明确\"避免模板化表述\"")
        if self.issues.get('no_citation'):
            print("  • 强调\"必须引用文献中的实际案例或数据\"")
        
        print("\n" + "="*60 + "\n")
    
    def export_problematic_samples(self, output_file: str):
        """导出有问题的样本供人工复查"""
        problematic_lines = set()
        for issues_list in self.issues.values():
            for item in issues_list:
                if isinstance(item, tuple):
                    problematic_lines.add(item[0])
                else:
                    problematic_lines.add(item)
        
        problematic_samples = [
            s for s in self.samples 
            if s['_line_num'] in problematic_lines
        ]
        
        if problematic_samples:
            with open(output_file, 'w', encoding='utf-8') as f:
                for sample in problematic_samples:
                    line_num = sample.pop('_line_num')
                    f.write(f"// 行号: {line_num}\n")
                    f.write(json.dumps(sample, ensure_ascii=False, indent=2))
                    f.write('\n\n')
            
            print(f"✓ 导出 {len(problematic_samples)} 个问题样本至: {output_file}")


def validate_all_datasets():
    """验证所有SFT数据集"""
    datasets = [
        ('sft_datasets/design_agent_sft.jsonl', 'design', 800, 1500),
        ('sft_datasets/synthesis_agent_sft.jsonl', 'synthesis', 600, 1200),
        ('sft_datasets/mechanism_agent_sft.jsonl', 'mechanism', 800, 1500),
    ]
    
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*18 + "SFT数据质量验证" + " "*18 + "║")
    print("╚" + "="*58 + "╝")
    
    for file_path, agent_type, min_len, max_len in datasets:
        if not Path(file_path).exists():
            print(f"\n⚠️  跳过 {file_path} (文件不存在)")
            continue
        
        validator = SFTValidator(file_path)
        validator.load_data()
        validator.check_required_fields()
        validator.check_output_length(min_len, max_len)
        validator.check_numbers_presence()
        validator.check_equations(agent_type)
        validator.check_template_phrases()
        validator.check_citation_evidence()
        validator.generate_report(agent_type)
        
        # 导出问题样本
        problem_file = file_path.replace('.jsonl', '_problems.txt')
        validator.export_problematic_samples(problem_file)


if __name__ == "__main__":
    validate_all_datasets()

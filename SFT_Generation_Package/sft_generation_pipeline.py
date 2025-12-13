#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECOMATS SFT数据生成管道
用于批量生成三个智能体(设计、合成、机理)的监督微调数据

使用方法:
1. 配置本地LLM API (Ollama/vLLM/LMStudio等)
2. 运行: python sft_generation_pipeline.py --agent design --num_samples 50
3. 生成的数据自动追加到对应的JSONL文件

依赖: pip install openai tqdm
"""

import os
import json
import random
import argparse
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

try:
    from openai import OpenAI
except ImportError:
    print("请安装OpenAI库: pip install openai")
    exit(1)


class SFTGenerator:
    """SFT数据生成器"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434/v1",  # Ollama默认地址
                 model: str = "qwen2.5:14b",  # 本地模型名称
                 literature_dir: str = "./processed_output"):
        """
        初始化生成器
        
        Args:
            base_url: 本地LLM API地址
            model: 模型名称
            literature_dir: 文献目录路径
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key="dummy"  # 本地模型不需要真实API key
        )
        self.model = model
        self.literature_dir = Path(literature_dir)
        
        # 加载文献列表
        self.literature_files = list(self.literature_dir.glob("*.md"))
        print(f"✓ 找到 {len(self.literature_files)} 篇文献")
        
    def read_literature(self, file_path: Path, max_chars: int = 8000) -> str:
        """读取文献内容(截断至合理长度)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 截取前max_chars字符,避免超出上下文
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n[文献内容已截断...]"
            return content
        except Exception as e:
            print(f"读取文献失败 {file_path}: {e}")
            return ""
    
    def generate_design_agent_sample(self, literature_content: str) -> Dict:
        """生成设计智能体SFT样本"""
        
        system_prompt = """你是一位资深的环境催化材料专家，专注于水质净化催化剂的设计。

你的任务是基于提供的科研文献，生成高质量的材料设计问答对。

要求:
1. **Instruction**: 提出一个完整的催化剂设计问题，需包含:
   - 明确的应用场景(如降解某种污染物)
   - 目标污染物的化学特性和浓度
   - 性能目标(降解率、矿化率等)
   - 约束条件(成本、pH范围、可回收性等)
   - 废水/水质条件
   
   **重要**: instruction字段应该是一个完整的问题描述，包含所有必要的背景信息。

2. **Output**: 给出详细的设计方案，必须包含:
   - 材料体系选择及理由(结合文献中的实际案例)
   - 制备方法和关键参数
   - 预期性能指标
   - 设计依据和文献支撑
   - 成本估算(如适用)
   
输出格式要求:
- 使用Markdown格式组织内容
- 包含具体数值和参数
- 引用文献中的真实数据
- 避免模板化表述,结合具体案例

请直接输出JSON格式(仅包含instruction和output两个字段):
{
    "instruction": "完整的问题描述，包含应用场景、污染物特性、性能目标、约束条件等所有信息",
    "output": "详细的设计方案"
}"""

        user_prompt = f"""基于以下文献内容，生成1个设计智能体的SFT样本:

<文献内容>
{literature_content}
</文献内容>

请从文献中提取关键信息(催化剂材料、制备方法、性能数据、降解机理等)，设计一个真实、有深度的材料设计问答。

要求:
1. instruction字段应包含完整的问题和所有背景信息，例如:
   "你是一个环境催化材料专家。现有一个印染废水处理项目，废水中含有亚甲基蓝染料(浓度50 mg/L)，要求在可见光下1小时内降解率>90%，催化剂可循环使用5次以上，金属用量<2 wt%。请设计一个单原子催化剂并说明设计思路。"

2. 问题要具体且有挑战性，包含明确的数值指标
3. 答案要包含定量数据(如比表面积、降解率、成本等)
4. 必须引用文献中的实际案例或数据
5. 输出长度800-1500字

现在请生成样本(仅输出JSON格式，只包含instruction和output两个字段，不要其他解释):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # 适度创造性
                max_tokens=3000
            )
            
            result = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            # 移除可能的markdown代码块标记
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
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"模型输出: {result[:200]}...")
            return None
        except Exception as e:
            print(f"生成失败: {e}")
            return None
    
    def generate_synthesis_agent_sample(self, literature_content: str) -> Dict:
        """生成合成方法智能体SFT样本"""
        
        system_prompt = """你是一位材料合成工艺专家，专注于环境催化材料的制备。

你的任务是基于提供的科研文献，生成高质量的合成方法问答对。

要求:
1. **Instruction**: 提出一个完整的材料制备问题，需包含:
   - 制备某种特定催化剂
   - 目标材料的组成和结构
   - 性能要求(比表面积、粒径、负载量等)
   - 设备和成本限制
   
   **重要**: instruction字段应该是一个完整的问题描述，包含所有必要的需求和条件。

2. **Output**: 给出详细的合成方案，必须包含:
   - 完整的制备步骤(反应条件、时间、温度等)
   - 关键参数的选择依据
   - 质量控制要点
   - 常见问题及解决方法
   - 表征方法建议
   
输出格式要求:
- 步骤清晰，参数具体
- 包含反应方程式(如适用)
- 引用文献中的实际制备案例
- 标注关键控制点和注意事项

请直接输出JSON格式(仅包含instruction和output两个字段):
{
    "instruction": "完整的制备问题描述，包含目标材料、性能要求、设备限制等所有信息",
    "output": "详细的制备方案"
}"""

        user_prompt = f"""基于以下文献内容，生成1个合成方法智能体的SFT样本:

<文献内容>
{literature_content}
</文献内容>

请从文献中提取制备方法的详细信息，设计一个完整的合成工艺问答。

要求:
1. instruction字段应包含完整的制备问题和所有要求，例如:
   "你是一个材料合成工艺专家。请提供Fe/Co双金属负载的N掺杂生物炭催化剂的详细制备方法。要求比表面积>800 m²/g，Fe+Co总负载量8 wt%，N含量5-8 wt%。原料使用玉米秸秆、FeCl₃·6H₂O、Co(NO₃)₂·6H₂O、尿素，设备为常规实验室条件。"

2. 聚焦于具体的制备步骤和参数
3. 包含详细的操作细节(温度、时间、浓度、pH等)
4. 解释关键参数选择的原因
5. 输出长度600-1200字

现在请生成样本(仅输出JSON格式，只包含instruction和output两个字段，不要其他解释):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
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
    
    def generate_mechanism_agent_sample(self, literature_content: str) -> Dict:
        """生成机理挖掘智能体SFT样本"""
        
        system_prompt = """你是一位催化反应机理研究专家，专注于高级氧化工艺的反应机制。

你的任务是基于提供的科研文献，生成高质量的机理解析问答对。

要求:
1. **Instruction**: 提出一个完整的机理分析问题，需包含:
   - 催化体系组成(催化剂、氧化剂等)
   - 实验条件(pH、温度、浓度等)
   - 表征数据(EPR、XPS、淬灭实验等)
   - 需要解释的机理现象
   
   **重要**: instruction字段应该是一个完整的问题描述，包含所有实验条件和背景信息。

2. **Output**: 给出深入的机理分析，必须包含:
   - 逐步的反应路径(配平的化学方程式)
   - 活性物种识别及证据
   - 关键中间体和价态变化
   - 淬灭实验或表征数据的解读
   - 机理的创新点或独特性
   
输出格式要求:
- 包含详细的反应方程式
- 结合XPS、EPR等表征数据
- 定量分析活性物种贡献
- 解释协同效应或电子转移

请直接输出JSON格式(仅包含instruction和output两个字段):
{
    "instruction": "完整的机理分析问题，包含催化体系、实验条件、表征数据等所有信息",
    "output": "详细的机理分析"
}"""

        user_prompt = f"""基于以下文献内容，生成1个机理挖掘智能体的SFT样本:

<文献内容>
{literature_content}
</文献内容>

请从文献中提取机理相关信息(活性物种、反应路径、电子转移、表征数据等)，设计一个深入的机理分析问答。

要求:
1. instruction字段应包含完整的问题和所有实验信息，例如:
   "你是一个催化反应机理专家。请分析Fe₂.₅Co₀.₃Zn₀.₂O₄/UVA/PMS体系降解Sulfalene的活性氧物种生成机理，并解释双金属掺杂的协同效应。实验条件：催化剂用量0.2 g/L，PMS浓度0.4 mM，UVA光照，pH=8，反应时间60 min。淬灭实验使用甲醇（MeOH）、叔丁醇（TBA）、对苯醌（p-BQ）和碘化钾（KI）作为清除剂。EPR检测到DMPO-SO₄和DMPO-OH信号。"

2. 聚焦于反应机制和活性物种
3. 包含具体的反应方程式和价态变化
4. 结合淬灭实验、EPR、XPS等证据
5. 输出长度800-1500字

现在请生成样本(仅输出JSON格式，只包含instruction和output两个字段，不要其他解释):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=3500
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
    
    def generate_samples(self, agent_type: str, num_samples: int, output_file: str):
        """批量生成SFT样本"""
        
        agent_generators = {
            "design": self.generate_design_agent_sample,
            "synthesis": self.generate_synthesis_agent_sample,
            "mechanism": self.generate_mechanism_agent_sample
        }
        
        if agent_type not in agent_generators:
            raise ValueError(f"不支持的智能体类型: {agent_type}")
        
        generator = agent_generators[agent_type]
        
        print(f"\n开始生成 {agent_type} 智能体的SFT数据...")
        print(f"目标数量: {num_samples}")
        print(f"输出文件: {output_file}")
        
        successful = 0
        failed = 0
        
        # 确保输出目录存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 以追加模式打开文件
        with open(output_file, 'a', encoding='utf-8') as f:
            for i in tqdm(range(num_samples), desc=f"生成{agent_type}样本"):
                # 随机选择一篇文献
                lit_file = random.choice(self.literature_files)
                lit_content = self.read_literature(lit_file)
                
                if not lit_content:
                    failed += 1
                    continue
                
                # 生成样本
                sample = generator(lit_content)
                
                if sample:
                    # 写入JSONL文件
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
                    f.flush()  # 立即写入磁盘
                    successful += 1
                else:
                    failed += 1
                    
        print(f"\n✓ 生成完成!")
        print(f"  成功: {successful}")
        print(f"  失败: {failed}")
        print(f"  成功率: {successful/(successful+failed)*100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="ECOMATS SFT数据生成管道")
    parser.add_argument("--agent", type=str, required=True,
                       choices=["design", "synthesis", "mechanism"],
                       help="智能体类型: design/synthesis/mechanism")
    parser.add_argument("--num_samples", type=int, default=50,
                       help="生成样本数量 (默认: 50)")
    parser.add_argument("--model", type=str, default="qwen2.5:14b",
                       help="本地模型名称 (默认: qwen2.5:14b)")
    parser.add_argument("--base_url", type=str, default="http://localhost:11434/v1",
                       help="本地LLM API地址 (默认: Ollama)")
    parser.add_argument("--literature_dir", type=str, default="./processed_output",
                       help="文献目录路径")
    
    args = parser.parse_args()
    
    # 输出文件路径
    output_files = {
        "design": "./sft_datasets/design_agent_sft.jsonl",
        "synthesis": "./sft_datasets/synthesis_agent_sft.jsonl",
        "mechanism": "./sft_datasets/mechanism_agent_sft.jsonl"
    }
    
    # 创建生成器
    generator = SFTGenerator(
        base_url=args.base_url,
        model=args.model,
        literature_dir=args.literature_dir
    )
    
    # 生成样本
    generator.generate_samples(
        agent_type=args.agent,
        num_samples=args.num_samples,
        output_file=output_files[args.agent]
    )


if __name__ == "__main__":
    main()

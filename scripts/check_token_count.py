#!/usr/bin/env python3
"""检查TOA SFT训练集的token数量"""
import json
import tiktoken

enc = tiktoken.get_encoding('cl100k_base')

with open('/home/axlhuang/ECOMATS/sft_datasets/toa_intent_recognition_sft.jsonl', 'r') as f:
    lines = f.readlines()

total = len(lines)
max_t = 0
min_t = 999
over = 0
token_list = []

for line in lines:
    data = json.loads(line)
    text = data['instruction'] + data['output']
    tokens = len(enc.encode(text))
    token_list.append(tokens)
    max_t = max(max_t, tokens)
    min_t = min(min_t, tokens)
    if tokens > 128:
        over += 1

avg_t = sum(token_list) / len(token_list)

print("=" * 50)
print("TOA Intent Recognition SFT Dataset Statistics")
print("=" * 50)
print(f"Total samples: {total}")
print(f"Max tokens: {max_t}")
print(f"Min tokens: {min_t}")
print(f"Avg tokens: {avg_t:.1f}")
print(f"Samples over 128 tokens: {over}")
print(f"Fits 128 token limit: {'YES' if over == 0 else 'NO'}")
print("=" * 50)

#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

model_name = "qwen3-next-80b-a3b-thinking"

print(f"快速测试模型: {model_name}")
print("="*60)

client = OpenAI(
    api_key=os.getenv('QWEN_API_KEY'),
    base_url=os.getenv('QWEN_API_BASE'),
)

try:
    print("发送请求...")
    response = client.chat.completions.create(
        model=model_name,
        messages=[{'role': 'user', 'content': 'Hi'}],
        max_tokens=50,
        timeout=30
    )
    print(f"\n✅ SUCCESS! 模型可用")
    print(f"模型名: {response.model}")
    print(f"响应: {response.choices[0].message.content[:100]}")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ FAILED: {str(e)[:200]}")
    sys.exit(1)

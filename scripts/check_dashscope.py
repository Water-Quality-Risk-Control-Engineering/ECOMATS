#!/usr/bin/env python3
"""
DashScope 兼容接口连通性检测
- 使用 OpenAI 官方 SDK 通过兼容模式端点进行最小化调用
- 读取 .env 或环境中的 QWEN/OPENAI/DASHSCOPE 变量
"""

import os
import sys
from dotenv import load_dotenv, find_dotenv
from typing import Tuple


def load_env():
    try:
        dotenv_path = find_dotenv(usecwd=True)
        if dotenv_path:
            load_dotenv(dotenv_path)
    except Exception:
        # 忽略 .env 查找异常，继续读取现有环境
        pass


def resolve_config() -> Tuple[str, str, str, str, str, str]:
    # 解析端点
    base = None
    base_src = None
    for name in ("QWEN_API_BASE", "OPENAI_API_BASE", "OPENAI_BASE_URL"):
        v = os.getenv(name)
        if v:
            base = v
            base_src = name
            break

    # 解析密钥
    key = None
    key_src = None
    for name in ("QWEN_API_KEY", "OPENAI_API_KEY", "DASHSCOPE_API_KEY"):
        v = os.getenv(name)
        if v:
            key = v
            key_src = name
            break

    # 解析模型
    model = None
    model_src = None
    for name in ("QWEN_MODEL_NAME", "OPENAI_MODEL_NAME"):
        v = os.getenv(name)
        if v:
            model = v
            model_src = name
            break
    if not model:
        model = "qwen-plus"
        model_src = "default"

    return base, key, model, base_src or "<unset>", key_src or "<unset>", model_src


def mask_key(k: str) -> str:
    if not k:
        return "<empty>"
    k = k.strip()
    if len(k) <= 10:
        return k[:3] + "***" + k[-2:]
    return k[:6] + "***" + k[-4:]


def check(base: str, key: str, model: str) -> int:
    if not base or not key:
        print("[ERROR] 未找到端点或密钥，请在 .env 中设置 QWEN_API_BASE/QWEN_API_KEY 或导出 OPENAI_API_* / DASHSCOPE_API_KEY")
        return 2
    try:
        from openai import OpenAI
    except Exception:
        print("[ERROR] 未安装 openai 库，请先执行: pip install openai")
        return 3
    try:
        client = OpenAI(api_key=key, base_url=base)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "ping"},
            ],
            max_tokens=8,
        )
        text = resp.choices[0].message.content
        print("[OK] 调用成功，返回: ", (text or "<empty>")[:80])
        return 0
    except Exception as e:
        print("[FAIL] 调用失败:")
        print(e)
        # 简单字符串匹配，识别 401/密钥错误并尝试回退端点
        msg = str(e)
        is_invalid_key = ("invalid_api_key" in msg) or ("Incorrect API key" in msg) or ("401" in msg)
        if is_invalid_key:
            if "dashscope-intl.aliyuncs.com" in base:
                fallback_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            elif "dashscope.aliyuncs.com" in base:
                fallback_base = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
            else:
                fallback_base = None

            if fallback_base:
                print("[INFO] 检测到 401/密钥错误，尝试回退端点:", fallback_base)
                try:
                    from openai import OpenAI as _OpenAI
                    client2 = _OpenAI(api_key=key, base_url=fallback_base)
                    resp2 = client2.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "ping"},
                        ],
                        max_tokens=8,
                    )
                    text2 = resp2.choices[0].message.content
                    print("[OK] 回退端点调用成功，返回:", (text2 or "<empty>")[:80])
                    return 0
                except Exception as e2:
                    print("[FAIL] 回退端点仍失败:")
                    print(e2)

        print("[HINT] 可能原因与修复建议：")
        print("- API Key 与端点区域不匹配（国内/国际）。请使用对应区域的 Key。")
        print("- 确认 .env 中只保留一种 Key（建议 QWEN_API_KEY），避免变量覆盖。")
        print("- 若使用国内 Key，请将端点设为 https://dashscope.aliyuncs.com/compatible-mode/v1；国际则使用 intl 域名。")
        print("- 若仍失败，请在 .env 更新正确的 Key 后重试。")
        return 1


def main():
    load_env()
    base, key, model, base_src, key_src, model_src = resolve_config()
    print("使用端点:", base, "(来源:", base_src, ")")
    print("使用模型:", model, "(来源:", model_src, ")")
    print("使用密钥来源:", key_src, "; 密钥指纹:", mask_key(key))
    code = check(base, key, model)
    sys.exit(code)


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""DeepSeek 连通性自检：发一个最小请求，确认密钥 + 模型名 + 网络可用。"""
import sys
from llm_config import chat, MODEL, BASE_URL, ENV_PATH, API_KEY


def main():
    print(f"模型: {MODEL}")
    print(f"接口: {BASE_URL}")
    print(f".env: {ENV_PATH}")
    print(f"密钥: {'已加载 (sk-***' + (API_KEY[-4:] if API_KEY else '') + ')' if API_KEY else '未找到'}")
    print("-" * 40)
    try:
        reply = chat(
            [
                {"role": "system", "content": "你是连通性测试助手，回答简短。"},
                {"role": "user", "content": "请回复一句话确认连通正常，并报出你的模型名称。"},
            ],
            max_tokens=80,
        )
        print("[成功] 模型响应：", reply.strip())
    except Exception as e:
        print("[失败]", repr(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

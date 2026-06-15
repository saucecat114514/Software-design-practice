# -*- coding: utf-8 -*-
"""
统一语言模型配置 —— 所有 AI 智能体（A1~A6）共用。
模型：DeepSeek 官方 API，deepseek-v4-pro。
密钥从项目根目录 .env 读取（.env 已被 .gitignore 排除，绝不提交）。

提供两种使用方式：
  1) chat(messages)        轻量调用（仅依赖 requests，本机可跑，无需 crewai）
  2) get_crew_llm()        构建 CrewAI LLM 对象（需 pip install crewai）
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # 兜底：手动解析 .env
    load_dotenv = None


def _find_and_load_env():
    """从本文件向上逐级寻找 .env 并加载。"""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        cand = parent / ".env"
        if cand.exists():
            if load_dotenv:
                load_dotenv(cand)
            else:
                for line in cand.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            return cand
    return None


ENV_PATH = _find_and_load_env()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def chat(messages, temperature=0.7, max_tokens=1024, timeout=90):
    """轻量对话调用（OpenAI 兼容接口，requests 实现）。返回 assistant 文本。"""
    import requests

    if not API_KEY:
        raise RuntimeError(f"未找到 DEEPSEEK_API_KEY（.env 路径：{ENV_PATH}）")
    url = BASE_URL.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def get_crew_llm():
    """构建 CrewAI LLM 对象（需 pip install crewai）。"""
    from crewai import LLM

    return LLM(model=f"deepseek/{MODEL}", base_url=BASE_URL, api_key=API_KEY)

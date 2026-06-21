# -*- coding: utf-8 -*-
"""A1 需求获取对话页面 · 本地后端（零第三方依赖，仅用标准库 + 同级 llm_config）。

模型：己方(人)=涉众，对方=A1 需求获取 agent。密钥仅在服务端 .env，绝不下发前端。
启动：python server.py  → 浏览器开 http://127.0.0.1:8000
接口：
  GET  /                       静态页面 index.html
  GET  /api/agents             返回 5 个 A1 agent 列表
  GET  /api/last?agent&kind     取最后保存的会话(供恢复)，kind=首访/补访
  GET  /api/followup?agent      取该涉众的补访问题(从 补访问题清单-v1.0.md)
  POST /api/chat   {agent, messages, agenda?, max_tokens?} → {reply}   agenda 非空=补访模式
  POST /api/save   {agent, target, kind?, transcript, messages} → {path, kind}  kind=首访/补访
"""
import json
import re
import sys
import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = Path(__file__).resolve()
AGENTS_DIR = HERE.parent.parent          # wiki/summaries/agents
# server.py 位于 …/wiki/summaries/agents/web/，向上 5 级才是项目根 D:\Project
# parents: [0]=web [1]=agents [2]=summaries [3]=wiki [4]=D:\Project
PROJECT_ROOT = HERE.parents[4]           # D:\Project
RAW_NOTES = PROJECT_ROOT / "raw" / "notes"
SESSIONS_DIR = HERE.parent / "sessions"   # web/sessions/：保存最近一次会话 JSON，供恢复（运行态，已 gitignore）
FOLLOWUP_MD = PROJECT_ROOT / "wiki" / "summaries" / "补访问题清单-v1.0.md"
sys.path.insert(0, str(AGENTS_DIR))

import llm_config  # noqa: E402
import agent_course_consultant as a_consultant      # noqa: E402
import agent_academic_affairs as a_academic         # noqa: E402
import agent_finance as a_finance                   # noqa: E402
import agent_principal as a_principal               # noqa: E402
import agent_sysadmin as a_sysadmin                 # noqa: E402

AGENTS = {
    "course_consultant": a_consultant,
    "academic_affairs": a_academic,
    "finance": a_finance,
    "principal": a_principal,
    "sysadmin": a_sysadmin,
}

KICKOFF = "请开始这次需求访谈：先用一两句话说明你是谁、想了解哪方面，然后提出你的第一个问题。"
FOLLOWUP_KICKOFF = "这是一次补充访谈（补访）。请先用一句话说明这是针对上次访谈遗留问题的补访，然后提出待澄清清单里的第一个问题。"


def followup_system(agenda):
    """补访模式下追加到系统提示词的指令 + 待澄清清单。"""
    return ("\n\n【本次为补充访谈（补访），不是首访】不要从头重问，"
            "只围绕下面这份「待澄清问题清单」逐条追问澄清，每次聚焦 1~2 条，"
            "把模糊处追到可量化的具体数字；清单全部问完后做一个小结。\n"
            "待澄清问题清单：\n" + agenda)


def followup_for(target):
    """从补访问题清单 md 中取出某涉众那一节的问题文本（供前端自动载入）。"""
    if not FOLLOWUP_MD.exists():
        return ""
    text = FOLLOWUP_MD.read_text(encoding="utf-8")
    for sec in re.split(r'(?m)^## ', text):
        if not sec.strip():
            continue
        head = sec.splitlines()[0]
        if target in head and "附" not in head:
            return sec.split("\n", 1)[1].strip() if "\n" in sec else ""
    return ""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html = (HERE.parent / "index.html").read_text(encoding="utf-8")
            return self._send(200, html, "text/html; charset=utf-8")
        if self.path == "/api/agents":
            items = [{"key": k, "target": m.TARGET_STAKEHOLDER} for k, m in AGENTS.items()]
            return self._send(200, json.dumps(items, ensure_ascii=False))
        if self.path.startswith("/api/last"):
            qs = parse_qs(urlparse(self.path).query)
            key = (qs.get("agent") or [""])[0]
            kind = (qs.get("kind") or [""])[0]
            sess_key = f"{key}_补访" if kind == "补访" else key
            f = SESSIONS_DIR / f"{sess_key}.json"
            if key and f.exists():
                return self._send(200, f.read_text(encoding="utf-8"))
            return self._send(404, json.dumps({"error": "无法恢复：未找到上次保存的对话记录"}, ensure_ascii=False))
        if self.path.startswith("/api/followup"):
            qs = parse_qs(urlparse(self.path).query)
            agent = AGENTS.get((qs.get("agent") or [""])[0])
            if not agent:
                return self._send(400, json.dumps({"error": "unknown agent"}, ensure_ascii=False))
            agenda = followup_for(agent.TARGET_STAKEHOLDER)
            if agenda:
                return self._send(200, json.dumps(
                    {"target": agent.TARGET_STAKEHOLDER, "agenda": agenda}, ensure_ascii=False))
            return self._send(404, json.dumps(
                {"error": "未找到该涉众的补访问题（请确认 补访问题清单-v1.0.md 存在）"}, ensure_ascii=False))
        return self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        try:
            body = self._json_body()
            if self.path == "/api/chat":
                agent = AGENTS.get(body.get("agent"))
                if not agent:
                    return self._send(400, json.dumps({"error": "unknown agent"}, ensure_ascii=False))
                agenda = (body.get("agenda") or "").strip()   # 补访提纲（首访为空）
                sys_prompt = agent.system_prompt() + (followup_system(agenda) if agenda else "")
                raw_msgs = body.get("messages")
                if not raw_msgs:                               # 开场：补访用补访 kickoff
                    convo = [{"role": "user", "content": FOLLOWUP_KICKOFF if agenda else KICKOFF}]
                else:
                    convo = raw_msgs
                msgs = [{"role": "system", "content": sys_prompt}] + convo
                # 每轮 2048，截断则自动续写最多 6 轮 → 普通轮/整理需求都能完整输出
                max_tokens = int(body.get("max_tokens") or 2048)
                reply = llm_config.chat_complete(msgs, max_tokens=max_tokens)
                return self._send(200, json.dumps({"reply": reply}, ensure_ascii=False))
            if self.path == "/api/save":
                agent = AGENTS.get(body.get("agent"))
                target = (agent.TARGET_STAKEHOLDER if agent else body.get("target", "未知涉众"))
                kind = "补访" if body.get("kind") == "补访" else "首访"
                ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
                RAW_NOTES.mkdir(parents=True, exist_ok=True)
                suffix = "补访记录" if kind == "补访" else "需求记录"
                title = "补充访谈(补访)记录" if kind == "补访" else "需求获取记录"
                fn = RAW_NOTES / f"{target}-{ts}-{suffix}.md"
                header = (f"# {target} {title}\n\n- 涉众：{target}\n- 采访方：A1 需求获取智能体\n"
                          f"- 类型：{kind}\n- 时间：{ts}\n"
                          f"- 来源：A1 对话页面（己方扮涉众，涉众侧由教师 5000 平台 agent 简化代表）\n\n---\n\n")
                fn.write_text(header + body.get("transcript", ""), encoding="utf-8")
                # 同时写一份会话 JSON（供"恢复上次保存的对话"）；补访与首访分开存，互不覆盖
                key = body.get("agent") or target
                sess_key = f"{key}_补访" if kind == "补访" else key
                msgs = body.get("messages") or []
                if msgs:
                    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
                    (SESSIONS_DIR / f"{sess_key}.json").write_text(
                        json.dumps({"agent": key, "target": target, "kind": kind, "saved_at": ts, "messages": msgs}, ensure_ascii=False),
                        encoding="utf-8")
                return self._send(200, json.dumps({"path": str(fn), "kind": kind}, ensure_ascii=False))
            return self._send(404, json.dumps({"error": "not found"}))
        except Exception as e:
            return self._send(500, json.dumps({"error": repr(e)}, ensure_ascii=False))

    def log_message(self, *a):  # 静默
        pass


if __name__ == "__main__":
    port = 8000
    print(f"A1 对话页面后端启动：http://127.0.0.1:{port}  （Ctrl+C 退出）")
    print(f"模型 {llm_config.MODEL} | 需求记录写入 {RAW_NOTES}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

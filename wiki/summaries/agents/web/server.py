# -*- coding: utf-8 -*-
"""A1 需求获取对话页面 · 本地后端（零第三方依赖，仅用标准库 + 同级 llm_config）。

模型：己方(人)=涉众，对方=A1 需求获取 agent。密钥仅在服务端 .env，绝不下发前端。
启动：python server.py  → 浏览器开 http://127.0.0.1:8000
接口：
  GET  /              静态页面 index.html
  GET  /api/agents    返回 5 个 A1 agent 列表
  POST /api/chat      {agent, messages:[{role,content}]} → {reply}
  POST /api/save      {agent, target, transcript} → 写入 raw/notes/，返回 {path}
"""
import json
import sys
import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = Path(__file__).resolve()
AGENTS_DIR = HERE.parent.parent          # wiki/summaries/agents
PROJECT_ROOT = HERE.parents[3]           # D:\Project
RAW_NOTES = PROJECT_ROOT / "raw" / "notes"
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
        return self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        try:
            body = self._json_body()
            if self.path == "/api/chat":
                agent = AGENTS.get(body.get("agent"))
                if not agent:
                    return self._send(400, json.dumps({"error": "unknown agent"}, ensure_ascii=False))
                convo = body.get("messages") or [{"role": "user", "content": KICKOFF}]
                msgs = [{"role": "system", "content": agent.system_prompt()}] + convo
                reply = llm_config.chat(msgs, max_tokens=900)
                return self._send(200, json.dumps({"reply": reply}, ensure_ascii=False))
            if self.path == "/api/save":
                agent = AGENTS.get(body.get("agent"))
                target = (agent.TARGET_STAKEHOLDER if agent else body.get("target", "未知涉众"))
                ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
                RAW_NOTES.mkdir(parents=True, exist_ok=True)
                fn = RAW_NOTES / f"{target}-{ts}-需求记录.md"
                header = f"# {target} 需求获取记录\n\n- 涉众：{target}\n- 采访方：A1 需求获取智能体\n- 时间：{ts}\n- 来源：A1 对话页面（己方扮涉众，涉众侧由教师 5000 平台 agent 简化代表）\n\n---\n\n"
                fn.write_text(header + body.get("transcript", ""), encoding="utf-8")
                return self._send(200, json.dumps({"path": str(fn)}, ensure_ascii=False))
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

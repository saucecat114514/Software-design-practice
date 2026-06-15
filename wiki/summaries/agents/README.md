# agents/ —— A1 需求获取智能体（采访方）

5 个 A1 需求获取智能体 + 对话 Web 页面。**A1 是与涉众对话、挖掘需求的采访方，不是扮演涉众**（涉众侧由教师 5000 平台 agent 扮演）。设计说明见上级目录 [[涉众智能体设计-v2.0]]。

## 文件清单
| 文件 | 说明 |
|---|---|
| `llm_config.py` | 统一 DeepSeek LLM 配置（从根目录 `.env` 读密钥）。`chat()` 轻量调用 / `get_crew_llm()` 构建 CrewAI LLM |
| `prompt_kit.py` | 共享提示词：采访方框架 INTERVIEWER_FRAME + 访谈技巧 DIALOGUE_STRATEGY + 记录规范 OUTPUT_SPEC |
| `agent_course_consultant.py` | A1-1 访谈课程顾问 |
| `agent_academic_affairs.py` | A1-2 访谈教务老师 |
| `agent_finance.py` | A1-3 访谈财务人员 |
| `agent_principal.py` | A1-4 访谈校长 |
| `agent_sysadmin.py` | A1-5 访谈系统管理员 |
| `test_connection.py` | DeepSeek 连通性自检 |
| `web/server.py` | 对话页面本地后端（标准库，密钥服务端保管） |
| `web/index.html` | 对话页面前端（己方=涉众，对方=A1 agent） |

每个 agent 导出：`TARGET_STAKEHOLDER`、`ROLE`/`GOAL`/`BACKSTORY`、`PROBE_TOPICS`、`system_prompt()`、`build_agent()`。

## 运行

前置：根目录 `.env` 配好 `DEEPSEEK_API_KEY`（已 gitignore，不在仓库）。

```bash
# 1) 连通性自检
python test_connection.py

# 2) 启动对话页面（推荐用法）
python web/server.py          # 浏览器开 http://127.0.0.1:8000
#   选访谈涉众 → 开始/重新访谈（A1 先开场提问）→ 你以涉众身份作答 → 整理需求 → 保存到知识库

# 3) 轻量命令行调用某个 A1（无需 crewai）
python -c "import agent_finance as a; from llm_config import chat; \
print(chat([{'role':'system','content':a.system_prompt()},{'role':'user','content':'我是财务，平时主要对账和处理退费。'}]))"
```

标准 CrewAI 用法需 `pip install crewai`：`from agent_finance import build_agent; agent = build_agent()`。

> 依赖：`requests`、`python-dotenv`（已装）；`crewai`（可选，仅 `build_agent()` 需要）。

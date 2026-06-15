# agents/ —— 涉众 AI 智能体（A1）可运行配置

5 个涉众 CrewAI Agent 的定义文件。设计说明见上级目录 [[涉众智能体设计-v1.0]]。

## 文件清单
| 文件 | 说明 |
|---|---|
| `llm_config.py` | 统一 DeepSeek LLM 配置（从根目录 `.env` 读密钥）。`chat()` 轻量调用 / `get_crew_llm()` 构建 CrewAI LLM |
| `prompt_kit.py` | 共享提示词：身份隔离 + 对话策略 |
| `agent_course_consultant.py` | A1-1 课程顾问 |
| `agent_academic_affairs.py` | A1-2 教务老师 |
| `agent_finance.py` | A1-3 财务人员 |
| `agent_principal.py` | A1-4 校长 |
| `agent_sysadmin.py` | A1-5 系统管理员 |
| `test_connection.py` | DeepSeek 连通性自检 |

每个 agent 文件导出：`ROLE_NAME` / `ROLE` / `GOAL` / `BACKSTORY` / `FOCUS`、`system_prompt()`（轻量运行器用）、`build_agent()`（CrewAI 用）。

## 运行

前置：根目录 `.env` 配好 `DEEPSEEK_API_KEY`（已 gitignore，不在仓库）。

```bash
# 连通性自检
python test_connection.py

# 让某个涉众在角色内作答（轻量通道，无需 crewai）
python -c "import agent_course_consultant as a; from llm_config import chat; \
print(chat([{'role':'system','content':a.system_prompt()},{'role':'user','content':'作为课程顾问，请说明报名流程的核心需求。'}]))"
```

标准 CrewAI 用法需先 `pip install crewai`：
```python
from agent_finance import build_agent
agent = build_agent()      # 自动用 DeepSeek LLM
```

> 依赖：`requests`、`python-dotenv`（已装）；`crewai`（可选，仅 `build_agent()` 需要）。

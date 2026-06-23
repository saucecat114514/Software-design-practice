# 自动化工作流（n8n）

> 课程要求用 n8n 编排「需求开发全流程」工作流（含人工审批节点）。本目录为**本机等效落地**：可直接导入 n8n 的工作流 JSON + 说明。

## 工作流1 · 需求开发全流程

**文件**：[`n8n_工作流1_需求开发全流程.json`](n8n_工作流1_需求开发全流程.json)

### 流程编排（A1→A6 + CCB 人工审批 + 三处回退环）

```
手动触发(一键启动)
  → 初始化配置(项目/涉众/LLM)
  → A1 需求获取(5 涉众·采访方, 落 raw/notes)
  → A2 需求分析(四维质量检测)
  → IF 检出模糊/冲突？
       ├─是→ 回退补访 + A2 整合(A1↔涉众) ─┐   ← 回退环①(获取回退)
       └─否────────────────────────────────┤
  → A3 建模(用例图/活动图)  ←───────────────┘
  → A4 生成 SRS(IEEE 830)  ←──────────────┐
  → A5 交叉验证                            │
  → IF A5 验证通过？                        │
       ├─否→ 回退修订 SRS ─────────────────┘   ← 回退环②(验证回退)
       └─是→ CCB 人工审批(Webhook 暂停)
  → IF CCB 通过？
       ├─否→ (回退到 A2 需求分析)              ← 回退环③(审批回退)
       └─是→ A6 创立基线 + RTM
  → 归档基线 + 通知涉众(完成)
```

### 节点 ↔ 本项目智能体/脚本对照
| n8n 节点 | 类型 | 实际执行（本机等效） |
|---|---|---|
| 手动触发·一键启动 | Manual Trigger | n8n 界面点击「Execute Workflow」一键触发 |
| 初始化配置 | Set | 注入项目=EDU、5 涉众、LLM=deepseek-v4-pro |
| A1 需求获取 | Execute Command | `python wiki/summaries/agents/web/server.py`（对话页面采访教师 5000 平台 5 涉众 agent） |
| A2 需求分析 | Execute Command | `python wiki/summaries/agents/run_analysis.py` |
| 回退补访 + A2 整合 | Execute Command | `python wiki/summaries/agents/run_followup_integration.py` |
| A3 建模 | Execute Command | `python wiki/summaries/agents/run_modeling.py all` |
| A4 生成 SRS | Execute Command | `python wiki/summaries/agents/run_srs.py all` |
| A5 交叉验证 | Execute Command | `python wiki/summaries/agents/run_verification.py all` |
| 回退修订 SRS | Execute Command | `python wiki/summaries/agents/run_verification.py revise` |
| **CCB 人工审批** | **Wait（Webhook 恢复）** | **流程在此暂停，等待人工 POST 审批结果（approve/reject）恢复执行** |
| A6 创立基线 + RTM | Execute Command | `python wiki/summaries/agents/run_baseline.py` |
| 归档 + 通知 | NoOp | 基线归档 `wiki/baselines/`，通知涉众 |

### 三处反馈回退环（内嵌质量门）
- **回退环①（获取回退）**：A2 检出模糊/冲突 → 回退补访对应涉众、整合澄清，再进 A3。
- **回退环②（验证回退）**：A5 验证不通过 → 据验证报告修订 SRS（revise）后回 A4 重拼装。
- **回退环③（审批回退）**：CCB 审批退回 → 回到 A2 重新分析。

### 人工审批节点说明
- `CCB 人工审批` 用 n8n **Wait 节点（resume=webhook）** 实现：工作流执行到此**暂停**，n8n 给出一个恢复 URL；CCB（人工）评审后向该 URL POST `{"ccb_decision":"approve"}` 或 `{"ccb_decision":"reject"}`，工作流据此走「通过→A6」或「退回→A2」。
- 这正是课程要求的「含人工审批 Webhook 节点」。

### 导入与运行
1. n8n 中 `Workflows → Import from File`，选本 JSON。
2. 各 Execute Command 节点的工作目录设为项目根 `D:\Project`（命令中已用相对路径）。
3. 点击 `Execute Workflow` 一键触发；到 `CCB 人工审批` 节点会暂停，按上节 POST 审批结果恢复。
4. IF 节点的判定字段（`has_issue`/`verify_pass`/`ccb_decision`）为决策占位：实际接入时由上游节点输出或人工置值；当前 JSON 为可导入模板。

> 说明：IF 条件用占位字段表达「决策点」，便于演示回退环结构；真实运行可把各 agent 脚本的退出码/标准输出解析为判定值（如 A5 报告中"严重"问题数 > 0 则走回退）。

## 工作流2（需求变更全流程）
第 3-4 周（期末）实现：CR→影响分析(CIA)→建模/SRS 更新→基线比对(DIFF)→CCB→新基线，含人工审批节点。届时新增 `n8n_工作流2_需求变更全流程.json`。

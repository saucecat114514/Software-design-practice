# CCB 评审记录 · TLCD-EDU-V1 + OAS-EDU-V1 + 约束提示词（D13 约束与契约）

| 项 | 内容 |
|---|---|
| 评审对象 | [TLCD-EDU-V1 三层约束](constraint/TLCD_V1_教育培训收费系统_三层约束设计规范.md) + [OAS-EDU-V1 接口契约](oas/OAS_V1_教育培训收费系统_接口契约.yaml) + [接口清单](oas/接口清单-API-Inventory-v1.0.md) + [约束提示词](constraint/约束提示词-AI代码生成-v1.0.md) |
| 评审依据 | TLCD 规范、OAS 规范 + 全覆盖范围 + 使用指南、ADR-001~004、ASD/MDS/DTS、基线 BL-20260623-01 |
| 评审主体 | CCB（本项目由项目负责人代行） |
| 评审日期 | 2026-06-26 |
| 评审结论 | **通过**。TLCD-EDU-V1、OAS-EDU-V1、约束提示词置「正式生效」，纳入基线设计产物集 |

## 一、评审要点核对

| 核对项 | 结果 |
|---|---|
| TLCD 三层结构完整（C-ARCH/C-MOD/C-CODE） | ✔（12+12+14=38 条） |
| TLCD 每条 100% 溯源 ASD/ADR/MDS/DTS，无主观自定义 | ✔（各表「溯源」列） |
| TLCD 自上而下收敛、无上下层冲突、可机器校验（含漂移等级） | ✔ |
| OAS 基于 OpenAPI 3.0.3、10 大结构完整 | ✔（info/servers/tags/paths/components/parameters/responses/security/x-extension，YAML 解析通过） |
| OAS 每接口绑定 x-api-id/x-mod-id/x-rtm-id/x-tlcd-id | ✔（13 操作全覆盖） |
| OAS「全覆盖/零遗漏」 | ✔（接口清单登记 93 条 FR/IFR，绑定 MOD/RTM；核心主线 12 接口写完整字段级 YAML） |
| 契约不超模块职责、符合 DTS 拓扑 | ✔（path 模块标识与 MDS 对齐） |
| 约束提示词 固定前缀+变动后缀（缓存优化） | ✔（含 MOD-010 实例） |

## 二、评审意见与确认
1. **TLCD 确认**：三层逐条溯源、漂移分级量化（Blocker/Major/Minor）、合规线 Blocker=0/总漂移≤2，**确认**作为 D14 生成与 D15 RCR 校验依据。
2. **OAS 范围确认**：CCB 认可"台账全覆盖 + 核心主线完整 YAML"的务实范围——满足"凡有调用必有契约"的台账层零遗漏；核心主线（报名→收款→考勤课时→收入确认→**退费/转班**→发票 + 支付回调/通知）写字段级完整契约，足以驱动 D14 v1 代码与 D16~18 v2 变更；其余模块 YAML 体随对应模块开发补全（与 v1 代码为代表性切片一致），**如实声明、予以确认**。
3. **变更目标契约确认**：MOD-010 退费（FR-REF-001/003）、MOD-007 转班（FR-TRF-002）已写完整契约，含 DEF-001（均价口径+折价系数+快照冻结）、DEF-004（实际支付单价），为 D16 CR 埋好契约锚点，**确认**。
4. **约束提示词确认**：固定前缀（C-ARCH+C-CODE）/变动后缀（C-MOD+OAS）分离符合缓存优化策略，**确认**用于 D14。

## 三、状态变更决议
1. TLCD-EDU-V1：状态 **草稿 → 正式生效**。
2. OAS-EDU-V1：状态 **草稿 → 正式生效**（OAS 版本与 MDS/DTS/TLCD 强绑定）。
3. 约束提示词 v1.0：状态 **草稿 → 正式生效**。
4. 设计产物继续置 `wiki/summaries/design/` 工作层迭代；期末成套后整体冻结进新基线目录，需求基线 BL-20260623-01 保持不可变。

> 下游：进入 D14——Reasonix/AI 分层注入约束提示词，自底向上生成 v1 代码（infra→repo→service→controller），记录 /stats。

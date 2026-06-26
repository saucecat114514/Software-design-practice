# AI 代码生成约束提示词 v1.0（固定前缀 + 变动后缀）

> 用途：D14 用 AI（Reasonix/Claude）分层生成 v1 代码时注入的**约束提示词**。把 TLCD 三层约束 + MDS 边界 + DTS 白名单 + OAS 契约翻译成可直接喂给模型的负面约束 + 强制结构。
> 缓存策略（对齐作战计划 §11）：**固定前缀**（全局架构 C-ARCH + 代码规范 C-CODE，所有模块共用、措辞统一）放最前以最大化 KV 缓存命中（~62%→~76%）；**变动后缀**（单模块边界 C-MOD + 接口契约）放最后。每生成一个模块只替换后缀。
> 溯源：[TLCD-EDU-V1](TLCD_V1_教育培训收费系统_三层约束设计规范.md)、[MDS-EDU-V1](../module/MDS_V1_教育培训收费系统_模块划分方案.md)、[DTS-EDU-V1](../topology/DTS_V1_教育培训收费系统_模块依赖拓扑方案.md)、[OAS-EDU-V1](../oas/OAS_V1_教育培训收费系统_接口契约.yaml)。

---

## 一、固定前缀（全局，所有模块生成共用 · 逐字复用以命中缓存）

```text
你是本系统的 Java 后端代码生成器。技术栈 = Java 17 + Spring Boot + MyBatis。
你只能在我给定的架构、模块、契约约束内生成代码，禁止自由发挥。下面是全局硬约束，任何模块都必须遵守。

【架构层 C-ARCH（最高优先级，不可被任何下层突破）】
1. 唯一架构风格=四层分层：Controller → Service → Repository → Model，严格单向依赖。
2. 禁止反向依赖（下层引用上层）、禁止跨层穿透（如 Controller 直达 Repository/数据库）。
3. 业务逻辑只写在 Service；数据访问只写在 Repository；Controller 只做参数校验/路由/响应封装；Model 只承载数据。
4. 通信：进程内本地调用为主；弱一致跨域用领域事件；外部系统只经 common 基础模块（网关/第三方对接/通知）调用，禁止业务层直连外部 SDK。
5. 单体工程；禁止引入事件总线/服务注册中心/分布式事务协调器等改变主风格的框架。
6. 事务注解 @Transactional 只标在 Service 方法；禁止分布式强事务，跨域用最终一致+补偿。
7. 量化阈值（缓冲、折价系数、发票阈值、续费、请假率、RTO 等）一律经 @ConfigurationProperties 从配置注入，禁止硬编码魔数。

【代码层 C-CODE（工程与编码落地）】
8. 目录即层级：controller/ service(impl/)/ repository(mapper/)/ model(entity/ dto/ vo/)/ config/；common/ 放基础模块。
9. 包路径：com.edu.{域}.{模块}；基础模块 com.edu.common.{base}。
10. 命名：XxxController / XxxService(+XxxServiceImpl) / XxxRepository / 实体 Xxx(DO) / XxxDTO / XxxVO；方法动词开头小驼峰。
11. 数据表名 {域}_{实体}（如 fin_refund、crm_order、edu_attendance）；DTO/VO 与持久层 Entity/DO 分离，跨层用 DTO/VO。
12. 接口路径 /api/{模块标识}/v1/{资源}/{操作}；统一响应体 {code,message,data,timestamp}。
13. 统一异常：业务异常用 BizException + 错误码 "{域}-{编号}"，全局 @RestControllerAdvice 兜底；禁止吞异常、禁止抛裸 Exception。
14. 日志分级；高危/审计操作写不可篡改审计日志（操作人/时间/IP/模块/动作/改前改后值）；手机号、密码等敏感字段脱敏，禁止明文入日志。
15. 生成顺序自底向上：Model → Repository → Service → Controller。

【全局禁止清单（AI 红线，违反即废）】
- 禁止 Controller 调用 Repository 或直接操作数据库。
- 禁止 Service 拼裸 SQL（统一经 Repository/ORM）。
- 禁止跨业务域直接引用对方 Repository/Model（跨域只能调用对方 Service 接口）。
- 禁止基础模块反向依赖任何业务模块。
- 禁止任意模块间直接/间接循环依赖。
- 禁止读写非本模块归属的数据表。
- 禁止把业务逻辑写进 Controller、Repository 或基础模块。
- 禁止生成依赖白名单（见后缀）之外的模块调用。
```

---

## 二、变动后缀模板（每个模块替换以下占位后拼到固定前缀之后）

```text
【本次生成目标模块】
- 模块：{MOD-ID} {模块名称}（归属服务 {service}，包 com.edu.{域}.{模块}）
- 唯一职责：{responsibility}
- 可做(Include)：{includes}
- 禁做/不归属(Exclude)：{excludes}
- 归属数据表（仅可读写这些表）：{tables}

【模块层 C-MOD 边界（本模块强制）】
- 一表一归属：仅操作上面列出的归属表，禁止读写他模块表。
- 跨域协作只调用对方 Service 接口；涉及 {事件场景} 用领域事件解耦，不要同步硬调用。
- 允许依赖（白名单，DTS）：{依赖白名单 EDGE 列表，含方式}；全局基础（RBAC/缓存/日志审计）可依赖。
- 禁止依赖：白名单之外的一切模块；外部系统经基础模块适配。

【接口契约（OAS，必须严格按字段生成 Controller + DTO/VO）】
{逐接口：API-ID / 方法 / 路径 / 请求体schema / 响应体schema / 关键业务规则}

【需求与校验】
- 需求溯源：{FR/IFR 列表}
- 验收/业务规则：{从 SRS 验收标准摘录的关键规则，如阈值、状态机、口径}
```

---

## 三、变动后缀实例（MOD-010 退费管理，可直接用于 D14）

```text
【本次生成目标模块】
- 模块：MOD-010 退费管理（归属服务 finance-service，包 com.edu.finance.refund）
- 唯一职责：退费金额计算（固化消耗顺序+总课时均价）、分级审批、收入红冲、跨月消课调整
- 可做(Include)：退费明细计算；参数快照冻结；三级分级审批；收入红冲凭证
- 禁做/不归属(Exclude)：发票红冲开具（归 MOD-011）；转班退款发起（归 MOD-007）；审批引擎（归 MOD-104）
- 归属数据表（仅可读写这些表）：fin_refund、fin_refund_detail、fin_reverse_voucher

【模块层 C-MOD 边界（本模块强制）】
- 一表一归属：仅操作 fin_refund / fin_refund_detail / fin_reverse_voucher，禁止读写他模块表。
- 跨域协作只调用对方 Service：退费触发发票红冲校验 → 调 MOD-011 InvoiceService（本地调用）；
  退费驱动收入红冲调整 → 发领域事件 RefundApproved，由 MOD-012 收入确认订阅（事件解耦，不要同步硬调用）。
- 允许依赖（白名单 DTS）：MOD-010→MOD-104 审批流引擎(本地调用)、MOD-010→MOD-011 发票(本地调用)、
  MOD-010→MOD-012 收入确认(事件)；全局基础 MOD-105/106/108 可依赖。
- 禁止依赖：白名单之外一切模块。

【接口契约（OAS，严格按字段生成）】
- API-0046 POST /api/refund/v1/calc/create 退费金额计算：
  请求 RefundCalcReq{order_id, reason}；响应 RefundCalcVO{purchased_hours, gift_hours, consumed_hours,
  avg_unit_price, gift_discount_factor(默认1.0,配置注入), refund_amount, snapshot_id}。
  规则：先扣购买课时再扣赠送；均价=含赠送总课时均价；计算即冻结参数快照；存在已开票未红冲发票返回 409 阻断。
- API-0048 POST /api/refund/v1/approve/update 退费分级审批：
  请求 RefundApproveReq{refund_id, action, approver_id, comment}；响应 RefundApproveVO{refund_status,
  approval_level, auto_passed}。
  规则：小额(≤阈值)自动通过留异常标记；大额强制校长三级审批、auto_passed 恒 false、绝不自动放款；超时按规则抄送。

【需求与校验】
- 需求溯源：FR-REF-001、FR-REF-003、FR-REF-004（红冲）、FR-REF-005（跨月）
- 关键规则：退费金额口径与折价系数为 MOD-010 独占（C-MOD-0010）；阈值经配置注入（C-ARCH-0008）；
  审批分级与"大额绝不自动通过"来自 CCB 裁决；红冲凭证生成失败时退费单置"红冲失败-待处理"，不放款不变更课时。
```

---

## 四、使用说明（D14）
1. 每生成一个模块：固定前缀（第一节，逐字不变）+ 该模块变动后缀（按第二节模板填，或直接用 module-catalog.json + DTS + OAS 自动拼）。
2. 自底向上逐层生成，生成后用 C-CODE 红线自查；D15 用 CodeGraph 逆向比对 MDS/DTS/TLCD，输出 RCR 漂移（目标 Blocker=0、总漂移≤2）。
3. 变动后缀可由脚本从 module-catalog.json（边界/表）、dependency-topology.json（白名单）、OAS（接口）自动装配，保证与基线一致。

## 变更日志
- 2026-06-26：V1 初始创建（草稿），随 TLCD/OAS 提交 CCB 评审。
- 2026-06-26：CCB 评审通过，正式生效。

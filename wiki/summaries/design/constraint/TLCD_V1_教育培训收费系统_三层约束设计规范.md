# TLCD-EDU-V1：教育培训机构教务收费管理系统 · 三层约束设计规范

## 1 基础元数据

| 字段 | 值 |
|---|---|
| 文档编号 | TLCD-EDU-V1 |
| 文档状态 | 正式生效（CCB 2026-06-26 评审通过，见 [CCB 评审记录](../CCB_TLCD-OAS_评审记录-v1.0.md)） |
| 生效基线 | BL-20260623-01 |
| 前置依赖 | [ADR-001](../adr/ADR-001_系统顶层架构风格选型决策.md)、[ASD-EDU-V1](../style/ASD_V1_教育培训收费系统_分层架构风格声明.md)、[ADR-002/003/004](../adr/)、[MDS-EDU-V1](../module/MDS_V1_教育培训收费系统_模块划分方案.md)、[DTS-EDU-V1](../topology/DTS_V1_教育培训收费系统_模块依赖拓扑方案.md) |
| 下游输出 | OAS 接口契约、AI 代码生成约束提示词、CodeGraph 三级校验规则 |
| 责任人 | 架构设计（AI 全量执行）/ CCB 评审 |

> **三层定义**：架构层(C-ARCH)定基调 → 模块层(C-MOD)定边界 → 代码层(C-CODE)定写法。
> **核心原则**：自上而下收敛（下层不得突破上层）、层级唯一职责、100% 溯源（无源头约束禁止）、全量覆盖、可机器校验。
> 全部约束 100% 溯源已生效的 ADR/ASD/MDS/DTS，无主观自定义。

---

## 2 第一层：架构层约束 C-ARCH（顶层·全局强制，溯源 ASD/ADR）

| 约束ID | 溯源 | 约束内容 | 漂移判定（量化） | AI 生成约束 | 等级 |
|---|---|---|---|---|---|
| C-ARCH-0001 | ADR-001 / ASD §1 | 主架构风格唯一=四层分层；禁混合多主风格 | 出现事件驱动/微服务/CQRS 等第二主风格结构 | 只生成分层结构，不演化第二范式 | Blocker |
| C-ARCH-0002 | ASD §2.2/§3 | 层级单向 Controller→Service→Repository→Model；禁反向/跨层穿透 | 出现下层→上层引用或跨层穿透调用边 | 严格单向，禁穿透 | Blocker |
| C-ARCH-0003 | ASD §3.1 | 业务逻辑 100% 收敛 Service 层 | Controller/Repository 出现业务分支/规则计算 | 业务只写 Service | Major |
| C-ARCH-0004 | ASD §3.1 | 数据访问 100% 收敛 Repository 层 | Controller/Service 出现 SQL/JDBC/数据源操作 | DB 操作只写 Repository | Blocker |
| C-ARCH-0005 | ASD §2.3 / ADR-004 | 通信范式：进程内本地调用为主，弱一致跨域用领域事件，外部仅经基础模块 API | 跨域硬同步耦合成环 / 业务直连外部 SDK | 按范式分工生成 | Major |
| C-ARCH-0006 | ASD §4.3 | 技术栈红线：禁引入事件总线/服务注册中心/分布式事务协调器等改变主风格的框架 | 依赖清单出现禁用框架 | 不得引入禁用依赖 | Blocker |
| C-ARCH-0007 | ADR-001 | 单工程单体部署，禁服务级拆分 | 出现独立部署单元/服务注册 | 单体内模块化 | Blocker |
| C-ARCH-0008 | ASD §3.1.5 | CCB 8 项量化阈值经配置注入，禁硬编码 | 阈值魔数硬编码（缓冲/折价/发票阈值/续费/请假率/RTO 等） | 阈值从配置读取 | Major |
| C-ARCH-0009 | SRS §3.3 / NFR-PERF | 性能：报名/缴费/查名额 ≤3s，试听 P99≤3s（目标≤1s） | 关键路径设计无缓存/索引兜底致超标 | 热点读走缓存/索引 | Major |
| C-ARCH-0010 | SRS §3.3 / NFR-REL | 可靠性：灾备 RTO 30min/RPO≈5min；审计日志不可篡改；财务数据≥3 年留存 | 审计可删改 / 财务无留存策略 | 审计追加写+哈希链 | Blocker |
| C-ARCH-0011 | SRS §3.3 / NFR-SEC | 安全：RBAC×校区双维数据隔离；高危操作告警；备份加密；高危角色 2FA | 越权可见跨校区数据 / 高危无告警 | 数据范围过滤强制 | Blocker |
| C-ARCH-0012 | ASD §2.3 / ADR-004 | 事务边界仅 Service；禁分布式强事务，跨域用最终一致+补偿 | @Transactional 出现在非 Service 层 / 跨服务强事务 | 事务只标 Service | Major |

---

## 3 第二层：模块层约束 C-MOD（中层·边界与拓扑强制，溯源 MDS/DTS/ADR-002~004）

| 约束ID | 关联模块 | 溯源 | 约束内容 | 漂移判定 | AI 生成约束 | 等级 |
|---|---|---|---|---|---|---|
| C-MOD-0001 | 全部 | ADR-002 / MDS §3 | 模块集固定=21 业务+8 基础=29；禁计划外新增/碎片化 | 出现非 MOD 目录的能力代码 | 只在既有 MOD 内落地 | Major |
| C-MOD-0002 | 全部 | ADR-003 / MDS §4 | 职责唯一：一能力一模块，遵守各模块 Include/Exclude | 模块出现非本模块 Include 的业务 | 按黑白名单生成 | Major |
| C-MOD-0003 | 全部 | ADR-003 | 一表一归属：每表唯一主模块；禁跨模块读写他表 | 模块直接读/写非归属表 | 禁跨表越权 | Blocker |
| C-MOD-0004 | 全部 | ADR-004 / DTS §6 | 跨业务域仅 Service→Service；禁直连他模块 Repository/Model | 出现跨域 Repository/Model 引用 | 跨域只调对方 Service | Blocker |
| C-MOD-0005 | 全部 | DTS §4 | 依赖白名单：仅 34 条 EDGE + 全局基础矩阵(MOD-105/106/108)合法 | 出现白名单外依赖边 | 只生成白名单依赖 | Blocker |
| C-MOD-0006 | 业务模块 | ADR-004 / DTS §10 | 拓扑无环：业务模块禁直接/间接循环依赖 | 检出依赖环 | 不得成环 | Blocker |
| C-MOD-0007 | MOD-101~108 | DTS §2 | 基础模块单向被依赖，禁反向依赖任何业务模块 | 基础模块引用业务模块 | 基础不反依业务 | Blocker |
| C-MOD-0008 | MOD-008/012/009/011/010 | DTS §5 | 弱一致跨域用领域事件：课消→收入确认、收款→开票、退费→红冲 | 应事件处误用同步硬调用 | 按事件解耦生成 | Major |
| C-MOD-0009 | 业务模块 | DTS §5 | 外部系统仅经基础模块(网关/第三方对接/通知)适配，禁业务直连 SDK | 业务模块直连外部 SDK | 经基础适配层 | Major |
| C-MOD-0010 | MOD-010/012/014 | ADR-003 | 财务口径独占：退费/收入确认/工资口径由唯一归属模块独占 | 多模块各算财务口径 | 口径只在归属模块 | Blocker |
| C-MOD-0011 | MOD-016 | DTS §5 | BI 看板只读：禁写业务表，仅只读查询/视图取数 | BI 模块写业务表 | BI 只读 | Major |
| C-MOD-0012 | 全部 | MDS §6 | 工程目录映射：MOD-ID→固定包路径，代码按层级+模块双重收敛 | 模块代码跨目录散落 | 按映射表归位 | Major |

---

## 4 第三层：代码层约束 C-CODE（底层·工程与编码强制，承接 C-ARCH+C-MOD）

| 约束ID | 上层溯源 | 约束内容 | 禁止写法（AI 重点） | 漂移判定 | 等级 |
|---|---|---|---|---|---|
| C-CODE-0001 | C-ARCH-0002 / ASD §4.1 | 目录即层级：controller/ service/ repository/ model/（+config/ common/） | 文件放错层目录 | 层级目录错位 | Major |
| C-CODE-0002 | C-MOD-0012 | 包路径 com.edu.{域}.{模块}；基础 com.edu.common.{base} | 跨模块包散落 | 包路径不符 | Major |
| C-CODE-0003 | ASD §4.2 | 命名 XxxController/XxxService(+Impl)/XxxRepository/Xxx(DO)/XxxDTO/XxxVO | 后缀缺失/混名 | 命名不符 | Minor |
| C-CODE-0004 | ASD §4.2 / C-MOD-0003 | 表名 {域}_{实体}（crm_order/fin_refund/edu_attendance…） | 无前缀/驼峰/拼音表名 | 表名不符 | Minor |
| C-CODE-0005 | OAS §2.3 | 接口路径 /api/{模块}/{v1\|v2}/{资源}/{操作} | POST 做查询/GET 带复杂 Body | 路径/方法不符 | Major |
| C-CODE-0006 | C-ARCH-0002/0004 | Controller 仅校验/路由/封装；禁业务逻辑、禁直访 DB/Repository | Controller 调 Repository/DB | 跨层穿透 | Blocker |
| C-CODE-0007 | C-ARCH-0004 | Service 禁拼裸 SQL，统一经 Repository/ORM | Service 出现裸 SQL | 数据越层 | Blocker |
| C-CODE-0008 | ASD §3.1 | DTO/VO 与持久层 Entity/DO 分离，跨层用 DTO/VO | 持久实体直接当出参 | DTO/VO 未分离 | Major |
| C-CODE-0009 | ASD §4.4 | 统一异常 BizException + 错误码 `{域}-{编号}` + 全局 @RestControllerAdvice | 吞异常/抛裸 Exception | 异常不统一 | Major |
| C-CODE-0010 | ASD §4.4 / NFR-SEC | 日志分级；高危/审计操作写不可篡改审计日志；敏感字段脱敏 | 明文手机号/密码入日志 | 日志违规 | Major |
| C-CODE-0011 | C-ARCH-0012 | 事务注解 @Transactional 仅 Service 方法 | 事务标在 Controller/Repository | 事务越层 | Major |
| C-CODE-0012 | C-ARCH-0008 | 量化阈值经 @ConfigurationProperties/配置注入，禁魔数 | 阈值魔数硬编码 | 硬编码阈值 | Major |
| C-CODE-0013 | OAS §2.5 | 统一响应体 `{code,message,data,timestamp}` | 自定义返回体 | 响应不统一 | Major |
| C-CODE-0014 | ASD §5 | AI 生成顺序自底向上 Model→Repository→Service→Controller | 自顶向下/层级跳生成 | — | 提示 |

---

## 5 三层联动与闭环

- **层级穿透禁止**：下层约束兼容上层；冲突时**以上层为最高优先级**，自动否决下层违规。
- **溯源闭环**：每条 C-MOD/C-CODE 均向上溯源至唯一 C-ARCH/ADR/ASD/MDS/DTS 条款（见各表「溯源」列），无源头约束禁止。
- **全覆盖**：ASD 架构规则 + MDS 边界 + DTS 拓扑 + 工程/编码规范已全部纳入，无盲区。
- **校验对齐**：C-ARCH↔架构级漂移校验、C-MOD↔模块/拓扑漂移校验、C-CODE↔代码规范校验（D15 RCR 三级）。量化合规线：**Blocker=0、全系统总漂移≤2**。

## 6 迭代与版本规则
- 底层微调（仅 C-CODE）→ 小版本；中层调整（C-MOD 边界/拓扑）→ 同步 C-MOD+C-CODE；顶层重构（C-ARCH）→ 三层全升、旧版冻结。
- TLCD 版本与 ASD/MDS/DTS/OAS 基线一一对应、同迭代同生效；约束 ID 终身唯一、废弃保留不复用；变更走 ADR-005+ 闭环。

## 变更日志
- 2026-06-26：V1 初始创建（草稿），逐条溯源 ADR-001/ASD/ADR-002~004/MDS/DTS，提交 CCB 评审。
- 2026-06-26：CCB 评审通过，状态 草稿 → 正式生效。

# ASD-EDU-V1：教育培训机构教务收费管理系统 · 分层架构风格声明

## 元数据
- 声明编号：ASD-EDU-V1
- 文档名称：教育培训机构教务收费管理系统架构风格声明
- 主架构风格：**分层架构（Controller→Service→Repository→Model）**
- 辅助架构风格：无（缓存/消息/定时/审批为基础模块辅助手段，不构成主风格）
- 文档状态：正式生效（CCB 2026-06-26 评审通过，见 [CCB 评审记录](../CCB_ADR001-ASD_评审记录-v1.0.md)）
- 生效基线：BL-20260623-01
- 关联核心 ADR：[ADR-001](../adr/ADR-001_系统顶层架构风格选型决策.md)
- 更新日期：2026-06-26
- 编写人：架构设计（AI 全量执行）
- 评审人（CCB）：项目负责人代行

> 本声明是系统顶层架构约束的**唯一官方声明**，承接 ADR-001，向下衍生 MDS/DTS（D12）、TLCD/OAS（D13）、AI 代码生成（D14）、RCR 逆向校验（D15）。所有规则**可读取、可校验、可强制执行、可防漂移**。

---

## 1 架构风格选型依据

基于教材**五维度评估框架**（功能复杂度、并发性能、可扩展性、团队规模、运维能力）及两项工程维度（AI 代码生成适配性、落地成本），选定本系统主架构风格为 **Controller→Service→Repository→Model 四层分层架构**。完整加权打分见 [架构选型评估报告 v1.0](../架构选型评估报告-v1.0.md)（四层分层 4.82 / DDD 2.72 / 微服务 2.44），决策正式记录见 ADR-001。

逐维结论（锚定知识图谱 KG-EDU-V1）：
- **功能复杂度**：88 FR + 5 IFR 跨 37 组件 / 6 子系统，以事务型 CRUD+审批+对账为主，分层职责切分最契合；
- **并发性能**：约 100 并发 / 500 用户、关键路径 ≤3s，分层 + 缓存 + 索引即可满足，无需微服务弹性；
- **可扩展性**：多校区用数据隔离 + 配置满足，水平扩展诉求中等，分层 + 模块化即可；
- **团队规模**：1 人全量执行，分层认知负担最低；
- **运维能力**：单体部署、无 SRE，分层运维最简。
- 排除 DDD（事务型为主，过度设计、AI 适配差）、排除微服务（量级无隔离/弹性诉求，单人运维灾难）。

## 2 整体架构拓扑定义（机器可读）

### 2.1 整体架构结构
系统为**单工程单体**，纵向四层、横向按业务域分包：

- 纵向四层（自上而下，单向依赖）：
  1. **Controller（接入层）**：HTTP 入口、参数校验、鉴权、请求路由、响应封装。
  2. **Service（业务层）**：业务逻辑、事务边界、算价/审批/对账/收入确认等业务规则。
  3. **Repository（数据访问层）**：唯一数据出口，封装 DB CRUD（MyBatis/JPA）。
  4. **Model（模型层）**：Entity/DO/DTO/VO 数据载体，无行为。
- 横向业务域（包级划分，D12 MDS 细化）：招生客户(crm) / 教务(academic) / 财务(finance) / 经营BI(bi) / 系统管理(admin) / 综合横切(common)。
- 基础模块（被 Service 调用的横切关注点）：支付网关、第三方对接、缓存、定时任务、通知中心、审批流引擎、RBAC×校区、日志审计、校区组织隔离、系统参数配置。

### 2.2 依赖方向规则
- 纵向：**Controller → Service → Repository → Model，严格单向**；下层不得反向依赖上层；不得跨层穿透（如 Controller→Repository、Controller→DB）。
- 横向：业务域之间**禁止 Repository/Model 直接互访**；跨域协作只允许 **Service → 其它域 Service**（D12 起以依赖白名单收敛）。
- 基础模块：业务 Service 可依赖基础模块；**基础模块禁止反向依赖任何业务域**。

### 2.3 全局通信范式
- 进程内：**本地方法调用**（Spring Bean 注入）为唯一主通信方式。
- 外部集成：经基础模块封装的 **HTTP/SDK** 调用 5 个外部接口（支付渠道、电子发票、第三方财务、统一通知、家长小程序），契约由 OAS（D13）定义。
- 异步：通知/对账拉取/灾备演练等经定时任务或消息**局部异步**，不改变同步分层主范式。

## 3 分层/分域强制约束规则（核心）

### 3.1 强制规则（MUST）
1. 严格遵循 Controller→Service→Repository→Model 四层单向依赖。
2. 全部业务逻辑收敛至 **Service 层**；全部数据访问收敛至 **Repository 层**。
3. 代码按 `controller/ service/ repository/ model/`（及 `config/ common/`）分目录，**目录即层级**。
4. 事务边界（`@Transactional`）只声明在 **Service 层**。
5. CCB 8 项量化阈值（缓冲、折价系数、发票阈值、续费参数、请假率、RTO、审批分级、并发独占）一律经**配置模块注入**，禁止硬编码。
6. 对外暴露的 DTO/VO 与持久层 Entity/DO **分离**，跨层传输用 DTO/VO。

### 3.2 允许规则（MAY）
1. Controller 仅做参数校验、请求转发、响应封装、鉴权入口。
2. Service 可调用工具类、缓存、消息、定时任务、审批流引擎及**其它域 Service**。
3. Repository 仅操作数据源（DB/ORM）。
4. 富规则模块（退费计算、收入确认、对账勾稽）可在 Service 内拆充血领域服务/领域对象，但**仍属分层、不引入整体 DDD**。
5. 只读报表类查询可走专用 Repository 查询方法或视图，允许必要的读优化。

### 3.3 禁止规则（MUST NOT）
1. **禁止 Controller 直接访问数据库或调用 Repository**。
2. **禁止 Service 拼裸 SQL / 直接操作数据源**（统一经 Repository/ORM）。
3. **禁止跨层穿透**（任意层跳过相邻层调用非相邻层）。
4. **禁止下层反向调用上层**（Repository/Service 不得引用 Controller；Model 不得引用任何上层）。
5. **禁止跨业务域直接访问对方 Repository/Model**；跨域只能 Service→Service。
6. **禁止基础模块反向依赖业务域**。
7. **禁止层内/模块间循环依赖**。
8. 禁止在 Controller/Repository 写业务分支逻辑；禁止 Model 内写业务行为。

## 4 全局工程规范约束

### 4.1 目录结构规范
```
src/main/java/com/edu/{domain}/
  ├── controller/   # 接入层
  ├── service/      # 业务层（impl/ 放实现）
  ├── repository/   # 数据访问层（mapper/）
  ├── model/        # entity/ dto/ vo/
  └── config/       # 模块配置
com/edu/common/      # 基础模块：gateway/ integration/ cache/ schedule/ notify/ approval/ rbac/ audit/ org/ config
```
- `{domain}` ∈ {crm, academic, finance, bi, admin}；综合横切归 common。

### 4.2 命名规范
- 类名：`XxxController` / `XxxService`(+`XxxServiceImpl`) / `XxxRepository` / 实体 `Xxx`(DO)、`XxxDTO`、`XxxVO`。
- 方法名：动词开头小驼峰（`createOrder`、`calcRefund`、`reconcileDaily`）。
- 接口名：REST 资源式（`/api/{domain}/{resource}`），与 OAS（D13）一致。
- 数据表名：小写下划线、按域加前缀（`crm_lead`、`fin_refund_order`、`edu_attendance`）；一表一模块归属（ADR-003 固化）。

### 4.3 依赖规范
- 允许依赖：Spring Boot/MVC、MyBatis 或 Spring Data JPA、连接池、缓存客户端、JSON、校验、日志框架。
- 禁止依赖：任何引入第二主架构风格的框架（如全量事件总线、服务注册中心、分布式事务协调器）；业务层禁止直接依赖具体外部 SDK（须经基础模块封装）。

### 4.4 异常与日志规范
- 异常：全局统一异常处理器（`@RestControllerAdvice`）；业务异常用统一 `BizException` + 错误码（`{域}-{编号}`）；禁止吞异常、禁止向 Controller 抛裸 `Exception`。
- 日志：分级（ERROR/WARN/INFO/DEBUG）；高危/审计操作必记不可篡改审计日志（含操作人/时间/IP/模块/动作/改前改后值，对应 NFR-SEC-005/REL-001）；禁止日志输出敏感明文（手机号/密码脱敏）。

## 5 AI 代码生成专属约束（可直接导入提示词）

> 以下为「负面约束 + 强制结构」，供 D14 Reasonix/Claude 分层注入；与 ADR-001 §7 一致。

1. 你**只能**生成 Controller→Service→Repository→Model 四层结构代码，按目录归位，层级单向。
2. **禁止**：Controller 调 Repository/DB；Service 拼裸 SQL；跨层穿透；下层反向引用上层；跨域直访对方 Repository/Model；基础模块反向依赖业务；任何循环依赖。
3. 业务逻辑**只**写在 Service；数据访问**只**写在 Repository；Controller 只编排，Model 只承载数据。
4. 量化阈值**一律**从配置读取（注入 `@ConfigurationProperties`/配置中心），不得硬编码魔数。
5. 跨域协作**只**通过调用对方 `Service` 接口；外部系统**只**通过 `common` 基础模块封装调用。
6. 事务注解只加在 Service 方法；DTO/VO 与 Entity 分离。
7. 不得自行引入事件驱动、微服务、CQRS 等改变主风格的范式；缓存/消息/定时仅作辅助工具调用。
8. 生成顺序自底向上：Model → Repository → Service → Controller（便于逐层校验）。

## 6 架构漂移校验标准（对接 CodeGraph / D15 RCR，可量化可自动化）

| 校验项 | 判定规则（违规即记） | 等级 |
|---|---|---|
| 层级穿透 | 存在 Controller→Repository 或 任意层→非相邻下层 的调用边 | Blocker（必修） |
| 反向依赖 | 存在 下层→上层 的引用（Repository/Service→Controller、Model→任意上层） | Blocker（必修） |
| 数据访问越层 | Controller/Service 中出现直接 SQL/JDBC/数据源操作 | Blocker（必修） |
| 业务逻辑外溢 | Controller/Repository 中出现业务分支/规则计算 | Major（须改） |
| 跨域越界 | 业务域 A 直接引用域 B 的 Repository/Model（非 Service→Service） | Major（须改） |
| 基础模块反向依赖 | common 基础模块引用任一业务域 | Major（须改） |
| 循环依赖 | 类/包级存在依赖环 | Major（须改） |
| 命名/目录不规范 | 类名后缀或目录层级不符 §4 | Minor（可评审豁免） |
| 硬编码阈值 | CCB 8 项量化阈值出现魔数硬编码 | Major（须改） |

- 量化合规线（期末）：**Blocker = 0**，全系统总漂移 **≤ 2 处**（红线）。
- 校验方式：CodeGraph 构建逆向依赖图，与本 ASD/MDS/DTS 正向图比对，自动输出 RCR 漂移清单。

## 7 架构适用边界与取舍说明

### 7.1 架构优势与解决问题
- 解决 AI 自由生成导致的架构混杂、层次错乱、依赖无序；
- 提供职责清晰、可模式化复制、可自动化校验的事务型系统骨架；
- 单人 + 单体下落地与运维成本最低，把精力集中到业务正确性与变更闭环。

### 7.2 架构固有局限与取舍
- 分层链路固定，单点极致性能优化空间有限（以缓存/索引/读写分离弥补）；
- 单体在超大规模下伸缩有上限（当前 100 并发/500 用户量级无此问题）——取舍：**用"够用且可校验"换"过度弹性"**。

### 7.3 未来架构升级触发条件
- 某子系统并发/数据量跃升至单体无法支撑；
- 团队扩张到多团队并行需服务隔离；
- 引入与分层根本冲突的范式（如全面事件驱动）。
- 触发后须经 **ADR-005** 重新决策并新建 ASD 主版本，旧版标「迭代过期」归档。

## 8 迭代与版本升级规则
- **小版本（V1→V2）**：仅规则细化/约束补充，不改主风格——升级版本、记变更日志、旧版标「迭代过期」。
- **大版本（主风格切换）**：重走 ADR 选型决策、新建 ASD 主版本、完整重走 CCB 评审归档。
- 所有迭代必须同步更新关联的 TLCD 约束、CodeGraph 校验规则、基线版本与 AI 提示词。

## 变更日志
- 2026-06-26：V1 版本初始创建（状态：草稿），承接 ADR-001，提交 CCB 评审。
- 2026-06-26：CCB 评审通过，状态 草稿 → 正式生效，驱动 D12+ 设计与 AI 代码生成。

# v1 代码生成统计（/stats）· D14

> 工程：edu-charge-system v1.0.0　生成方式：AI 分层注入 [约束提示词](../../wiki/summaries/design/constraint/约束提示词-AI代码生成-v1.0.md)，自底向上 Model→Repository→Service→Controller。
> 生成日期：2026-06-26　构建：**Maven BUILD SUCCESS（41 源文件，javac release 17）**。

## 一、规模度量

| 指标 | 数值 |
|---|---|
| Java 源文件 | 41 |
| 代码行（LOC，含注释） | 1390 |
| HTTP 端点（@*Mapping） | 5 |
| Spring Bean（@Service/@Repository/@Component/@RestController） | 18 |

**按分层**：controller 4 / service 8（接口+实现）/ repository 4（接口+内存实现）/ model 13（entity/dto/vo/record）/ event 1 / listener 1 / config 1 / 其余 common（response/exception/notify/gateway）。
**按业务域包**：crm 5 / academic 9 / finance 17 / common 9。

## 二、实现范围（如实声明）

v1 为**以 v2 变更目标为核心的代表性纵切**，覆盖全部架构分层 + 约束 + 事件解耦，编译通过、可启动。

| 模块 | 端点/能力 | OAS 契约 | 状态 |
|---|---|---|---|
| MOD-010 退费（finance/refund）★ | API-0046 退费计算 + API-0048 分级审批 | OAS_V1 | **完整实现**（含 DEF-001 口径：含赠送均价+先购后赠+折价系数+快照冻结+大额绝不自动通过） |
| MOD-007 转班（academic/transfer）★ | API-0030 费用确认 | OAS_V1 | **完整实现**（含 DEF-004 口径：实际支付单价；EDGE-0023 跨域调退费） |
| MOD-012 收入确认（finance/revenue） | API-0052 确认 + 退费红冲事件监听 | OAS_V1 | **完整实现**（EDGE-0026 事件解耦） |
| MOD-003 报名订单（crm/order） | API-0009 优惠算价 | OAS_V1 | 代表性实现（互斥校验+触发审批） |
| MOD-101/103 基础模块 | 支付网关/通知中心 | IFR-PAY/MSG | 接口+桩（适配层模式） |
| 其余 17 业务模块 + 收款认领/对账/签到/发票/回调等端点 | — | 已登记 OAS 接口台账 | 台账登记、随开发补全（与 OAS v1 切片范围一致） |

> 端点实现 5 个；★退费/转班为 D16~18 需求变更（DEF-001/004）目标，故写完整业务逻辑以保证 v1→v2 diff 有意义。

## 三、约束遵循自查（对照 TLCD-EDU-V1）

| 约束 | 检查 | 结果 |
|---|---|---|
| C-ARCH-0002 层级单向/禁穿透 | Controller 直连 Repository 数 | **0** ✔ |
| C-ARCH-0004 数据访问收敛 Repository | Service/Controller 拼裸 SQL 数 | **0** ✔ |
| C-ARCH-0012 / C-CODE-0011 事务仅 Service | 非 service 层含 @Transactional 数 | **0** ✔ |
| C-ARCH-0008 / C-CODE-0012 阈值配置注入 | CCB 阈值经 ChargeProperties 注入，无硬编码魔数 | ✔（折价系数/发票阈值/退费分级阈值/缓冲均在 application.yml） |
| C-MOD-0004 跨域仅 Service→Service | 转班→退费经 RefundService 接口（非直连 Repository） | ✔（EDGE-0023） |
| C-MOD-0008 弱一致事件解耦 | 退费→收入红冲经领域事件 | ✔（EDGE-0026，发布/订阅） |
| C-CODE-0001/0002 目录即层级/包路径 | com.edu.{域}.{模块}.{controller/service/repository/model} | ✔ |
| C-CODE-0009 统一异常 + 错误码 | BizException + ErrorCode「{域}-{编号}」+ 全局处理器 | ✔ |
| C-CODE-0010 日志脱敏 | 通知手机号脱敏 | ✔ |
| C-CODE-0013 统一响应体 | ApiResponse{code,message,data,timestamp} | ✔ |

> 完整架构漂移校验（CodeGraph 三级）见 D15 RCR，本自查为生成侧预检。

## 四、构建与运行

```bash
cd code/edu-charge-system
mvn clean compile      # 已验证 BUILD SUCCESS
mvn spring-boot:run    # 启动（默认 8080；内存仓库，无需外部 DB）
```
> v1 用内存 Repository（ConcurrentHashMap）模拟持久层以便零依赖演示；真实实现为 MyBatis Mapper（边界/层级不变）。

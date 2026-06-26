# edu-charge-system · v1（教育培训机构教务收费管理系统）

AI 工程六步工作流第④步「AI 代码生成」的 v1 项目源代码。技术栈 **Java 17 + Spring Boot 3.2.5**，四层分层单体。

## 设计依据（全部可追溯）
- 架构：[ADR-001 四层分层](../../wiki/summaries/design/adr/ADR-001_系统顶层架构风格选型决策.md) + [ASD-EDU-V1](../../wiki/summaries/design/style/ASD_V1_教育培训收费系统_分层架构风格声明.md)
- 模块/拓扑：[MDS-EDU-V1](../../wiki/summaries/design/module/MDS_V1_教育培训收费系统_模块划分方案.md) + [DTS-EDU-V1](../../wiki/summaries/design/topology/DTS_V1_教育培训收费系统_模块依赖拓扑方案.md)
- 约束/契约：[TLCD-EDU-V1](../../wiki/summaries/design/constraint/TLCD_V1_教育培训收费系统_三层约束设计规范.md) + [OAS-EDU-V1](../../wiki/summaries/design/oas/OAS_V1_教育培训收费系统_接口契约.yaml)
- 生成方式：[约束提示词](../../wiki/summaries/design/constraint/约束提示词-AI代码生成-v1.0.md)（固定前缀+变动后缀）分层注入

## 工程结构（C-CODE-0001/0002：目录即层级，包 com.edu.{域}.{模块}）
```
com.edu
├── common/                 基础设施：response(统一响应)/exception(BizException+全局处理)/config(阈值注入)/notify/gateway
├── crm/order/              MOD-003 报名订单与优惠（算价）
├── academic/transfer/      MOD-007 转班 ★（实际支付单价口径）
└── finance/
    ├── refund/             MOD-010 退费 ★（含赠送均价口径 + 分级审批 + 退费事件）
    └── revenue/            MOD-012 收入确认（订阅退费事件做红冲）
每模块内：controller / service(impl) / repository / model(entity/dto/vo) / event / listener
```

## 构建与运行
```bash
mvn clean compile      # 已验证 BUILD SUCCESS（41 源文件）
mvn spring-boot:run    # 默认 8080；内存仓库，零外部依赖
```

## 实现范围与统计
见 [STATS.md](STATS.md)。v1 为以 ★退费/转班（D16~18 变更目标）为核心的代表性纵切，编译通过、覆盖全部分层与约束；其余模块在 OAS 接口台账登记、随开发补全。

## 约束遵循
全部遵循 TLCD 三层约束，生成侧自查零违规（详见 STATS.md §三）；完整架构漂移校验由 D15 CodeGraph 逆向校验（RCR）产出。

# OAS v1 → v2 契约差异（CR-EDU-2026-0001 / P4）

> 变更前：[OAS_V1](../oas/OAS_V1_教育培训收费系统_接口契约.yaml)（13 端点，正式生效，BL-20260623-01）。
> 变更后：[OAS_V2](../oas/OAS_V2_教育培训收费系统_接口契约.yaml)（16 端点，草稿，拟 BL-…-02）。
> 兼容性：**向前兼容**——已有路径/字段不变，仅新增端点与扩展字段。

## 一、元数据与全局
| 项 | v1 | v2 |
|---|---|---|
| version / x-oas-id | V1 / OAS-EDU-V1 | **V2 / OAS-EDU-V2**（关联 CR-EDU-2026-0001） |
| servers | 本地+测试+生产 | **收敛为本地单机**（资源 NFR 降级，CR-ITEM-002） |
| x-impl-mode | 无 | **全 16 端点新增**：real 14 / mock 2 |

## 二、新增端点（3 个，补核心闭环，CR-ITEM-005）
| API | 路径 | 模块 | 说明 |
|---|---|---|---|
| API-0019 | POST /api/class/v1/class/create | MOD-005 | 创建班级（含容量） |
| API-0016 | POST /api/schedule/v1/lesson/create | MOD-004 | 排课（三维冲突检测） |
| API-0031 | POST /api/consume/v1/record/create | MOD-008 | 课消采集（驱动收入确认） |

> 同步新增 tags：class / schedule / consume。

## 三、资源降级标记（CR-ITEM-001/002）
| 端点 | x-impl-mode | 说明 |
|---|---|---|
| 支付回调 API-0089 | **mock** | 本地 Mock 支付沙箱（验签固定通过） |
| 统一通知 API-0092 | **mock** | 本地 Mock 通知（控制台/日志，脱敏） |
| 其余 14 端点 | real | 本地真实可运行（H2 持久化） |

## 四、退费口径变更（CR-ITEM-003 / DEF-001）
- `RefundCalcVO` **新增字段** `refund_loss_rate`（退费折损率，按消耗进度分档）。
- `refundCalc` 描述更新为 v2 口径：含赠送均价 + 折价系数 **× (1 − 折损率)**；折损率分档 消耗≤30%→0% / ≤60%→10% / >60%→20%（配置注入）。

## 五、转班口径变更（CR-ITEM-004 / DEF-004）
- `transferFeeConfirm` 描述与 `TransferFeeVO.actual_unit_price` 口径更新：单价**随赠课模式**——carry=实付/(购买+赠送)含赠送；void=实付/购买不含赠送。

## 六、其它对齐
- `RefundApproveReq` 新增 `principal_approver`（大额三级须校长本人，与 v1 代码 DTO 对齐）。
- `LoginReq` 去 `otp`、`LoginVO.token` 示例改本地 demo token（简化鉴权，CR-ITEM-002）。
- `PriceCalcReq.required` 去掉 discount_codes 必填（优惠可空）。

## 七、未变（保证向前兼容）
全部已有路径、请求方法、已有字段名/类型、统一响应体 `{code,message,data,timestamp}`、错误码规则、安全方案 bearerAuth 均不变。

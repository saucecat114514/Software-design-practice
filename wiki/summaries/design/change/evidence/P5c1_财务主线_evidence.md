# P5c-1 运行证据 · 财务主线补全（登录/下单/收款回调/对账）

> 留痕：CR-EDU-2026-0001 / CR-ITEM-005。本地实跑，证明收费主线端到端可运行。

## 端到端实跑（数据落 H2）
| 步 | 接口 | 结果 |
|---|---|---|
| 1 登录 | POST /api/auth/v1/session/login | `0000`，token=demo-token-finance01，campus_scope=[C001,C002] |
| 2 下单 | POST /api/order/v1/order/create | `0000`，order_id=ORD-…，status=paying（落 crm_order） |
| 3 支付回调入账(Mock) | POST /api/payment/v1/callback | `0000`（落 fin_payment，验签 Mock 固定通过） |
| 4 对账列表 | GET /api/payment/v1/reconcile/list?settle_date=2026-06-25 | `0000`，返回 2 条流水(RCN-001 matched / RCN-002 unclaimed，读 fin_reconcile) |

接合既有：算价(MOD-003)、退费(MOD-010★)、转班(MOD-007★)、收入确认(MOD-012)。
**完整收费链路**：登录→算价→下单→缴费回调→对账→（退费/转班/收入确认）。

## 新增模块（四层 + MyBatis）
- MOD-105 鉴权(admin/auth)：AuthController/AuthService + LoginDTO/VO（简化 token 桩）
- MOD-003 订单(crm/order)：补 createOrder + Order/OrderRepository/OrderCreateDTO/OrderVO
- MOD-009 收款对账(finance/payment)：PaymentController/Service/Repository + Payment + claim/callback/reconcile DTO/VO
- 新表：crm_order、fin_payment、fin_reconcile（+ 对账种子）

## 回归校验
逆向校验（对标 OAS v2）：**55 类，违规 0（Blocker/Major/Minor 全 0），关键漂移 0**。
- 端点全部命中 OAS v2 契约；新模块无跨层穿透/越界/非法依赖；payment 不写 crm_order（边界 C-MOD-0003 守住）。

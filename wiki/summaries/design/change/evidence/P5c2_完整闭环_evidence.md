# P5c-2 运行证据 · 教务主线+发票（完整闭环端到端可运行）

> 留痕：CR-EDU-2026-0001 / CR-ITEM-005。本地实跑，证明**完整收费+教务闭环**端到端可运行。

## 完整端到端剧本（11 步全 `code:0000`）
| 步 | 接口 | 结果 |
|---|---|---|
| 1 登录 | /api/auth/v1/session/login | 0000 |
| 2 算价 | /api/order/v1/price/calc | 0000 |
| 3 下单 | /api/order/v1/order/create | 0000（落 crm_order） |
| 4 缴费回调(Mock) | /api/payment/v1/callback | 0000（落 fin_payment） |
| 5 开票(<5000自动) | /api/invoice/v1/issue/create | 0000（auto_issued，落 fin_invoice） |
| 6 建班 | /api/class/v1/class/create | 0000（落 edu_class） |
| 7 排课(冲突检测) | /api/schedule/v1/lesson/create | 0000（落 edu_schedule） |
| 8 签到扣课时 | /api/attendance/v1/checkin/create | 0000（扣 edu_course_hour_account） |
| 9 消课(发事件) | /api/consume/v1/record/create | 0000（CSM-…，落 edu_consume_record） |
| 10 退费(高消耗折损) | /api/refund/v1/calc/create | 0000（折损20%→3200） |
| 11 对账 | /api/payment/v1/reconcile/list | 0000（读 fin_reconcile 2 流水） |

## 事件解耦验证（EDGE-0022 课消→收入确认）
消课(步9)发布 `ConsumeConfirmedEvent` → 收入确认模块监听处理，日志确证：
```
c.e.f.r.service.impl.RevenueServiceImpl : 确认收入 record=CSM-1782737661557 month=2026-07
```
消费者只订阅事件类型、不依赖生产者 Service（DTS §2.6.1），事件解耦端到端跑通。

## 新增模块（P5c-2，四层+MyBatis）
- MOD-005 班级(academic/clazz)、MOD-004 排课(academic/schedule，三维冲突检测)
- MOD-006 考勤(academic/attendance，签到扣课时账户)、MOD-008 课消(academic/consume，发事件)
- MOD-011 发票(finance/invoice，阈值自动/待审)
- MOD-012 收入确认新增 ConsumeEventListener（订阅 EDGE-0022）
- 新表：edu_class/edu_schedule/edu_attendance/edu_course_hour_account/edu_consume_record/fin_invoice

## 回归校验
逆向校验（对标 OAS v2）：**87 类，10 业务模块全实现（MOD-003~012），15 端点，违规 0（Blocker/Major/Minor 全 0），关键漂移 0**。

# P5b 运行证据 · 口径变更★（DEF-001 退费折损 / DEF-004 转班单价）

> 留痕：CR-EDU-2026-0001 / CR-ITEM-003、004。本地实跑，证明退费/转班口径 v1→v2 确实变化。
> 对比锚点：git tag `v1-baseline`（f646a0f）。

## 一、退费口径（DEF-001：叠加消耗进度折损率分档）

| 订单 | 购买/赠送/已消耗 | 消耗占比 | 折损率 | **v2 退费额** | v1 退费额(无折损) |
|---|---|---|---|---|---|
| ORD-…-0012 | 100/20/25 | 21% ≤30% | 0% | **9500.00** | 9500.00（同） |
| ORD-…-0099 | 100/20/80 | 67% >60% | **20%** | **3200.00**（基础4000×0.8） | 4000.00（变） |

实跑响应（节选）：
```json
0099 → {"refund_loss_rate":0.2,"refund_amount":3200.00,...}
0012 → {"refund_loss_rate":0,"refund_amount":9500.00,...}
```

## 二、转班口径（DEF-004：单价随赠课模式）

| 模式 | 单价公式 | **v2 单价** | **v2 差价** | v1 单价(固定/购买) |
|---|---|---|---|---|
| void 作废 | 实付/购买 | **245.00** | 1100.00 | 245.00（同） |
| carry 结转 | 实付/(购买+赠送) | **196.00**(9800/50) | **2080.00** | 245.00（变） |

实跑响应（节选）：
```json
void  → {"actual_unit_price":245.00,"diff_amount":1100.00,...}
carry → {"actual_unit_price":196.00,"diff_amount":2080.00,...}
```

## 三、变更可见性（git diff v1-baseline）
```
+ ★v2 新增：按消耗进度折损率分档——消耗占比 ≤30%→0% / ≤60%→10% / >60%→20%（配置注入）
+ BigDecimal baseRefund = purchasedValue.add(giftValue);
+ BigDecimal lossRate = lossRateOf(consumedRatio);
+ BigDecimal refundAmount = baseRefund.multiply(BigDecimal.ONE.subtract(lossRate))...
```
RefundServiceImpl +32/-? 行、TransferServiceImpl 18 行变更，口径差异在 `git diff v1-baseline` 完整可见。

## 四、回归校验
口径变更后逆向校验：39 类，**违规 0（Blocker 0 / Major 0 / Minor 0），关键漂移 0**。

## 五、合规
- 折损分档阈值（0.30/0.60/0.10/0.20）全部配置注入（`edu.charge.refund-loss-*`），无硬编码（C-CODE-0016）。
- 退费旧单按冻结快照保留；新口径以新快照计算（向前兼容隔离，CIA §4.8）。

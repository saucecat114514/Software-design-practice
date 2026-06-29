-- 教育培训收费系统 v2 · H2 种子数据（P5a）
-- 退费/转班演示用读模型数据（v1 内存种子迁移至 H2）。

-- 退费订单快照A：购买100+赠送20，已消耗25(占比21%≤30%→折损0%)，实付12000，无未红冲发票
MERGE INTO fin_order_snapshot (order_id, purchased_hours, gift_hours, consumed_hours, paid_amount, has_unred_flushed_invoice)
VALUES ('ORD-20260301-0012', 100, 20, 25, 12000.00, FALSE);

-- 退费订单快照B：购买100+赠送20，已消耗80(占比67%>60%→折损20%)，实付12000——演示 v2 折损分档
MERGE INTO fin_order_snapshot (order_id, purchased_hours, gift_hours, consumed_hours, paid_amount, has_unred_flushed_invoice)
VALUES ('ORD-20260301-0099', 100, 20, 80, 12000.00, FALSE);

-- 转班原订单快照：购买40、已消耗20、赠送10、实付9800
MERGE INTO edu_transfer_snapshot (order_id, purchased_hours, consumed_hours, gift_hours, paid_amount)
VALUES ('ORD-20260601-0007', 40, 20, 10, 9800.00);

-- 转班目标班级应付价
MERGE INTO edu_transfer_target_price (target_class_id, target_amount)
VALUES ('CLS-A2', 6000.00);

-- P5c 对账演示流水（日终对账列表查询用）
MERGE INTO fin_reconcile (reconcile_id, settle_date, channel_txn_no, amount, match_status)
VALUES ('RCN-001', '2026-06-25', 'MOCK-TXN-001', 9800.00, 'matched');
MERGE INTO fin_reconcile (reconcile_id, settle_date, channel_txn_no, amount, match_status)
VALUES ('RCN-002', '2026-06-25', 'MOCK-TXN-002', 5000.00, 'unclaimed');

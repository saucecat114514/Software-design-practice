-- 教育培训收费系统 v2 · H2 建表（P5a 持久化底座）
-- 一表一归属（C-MOD-0003）；表名 {域}_{实体}（C-CODE-0004）。
-- P5a 先建退费/转班相关表，其余核心闭环表于 P5c 增补。

-- 退费（MOD-010 finance/refund）
DROP TABLE IF EXISTS fin_refund;
CREATE TABLE fin_refund (
  refund_id            VARCHAR(64) PRIMARY KEY,
  order_id             VARCHAR(64) NOT NULL,
  reason               VARCHAR(255),
  refund_amount        DECIMAL(14,2),
  gift_discount_factor DECIMAL(6,4),
  refund_loss_rate     DECIMAL(6,4),
  snapshot_id          VARCHAR(64),
  approval_level       VARCHAR(16),
  status               VARCHAR(32)
);

-- 退费读模型：订单财务快照（MOD-010 自有，经事件同步，不跨域直读订单表）
DROP TABLE IF EXISTS fin_order_snapshot;
CREATE TABLE fin_order_snapshot (
  order_id                  VARCHAR(64) PRIMARY KEY,
  purchased_hours           INT,
  gift_hours                INT,
  consumed_hours            INT,
  paid_amount               DECIMAL(14,2),
  has_unred_flushed_invoice BOOLEAN
);

-- 转班（MOD-007 academic/transfer）
DROP TABLE IF EXISTS edu_transfer;
CREATE TABLE edu_transfer (
  transfer_id     VARCHAR(64) PRIMARY KEY,
  order_id        VARCHAR(64) NOT NULL,
  target_class_id VARCHAR(64),
  diff_amount     DECIMAL(14,2),
  gift_voided     BOOLEAN,
  status          VARCHAR(32)
);

-- 转班读模型：原订单快照
DROP TABLE IF EXISTS edu_transfer_snapshot;
CREATE TABLE edu_transfer_snapshot (
  order_id        VARCHAR(64) PRIMARY KEY,
  purchased_hours INT,
  consumed_hours  INT,
  gift_hours      INT,
  paid_amount     DECIMAL(14,2)
);

-- 转班目标班级应付价
DROP TABLE IF EXISTS edu_transfer_target_price;
CREATE TABLE edu_transfer_target_price (
  target_class_id VARCHAR(64) PRIMARY KEY,
  target_amount   DECIMAL(14,2)
);

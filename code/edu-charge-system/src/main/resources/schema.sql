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

-- ===== P5c 财务主线 =====
-- 报名订单（MOD-003 crm/order）
DROP TABLE IF EXISTS crm_order;
CREATE TABLE crm_order (
  order_id       VARCHAR(64) PRIMARY KEY,
  customer_phone VARCHAR(32),
  course_id      VARCHAR(64),
  final_amount   DECIMAL(14,2),
  pay_channel    VARCHAR(16),
  status         VARCHAR(16)
);

-- 收款（MOD-009 finance/payment）
DROP TABLE IF EXISTS fin_payment;
CREATE TABLE fin_payment (
  payment_id     VARCHAR(64) PRIMARY KEY,
  order_id       VARCHAR(64),
  channel        VARCHAR(16),
  channel_txn_no VARCHAR(64),
  amount         DECIMAL(14,2),
  status         VARCHAR(16)
);

-- 对账（MOD-009 finance/payment）
DROP TABLE IF EXISTS fin_reconcile;
CREATE TABLE fin_reconcile (
  reconcile_id   VARCHAR(64) PRIMARY KEY,
  settle_date    VARCHAR(16),
  channel_txn_no VARCHAR(64),
  amount         DECIMAL(14,2),
  match_status   VARCHAR(24)
);

-- ===== P5c-2 教务主线 + 发票 =====
-- 班级（MOD-005 academic/clazz）
DROP TABLE IF EXISTS edu_class;
CREATE TABLE edu_class (
  class_id   VARCHAR(64) PRIMARY KEY,
  class_name VARCHAR(128),
  class_type VARCHAR(16),
  capacity   INT,
  enrolled   INT,
  campus_id  VARCHAR(32)
);

-- 排课（MOD-004 academic/schedule）
DROP TABLE IF EXISTS edu_schedule;
CREATE TABLE edu_schedule (
  lesson_id    VARCHAR(64) PRIMARY KEY,
  class_id     VARCHAR(64),
  teacher_id   VARCHAR(32),
  classroom_id VARCHAR(32),
  start_time   VARCHAR(32),
  end_time     VARCHAR(32)
);

-- 课时账户（MOD-006 academic/attendance）
DROP TABLE IF EXISTS edu_course_hour_account;
CREATE TABLE edu_course_hour_account (
  student_id      VARCHAR(32) PRIMARY KEY,
  total_hours     INT,
  remaining_hours INT
);

-- 考勤（MOD-006 academic/attendance）
DROP TABLE IF EXISTS edu_attendance;
CREATE TABLE edu_attendance (
  attendance_id VARCHAR(64) PRIMARY KEY,
  lesson_id     VARCHAR(64),
  student_id    VARCHAR(32),
  status        VARCHAR(24),
  hour_deducted INT
);

-- 课消（MOD-008 academic/consume）
DROP TABLE IF EXISTS edu_consume_record;
CREATE TABLE edu_consume_record (
  consume_id   VARCHAR(64) PRIMARY KEY,
  lesson_id    VARCHAR(64),
  student_id   VARCHAR(32),
  is_gift      BOOLEAN,
  signed_month VARCHAR(16)
);

-- 发票（MOD-011 finance/invoice）
DROP TABLE IF EXISTS fin_invoice;
CREATE TABLE fin_invoice (
  invoice_id  VARCHAR(64) PRIMARY KEY,
  order_id    VARCHAR(64),
  title       VARCHAR(128),
  amount      DECIMAL(14,2),
  status      VARCHAR(24),
  need_review BOOLEAN
);

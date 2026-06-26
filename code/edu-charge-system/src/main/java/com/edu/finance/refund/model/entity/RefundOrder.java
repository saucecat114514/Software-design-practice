package com.edu.finance.refund.model.entity;

import java.math.BigDecimal;

/**
 * 退费单实体（归属表 fin_refund，MOD-010 独占，C-MOD-0003）。
 * 状态：CALCULATED 已计算 / APPROVING 审批中 / APPROVED 已通过 / ABNORMAL_PASSED 超时异常通过 / REJECTED 已驳回。
 */
public class RefundOrder {

    private String refundId;
    private String orderId;
    private String reason;
    private BigDecimal refundAmount;
    private BigDecimal giftDiscountFactor;
    private String snapshotId;
    private String approvalLevel;
    private String status;

    public RefundOrder() {
    }

    public String getRefundId() {
        return refundId;
    }

    public void setRefundId(String refundId) {
        this.refundId = refundId;
    }

    public String getOrderId() {
        return orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public BigDecimal getRefundAmount() {
        return refundAmount;
    }

    public void setRefundAmount(BigDecimal refundAmount) {
        this.refundAmount = refundAmount;
    }

    public BigDecimal getGiftDiscountFactor() {
        return giftDiscountFactor;
    }

    public void setGiftDiscountFactor(BigDecimal giftDiscountFactor) {
        this.giftDiscountFactor = giftDiscountFactor;
    }

    public String getSnapshotId() {
        return snapshotId;
    }

    public void setSnapshotId(String snapshotId) {
        this.snapshotId = snapshotId;
    }

    public String getApprovalLevel() {
        return approvalLevel;
    }

    public void setApprovalLevel(String approvalLevel) {
        this.approvalLevel = approvalLevel;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}

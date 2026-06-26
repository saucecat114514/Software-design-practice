package com.edu.academic.transfer.model.entity;

import java.math.BigDecimal;

/**
 * 转班单实体（归属表 edu_transfer，MOD-007 独占，C-MOD-0003）。
 */
public class TransferOrder {

    private String transferId;
    private String orderId;
    private String targetClassId;
    private BigDecimal diffAmount;
    private boolean giftVoided;
    private String status;

    public String getTransferId() {
        return transferId;
    }

    public void setTransferId(String transferId) {
        this.transferId = transferId;
    }

    public String getOrderId() {
        return orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }

    public String getTargetClassId() {
        return targetClassId;
    }

    public void setTargetClassId(String targetClassId) {
        this.targetClassId = targetClassId;
    }

    public BigDecimal getDiffAmount() {
        return diffAmount;
    }

    public void setDiffAmount(BigDecimal diffAmount) {
        this.diffAmount = diffAmount;
    }

    public boolean isGiftVoided() {
        return giftVoided;
    }

    public void setGiftVoided(boolean giftVoided) {
        this.giftVoided = giftVoided;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}

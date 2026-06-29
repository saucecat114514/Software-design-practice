package com.edu.finance.invoice.model.entity;

import java.math.BigDecimal;

/** 发票实体（归属表 fin_invoice，MOD-011 独占）。 */
public class Invoice {

    private String invoiceId;
    private String orderId;
    private String title;
    private BigDecimal amount;
    private String status;
    private Boolean needReview;

    public String getInvoiceId() { return invoiceId; }
    public void setInvoiceId(String invoiceId) { this.invoiceId = invoiceId; }
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Boolean getNeedReview() { return needReview; }
    public void setNeedReview(Boolean needReview) { this.needReview = needReview; }
}

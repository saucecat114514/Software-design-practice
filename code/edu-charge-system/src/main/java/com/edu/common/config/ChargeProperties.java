package com.edu.common.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.math.BigDecimal;

/**
 * CCB 量化阈值统一配置注入（C-ARCH-0008 / C-CODE-0012）。
 * 所有阈值禁止硬编码，统一从 application.yml 的 edu.charge.* 注入。
 */
@ConfigurationProperties(prefix = "edu.charge")
public class ChargeProperties {

    /** 赠送课时退费折价系数，默认 1.0，范围 0~1（CON-CCB-002 / DEF-001）。 */
    private BigDecimal giftRefundDiscountFactor = BigDecimal.ONE;

    /** 发票自动开票审核阈值（元），默认 5000（CON-CCB-003）。 */
    private BigDecimal invoiceAutoThreshold = new BigDecimal("5000");

    /** 退费小额自动审批阈值（元）。 */
    private BigDecimal refundSmallAmountThreshold = new BigDecimal("5000");

    /** 退费大额强制校长审批阈值（元），达到即必须校长手动、绝不自动通过。 */
    private BigDecimal refundPrincipalThreshold = new BigDecimal("10000");

    /** 排课/试听占用缓冲（分钟），默认 5，范围 1~30（CON-CCB-001）。 */
    private int scheduleBufferMinutes = 5;

    /** 报名优惠合计触发特批审批的占比阈值，默认 0.25（业务规则，配置注入避免硬编码）。 */
    private BigDecimal orderApprovalRatio = new BigDecimal("0.25");

    // ===== v2 / DEF-001：退费按消耗进度折损率分档（配置注入，C-CODE-0016）=====
    /** 折损低档消耗占比阈值，默认 0.30（≤该值折损率为低档=0）。 */
    private BigDecimal refundLossLowThreshold = new BigDecimal("0.30");
    /** 折损高档消耗占比阈值，默认 0.60（≤该值中档、>该值高档）。 */
    private BigDecimal refundLossHighThreshold = new BigDecimal("0.60");
    /** 中档折损率，默认 0.10。 */
    private BigDecimal refundLossRateMid = new BigDecimal("0.10");
    /** 高档折损率，默认 0.20。 */
    private BigDecimal refundLossRateHigh = new BigDecimal("0.20");

    public BigDecimal getGiftRefundDiscountFactor() {
        return giftRefundDiscountFactor;
    }

    public void setGiftRefundDiscountFactor(BigDecimal giftRefundDiscountFactor) {
        this.giftRefundDiscountFactor = giftRefundDiscountFactor;
    }

    public BigDecimal getInvoiceAutoThreshold() {
        return invoiceAutoThreshold;
    }

    public void setInvoiceAutoThreshold(BigDecimal invoiceAutoThreshold) {
        this.invoiceAutoThreshold = invoiceAutoThreshold;
    }

    public BigDecimal getRefundSmallAmountThreshold() {
        return refundSmallAmountThreshold;
    }

    public void setRefundSmallAmountThreshold(BigDecimal refundSmallAmountThreshold) {
        this.refundSmallAmountThreshold = refundSmallAmountThreshold;
    }

    public BigDecimal getRefundPrincipalThreshold() {
        return refundPrincipalThreshold;
    }

    public void setRefundPrincipalThreshold(BigDecimal refundPrincipalThreshold) {
        this.refundPrincipalThreshold = refundPrincipalThreshold;
    }

    public int getScheduleBufferMinutes() {
        return scheduleBufferMinutes;
    }

    public void setScheduleBufferMinutes(int scheduleBufferMinutes) {
        this.scheduleBufferMinutes = scheduleBufferMinutes;
    }

    public BigDecimal getOrderApprovalRatio() {
        return orderApprovalRatio;
    }

    public void setOrderApprovalRatio(BigDecimal orderApprovalRatio) {
        this.orderApprovalRatio = orderApprovalRatio;
    }

    public BigDecimal getRefundLossLowThreshold() {
        return refundLossLowThreshold;
    }

    public void setRefundLossLowThreshold(BigDecimal refundLossLowThreshold) {
        this.refundLossLowThreshold = refundLossLowThreshold;
    }

    public BigDecimal getRefundLossHighThreshold() {
        return refundLossHighThreshold;
    }

    public void setRefundLossHighThreshold(BigDecimal refundLossHighThreshold) {
        this.refundLossHighThreshold = refundLossHighThreshold;
    }

    public BigDecimal getRefundLossRateMid() {
        return refundLossRateMid;
    }

    public void setRefundLossRateMid(BigDecimal refundLossRateMid) {
        this.refundLossRateMid = refundLossRateMid;
    }

    public BigDecimal getRefundLossRateHigh() {
        return refundLossRateHigh;
    }

    public void setRefundLossRateHigh(BigDecimal refundLossRateHigh) {
        this.refundLossRateHigh = refundLossRateHigh;
    }
}

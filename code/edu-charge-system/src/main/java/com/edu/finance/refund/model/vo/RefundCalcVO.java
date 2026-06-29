package com.edu.finance.refund.model.vo;

import java.math.BigDecimal;

/**
 * 退费明细单（OAS RefundCalcVO）。含赠送总课时均价口径 + 折价系数，参数快照冻结（DEF-001）。
 */
public record RefundCalcVO(
        int purchasedHours,
        int giftHours,
        int consumedHours,
        BigDecimal avgUnitPrice,
        BigDecimal giftDiscountFactor,
        BigDecimal refundLossRate,
        BigDecimal refundAmount,
        String snapshotId) {
}

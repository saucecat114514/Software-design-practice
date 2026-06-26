package com.edu.academic.transfer.model.vo;

import java.math.BigDecimal;

/**
 * 转班费用单（OAS TransferFeeVO）。差价按**实际支付单价**计算（DEF-004 口径，v2 变更目标）。
 *
 * @param diffAmount 差价（正=补款 / 负=退款）
 */
public record TransferFeeVO(
        BigDecimal actualUnitPrice,
        BigDecimal remainingValue,
        BigDecimal targetAmount,
        BigDecimal diffAmount,
        boolean giftVoided) {
}

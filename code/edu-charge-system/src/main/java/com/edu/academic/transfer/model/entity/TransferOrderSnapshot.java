package com.edu.academic.transfer.model.entity;

import java.math.BigDecimal;

/**
 * 转班所需订单快照（MOD-007 自有读模型，不跨域直读订单表，C-MOD-0004）。
 *
 * @param orderId        原订单号
 * @param purchasedHours 购买课时
 * @param consumedHours  已消耗课时
 * @param giftHours      赠送课时
 * @param paidAmount     实付金额（元）
 */
public record TransferOrderSnapshot(
        String orderId,
        int purchasedHours,
        int consumedHours,
        int giftHours,
        BigDecimal paidAmount) {
}

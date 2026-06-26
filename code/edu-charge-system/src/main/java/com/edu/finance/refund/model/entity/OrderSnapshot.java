package com.edu.finance.refund.model.entity;

import java.math.BigDecimal;

/**
 * 订单财务快照（退费模块 MOD-010 自有读模型）。
 * 退费计算所需的订单课时/金额数据，由报名/收款经事件同步进本模块读模型，
 * 退费**不跨域直读**订单/收款表（C-MOD-0003/0004）。
 *
 * @param orderId               订单号
 * @param purchasedHours        购买课时
 * @param giftHours             赠送课时
 * @param consumedHours         已消耗课时（先扣购买后扣赠送）
 * @param paidAmount            实付金额（元）
 * @param hasUnredFlushedInvoice 是否存在已开票未红冲发票
 */
public record OrderSnapshot(
        String orderId,
        int purchasedHours,
        int giftHours,
        int consumedHours,
        BigDecimal paidAmount,
        boolean hasUnredFlushedInvoice) {
}

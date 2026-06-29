package com.edu.finance.payment.model.vo;

import java.math.BigDecimal;

/** 对账记录（OAS ReconcileItem）。matchStatus：matched/unclaimed/pending_confirm/amount_mismatch/in_transit。 */
public record ReconcileVO(String reconcileId, String channelTxnNo, BigDecimal amount, String matchStatus) {
}

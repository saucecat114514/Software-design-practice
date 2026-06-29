package com.edu.finance.payment.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

/** 收款认领请求（OAS PaymentClaimReq / API-0035）。 */
public record PaymentClaimDTO(
        @NotBlank(message = "渠道流水号必填") String channelTxnNo,
        @NotBlank(message = "认领订单必填") String orderId,
        @NotNull(message = "金额必填") BigDecimal amount) {
}

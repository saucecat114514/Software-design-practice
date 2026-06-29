package com.edu.finance.payment.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

/** 支付渠道回调请求（OAS PayCallbackReq / API-0089，v2 Mock 沙箱）。 */
public record PayCallbackDTO(
        @NotBlank(message = "渠道必填") String channel,
        @NotBlank(message = "渠道流水号必填") String channelTxnNo,
        String outOrderId,
        @NotNull(message = "金额必填") BigDecimal amount,
        @NotBlank(message = "验签串必填") String sign) {
}

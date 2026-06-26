package com.edu.finance.refund.model.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * 退费计算请求（OAS RefundCalcReq / API-0046）。
 */
public record RefundCalcDTO(
        @NotBlank(message = "订单ID必填") String orderId,
        String reason) {
}

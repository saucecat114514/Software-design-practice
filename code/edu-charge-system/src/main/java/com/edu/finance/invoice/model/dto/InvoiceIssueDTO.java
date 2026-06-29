package com.edu.finance.invoice.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

/** 开票请求（OAS InvoiceIssueReq / API-0051）。 */
public record InvoiceIssueDTO(
        @NotBlank(message = "订单ID必填") String orderId,
        @NotBlank(message = "抬头必填") String title,
        @NotNull(message = "金额必填") BigDecimal amount,
        String taxNo) {
}

package com.edu.finance.revenue.model.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * 收入确认请求（OAS RevenueConfirmReq / API-0052）。
 *
 * @param isGift 是否赠课消耗（只计成本不计收入）
 */
public record RevenueConfirmDTO(
        @NotBlank(message = "课消记录ID必填") String consumeRecordId,
        String signedMonth,
        boolean isGift) {
}

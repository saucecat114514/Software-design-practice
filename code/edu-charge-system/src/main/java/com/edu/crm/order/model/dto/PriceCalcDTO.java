package com.edu.crm.order.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;
import java.util.List;

/**
 * 报名算价请求（OAS PriceCalcReq / API-0009）。
 */
public record PriceCalcDTO(
        @NotBlank(message = "客户手机号必填") String customerPhone,
        @NotBlank(message = "课程ID必填") String courseId,
        @NotNull(message = "原价必填") BigDecimal originalAmount,
        List<String> discountCodes,
        String referrerPhone) {
}

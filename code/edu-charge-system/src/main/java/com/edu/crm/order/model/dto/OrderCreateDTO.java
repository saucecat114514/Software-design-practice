package com.edu.crm.order.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

/** 创建订单请求（OAS OrderCreateReq / API-0013）。 */
public record OrderCreateDTO(
        @NotBlank(message = "客户手机号必填") String customerPhone,
        @NotBlank(message = "课程ID必填") String courseId,
        @NotNull(message = "应付金额必填") BigDecimal finalAmount,
        @NotBlank(message = "支付渠道必填") String payChannel) {
}

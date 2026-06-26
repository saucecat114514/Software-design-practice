package com.edu.academic.transfer.model.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * 转班费用确认请求（OAS TransferFeeReq / API-0030）。
 *
 * @param giftHandleMode void 赠课作废 / carry 赠课结转
 * @param refundRoute    balance 转余额 / original_route 原路退款（差价为负时）
 */
public record TransferFeeDTO(
        @NotBlank(message = "原订单ID必填") String orderId,
        @NotBlank(message = "目标班级ID必填") String targetClassId,
        @NotBlank(message = "赠课处理模式必填") String giftHandleMode,
        String refundRoute) {
}

package com.edu.finance.refund.model.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * 退费审批请求（OAS RefundApproveReq / API-0048）。
 *
 * @param action approve / reject
 * @param principalApprover 是否校长本人审批（大额三级必须 true）
 */
public record RefundApproveDTO(
        @NotBlank(message = "退费单ID必填") String refundId,
        @NotBlank(message = "审批动作必填") String action,
        String approverId,
        boolean principalApprover,
        String comment) {
}

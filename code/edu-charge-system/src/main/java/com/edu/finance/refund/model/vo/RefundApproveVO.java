package com.edu.finance.refund.model.vo;

/**
 * 退费审批结果（OAS RefundApproveVO）。
 *
 * @param refundStatus  APPROVED / ABNORMAL_PASSED / REJECTED / APPROVING
 * @param approvalLevel level1 / level2 / level3
 * @param autoPassed    是否超时异常通过（大额 level3 恒为 false）
 */
public record RefundApproveVO(
        String refundStatus,
        String approvalLevel,
        boolean autoPassed) {
}

package com.edu.crm.order.model.vo;

import java.math.BigDecimal;
import java.util.List;

/**
 * 报名算价结果（OAS PriceCalcVO）。
 */
public record PriceCalcVO(
        BigDecimal finalAmount,
        List<String> appliedDiscounts,
        boolean needApproval,
        String approvalReason) {
}

package com.edu.finance.revenue.service;

import com.edu.finance.revenue.model.dto.RevenueConfirmDTO;

import java.math.BigDecimal;

/**
 * 收入确认业务服务（MOD-012 Service 层，收入口径独占，C-MOD-0010）。
 */
public interface RevenueService {

    /** 按签到月确认收入；旷课不计、赠课只计成本（FR-REV-001）。 */
    void confirm(RevenueConfirmDTO dto);

    /** 退费驱动的收入红冲调整（由退费通过事件触发，DTS EDGE-0026）。 */
    void reverseForRefund(String refundId, String orderId, BigDecimal refundAmount);
}

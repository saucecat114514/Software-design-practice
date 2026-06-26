package com.edu.finance.refund.event;

import java.math.BigDecimal;

/**
 * 退费通过领域事件（DTS EDGE-0026：退费→收入红冲，弱一致**事件解耦**，C-MOD-0008）。
 * 退费模块只发布事件，收入确认模块（MOD-012）订阅处理红冲，不做同步硬调用。
 */
public record RefundApprovedEvent(String refundId, String orderId, BigDecimal refundAmount) {
}

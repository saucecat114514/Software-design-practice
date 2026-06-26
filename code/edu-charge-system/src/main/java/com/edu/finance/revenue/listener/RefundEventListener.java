package com.edu.finance.revenue.listener;

import com.edu.finance.refund.event.RefundApprovedEvent;
import com.edu.finance.revenue.service.RevenueService;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

/**
 * 退费通过事件监听（MOD-012 订阅 MOD-010 的领域事件，DTS EDGE-0026 弱一致解耦）。
 * 消费者只订阅事件类型，不强依赖生产者 Service（DTS §2.6.1）。
 */
@Component
public class RefundEventListener {

    private final RevenueService revenueService;

    public RefundEventListener(RevenueService revenueService) {
        this.revenueService = revenueService;
    }

    @EventListener
    public void onRefundApproved(RefundApprovedEvent event) {
        revenueService.reverseForRefund(event.refundId(), event.orderId(), event.refundAmount());
    }
}

package com.edu.finance.revenue.listener;

import com.edu.academic.consume.event.ConsumeConfirmedEvent;
import com.edu.finance.revenue.model.dto.RevenueConfirmDTO;
import com.edu.finance.revenue.service.RevenueService;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

/**
 * 课消事件监听（MOD-012 订阅 MOD-008 的领域事件，DTS EDGE-0022 弱一致解耦）。
 * 消费者只订阅事件类型，不强依赖生产者 Service（DTS §2.6.1）。
 */
@Component
public class ConsumeEventListener {

    private final RevenueService revenueService;

    public ConsumeEventListener(RevenueService revenueService) {
        this.revenueService = revenueService;
    }

    @EventListener
    public void onConsumeConfirmed(ConsumeConfirmedEvent event) {
        revenueService.confirm(new RevenueConfirmDTO(event.consumeId(), event.signedMonth(), event.gift()));
    }
}

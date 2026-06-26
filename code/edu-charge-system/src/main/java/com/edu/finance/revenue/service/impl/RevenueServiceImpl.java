package com.edu.finance.revenue.service.impl;

import com.edu.finance.revenue.model.dto.RevenueConfirmDTO;
import com.edu.finance.revenue.service.RevenueService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

/**
 * 收入确认实现（MOD-012）。v1 以日志记录确认/红冲，真实落 fin_revenue_recognition 表。
 */
@Service
public class RevenueServiceImpl implements RevenueService {

    private static final Logger log = LoggerFactory.getLogger(RevenueServiceImpl.class);

    @Override
    @Transactional
    public void confirm(RevenueConfirmDTO dto) {
        if (dto.isGift()) {
            // 赠课消耗：只计成本不计收入（FR-REV-001）
            log.info("赠课消耗只记成本不计收入 record={} month={}", dto.consumeRecordId(), dto.signedMonth());
            return;
        }
        log.info("确认收入 record={} month={}", dto.consumeRecordId(), dto.signedMonth());
    }

    @Override
    @Transactional
    public void reverseForRefund(String refundId, String orderId, BigDecimal refundAmount) {
        // 退费通过 → 生成收入红冲（事件驱动，弱一致）
        log.info("收入红冲 refundId={} orderId={} amount={}", refundId, orderId, refundAmount);
    }
}

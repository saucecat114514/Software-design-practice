package com.edu.common.gateway;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

/**
 * 支付网关 Mock 适配器（基础模块 MOD-101 / CR-ITEM-001 资源降级）。
 * v2 本地沙箱：验签固定通过、查单固定成功；真实接微信/支付宝/银行时按变更流程升级（ADR-005）。
 */
@Component
public class PaymentGatewayClientImpl implements PaymentGatewayClient {

    private static final Logger log = LoggerFactory.getLogger(PaymentGatewayClientImpl.class);

    @Override
    public boolean verifySign(String channel, String payload, String sign) {
        log.info("[Mock网关] 验签 channel={} sign={} -> 通过", channel, sign);
        return true;
    }

    @Override
    public boolean querySuccess(String channel, String channelTxnNo, BigDecimal amount) {
        log.info("[Mock网关] 主动查单 channel={} txn={} amount={} -> 成功", channel, channelTxnNo, amount);
        return true;
    }
}

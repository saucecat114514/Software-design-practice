package com.edu.common.gateway;

import java.math.BigDecimal;

/**
 * 支付网关（基础模块 MOD-101 / IFR-PAY-001）。
 * 封装渠道下单、回调验签、主动查单；业务模块经此适配，禁止直连渠道 SDK（C-MOD-0009）。
 */
public interface PaymentGatewayClient {

    /** 回调验签。 */
    boolean verifySign(String channel, String payload, String sign);

    /** 主动查单兜底，返回是否支付成功。 */
    boolean querySuccess(String channel, String channelTxnNo, BigDecimal amount);
}

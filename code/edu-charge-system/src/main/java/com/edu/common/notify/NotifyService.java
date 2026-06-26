package com.edu.common.notify;

import java.util.Map;

/**
 * 统一通知中心（基础模块 MOD-103 / IFR-MSG-001）。
 * 业务模块经本基础能力下发通知，禁止业务模块直连外部短信/小程序 SDK（C-MOD-0009）。
 */
public interface NotifyService {

    /**
     * 发送通知。
     *
     * @param channel      通道：app / sms / miniprogram
     * @param templateCode 模板编码
     * @param receiver     接收人（手机号或用户ID）
     * @param params       模板变量
     */
    void send(String channel, String templateCode, String receiver, Map<String, String> params);
}

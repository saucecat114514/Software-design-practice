package com.edu.common.notify;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * 通知中心实现（MOD-103）。v1 以日志桩模拟下发，真实通道经第三方对接基础模块（MOD-102）适配。
 * 注意：日志中手机号等敏感字段需脱敏（C-CODE-0010）。
 */
@Service
public class NotifyServiceImpl implements NotifyService {

    private static final Logger log = LoggerFactory.getLogger(NotifyServiceImpl.class);

    @Override
    public void send(String channel, String templateCode, String receiver, Map<String, String> params) {
        log.info("通知下发 channel={} template={} receiver={} params={}",
                channel, templateCode, mask(receiver), params);
    }

    /** 手机号脱敏（C-CODE-0010）。 */
    private String mask(String receiver) {
        if (receiver == null || receiver.length() < 7) {
            return "***";
        }
        return receiver.substring(0, 3) + "****" + receiver.substring(receiver.length() - 4);
    }
}

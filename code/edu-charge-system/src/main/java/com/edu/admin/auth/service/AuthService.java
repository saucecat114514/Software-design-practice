package com.edu.admin.auth.service;

import com.edu.admin.auth.model.dto.LoginDTO;
import com.edu.admin.auth.model.vo.LoginVO;
import com.edu.common.exception.BizException;
import com.edu.common.exception.ErrorCode;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 鉴权服务（MOD-105 RBAC，admin 域）。
 * v2 为本地简化 token（演示 RBAC 数据范围，不接真 2FA，x-impl-mode: real 简化）。
 */
@Service
public class AuthService {

    /** 登录：校验密码非空，返回简化令牌与数据范围。 */
    public LoginVO login(LoginDTO dto) {
        if (dto.password() == null || dto.password().isBlank()) {
            throw new BizException(ErrorCode.UNAUTHORIZED, "密码不能为空");
        }
        String userId = "U-" + dto.account();
        return new LoginVO("demo-token-" + dto.account(), userId, List.of("C001", "C002"));
    }
}

package com.edu.admin.auth.controller;

import com.edu.admin.auth.model.dto.LoginDTO;
import com.edu.admin.auth.model.vo.LoginVO;
import com.edu.admin.auth.service.AuthService;
import com.edu.common.response.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 鉴权接入层（MOD-105）。契约：OAS API-0000。 */
@RestController
@RequestMapping("/api/auth/v1")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /** API-0000 用户登录。 */
    @PostMapping("/session/login")
    public ApiResponse<LoginVO> login(@Valid @RequestBody LoginDTO dto) {
        return ApiResponse.ok(authService.login(dto));
    }
}

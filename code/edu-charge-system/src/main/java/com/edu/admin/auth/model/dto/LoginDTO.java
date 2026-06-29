package com.edu.admin.auth.model.dto;

import jakarta.validation.constraints.NotBlank;

/** 登录请求（OAS LoginReq / API-0000）。 */
public record LoginDTO(
        @NotBlank(message = "账号必填") String account,
        @NotBlank(message = "密码必填") String password) {
}

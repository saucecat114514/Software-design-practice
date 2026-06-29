package com.edu.admin.auth.model.vo;

import java.util.List;

/** 登录结果（OAS LoginVO）。campusScope=数据范围（可见校区）。 */
public record LoginVO(String token, String userId, List<String> campusScope) {
}

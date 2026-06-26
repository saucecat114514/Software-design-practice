package com.edu.common.response;

import java.time.OffsetDateTime;

/**
 * 全局统一响应体（C-CODE-0013 / OAS §2.5）：{code, message, data, timestamp}。
 * 禁止各接口自定义返回结构。
 */
public class ApiResponse<T> {

    private String code;
    private String message;
    private T data;
    private String timestamp;

    public ApiResponse() {
    }

    public ApiResponse(String code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.timestamp = OffsetDateTime.now().toString();
    }

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>("0000", "成功", data);
    }

    public static <T> ApiResponse<T> ok() {
        return new ApiResponse<>("0000", "成功", null);
    }

    public static <T> ApiResponse<T> fail(String code, String message) {
        return new ApiResponse<>(code, message, null);
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}

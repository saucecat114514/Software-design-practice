package com.edu.common.exception;

/**
 * 统一业务异常（C-CODE-0009）：携带错误码，禁止吞异常 / 抛裸 Exception。
 */
public class BizException extends RuntimeException {

    private final String code;

    public BizException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.code = errorCode.getCode();
    }

    public BizException(ErrorCode errorCode, String detail) {
        super(detail);
        this.code = errorCode.getCode();
    }

    public String getCode() {
        return code;
    }
}

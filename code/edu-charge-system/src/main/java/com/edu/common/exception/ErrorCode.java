package com.edu.common.exception;

/**
 * 全局错误码（C-CODE-0009 / OAS §4.5）：系统级 + 模块级 + 场景码，格式 "{域}-{编号}"。
 */
public enum ErrorCode {

    SUCCESS("0000", "成功"),

    // 系统级
    PARAM_ERROR("SYS-0400", "参数错误"),
    UNAUTHORIZED("SYS-0401", "未认证或令牌失效"),
    FORBIDDEN("SYS-0403", "无权限"),
    SERVER_ERROR("SYS-0500", "服务器内部错误"),

    // 退费（finance/refund，MOD-010）
    REFUND_INVOICE_BLOCK("FIN-1001", "存在已开票未红冲发票，退费被阻断"),
    REFUND_SNAPSHOT_REQUIRED("FIN-1002", "退费审批前必须先计算并冻结参数快照"),
    REFUND_PRINCIPAL_REQUIRED("FIN-1003", "大额退费必须校长手动审批，不可自动通过"),

    // 转班（academic/transfer，MOD-007）
    TRANSFER_TARGET_INVALID("EDU-2001", "目标班级不存在或不可转入"),

    // 报名（crm/order，MOD-003）
    ORDER_DISCOUNT_CONFLICT("CRM-3001", "存在互斥优惠，无法同时使用");

    private final String code;
    private final String message;

    ErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}

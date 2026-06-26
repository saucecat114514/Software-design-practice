package com.edu.finance.refund.controller;

import com.edu.common.response.ApiResponse;
import com.edu.finance.refund.model.dto.RefundApproveDTO;
import com.edu.finance.refund.model.dto.RefundCalcDTO;
import com.edu.finance.refund.model.vo.RefundApproveVO;
import com.edu.finance.refund.model.vo.RefundCalcVO;
import com.edu.finance.refund.service.RefundService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 退费接入层（MOD-010 Controller）。仅做参数校验/路由/响应封装，禁业务逻辑（C-ARCH-0002）。
 * 契约：OAS API-0046 / API-0048。
 */
@RestController
@RequestMapping("/api/refund/v1")
public class RefundController {

    private final RefundService refundService;

    public RefundController(RefundService refundService) {
        this.refundService = refundService;
    }

    /** API-0046 退费金额计算。 */
    @PostMapping("/calc/create")
    public ApiResponse<RefundCalcVO> calc(@Valid @RequestBody RefundCalcDTO dto) {
        return ApiResponse.ok(refundService.calc(dto));
    }

    /** API-0048 退费分级审批。 */
    @PostMapping("/approve/update")
    public ApiResponse<RefundApproveVO> approve(@Valid @RequestBody RefundApproveDTO dto) {
        return ApiResponse.ok(refundService.approve(dto));
    }
}

package com.edu.finance.payment.controller;

import com.edu.common.response.ApiResponse;
import com.edu.common.response.PageResult;
import com.edu.finance.payment.model.dto.PayCallbackDTO;
import com.edu.finance.payment.model.dto.PaymentClaimDTO;
import com.edu.finance.payment.model.vo.PaymentClaimVO;
import com.edu.finance.payment.model.vo.ReconcileVO;
import com.edu.finance.payment.service.PaymentService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** 收款与对账接入层（MOD-009）。契约：OAS API-0035/0042/0089。 */
@RestController
@RequestMapping("/api/payment/v1")
public class PaymentController {

    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    /** API-0035 收款认领。 */
    @PostMapping("/claim/create")
    public ApiResponse<PaymentClaimVO> claim(@Valid @RequestBody PaymentClaimDTO dto) {
        return ApiResponse.ok(paymentService.claim(dto));
    }

    /** API-0089 支付渠道回调（Mock）。 */
    @PostMapping("/callback")
    public ApiResponse<Void> callback(@Valid @RequestBody PayCallbackDTO dto) {
        paymentService.callback(dto);
        return ApiResponse.ok();
    }

    /** API-0042 对账结果查询。 */
    @GetMapping("/reconcile/list")
    public ApiResponse<PageResult<ReconcileVO>> reconcileList(
            @RequestParam("settle_date") String settleDate,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "size", defaultValue = "10") int size) {
        return ApiResponse.ok(paymentService.reconcileList(settleDate, page, size));
    }
}

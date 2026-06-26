package com.edu.academic.transfer.controller;

import com.edu.academic.transfer.model.dto.TransferFeeDTO;
import com.edu.academic.transfer.model.vo.TransferFeeVO;
import com.edu.academic.transfer.service.TransferService;
import com.edu.common.response.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 转班接入层（MOD-007 Controller）。仅校验/路由/封装（C-ARCH-0002）。契约：OAS API-0030。
 */
@RestController
@RequestMapping("/api/transfer/v1")
public class TransferController {

    private final TransferService transferService;

    public TransferController(TransferService transferService) {
        this.transferService = transferService;
    }

    /** API-0030 转班费用确认。 */
    @PostMapping("/fee/confirm")
    public ApiResponse<TransferFeeVO> confirmFee(@Valid @RequestBody TransferFeeDTO dto) {
        return ApiResponse.ok(transferService.confirmFee(dto));
    }
}

package com.edu.finance.revenue.controller;

import com.edu.common.response.ApiResponse;
import com.edu.finance.revenue.model.dto.RevenueConfirmDTO;
import com.edu.finance.revenue.service.RevenueService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 收入确认接入层（MOD-012 Controller）。契约：OAS API-0052。
 */
@RestController
@RequestMapping("/api/revenue/v1")
public class RevenueController {

    private final RevenueService revenueService;

    public RevenueController(RevenueService revenueService) {
        this.revenueService = revenueService;
    }

    /** API-0052 收入确认。 */
    @PostMapping("/confirm/create")
    public ApiResponse<Void> confirm(@Valid @RequestBody RevenueConfirmDTO dto) {
        revenueService.confirm(dto);
        return ApiResponse.ok();
    }
}

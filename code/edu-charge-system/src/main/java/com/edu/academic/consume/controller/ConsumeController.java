package com.edu.academic.consume.controller;

import com.edu.academic.consume.model.dto.ConsumeDTO;
import com.edu.academic.consume.service.ConsumeService;
import com.edu.common.response.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 课消接入层（MOD-008）。契约：OAS API-0031。 */
@RestController
@RequestMapping("/api/consume/v1")
public class ConsumeController {

    private final ConsumeService consumeService;

    public ConsumeController(ConsumeService consumeService) {
        this.consumeService = consumeService;
    }

    /** API-0031 课消采集。 */
    @PostMapping("/record/create")
    public ApiResponse<String> create(@Valid @RequestBody ConsumeDTO dto) {
        return ApiResponse.ok(consumeService.create(dto));
    }
}

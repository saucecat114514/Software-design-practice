package com.edu.academic.schedule.controller;

import com.edu.academic.schedule.model.dto.ScheduleDTO;
import com.edu.academic.schedule.model.vo.ScheduleVO;
import com.edu.academic.schedule.service.ScheduleService;
import com.edu.common.response.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 排课接入层（MOD-004）。契约：OAS API-0016。 */
@RestController
@RequestMapping("/api/schedule/v1")
public class ScheduleController {

    private final ScheduleService scheduleService;

    public ScheduleController(ScheduleService scheduleService) {
        this.scheduleService = scheduleService;
    }

    /** API-0016 排课。 */
    @PostMapping("/lesson/create")
    public ApiResponse<ScheduleVO> create(@Valid @RequestBody ScheduleDTO dto) {
        return ApiResponse.ok(scheduleService.create(dto));
    }
}

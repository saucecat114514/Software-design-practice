package com.edu.academic.attendance.controller;

import com.edu.academic.attendance.model.dto.CheckinDTO;
import com.edu.academic.attendance.model.vo.CheckinVO;
import com.edu.academic.attendance.service.AttendanceService;
import com.edu.common.response.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 考勤接入层（MOD-006）。契约：OAS API-0023。 */
@RestController
@RequestMapping("/api/attendance/v1")
public class AttendanceController {

    private final AttendanceService attendanceService;

    public AttendanceController(AttendanceService attendanceService) {
        this.attendanceService = attendanceService;
    }

    /** API-0023 签到与课时扣减。 */
    @PostMapping("/checkin/create")
    public ApiResponse<CheckinVO> checkin(@Valid @RequestBody CheckinDTO dto) {
        return ApiResponse.ok(attendanceService.checkin(dto));
    }
}

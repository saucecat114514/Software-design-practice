package com.edu.academic.attendance.model.dto;

import jakarta.validation.constraints.NotBlank;

/** 签到请求（OAS CheckinReq / API-0023）。 */
public record CheckinDTO(
        @NotBlank(message = "课节ID必填") String lessonId,
        @NotBlank(message = "学员ID必填") String studentId,
        @NotBlank(message = "签到模式必填") String mode,
        String checkinTime) {
}

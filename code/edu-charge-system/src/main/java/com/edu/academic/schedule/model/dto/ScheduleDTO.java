package com.edu.academic.schedule.model.dto;

import jakarta.validation.constraints.NotBlank;

/** 排课请求（OAS ScheduleReq / API-0016）。 */
public record ScheduleDTO(
        @NotBlank(message = "班级ID必填") String classId,
        @NotBlank(message = "教师ID必填") String teacherId,
        @NotBlank(message = "教室ID必填") String classroomId,
        @NotBlank(message = "开始时间必填") String startTime,
        @NotBlank(message = "结束时间必填") String endTime) {
}

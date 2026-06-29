package com.edu.academic.consume.model.dto;

import jakarta.validation.constraints.NotBlank;

/** 课消请求（OAS ConsumeReq / API-0031）。 */
public record ConsumeDTO(
        @NotBlank(message = "课节ID必填") String lessonId,
        @NotBlank(message = "学员ID必填") String studentId,
        boolean isGift) {
}

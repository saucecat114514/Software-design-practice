package com.edu.academic.clazz.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

/** 创建班级请求（OAS ClassCreateReq / API-0019）。 */
public record ClassCreateDTO(
        @NotBlank(message = "班级名称必填") String className,
        @NotBlank(message = "班型必填") String classType,
        @NotNull(message = "容量必填") Integer capacity,
        String campusId) {
}

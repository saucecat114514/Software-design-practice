package com.edu.academic.clazz.controller;

import com.edu.academic.clazz.model.dto.ClassCreateDTO;
import com.edu.academic.clazz.model.vo.ClassVO;
import com.edu.academic.clazz.service.ClassService;
import com.edu.common.response.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 班级接入层（MOD-005）。契约：OAS API-0019。 */
@RestController
@RequestMapping("/api/class/v1")
public class ClassController {

    private final ClassService classService;

    public ClassController(ClassService classService) {
        this.classService = classService;
    }

    /** API-0019 创建班级。 */
    @PostMapping("/class/create")
    public ApiResponse<ClassVO> create(@Valid @RequestBody ClassCreateDTO dto) {
        return ApiResponse.ok(classService.create(dto));
    }
}

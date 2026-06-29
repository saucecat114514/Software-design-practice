package com.edu.academic.clazz.service;

import com.edu.academic.clazz.model.dto.ClassCreateDTO;
import com.edu.academic.clazz.model.entity.Clazz;
import com.edu.academic.clazz.model.vo.ClassVO;
import com.edu.academic.clazz.repository.ClassRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** 班级服务（MOD-005）。业务逻辑收敛此处（C-ARCH-0003）。 */
@Service
public class ClassService {

    private final ClassRepository classRepository;

    public ClassService(ClassRepository classRepository) {
        this.classRepository = classRepository;
    }

    /** 创建班级（FR-CLS-001）。 */
    @Transactional
    public ClassVO create(ClassCreateDTO dto) {
        Clazz c = new Clazz();
        c.setClassId("CLS-" + System.currentTimeMillis());
        c.setClassName(dto.className());
        c.setClassType(dto.classType());
        c.setCapacity(dto.capacity());
        c.setEnrolled(0);
        c.setCampusId(dto.campusId());
        classRepository.save(c);
        return new ClassVO(c.getClassId(), c.getCapacity(), c.getEnrolled());
    }
}

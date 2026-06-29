package com.edu.academic.schedule.service;

import com.edu.academic.schedule.model.dto.ScheduleDTO;
import com.edu.academic.schedule.model.entity.Schedule;
import com.edu.academic.schedule.model.vo.ScheduleVO;
import com.edu.academic.schedule.repository.ScheduleRepository;
import com.edu.common.exception.BizException;
import com.edu.common.exception.ErrorCode;
import org.apache.ibatis.annotations.Param;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** 排课服务（MOD-004）。三维冲突检测，冲突即拦截（FR-SCH-001）。 */
@Service
public class ScheduleService {

    private final ScheduleRepository scheduleRepository;

    public ScheduleService(ScheduleRepository scheduleRepository) {
        this.scheduleRepository = scheduleRepository;
    }

    /** 排课（FR-SCH-001）：同教师同时段冲突则拦截。 */
    @Transactional
    public ScheduleVO create(ScheduleDTO dto) {
        if (scheduleRepository.countConflict(dto.teacherId(), dto.startTime()) > 0) {
            throw new BizException(ErrorCode.PARAM_ERROR, "排课冲突：教师该时段已有课");
        }
        Schedule s = new Schedule();
        s.setLessonId("LSN-" + System.currentTimeMillis());
        s.setClassId(dto.classId());
        s.setTeacherId(dto.teacherId());
        s.setClassroomId(dto.classroomId());
        s.setStartTime(dto.startTime());
        s.setEndTime(dto.endTime());
        scheduleRepository.save(s);
        return new ScheduleVO(s.getLessonId(), false);
    }
}

package com.edu.academic.attendance.service;

import com.edu.academic.attendance.model.dto.CheckinDTO;
import com.edu.academic.attendance.model.entity.AttendanceRecord;
import com.edu.academic.attendance.model.entity.HourAccount;
import com.edu.academic.attendance.model.vo.CheckinVO;
import com.edu.academic.attendance.repository.AttendanceRepository;
import com.edu.common.exception.BizException;
import com.edu.common.exception.ErrorCode;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** 考勤服务（MOD-006）。签到扣课时为课时账户唯一出口（FR-ATT-002）。 */
@Service
public class AttendanceService {

    private final AttendanceRepository attendanceRepository;

    public AttendanceService(AttendanceRepository attendanceRepository) {
        this.attendanceRepository = attendanceRepository;
    }

    /** 签到扣课时：正常出勤扣 1 课时（迟到/早退规则略，演示版）。 */
    @Transactional
    public CheckinVO checkin(CheckinDTO dto) {
        HourAccount acc = attendanceRepository.findAccount(dto.studentId());
        if (acc == null) {
            throw new BizException(ErrorCode.PARAM_ERROR, "学员课时账户不存在: " + dto.studentId());
        }
        // 课时不足则不扣（避免账户余额与上报扣减不一致）
        int deduct = acc.remainingHours() > 0 ? 1 : 0;
        int remaining = acc.remainingHours() - deduct;
        attendanceRepository.updateRemaining(dto.studentId(), remaining);

        AttendanceRecord r = new AttendanceRecord();
        r.setAttendanceId("ATT-" + System.currentTimeMillis());
        r.setLessonId(dto.lessonId());
        r.setStudentId(dto.studentId());
        r.setStatus("present");
        r.setHourDeducted(deduct);
        attendanceRepository.save(r);

        return new CheckinVO("present", deduct, remaining);
    }
}

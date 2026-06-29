package com.edu.academic.attendance.repository;

import com.edu.academic.attendance.model.entity.AttendanceRecord;
import com.edu.academic.attendance.model.entity.HourAccount;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/** 考勤数据访问（MOD-006 Repository，MyBatis）。仅操作 edu_attendance / edu_course_hour_account（C-MOD-0003）。 */
@Mapper
public interface AttendanceRepository {

    @Select("SELECT student_id, total_hours, remaining_hours FROM edu_course_hour_account WHERE student_id = #{studentId}")
    HourAccount findAccount(String studentId);

    @Update("UPDATE edu_course_hour_account SET remaining_hours = #{remaining} WHERE student_id = #{studentId}")
    void updateRemaining(String studentId, int remaining);

    @Insert("MERGE INTO edu_attendance (attendance_id, lesson_id, student_id, status, hour_deducted) "
            + "VALUES (#{attendanceId}, #{lessonId}, #{studentId}, #{status}, #{hourDeducted})")
    void save(AttendanceRecord record);
}

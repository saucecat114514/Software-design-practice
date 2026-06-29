package com.edu.academic.schedule.repository;

import com.edu.academic.schedule.model.entity.Schedule;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

/** 排课数据访问（MOD-004 Repository，MyBatis）。仅操作 edu_schedule（C-MOD-0003）。 */
@Mapper
public interface ScheduleRepository {

    /** 三维冲突检测：同教师同开始时间已排课数。 */
    @Select("SELECT COUNT(*) FROM edu_schedule WHERE teacher_id = #{teacherId} AND start_time = #{startTime}")
    int countConflict(String teacherId, String startTime);

    @Insert("MERGE INTO edu_schedule (lesson_id, class_id, teacher_id, classroom_id, start_time, end_time) "
            + "VALUES (#{lessonId}, #{classId}, #{teacherId}, #{classroomId}, #{startTime}, #{endTime})")
    void save(Schedule schedule);
}

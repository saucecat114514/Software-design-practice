package com.edu.academic.consume.repository;

import com.edu.academic.consume.model.entity.ConsumeRecord;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;

/** 课消数据访问（MOD-008 Repository，MyBatis）。仅操作 edu_consume_record（C-MOD-0003）。 */
@Mapper
public interface ConsumeRepository {

    @Insert("MERGE INTO edu_consume_record (consume_id, lesson_id, student_id, is_gift, signed_month) "
            + "VALUES (#{consumeId}, #{lessonId}, #{studentId}, #{isGift}, #{signedMonth})")
    void save(ConsumeRecord record);
}

package com.edu.academic.clazz.repository;

import com.edu.academic.clazz.model.entity.Clazz;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;

/** 班级数据访问（MOD-005 Repository，MyBatis）。仅操作 edu_class（C-MOD-0003）。 */
@Mapper
public interface ClassRepository {

    @Insert("MERGE INTO edu_class (class_id, class_name, class_type, capacity, enrolled, campus_id) "
            + "VALUES (#{classId}, #{className}, #{classType}, #{capacity}, #{enrolled}, #{campusId})")
    void save(Clazz clazz);
}

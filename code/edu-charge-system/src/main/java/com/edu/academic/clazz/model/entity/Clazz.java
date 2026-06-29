package com.edu.academic.clazz.model.entity;

/** 班级实体（归属表 edu_class，MOD-005 独占）。命名 Clazz 避开 java 关键字 class。 */
public class Clazz {

    private String classId;
    private String className;
    private String classType;
    private Integer capacity;
    private Integer enrolled;
    private String campusId;

    public String getClassId() { return classId; }
    public void setClassId(String classId) { this.classId = classId; }
    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }
    public String getClassType() { return classType; }
    public void setClassType(String classType) { this.classType = classType; }
    public Integer getCapacity() { return capacity; }
    public void setCapacity(Integer capacity) { this.capacity = capacity; }
    public Integer getEnrolled() { return enrolled; }
    public void setEnrolled(Integer enrolled) { this.enrolled = enrolled; }
    public String getCampusId() { return campusId; }
    public void setCampusId(String campusId) { this.campusId = campusId; }
}

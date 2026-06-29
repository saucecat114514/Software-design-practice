package com.edu.academic.attendance.model.entity;

/** 考勤记录实体（归属表 edu_attendance，MOD-006 独占）。 */
public class AttendanceRecord {

    private String attendanceId;
    private String lessonId;
    private String studentId;
    private String status;
    private Integer hourDeducted;

    public String getAttendanceId() { return attendanceId; }
    public void setAttendanceId(String attendanceId) { this.attendanceId = attendanceId; }
    public String getLessonId() { return lessonId; }
    public void setLessonId(String lessonId) { this.lessonId = lessonId; }
    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Integer getHourDeducted() { return hourDeducted; }
    public void setHourDeducted(Integer hourDeducted) { this.hourDeducted = hourDeducted; }
}

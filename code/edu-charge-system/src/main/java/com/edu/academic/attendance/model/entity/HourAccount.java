package com.edu.academic.attendance.model.entity;

/** 学员课时账户读模型（归属表 edu_course_hour_account，MOD-006）。 */
public record HourAccount(String studentId, Integer totalHours, Integer remainingHours) {
}

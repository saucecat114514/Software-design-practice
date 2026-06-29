package com.edu.academic.attendance.model.vo;

/** 签到结果（OAS CheckinVO）。 */
public record CheckinVO(String attendanceStatus, Integer hourDeducted, Integer hourRemaining) {
}

package com.edu.academic.consume.model.entity;

/** 课消记录实体（归属表 edu_consume_record，MOD-008 独占）。 */
public class ConsumeRecord {

    private String consumeId;
    private String lessonId;
    private String studentId;
    private Boolean isGift;
    private String signedMonth;

    public String getConsumeId() { return consumeId; }
    public void setConsumeId(String consumeId) { this.consumeId = consumeId; }
    public String getLessonId() { return lessonId; }
    public void setLessonId(String lessonId) { this.lessonId = lessonId; }
    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }
    public Boolean getIsGift() { return isGift; }
    public void setIsGift(Boolean isGift) { this.isGift = isGift; }
    public String getSignedMonth() { return signedMonth; }
    public void setSignedMonth(String signedMonth) { this.signedMonth = signedMonth; }
}

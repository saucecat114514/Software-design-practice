package com.edu.academic.consume.event;

/** 课消确认领域事件（DTS EDGE-0022：课消→收入确认，弱一致事件解耦，C-MOD-0008）。 */
public record ConsumeConfirmedEvent(String consumeId, String signedMonth, boolean gift) {
}

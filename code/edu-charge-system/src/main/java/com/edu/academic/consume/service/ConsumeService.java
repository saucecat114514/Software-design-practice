package com.edu.academic.consume.service;

import com.edu.academic.consume.event.ConsumeConfirmedEvent;
import com.edu.academic.consume.model.dto.ConsumeDTO;
import com.edu.academic.consume.model.entity.ConsumeRecord;
import com.edu.academic.consume.repository.ConsumeRepository;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 课消服务（MOD-008）。落课消记录并发领域事件驱动收入确认（DTS EDGE-0022 事件解耦）。
 */
@Service
public class ConsumeService {

    private final ConsumeRepository consumeRepository;
    private final ApplicationEventPublisher eventPublisher;

    public ConsumeService(ConsumeRepository consumeRepository, ApplicationEventPublisher eventPublisher) {
        this.consumeRepository = consumeRepository;
        this.eventPublisher = eventPublisher;
    }

    /** 课消采集（FR-FIN-001）：落库 + 发事件（收入确认订阅）。 */
    @Transactional
    public String create(ConsumeDTO dto) {
        String consumeId = "CSM-" + System.currentTimeMillis();
        ConsumeRecord r = new ConsumeRecord();
        r.setConsumeId(consumeId);
        r.setLessonId(dto.lessonId());
        r.setStudentId(dto.studentId());
        r.setIsGift(dto.isGift());
        r.setSignedMonth("2026-07");
        consumeRepository.save(r);
        // 弱一致跨域：课消 → 收入确认（事件，不同步硬调用）
        eventPublisher.publishEvent(new ConsumeConfirmedEvent(consumeId, r.getSignedMonth(), dto.isGift()));
        return consumeId;
    }
}

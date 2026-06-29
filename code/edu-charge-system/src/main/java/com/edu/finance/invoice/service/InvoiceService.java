package com.edu.finance.invoice.service;

import com.edu.common.config.ChargeProperties;
import com.edu.finance.invoice.model.dto.InvoiceIssueDTO;
import com.edu.finance.invoice.model.entity.Invoice;
import com.edu.finance.invoice.model.vo.InvoiceVO;
import com.edu.finance.invoice.repository.InvoiceRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 发票服务（MOD-011）。≤阈值自动开、>阈值入待审核（阈值配置注入 C-ARCH-0008）。
 * v2：经基础模块 Mock 电票适配（MOD-011→MOD-102 Mock）。
 */
@Service
public class InvoiceService {

    private final InvoiceRepository invoiceRepository;
    private final ChargeProperties chargeProperties;

    public InvoiceService(InvoiceRepository invoiceRepository, ChargeProperties chargeProperties) {
        this.invoiceRepository = invoiceRepository;
        this.chargeProperties = chargeProperties;
    }

    /** 开票（FR-INV-001）：阈值判定自动/待审。 */
    @Transactional
    public InvoiceVO issue(InvoiceIssueDTO dto) {
        boolean needReview = dto.amount().compareTo(chargeProperties.getInvoiceAutoThreshold()) > 0;
        String status = needReview ? "pending_review" : "auto_issued";
        Invoice inv = new Invoice();
        inv.setInvoiceId("INV-" + System.currentTimeMillis());
        inv.setOrderId(dto.orderId());
        inv.setTitle(dto.title());
        inv.setAmount(dto.amount());
        inv.setStatus(status);
        inv.setNeedReview(needReview);
        invoiceRepository.save(inv);
        return new InvoiceVO(inv.getInvoiceId(), status, needReview);
    }
}

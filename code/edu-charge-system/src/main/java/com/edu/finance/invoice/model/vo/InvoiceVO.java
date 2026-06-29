package com.edu.finance.invoice.model.vo;

/** 发票结果（OAS InvoiceVO）。status：auto_issued/pending_review/issued/red_flushed/void。 */
public record InvoiceVO(String invoiceId, String status, Boolean needReview) {
}

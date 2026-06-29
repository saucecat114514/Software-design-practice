package com.edu.finance.invoice.controller;

import com.edu.common.response.ApiResponse;
import com.edu.finance.invoice.model.dto.InvoiceIssueDTO;
import com.edu.finance.invoice.model.vo.InvoiceVO;
import com.edu.finance.invoice.service.InvoiceService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 发票接入层（MOD-011）。契约：OAS API-0051。 */
@RestController
@RequestMapping("/api/invoice/v1")
public class InvoiceController {

    private final InvoiceService invoiceService;

    public InvoiceController(InvoiceService invoiceService) {
        this.invoiceService = invoiceService;
    }

    /** API-0051 开具发票。 */
    @PostMapping("/issue/create")
    public ApiResponse<InvoiceVO> issue(@Valid @RequestBody InvoiceIssueDTO dto) {
        return ApiResponse.ok(invoiceService.issue(dto));
    }
}

package com.edu.finance.invoice.repository;

import com.edu.finance.invoice.model.entity.Invoice;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;

/** 发票数据访问（MOD-011 Repository，MyBatis）。仅操作 fin_invoice（C-MOD-0003）。 */
@Mapper
public interface InvoiceRepository {

    @Insert("MERGE INTO fin_invoice (invoice_id, order_id, title, amount, status, need_review) "
            + "VALUES (#{invoiceId}, #{orderId}, #{title}, #{amount}, #{status}, #{needReview})")
    void save(Invoice invoice);
}

package com.edu.crm.order.model.vo;

/** 订单结果（OAS OrderVO）。status：unpaid/paying/paid/approving/rejected。 */
public record OrderVO(String orderId, String status) {
}

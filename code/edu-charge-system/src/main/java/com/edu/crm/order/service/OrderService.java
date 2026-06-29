package com.edu.crm.order.service;

import com.edu.crm.order.model.dto.OrderCreateDTO;
import com.edu.crm.order.model.dto.PriceCalcDTO;
import com.edu.crm.order.model.vo.OrderVO;
import com.edu.crm.order.model.vo.PriceCalcVO;

/**
 * 报名订单业务服务（MOD-003 Service 层）。
 */
public interface OrderService {

    /** 优惠算价（互斥校验 + 触发审批判定，FR-ORDER-001）。 */
    PriceCalcVO calcPrice(PriceCalcDTO dto);

    /** 创建报名订单并触发统一收款（FR-ORDER-005）。 */
    OrderVO createOrder(OrderCreateDTO dto);
}

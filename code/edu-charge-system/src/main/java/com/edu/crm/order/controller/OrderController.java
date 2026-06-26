package com.edu.crm.order.controller;

import com.edu.common.response.ApiResponse;
import com.edu.crm.order.model.dto.PriceCalcDTO;
import com.edu.crm.order.model.vo.PriceCalcVO;
import com.edu.crm.order.service.OrderService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 报名订单接入层（MOD-003 Controller）。仅校验/路由/封装（C-ARCH-0002）。契约：OAS API-0009。
 */
@RestController
@RequestMapping("/api/order/v1")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    /** API-0009 报名优惠算价。 */
    @PostMapping("/price/calc")
    public ApiResponse<PriceCalcVO> calcPrice(@Valid @RequestBody PriceCalcDTO dto) {
        return ApiResponse.ok(orderService.calcPrice(dto));
    }
}

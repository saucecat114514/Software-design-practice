package com.edu.crm.order.repository;

import com.edu.crm.order.model.entity.Order;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

/** 订单数据访问（MOD-003 Repository，MyBatis）。仅操作 crm_order（C-MOD-0003）。 */
@Mapper
public interface OrderRepository {

    @Insert("MERGE INTO crm_order (order_id, customer_phone, course_id, final_amount, pay_channel, status) "
            + "VALUES (#{orderId}, #{customerPhone}, #{courseId}, #{finalAmount}, #{payChannel}, #{status})")
    void save(Order order);

    @Select("SELECT order_id, customer_phone, course_id, final_amount, pay_channel, status "
            + "FROM crm_order WHERE order_id = #{orderId}")
    Order findById(String orderId);
}

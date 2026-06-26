package com.edu.finance.refund.repository;

import com.edu.finance.refund.model.entity.OrderSnapshot;
import com.edu.finance.refund.model.entity.RefundOrder;

/**
 * 退费数据访问（MOD-010 Repository 层，C-ARCH-0004：数据访问唯一出口）。
 * v1 以内存实现模拟；真实实现为 MyBatis Mapper 操作 fin_refund / 读模型表。
 */
public interface RefundRepository {

    /** 查询订单财务快照（本模块读模型，不跨域直读订单表）。 */
    OrderSnapshot findOrderSnapshot(String orderId);

    /** 保存/更新退费单。 */
    void save(RefundOrder refundOrder);

    /** 按退费单ID查询。 */
    RefundOrder findById(String refundId);
}

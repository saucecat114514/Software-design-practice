package com.edu.finance.refund.repository;

import com.edu.finance.refund.model.entity.OrderSnapshot;
import com.edu.finance.refund.model.entity.RefundOrder;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 退费 Repository v1 内存实现（演示用，真实为 MyBatis）。
 * 仅操作本模块归属数据（fin_refund + 订单读模型），不读写他模块私有表（C-MOD-0003）。
 */
@Repository
public class RefundRepositoryImpl implements RefundRepository {

    private final Map<String, RefundOrder> refundStore = new ConcurrentHashMap<>();
    private final Map<String, OrderSnapshot> snapshotStore = new ConcurrentHashMap<>();

    public RefundRepositoryImpl() {
        // 演示种子：购买100 + 赠送20 课时，已消耗25，实付12000，无未红冲发票
        snapshotStore.put("ORD-20260301-0012",
                new OrderSnapshot("ORD-20260301-0012", 100, 20, 25, new BigDecimal("12000.00"), false));
    }

    @Override
    public OrderSnapshot findOrderSnapshot(String orderId) {
        return snapshotStore.get(orderId);
    }

    @Override
    public void save(RefundOrder refundOrder) {
        refundStore.put(refundOrder.getRefundId(), refundOrder);
    }

    @Override
    public RefundOrder findById(String refundId) {
        return refundStore.get(refundId);
    }
}

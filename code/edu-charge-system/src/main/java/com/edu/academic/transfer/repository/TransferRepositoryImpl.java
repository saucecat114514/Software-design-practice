package com.edu.academic.transfer.repository;

import com.edu.academic.transfer.model.entity.TransferOrder;
import com.edu.academic.transfer.model.entity.TransferOrderSnapshot;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 转班 Repository v1 内存实现（演示用）。仅操作本模块归属数据（C-MOD-0003）。
 */
@Repository
public class TransferRepositoryImpl implements TransferRepository {

    private final Map<String, TransferOrder> store = new ConcurrentHashMap<>();
    private final Map<String, TransferOrderSnapshot> snapshots = new ConcurrentHashMap<>();
    private final Map<String, BigDecimal> targetPrices = new ConcurrentHashMap<>();

    public TransferRepositoryImpl() {
        // 演示种子：购买40课时、已消耗20、赠送10、实付9800；目标班级 CLS-A2 应付6000
        snapshots.put("ORD-20260601-0007",
                new TransferOrderSnapshot("ORD-20260601-0007", 40, 20, 10, new BigDecimal("9800.00")));
        targetPrices.put("CLS-A2", new BigDecimal("6000.00"));
    }

    @Override
    public TransferOrderSnapshot findSnapshot(String orderId) {
        return snapshots.get(orderId);
    }

    @Override
    public BigDecimal findTargetAmount(String targetClassId) {
        return targetPrices.get(targetClassId);
    }

    @Override
    public void save(TransferOrder transferOrder) {
        store.put(transferOrder.getTransferId(), transferOrder);
    }
}

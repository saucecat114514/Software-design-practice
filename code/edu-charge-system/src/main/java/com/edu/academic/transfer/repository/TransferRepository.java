package com.edu.academic.transfer.repository;

import com.edu.academic.transfer.model.entity.TransferOrder;
import com.edu.academic.transfer.model.entity.TransferOrderSnapshot;

import java.math.BigDecimal;

/**
 * 转班数据访问（MOD-007 Repository 层）。v1 内存实现，真实为 MyBatis。
 */
public interface TransferRepository {

    /** 原订单快照（本模块读模型）。 */
    TransferOrderSnapshot findSnapshot(String orderId);

    /** 目标班级课包应付金额。 */
    BigDecimal findTargetAmount(String targetClassId);

    /** 保存转班单。 */
    void save(TransferOrder transferOrder);
}

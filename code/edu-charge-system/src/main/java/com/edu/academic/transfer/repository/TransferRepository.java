package com.edu.academic.transfer.repository;

import com.edu.academic.transfer.model.entity.TransferOrder;
import com.edu.academic.transfer.model.entity.TransferOrderSnapshot;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.math.BigDecimal;

/**
 * 转班数据访问（MOD-007 Repository 层）。v2：MyBatis Mapper 操作 H2（C-CODE-0015）。
 * 仅操作本模块归属表 edu_transfer / edu_transfer_snapshot / edu_transfer_target_price（C-MOD-0003）。
 */
@Mapper
public interface TransferRepository {

    /** 原订单快照（本模块读模型）。 */
    @Select("SELECT order_id, purchased_hours, consumed_hours, gift_hours, paid_amount "
            + "FROM edu_transfer_snapshot WHERE order_id = #{orderId}")
    TransferOrderSnapshot findSnapshot(String orderId);

    /** 目标班级课包应付金额。 */
    @Select("SELECT target_amount FROM edu_transfer_target_price WHERE target_class_id = #{targetClassId}")
    BigDecimal findTargetAmount(String targetClassId);

    /** 保存转班单（H2 MERGE upsert）。 */
    @Insert("MERGE INTO edu_transfer (transfer_id, order_id, target_class_id, diff_amount, gift_voided, status) "
            + "VALUES (#{transferId}, #{orderId}, #{targetClassId}, #{diffAmount}, #{giftVoided}, #{status})")
    void save(TransferOrder transferOrder);
}

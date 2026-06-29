package com.edu.finance.refund.repository;

import com.edu.finance.refund.model.entity.OrderSnapshot;
import com.edu.finance.refund.model.entity.RefundOrder;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

/**
 * 退费数据访问（MOD-010 Repository 层，C-ARCH-0004）。
 * v2：MyBatis Mapper 操作 H2（C-CODE-0015）。仅操作本模块归属表 fin_refund / fin_order_snapshot（C-MOD-0003）。
 */
@Mapper
public interface RefundRepository {

    /** 查询订单财务快照（本模块读模型，不跨域直读订单表）。 */
    @Select("SELECT order_id, purchased_hours, gift_hours, consumed_hours, paid_amount, has_unred_flushed_invoice "
            + "FROM fin_order_snapshot WHERE order_id = #{orderId}")
    OrderSnapshot findOrderSnapshot(String orderId);

    /** 保存/更新退费单（H2 MERGE 实现 upsert）。 */
    @Insert("MERGE INTO fin_refund (refund_id, order_id, reason, refund_amount, gift_discount_factor, "
            + "refund_loss_rate, snapshot_id, approval_level, status) VALUES (#{refundId}, #{orderId}, #{reason}, "
            + "#{refundAmount}, #{giftDiscountFactor}, #{refundLossRate}, #{snapshotId}, #{approvalLevel}, #{status})")
    void save(RefundOrder refundOrder);

    /** 按退费单ID查询。 */
    @Select("SELECT refund_id, order_id, reason, refund_amount, gift_discount_factor, refund_loss_rate, "
            + "snapshot_id, approval_level, status FROM fin_refund WHERE refund_id = #{refundId}")
    RefundOrder findById(String refundId);
}

package com.edu.finance.payment.repository;

import com.edu.finance.payment.model.entity.Payment;
import com.edu.finance.payment.model.vo.ReconcileVO;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/** 收款/对账数据访问（MOD-009 Repository，MyBatis）。仅操作 fin_payment / fin_reconcile（C-MOD-0003）。 */
@Mapper
public interface PaymentRepository {

    @Insert("MERGE INTO fin_payment (payment_id, order_id, channel, channel_txn_no, amount, status) "
            + "VALUES (#{paymentId}, #{orderId}, #{channel}, #{channelTxnNo}, #{amount}, #{status})")
    void save(Payment payment);

    @Select("SELECT reconcile_id, channel_txn_no, amount, match_status FROM fin_reconcile "
            + "WHERE settle_date = #{settleDate} ORDER BY reconcile_id")
    List<ReconcileVO> listBySettleDate(String settleDate);
}

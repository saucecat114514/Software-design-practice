package com.edu.finance.payment.service;

import com.edu.common.exception.BizException;
import com.edu.common.exception.ErrorCode;
import com.edu.common.gateway.PaymentGatewayClient;
import com.edu.common.response.PageResult;
import com.edu.finance.payment.model.dto.PayCallbackDTO;
import com.edu.finance.payment.model.dto.PaymentClaimDTO;
import com.edu.finance.payment.model.entity.Payment;
import com.edu.finance.payment.model.vo.PaymentClaimVO;
import com.edu.finance.payment.model.vo.ReconcileVO;
import com.edu.finance.payment.repository.PaymentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 收款与对账服务（MOD-009）。业务逻辑收敛此处（C-ARCH-0003）。
 * v2：支付回调为本地 Mock 沙箱（验签固定通过），契约不变（IFR-PAY-001）。
 */
@Service
public class PaymentService {

    private final PaymentRepository paymentRepository;
    private final PaymentGatewayClient paymentGatewayClient;

    public PaymentService(PaymentRepository paymentRepository, PaymentGatewayClient paymentGatewayClient) {
        this.paymentRepository = paymentRepository;
        this.paymentGatewayClient = paymentGatewayClient;
    }

    /** 收款认领（FR-PAY-001）：认领待认领收款至订单。 */
    @Transactional
    public PaymentClaimVO claim(PaymentClaimDTO dto) {
        Payment p = new Payment();
        p.setPaymentId("PAY-" + dto.channelTxnNo());
        p.setOrderId(dto.orderId());
        p.setChannelTxnNo(dto.channelTxnNo());
        p.setAmount(dto.amount());
        p.setStatus("claimed");
        paymentRepository.save(p);
        return new PaymentClaimVO(p.getPaymentId(), p.getStatus());
    }

    /** 支付回调入账（IFR-PAY-001，Mock 沙箱）：验签固定通过，落收款记录。 */
    @Transactional
    public void callback(PayCallbackDTO dto) {
        // 经基础模块支付网关验签（v2 Mock 固定通过，EDGE-0002 业务→基础白名单）
        if (!paymentGatewayClient.verifySign(dto.channel(), dto.channelTxnNo(), dto.sign())) {
            throw new BizException(ErrorCode.PARAM_ERROR, "支付回调验签失败");
        }
        Payment p = new Payment();
        p.setPaymentId("PAY-" + dto.channelTxnNo());
        p.setOrderId(dto.outOrderId());
        p.setChannel(dto.channel());
        p.setChannelTxnNo(dto.channelTxnNo());
        p.setAmount(dto.amount());
        p.setStatus("success");
        paymentRepository.save(p);
    }

    /** 对账结果查询（FR-RECON-002）。 */
    public PageResult<ReconcileVO> reconcileList(String settleDate, int page, int size) {
        List<ReconcileVO> list = paymentRepository.listBySettleDate(settleDate);
        return new PageResult<>(list.size(), page, size, list);
    }
}

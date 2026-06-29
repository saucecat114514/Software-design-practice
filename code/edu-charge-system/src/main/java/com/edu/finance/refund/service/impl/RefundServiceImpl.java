package com.edu.finance.refund.service.impl;

import com.edu.common.config.ChargeProperties;
import com.edu.common.exception.BizException;
import com.edu.common.exception.ErrorCode;
import com.edu.finance.refund.event.RefundApprovedEvent;
import com.edu.finance.refund.model.dto.RefundApproveDTO;
import com.edu.finance.refund.model.dto.RefundCalcDTO;
import com.edu.finance.refund.model.entity.OrderSnapshot;
import com.edu.finance.refund.model.entity.RefundOrder;
import com.edu.finance.refund.model.vo.RefundApproveVO;
import com.edu.finance.refund.model.vo.RefundCalcVO;
import com.edu.finance.refund.repository.RefundRepository;
import com.edu.finance.refund.service.RefundService;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * 退费业务实现（MOD-010）。
 *
 * 退费口径（v2 / DEF-001，CR-EDU-2026-0001 CR-ITEM-003）：
 *   均价 = 实付金额 / (购买课时 + 赠送课时)        —— 含赠送总课时均价
 *   消耗顺序 = 先扣购买课时，再扣赠送课时
 *   基础退费 = 剩余购买课时 × 均价 + 剩余赠送课时 × 均价 × 折价系数
 *   ★v2 新增：按消耗进度折损率分档——消耗占比 ≤30%→0% / ≤60%→10% / >60%→20%（配置注入）
 *   退费金额 = 基础退费 × (1 − 折损率)，计算即冻结参数快照。
 *
 * v1→v2 差异：v1 无折损率（refund=基础退费）；v2 叠加消耗进度折损分档。
 */
@Service
public class RefundServiceImpl implements RefundService {

    private final RefundRepository refundRepository;
    private final ChargeProperties chargeProperties;
    private final ApplicationEventPublisher eventPublisher;

    public RefundServiceImpl(RefundRepository refundRepository,
                             ChargeProperties chargeProperties,
                             ApplicationEventPublisher eventPublisher) {
        this.refundRepository = refundRepository;
        this.chargeProperties = chargeProperties;
        this.eventPublisher = eventPublisher;
    }

    @Override
    @Transactional
    public RefundCalcVO calc(RefundCalcDTO dto) {
        OrderSnapshot snap = refundRepository.findOrderSnapshot(dto.orderId());
        if (snap == null) {
            throw new BizException(ErrorCode.PARAM_ERROR, "退费订单不存在: " + dto.orderId());
        }
        // 已开票未红冲 → 阻断退费，给红冲指引（FR-REF-002）
        if (snap.hasUnredFlushedInvoice()) {
            throw new BizException(ErrorCode.REFUND_INVOICE_BLOCK);
        }

        int total = snap.purchasedHours() + snap.giftHours();
        if (total <= 0) {
            throw new BizException(ErrorCode.PARAM_ERROR, "课时数据异常");
        }
        // 含赠送总课时均价
        BigDecimal avg = snap.paidAmount().divide(BigDecimal.valueOf(total), 2, RoundingMode.HALF_UP);

        // 先扣购买、再扣赠送
        int consumed = snap.consumedHours();
        int remainingPurchased = Math.max(0, snap.purchasedHours() - consumed);
        int consumedFromGift = Math.max(0, consumed - snap.purchasedHours());
        int remainingGift = Math.max(0, snap.giftHours() - consumedFromGift);

        BigDecimal giftFactor = chargeProperties.getGiftRefundDiscountFactor();
        BigDecimal purchasedValue = avg.multiply(BigDecimal.valueOf(remainingPurchased));
        BigDecimal giftValue = avg.multiply(BigDecimal.valueOf(remainingGift)).multiply(giftFactor);
        BigDecimal baseRefund = purchasedValue.add(giftValue);

        // v2 / DEF-001：按消耗进度折损率分档（配置注入），退费额 = 基础额 × (1 − 折损率)
        BigDecimal consumedRatio = BigDecimal.valueOf(consumed)
                .divide(BigDecimal.valueOf(total), 4, RoundingMode.HALF_UP);
        BigDecimal lossRate = lossRateOf(consumedRatio);
        BigDecimal refundAmount = baseRefund.multiply(BigDecimal.ONE.subtract(lossRate))
                .setScale(2, RoundingMode.HALF_UP);

        // 冻结参数快照并落退费单
        String refundId = "REF-" + dto.orderId();
        String snapshotId = "RFS-" + dto.orderId();
        RefundOrder ro = new RefundOrder();
        ro.setRefundId(refundId);
        ro.setOrderId(dto.orderId());
        ro.setReason(dto.reason());
        ro.setRefundAmount(refundAmount);
        ro.setGiftDiscountFactor(giftFactor);
        ro.setRefundLossRate(lossRate);
        ro.setSnapshotId(snapshotId);
        ro.setStatus("CALCULATED");
        refundRepository.save(ro);

        return new RefundCalcVO(snap.purchasedHours(), snap.giftHours(), consumed,
                avg, giftFactor, lossRate, refundAmount, snapshotId);
    }

    /** v2 折损率分档（DEF-001）：消耗占比 ≤低档阈值→0；≤高档阈值→中档率；否则高档率。 */
    private BigDecimal lossRateOf(BigDecimal consumedRatio) {
        if (consumedRatio.compareTo(chargeProperties.getRefundLossLowThreshold()) <= 0) {
            return BigDecimal.ZERO;
        }
        if (consumedRatio.compareTo(chargeProperties.getRefundLossHighThreshold()) <= 0) {
            return chargeProperties.getRefundLossRateMid();
        }
        return chargeProperties.getRefundLossRateHigh();
    }

    @Override
    @Transactional
    public RefundApproveVO approve(RefundApproveDTO dto) {
        RefundOrder ro = refundRepository.findById(dto.refundId());
        if (ro == null) {
            throw new BizException(ErrorCode.PARAM_ERROR, "退费单不存在: " + dto.refundId());
        }
        if (ro.getSnapshotId() == null) {
            throw new BizException(ErrorCode.REFUND_SNAPSHOT_REQUIRED);
        }

        String level = decideLevel(ro.getRefundAmount());
        ro.setApprovalLevel(level);

        if ("reject".equalsIgnoreCase(dto.action())) {
            ro.setStatus("REJECTED");
            refundRepository.save(ro);
            return new RefundApproveVO("REJECTED", level, false);
        }

        // 大额（level3）必须校长本人手动审批，绝不自动通过（CCB 裁决 / CON-CCB-007）
        if ("level3".equals(level) && !dto.principalApprover()) {
            throw new BizException(ErrorCode.REFUND_PRINCIPAL_REQUIRED);
        }

        ro.setStatus("APPROVED");
        refundRepository.save(ro);

        // 发布退费通过事件 → 收入确认模块订阅做红冲（事件解耦，C-MOD-0008）
        eventPublisher.publishEvent(new RefundApprovedEvent(ro.getRefundId(), ro.getOrderId(), ro.getRefundAmount()));

        return new RefundApproveVO("APPROVED", level, false);
    }

    /** 分级：大额=校长三级、小额=一级、其余二级。 */
    private String decideLevel(BigDecimal amount) {
        if (amount.compareTo(chargeProperties.getRefundPrincipalThreshold()) >= 0) {
            return "level3";
        }
        if (amount.compareTo(chargeProperties.getRefundSmallAmountThreshold()) < 0) {
            return "level1";
        }
        return "level2";
    }
}

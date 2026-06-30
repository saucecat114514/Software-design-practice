package com.edu.academic.transfer.service.impl;

import com.edu.academic.transfer.model.dto.TransferFeeDTO;
import com.edu.academic.transfer.model.entity.TransferOrder;
import com.edu.academic.transfer.model.entity.TransferOrderSnapshot;
import com.edu.academic.transfer.model.vo.TransferFeeVO;
import com.edu.academic.transfer.repository.TransferRepository;
import com.edu.academic.transfer.service.TransferService;
import com.edu.common.exception.BizException;
import com.edu.common.exception.ErrorCode;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * 转班业务实现（MOD-007）。
 *
 * 转班费用口径（v2 / DEF-004，CR-EDU-2026-0001 CR-ITEM-004）：差价按**实际支付单价**，
 *   ★v2 单价随赠课模式对齐——作废(void)=实付/购买课时(不含赠送)；结转(carry)=实付/(购买+赠送)(含赠送，与退费均价口径对齐)
 *   剩余价值 = 剩余购买课时 × 实际支付单价
 *   差价 = 目标课包应付 − 剩余价值（正=补款 / 负=退款）
 *
 * 原路退款：差价为负即应退款额，记录于转班单 diffAmount（负值），由财务模块下游按既定退款流处理；
 *   本模块不直接调退费全额计算（退费 calc 为整单退课口径，与转班差价语义不同，避免误算与跨模块读模型耦合）。
 *
 * v1→v2 差异：v1 单价固定 实付/购买（不含赠送）；v2 carry 模式改为含赠送均价口径，消除与退费的口径不一致。
 */
@Service
public class TransferServiceImpl implements TransferService {

    private final TransferRepository transferRepository;

    public TransferServiceImpl(TransferRepository transferRepository) {
        this.transferRepository = transferRepository;
    }

    @Override
    @Transactional
    public TransferFeeVO confirmFee(TransferFeeDTO dto) {
        TransferOrderSnapshot snap = transferRepository.findSnapshot(dto.orderId());
        if (snap == null) {
            throw new BizException(ErrorCode.PARAM_ERROR, "原订单不存在: " + dto.orderId());
        }
        BigDecimal targetAmount = transferRepository.findTargetAmount(dto.targetClassId());
        if (targetAmount == null) {
            throw new BizException(ErrorCode.TRANSFER_TARGET_INVALID);
        }
        if (snap.purchasedHours() <= 0) {
            throw new BizException(ErrorCode.PARAM_ERROR, "购买课时异常");
        }

        boolean giftVoided = "void".equalsIgnoreCase(dto.giftHandleMode());

        // ★v2/DEF-004：实际支付单价随赠课模式——
        //   作废(void)=实付/购买课时(不含赠送)；结转(carry)=实付/(购买+赠送)(含赠送，与退费均价口径对齐)
        int unitDenominator = giftVoided
                ? snap.purchasedHours()
                : snap.purchasedHours() + snap.giftHours();
        BigDecimal actualUnitPrice = snap.paidAmount()
                .divide(BigDecimal.valueOf(unitDenominator), 2, RoundingMode.HALF_UP);

        int remainingPurchased = Math.max(0, snap.purchasedHours() - snap.consumedHours());
        BigDecimal remainingValue = actualUnitPrice.multiply(BigDecimal.valueOf(remainingPurchased))
                .setScale(2, RoundingMode.HALF_UP);

        BigDecimal diff = targetAmount.subtract(remainingValue).setScale(2, RoundingMode.HALF_UP);

        // 落转班单：差价为负且原路退款 → 标记退款待财务处理（退款额=|diff|，记录于 diffAmount 负值）
        boolean refundDue = diff.signum() < 0 && "original_route".equalsIgnoreCase(dto.refundRoute());
        TransferOrder to = new TransferOrder();
        to.setTransferId("TRF-" + dto.orderId());
        to.setOrderId(dto.orderId());
        to.setTargetClassId(dto.targetClassId());
        to.setDiffAmount(diff);
        to.setGiftVoided(giftVoided);
        to.setStatus(refundDue ? "REFUND_DUE" : "FEE_CONFIRMED");
        transferRepository.save(to);

        return new TransferFeeVO(actualUnitPrice, remainingValue, targetAmount, diff, giftVoided);
    }
}

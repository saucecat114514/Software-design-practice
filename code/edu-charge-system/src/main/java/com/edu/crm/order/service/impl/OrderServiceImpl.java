package com.edu.crm.order.service.impl;

import com.edu.common.exception.BizException;
import com.edu.common.exception.ErrorCode;
import com.edu.crm.order.model.dto.PriceCalcDTO;
import com.edu.crm.order.model.vo.PriceCalcVO;
import com.edu.crm.order.service.OrderService;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 报名算价实现（MOD-003）。
 * 规则：互斥优惠 100% 阻止；优惠合计占比 ≥25% 触发特批审批（FR-ORDER-001）。
 * v1 优惠目录内置演示值，真实由业务规则配置模块（MOD-020）下发。
 */
@Service
public class OrderServiceImpl implements OrderService {

    private static final Map<String, BigDecimal> DISCOUNTS = Map.of(
            "NEW2026", new BigDecimal("1000"),
            "REFERRAL", new BigDecimal("1200"),
            "VIP", new BigDecimal("2000"));

    /** 互斥组：同组内优惠不可叠加。 */
    private static final Set<String> MUTEX_GROUP = Set.of("NEW2026", "VIP");

    private static final BigDecimal APPROVAL_RATIO = new BigDecimal("0.25");

    @Override
    public PriceCalcVO calcPrice(PriceCalcDTO dto) {
        List<String> codes = dto.discountCodes() == null ? List.of() : dto.discountCodes();

        long mutexHit = codes.stream().filter(MUTEX_GROUP::contains).count();
        if (mutexHit > 1) {
            throw new BizException(ErrorCode.ORDER_DISCOUNT_CONFLICT);
        }

        BigDecimal totalDiscount = BigDecimal.ZERO;
        List<String> applied = new ArrayList<>();
        for (String code : codes) {
            BigDecimal v = DISCOUNTS.get(code);
            if (v != null) {
                totalDiscount = totalDiscount.add(v);
                applied.add(code + "-" + v.toPlainString());
            }
        }

        BigDecimal original = dto.originalAmount();
        BigDecimal finalAmount = original.subtract(totalDiscount).max(BigDecimal.ZERO).setScale(2, RoundingMode.HALF_UP);

        boolean needApproval = false;
        String reason = null;
        if (original.signum() > 0
                && totalDiscount.divide(original, 4, RoundingMode.HALF_UP).compareTo(APPROVAL_RATIO) >= 0) {
            needApproval = true;
            reason = "优惠合计占比超阈值，触发特批审批";
        }

        return new PriceCalcVO(finalAmount, applied, needApproval, reason);
    }
}

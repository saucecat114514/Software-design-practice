package com.edu.finance.refund.service;

import com.edu.finance.refund.model.dto.RefundApproveDTO;
import com.edu.finance.refund.model.dto.RefundCalcDTO;
import com.edu.finance.refund.model.vo.RefundApproveVO;
import com.edu.finance.refund.model.vo.RefundCalcVO;

/**
 * 退费业务服务（MOD-010 Service 层，业务逻辑收敛此处，C-ARCH-0003）。
 */
public interface RefundService {

    /** 退费金额计算并冻结参数快照（FR-REF-001）。 */
    RefundCalcVO calc(RefundCalcDTO dto);

    /** 退费分级审批（FR-REF-003）。 */
    RefundApproveVO approve(RefundApproveDTO dto);
}

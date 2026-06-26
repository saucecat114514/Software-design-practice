package com.edu.academic.transfer.service;

import com.edu.academic.transfer.model.dto.TransferFeeDTO;
import com.edu.academic.transfer.model.vo.TransferFeeVO;

/**
 * 转班业务服务（MOD-007 Service 层）。
 */
public interface TransferService {

    /** 转班费用确认（FR-TRF-002）。 */
    TransferFeeVO confirmFee(TransferFeeDTO dto);
}

import numpy as np
from core.formulas.criteria.ppt import partial_transpose

def negativity(rho: np.ndarray) -> float:
    """
    计算任意两比特量子态的负纠缠度 (Negativity)。
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("Negativity currently supports 2-qubit (4x4) states.")
        
    rho_pt = partial_transpose(rho, sys=1)
    eigvals = np.linalg.eigvals(rho_pt).real
    
    # 过滤负特征值并求绝对值之和
    neg_eigvals = eigvals[eigvals < 0]
    return float(np.sum(np.abs(neg_eigvals)))
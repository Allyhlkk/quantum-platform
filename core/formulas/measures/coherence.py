import numpy as np

def l1_coherence(rho: np.ndarray) -> float:
    """
    计算量子态在计算基下的 l1-范数相干性 (l1-norm of coherence)
    C_l1(rho) = sum_{i != j} |rho_{ij}|
    """
    # 提取所有元素绝对值的总和
    abs_sum = np.sum(np.abs(rho))
    # 减去对角线元素的绝对值总和
    diag_sum = np.sum(np.abs(np.diag(rho)))
    
    return float(abs_sum - diag_sum)
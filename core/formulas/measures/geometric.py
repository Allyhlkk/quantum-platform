import numpy as np
from core.formulas.measures.concurrence import concurrence

def geometric_measure(rho: np.ndarray) -> float:
    """
    计算两比特系统的几何纠缠度 (Geometric Measure of Entanglement)。
    它衡量了纠缠态与最近的可分态之间的距离。
    对于两比特态，利用 C(rho) 可计算：E_G = 1 - 0.5 * (1 + sqrt(1 - C^2))
    """
    c = concurrence(rho)
    if c <= 0:
        return 0.0
    
    # 计算最大重叠率的平方 Lambda^2
    lambda_sq = 0.5 * (1 + np.sqrt(1 - c**2))
    return float(1.0 - lambda_sq)
import numpy as np

def purity(rho: np.ndarray) -> float:
    """
    计算量子态的纯度 Purity = Tr(rho^2)
    纯态的纯度为 1，最大混合态的纯度为 1/d（两比特系统为 0.25）
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("Purity currently configured for 2-qubit (4x4) states.")
        
    rho_sq = rho @ rho
    return float(np.trace(rho_sq).real)
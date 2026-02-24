import numpy as np

def state_fidelity(rho: np.ndarray, sigma: np.ndarray = None) -> float:
    """
    计算两个量子态之间的保真度 (Fidelity)。
    如果 sigma 为 None，则默认计算 rho 与最大纠缠态 |Phi+> = 1/sqrt(2)(|00>+|11>) 的保真度。
    """
    if sigma is None:
        # 定义目标 Bell 态 |Phi+>
        psi_target = np.array([1, 0, 0, 1]) / np.sqrt(2)
        sigma = np.outer(psi_target, psi_target.conj())
    
    # 对于其中一个是纯态的情况，F = tr(rho * sigma)
    # 这里的实现采用通用的 Jost-Josza 公式（针对混合态）
    from scipy.linalg import sqrtm
    
    rho_sqrt = sqrtm(rho)
    inner = rho_sqrt @ sigma @ rho_sqrt
    f = np.trace(sqrtm(inner)).real ** 2
    return float(f)
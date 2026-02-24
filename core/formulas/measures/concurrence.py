import numpy as np

def concurrence(rho: np.ndarray) -> float:
    """
    Wootters' Concurrence for ANY two-qubit state.
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("Concurrence is only defined for 2-qubit (4x4) states")
    
    # 构造泡利 Y 矩阵的张量积: sigma_y \otimes sigma_y
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sy_sy = np.kron(sigma_y, sigma_y)
    
    # 核心公式计算
    rho_star = np.conj(rho)
    rho_tilde = sy_sy @ rho_star @ sy_sy
    R = rho @ rho_tilde
    
    # 特征值及容错处理
    eigvals = np.linalg.eigvals(R)
    eigvals = np.maximum(eigvals.real, 0)
    
    lambdas = np.sqrt(eigvals)
    lambdas = np.sort(lambdas)[::-1]  # 降序排列
    
    C = max(0.0, lambdas[0] - lambdas[1] - lambdas[2] - lambdas[3])
    return float(C)
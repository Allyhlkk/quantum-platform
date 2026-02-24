import numpy as np

def partial_transpose(rho: np.ndarray, sys: int = 1) -> np.ndarray:
    """
    Partial transpose for 2-qubit density matrix.
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("PPT only supports 2-qubit (4x4) states")

    rho_reshaped = rho.reshape(2, 2, 2, 2)
    if sys == 0:
        rho_pt = rho_reshaped.transpose(2, 1, 0, 3)
    elif sys == 1:
        rho_pt = rho_reshaped.transpose(0, 3, 2, 1)
    else:
        raise ValueError("sys must be 0 or 1")
    return rho_pt.reshape(4, 4)

def ppt_min_eigenvalue(rho: np.ndarray) -> float:
    """
    通用 PPT 判据：返回任意 2-qubit 密度矩阵的偏转置的最小特征值。
    """
    rho_pt = partial_transpose(rho, sys=1)
    eigvals = np.linalg.eigvals(rho_pt)
    return float(np.min(eigvals.real))
import numpy as np
from core.states.werner import werner_state


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


def ppt_min_eigenvalue_werner(p: float) -> float:
    """
    PPT criterion for Werner state:
    return minimum eigenvalue of partial transpose
    """
    rho = werner_state(p)
    rho_pt = partial_transpose(rho, sys=1)
    eigvals = np.linalg.eigvals(rho_pt)

    return float(np.min(eigvals.real))

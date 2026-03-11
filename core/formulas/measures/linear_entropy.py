import numpy as np


def linear_entropy(rho: np.ndarray) -> float:
    """
    Linear entropy:
      S_L = 1 - Tr(rho^2)
    For pure states S_L = 0, larger values indicate stronger mixedness.
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be a square matrix")

    pur = float(np.real(np.trace(rho @ rho)))
    return float(max(0.0, 1.0 - pur))

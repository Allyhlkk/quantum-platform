# core/states/werner.py
import numpy as np

def bell_psi_minus() -> np.ndarray:
    """
    |Psi-> = (|01> - |10>) / sqrt(2)
    """
    return np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)


def werner_state(p: float) -> np.ndarray:
    """
    Werner state:
        rho = p |Psi-><Psi-| + (1-p)/4 * I
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError("Parameter p must be in [0, 1].")

    psi = bell_psi_minus()
    projector = np.outer(psi, psi.conj())

    identity = np.eye(4, dtype=complex) / 4.0
    rho = p * projector + (1 - p) * identity

    return rho

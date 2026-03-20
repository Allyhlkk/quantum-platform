import numpy as np


def pure_theta_state(theta: float) -> np.ndarray:
    """
    |psi(theta)> = cos(theta)|00> + sin(theta)|11>
    """
    return np.array([np.cos(theta), 0, 0, np.sin(theta)], dtype=complex)


def pure_theta_density(theta: float) -> np.ndarray:
    psi = pure_theta_state(theta)
    return np.outer(psi, psi.conj())

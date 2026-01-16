import numpy as np


def psi_minus() -> np.ndarray:
    """
    |ψ⁻⟩ = (|01⟩ − |10⟩) / √2
    """
    return (1 / np.sqrt(2)) * np.array([0, 1, -1, 0], dtype=complex)

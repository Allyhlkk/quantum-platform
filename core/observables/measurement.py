import numpy as np
from .pauli import SIGMA_X, SIGMA_Z


def spin_measurement(theta: float) -> np.ndarray:
    """
    Measurement operator in x-z plane:
    A(θ) = cosθ · σ_z + sinθ · σ_x
    """
    return np.cos(theta) * SIGMA_Z + np.sin(theta) * SIGMA_X

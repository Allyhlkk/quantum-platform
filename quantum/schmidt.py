import numpy as np


def schmidt_coefficients(psi: np.ndarray) -> np.ndarray:
    _, s, _ = np.linalg.svd(psi)
    return s

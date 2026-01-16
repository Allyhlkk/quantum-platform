import numpy as np


def schmidt_coefficients(psi_matrix: np.ndarray) -> np.ndarray:
    """
    Compute Schmidt coefficients via SVD.
    psi_matrix: reshaped coefficient matrix
    """
    _, s, _ = np.linalg.svd(psi_matrix)
    return s

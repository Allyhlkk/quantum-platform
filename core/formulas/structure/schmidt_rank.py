import numpy as np
from core.formulas.structure.schmidt import schmidt_coefficients


def schmidt_rank(psi_matrix: np.ndarray, tol: float = 1e-10) -> int:
    coeffs = schmidt_coefficients(psi_matrix)
    return int((coeffs > tol).sum())

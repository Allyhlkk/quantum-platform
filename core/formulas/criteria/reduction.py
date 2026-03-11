import numpy as np


def _reduced_states(rho: np.ndarray):
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("Reduction criterion only supports 2-qubit (4x4) states")

    rho_tensor = rho.reshape(2, 2, 2, 2)
    rho_a = np.trace(rho_tensor, axis1=1, axis2=3)
    rho_b = np.trace(rho_tensor, axis1=0, axis2=2)
    return rho_a, rho_b


def reduction_min_eigenvalues(rho: np.ndarray):
    """
    Reduction criterion checks:
    rho_A ⊗ I - rho >= 0 and I ⊗ rho_B - rho >= 0 for separable states.
    Returns minimum eigenvalues for both operators.
    """
    rho = np.asarray(rho, dtype=complex)
    rho_a, rho_b = _reduced_states(rho)
    I2 = np.eye(2, dtype=complex)

    red_a = np.kron(rho_a, I2) - rho
    red_b = np.kron(I2, rho_b) - rho

    min_a = float(np.min(np.linalg.eigvals(red_a).real))
    min_b = float(np.min(np.linalg.eigvals(red_b).real))
    return min_a, min_b

import numpy as np


def realignment_matrix(rho: np.ndarray) -> np.ndarray:
    """
    Realignment (CCNR) transform for 2-qubit density matrix.
    R_{ik,jl} = rho_{ij,kl}
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("CCNR only supports 2-qubit (4x4) states")

    rho_tensor = rho.reshape(2, 2, 2, 2)
    return rho_tensor.transpose(0, 2, 1, 3).reshape(4, 4)


def ccnr_trace_norm(rho: np.ndarray) -> float:
    """
    CCNR criterion uses the trace norm of the realigned matrix:
    separable => ||R(rho)||_1 <= 1
    """
    R = realignment_matrix(rho)
    sing_vals = np.linalg.svd(R, compute_uv=False)
    return float(np.sum(np.abs(sing_vals)))

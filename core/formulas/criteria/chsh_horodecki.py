import numpy as np


_SIGMA_X = np.array([[0, 1], [1, 0]], dtype=complex)
_SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULI = (_SIGMA_X, _SIGMA_Y, _SIGMA_Z)


def correlation_matrix(rho: np.ndarray) -> np.ndarray:
    """
    Correlation matrix T with entries:
    T_ij = Tr[rho * (sigma_i ⊗ sigma_j)], i,j in {x,y,z}
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("Horodecki CHSH only supports 2-qubit (4x4) states")

    t = np.zeros((3, 3), dtype=float)
    for i, si in enumerate(_PAULI):
        for j, sj in enumerate(_PAULI):
            op = np.kron(si, sj)
            t[i, j] = float(np.real(np.trace(rho @ op)))
    return t


def max_chsh_horodecki(rho: np.ndarray):
    """
    Horodecki criterion:
      S_max = 2 * sqrt(u1 + u2)
    where u1,u2 are two largest eigenvalues of U = T^T T.
    """
    t = correlation_matrix(rho)
    u = t.T @ t
    eigvals = np.linalg.eigvalsh(u)
    eigvals = np.sort(np.real(eigvals))[::-1]
    m = float(max(0.0, eigvals[0] + eigvals[1]))
    s_max = float(2.0 * np.sqrt(m))
    return s_max, m, (s_max > 2.0 + 1e-12)

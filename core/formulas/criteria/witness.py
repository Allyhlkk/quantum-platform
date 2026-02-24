import numpy as np

def get_werner_optimal_witness() -> np.ndarray:
    """
    构建针对 Werner 态的最优纠缠见证 (Entanglement Witness) 算符。
    """
    psi_minus = np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
    proj = np.outer(psi_minus, psi_minus.conj())
    return np.eye(4, dtype=complex) / 2.0 - proj

def witness_expectation(rho: np.ndarray, w_matrix: np.ndarray = None) -> float:
    """
    计算纠缠见证的期望值：Tr(W * rho)
    """
    rho = np.asarray(rho, dtype=complex)
    if w_matrix is None:
        w_matrix = get_werner_optimal_witness()
        
    expectation = np.trace(w_matrix @ rho)
    return float(expectation.real)
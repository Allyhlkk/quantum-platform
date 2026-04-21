import numpy as np
from core.formulas.measures.negativity import negativity


def log_negativity(rho: np.ndarray) -> float:
    """
    Log-Negativity for a two-qubit state.
    E_N = log2(2N + 1), where N is Negativity.
    """
    n = negativity(rho)
    return float(np.log2(2.0 * n + 1.0))

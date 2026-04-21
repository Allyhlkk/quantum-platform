import numpy as np
from core.formulas.measures.concurrence import concurrence


def tangle(rho: np.ndarray) -> float:
    """
    Tangle (squared concurrence) for two-qubit states.
    """
    c = concurrence(rho)
    return float(np.square(c))

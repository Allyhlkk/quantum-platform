def concurrence_werner(p: float) -> float:
    """
    Concurrence of two-qubit Werner state:
    C = max(0, (3p - 1) / 2)
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0, 1]")
    return max(0.0, (3.0 * p - 1.0) / 2.0)

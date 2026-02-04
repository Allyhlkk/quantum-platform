def witness_expectation_werner(p: float) -> float:
    """
    Expectation value of entanglement witness
    W = 1/2 I - |Psi-><Psi-|
    for Werner state.

    <W> = 1/4 - 3p/4
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0, 1]")
    return 0.25 - 0.75 * p

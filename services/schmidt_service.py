import numpy as np
from quantum.schmidt import schmidt_coefficients
from utils.explain import explain_schmidt


def analyze_schmidt(a, b, c, d):
    psi = np.array([[a, b],
                    [c, d]], dtype=float)

    coeffs = schmidt_coefficients(psi)
    rank = np.sum(coeffs > 1e-10)
    is_entangled = rank >= 2

    return {
        "coeffs": coeffs.tolist(),
        "rank": int(rank),
        "is_entangled": is_entangled,
        "explanation": explain_schmidt(rank)
    }

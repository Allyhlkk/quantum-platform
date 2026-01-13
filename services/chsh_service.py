# services/chsh_service.py
import numpy as np
from functools import lru_cache
from quantum.chsh import chsh_value
from utils.explain import explain_chsh


@lru_cache(maxsize=512)
def _analyze_cached(a, a_p, b, step):
    theta = np.arange(0, 2 * np.pi, step)
    S_vals = [abs(chsh_value(a, a_p, b, bp)) for bp in theta]
    S_max = max(S_vals)

    return {
        "theta": theta.tolist(),
        "S_vals": S_vals,
        "S_max": round(float(S_max), 4),
        "violation": bool(S_max > 2),
        "explanation": explain_chsh(float(S_max)),
    }


def analyze_chsh(a, a_p, b, step=0.02):
    return _analyze_cached(a, a_p, b, step)

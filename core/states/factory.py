import numpy as np

from core.states.werner import werner_state
from core.states.generalized import generalized_werner
from core.states.bell import psi_minus
from core.states.pure import pure_theta_state, pure_theta_density


def _norm_state_type(state_type: str) -> str:
    raw = (state_type or "werner").strip().lower()
    alias = {
        "gwerner": "generalized",
        "generalized_werner": "generalized",
        "bell_psi_minus": "bell",
        "psi_minus": "bell",
        "psi-": "bell",
        "pure": "pure_theta",
        "pure_theta_state": "pure_theta",
    }
    return alias.get(raw, raw)


def _clamp_theta(theta: float) -> float:
    if theta is None:
        return float(np.pi / 4)
    val = float(theta)
    if val < 0.0:
        return 0.0
    if val > float(np.pi / 2):
        return float(np.pi / 2)
    return val


def _clamp_p(p: float) -> float:
    if p is None:
        return 0.5
    val = float(p)
    if val < 0.0:
        return 0.0
    if val > 1.0:
        return 1.0
    return val


def density_state(state_type: str, p: float = None, theta: float = None) -> np.ndarray:
    t = _norm_state_type(state_type)
    if t == "werner":
        return werner_state(_clamp_p(p))
    if t == "generalized":
        return generalized_werner(_clamp_p(p), _clamp_theta(theta))
    if t == "bell":
        psi = psi_minus()
        return np.outer(psi, psi.conj())
    if t == "pure_theta":
        return pure_theta_density(_clamp_theta(theta))
    raise ValueError(f"Unknown state_type: {state_type}")


def vector_state(state_type: str, theta: float = None) -> np.ndarray:
    t = _norm_state_type(state_type)
    if t in ("bell", "werner"):
        return psi_minus()
    if t in ("generalized", "pure_theta"):
        return pure_theta_state(_clamp_theta(theta))
    raise ValueError(f"Unknown state_type: {state_type}")


def scan_state_generator(state_type: str, theta: float = None):
    t = _norm_state_type(state_type)
    if t == "werner":
        return werner_state
    if t == "generalized":
        theta_val = _clamp_theta(theta)
        return lambda p: generalized_werner(_clamp_p(p), theta_val)
    if t == "bell":
        rho = density_state("bell")
        return lambda p: rho
    if t == "pure_theta":
        rho = density_state("pure_theta", theta=_clamp_theta(theta))
        return lambda p: rho
    raise ValueError(f"Unknown state_type: {state_type}")

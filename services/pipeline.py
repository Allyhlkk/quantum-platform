from functools import lru_cache
import numpy as np

from core.results import AnalysisResult
from core.formulas.structure.schmidt_rank import schmidt_rank
from core.formulas.criteria.chsh import chsh_scan
from utils.explain import explain_schmidt, explain_chsh
from core.states.werner import werner_state
from core.formulas.criteria.ppt import ppt_min_eigenvalue_werner
from visualization.renderers.curve import scan_1d
from utils.explain import explain_ppt
from core.formulas.criteria.ppt import ppt_min_eigenvalue_werner
from core.formulas.measures.negativity import negativity_werner

# ==========================================================
# 工具函数：hash key
# ==========================================================

def _matrix_key(mat: np.ndarray) -> tuple:
    return tuple(mat.flatten())


def _state_key(state) -> tuple:
    if isinstance(state, np.ndarray):
        return tuple(state.flatten())
    raise TypeError(f"Unsupported state type: {type(state)}")


def _quantize(x: float, step: float) -> float:
    return round(float(x) / step) * step


# ==========================================================
# Schmidt
# ==========================================================

@lru_cache(maxsize=512)
def _run_schmidt_pipeline_cached(psi_key: tuple) -> AnalysisResult:
    psi = np.array(psi_key).reshape(2, 2)
    rank = schmidt_rank(psi)

    return AnalysisResult(
        values={
            "rank": rank,
            "is_entangled": rank >= 2
        },
        explanation=explain_schmidt(rank)
    )


def run_schmidt_pipeline(psi: np.ndarray) -> AnalysisResult:
    return _run_schmidt_pipeline_cached(_matrix_key(psi))


# ==========================================================
# CHSH
# ==========================================================

@lru_cache(maxsize=512)
def _run_chsh_pipeline_cached(
    state_key: tuple,
    a: float,
    a_p: float,
    b: float,
    step: float
) -> AnalysisResult:

    state = np.array(state_key)

    theta, S_vals, S_max = chsh_scan(state, a, a_p, b, step)

    return AnalysisResult(
        values={
            "theta": theta,        # ✅ numpy
            "S_vals": S_vals,      # ✅ numpy
            "S_max": float(S_max),
            "violation": S_max > 2,
        },
        explanation=explain_chsh(float(S_max))
    )


def run_chsh_pipeline(state, a, a_p, b, step=0.02) -> AnalysisResult:
    return _run_chsh_pipeline_cached(
        _state_key(state),
        _quantize(a, step),
        _quantize(a_p, step),
        _quantize(b, step),
        step
    )

# ==========================================================
# PPT
# ==========================================================

def run_werner_entanglement_pipeline(p: float) -> AnalysisResult:
    ppt_min = ppt_min_eigenvalue_werner(p)
    neg = negativity_werner(p)

    return AnalysisResult(
        values={
            "p": p,
            "ppt_min_eigenvalue": ppt_min,
            "ppt_entangled": ppt_min < 0,
            "negativity": neg
        },
        explanation=(
            "PPT 判据显示该态为纠缠态。" if ppt_min < 0
            else "PPT 判据未检测到纠缠。"
        )
    )
def run_werner_scan(step: float = 0.01):
    ps = np.arange(0.0, 1.0 + step, step)

    ppt_vals = []
    neg_vals = []

    for p in ps:
        ppt_vals.append(ppt_min_eigenvalue_werner(p))
        neg_vals.append(negativity_werner(p))

    return {
        "p": ps.tolist(),
        "ppt_min_eigenvalues": ppt_vals,
        "negativities": neg_vals,
    }
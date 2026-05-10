from functools import lru_cache
import numpy as np

from core.results import AnalysisResult
from core.formulas.structure.schmidt_rank import schmidt_rank
from core.formulas.criteria.chsh import chsh_scan
from utils.explain import explain_schmidt, explain_chsh

# ==========================================================
# 工具函数
# ==========================================================
def _matrix_key(mat: np.ndarray) -> tuple:
    return tuple(mat.flatten())

def _state_key(state) -> tuple:
    if isinstance(state, np.ndarray):
        return tuple(state.flatten())
    raise TypeError(f"Unsupported state type: {type(state)}")

def _quantize(x: float, step: float) -> float:
    return round(float(x) / step) * step


# 通用一维扫描器 (1D Scanner)
def universal_1d_scan(state_generator, metric_fn, p_start=0.0, p_end=1.0, step=0.01) -> dict:
    p_list = []
    val_list = []
    ps = np.arange(p_start, p_end + step / 2, step)
    
    for p in ps:
        p_val = round(float(p), 6)
        rho = state_generator(p_val) 
        val = metric_fn(rho)         
        p_list.append(p_val)
        val_list.append(val)
        
    return {"x": p_list, "y": val_list}

# 通用二维扫描器 (2D Scanner/3D Surface)
def universal_2d_scan(state_generator, metric_fn, p1_range, p2_range) -> dict:
    """
    生成用于 3D 曲面图或热力图的二维网格数据
    参数 range 格式: (start, end, step)
    """
    p1_start, p1_end, p1_step = p1_range
    p2_start, p2_end, p2_step = p2_range
    
    p1_vals = np.arange(p1_start, p1_end + p1_step / 2, p1_step)
    p2_vals = np.arange(p2_start, p2_end + p2_step / 2, p2_step)
    
    # 构造 Z 轴高度矩阵
    Z = np.zeros((len(p2_vals), len(p1_vals)))
    
    for j, p2 in enumerate(p2_vals):
        for i, p1 in enumerate(p1_vals):
            rho = state_generator(p1, p2)
            Z[j, i] = metric_fn(rho)
            
    return {
        "x": [round(float(v), 4) for v in p1_vals],
        "y": [round(float(v), 4) for v in p2_vals],
        "z": Z.tolist()
    }

# ==========================================================
# Schmidt & CHSH
# ==========================================================
@lru_cache(maxsize=512)
def _run_schmidt_pipeline_cached(psi_key: tuple) -> AnalysisResult:
    psi = np.array(psi_key).reshape(2, 2)
    rank = schmidt_rank(psi)
    return AnalysisResult(
        values={"rank": rank, "is_entangled": rank >= 2},
        explanation=explain_schmidt(rank)
    )

def run_schmidt_pipeline(psi: np.ndarray) -> AnalysisResult:
    return _run_schmidt_pipeline_cached(_matrix_key(psi))

@lru_cache(maxsize=512)
def _run_chsh_pipeline_cached(state_key: tuple, a: float, a_p: float, b: float, step: float) -> AnalysisResult:
    state = np.array(state_key)
    theta, S_vals, S_max = chsh_scan(state, a, a_p, b, step)
    return AnalysisResult(
        values={
            "theta": theta,
            "S_vals": S_vals,
            "S_max": float(S_max),
            "violation": S_max > 2,
        },
        explanation=explain_chsh(float(S_max))
    )

def run_chsh_pipeline(state, a, a_p, b, step=0.02) -> AnalysisResult:
    return _run_chsh_pipeline_cached(
        _state_key(state), _quantize(a, step), _quantize(a_p, step), _quantize(b, step), step
    )
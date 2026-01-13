import numpy as np

from quantum.ppt import (
    werner_state,
    is_entangled_ppt,
)
from visualization.ppt_plot import plot_ppt_spectrum
from utils.explain import explain_ppt


def analyze_ppt(p, scan_step=0.01):
    """
    PPT 判据实验分析（以 Werner 态为例）

    参数
    ----
    p : float
        当前噪声参数
    scan_step : float
        扫描 p 用于画谱线的步长

    返回
    ----
    dict
        {
            "p": float,
            "min_eigenvalue": float,
            "entangled": bool,
            "explanation": str,
            "spectrum": {...}   # 给 visualization 用
        }
    """

    # ========== 当前点分析 ==========
    rho = werner_state(p)
    entangled, min_eig, eigvals = is_entangled_ppt(rho)

    # ========== 扫描谱线（用于可视化） ==========
    p_vals = np.arange(0, 1 + scan_step, scan_step)
    min_eigs = []

    for pi in p_vals:
        rho_i = werner_state(pi)
        _, min_i, _ = is_entangled_ppt(rho_i)
        min_eigs.append(min_i)

    spectrum = {
        "p_vals": p_vals.tolist(),
        "min_eigs": [float(x) for x in min_eigs],
    }

    plot = plot_ppt_spectrum(
        spectrum["p_vals"],
        spectrum["min_eigs"],
        p
    )
    
    return {
        "p": float(p),
        "min_eigenvalue": float(min_eig),
        "entangled": bool(entangled),
        "explanation": explain_ppt(p, min_eig),
        "plot": plot,
    }


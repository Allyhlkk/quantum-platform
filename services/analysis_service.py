from services.pipeline import run_schmidt_pipeline, run_chsh_pipeline
from visualization.renderers.curve import render_curve


def analyze_schmidt(a, b, c, d):
    """
    Schmidt 分析（当前无曲线可视化）
    """
    import numpy as np

    psi = np.array([[a, b],
                    [c, d]], dtype=float)

    result = run_schmidt_pipeline(psi)

    # ⭐ Service 层统一做 Web-safe
    result.values = result.to_safe_dict()

    return result


def analyze_chsh(
    state,
    a,
    a_p,
    b,
    step=0.02,
    *,
    with_plot=False
):
    """
    CHSH 分析
    with_plot=True 时生成 matplotlib 曲线（base64）
    """
    result = run_chsh_pipeline(state, a, a_p, b, step)

    # ===== Web-safe =====
    result.values = result.to_safe_dict()

    # ===== 可选：生成静态分析图 =====
    if with_plot:
        result.values["plot"] = render_curve(
            x=result.values["theta"],
            y=result.values["S_vals"],
            title="CHSH Inequality",
            xlabel="θ (rad)",
            ylabel="|S|",
            theme="chsh",
            overlays=["bell_bound"]
        )

    return result

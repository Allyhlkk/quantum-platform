from services.pipeline import run_schmidt_pipeline, run_chsh_pipeline, run_werner_scan
from visualization.renderers.curve import render_curve
from core.formulas.criteria.ppt import ppt_min_eigenvalue_werner
from core.formulas.measures.negativity import negativity_werner
from core.formulas.measures.concurrence import concurrence_werner
from core.formulas.criteria.witness import witness_expectation_werner
from core.results import AnalysisResult

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

def analyze_werner(p: float) -> AnalysisResult:
    ppt_min = ppt_min_eigenvalue_werner(p)
    neg = negativity_werner(p)
    conc = concurrence_werner(p)

    return AnalysisResult(
        values={
            "p": p,
            "ppt_min_eigenvalue": ppt_min,
            "ppt_entangled": ppt_min < 0,
            "negativity": neg,
            "concurrence": conc,
        },
        explanation=(
            "PPT 判据检测到纠缠态。" if ppt_min < 0
            else "PPT 判据未检测到纠缠。"
        )
    )

def analyze_werner_scan(step: float = 0.01):
    """
    Werner 态 p ∈ [0,1] 扫描
    返回 PPT 最小特征值 & Negativity 曲线
    """
    return run_werner_scan(step)


def analyze_concurrence(p: float) -> AnalysisResult:
    """
    Concurrence analysis for Werner state
    """
    c = concurrence_werner(p)

    return AnalysisResult(
        values={
            "p": p,
            "concurrence": c,
            "entangled": c > 0,
        },
        explanation=(
            "Concurrence 大于 0，系统处于纠缠态。"
            if c > 0 else
            "Concurrence 为 0，系统为可分态。"
        )
    )

def analyze_concurrence_scan(step: float = 0.01):
    """
    p-scan for concurrence curve
    """
    p_list = []
    c_list = []

    n = int(1 / step) + 1
    for i in range(n):
        p = round(i * step, 6)
        p_list.append(p)
        c_list.append(concurrence_werner(p))

    return {
        "p": p_list,
        "concurrence": c_list,
    }


def analyze_witness(p: float) -> AnalysisResult:
    val = witness_expectation_werner(p)

    return AnalysisResult(
        values={
            "p": p,
            "witness": val,
            "entangled": val < 0,
        },
        explanation=(
            "纠缠见证期望值为负，检测到纠缠态。"
            if val < 0 else
            "纠缠见证期望值为正，未检测到纠缠。"
        )
    )

def analyze_witness_scan(step: float = 0.01):
    p_list = []
    w_list = []

    n = int(1 / step) + 1
    for i in range(n):
        p = round(i * step, 6)
        p_list.append(p)
        w_list.append(witness_expectation_werner(p))

    return {
        "p": p_list,
        "witness": w_list,
    }

import numpy as np
from services.pipeline import run_schmidt_pipeline, run_chsh_pipeline, universal_1d_scan, universal_2d_scan
from visualization.renderers.curve import render_curve

from core.states.werner import werner_state
from core.states.generalized import generalized_werner
from core.formulas.criteria.ppt import ppt_min_eigenvalue
from core.formulas.measures.negativity import negativity
from core.formulas.measures.concurrence import concurrence
from core.formulas.criteria.witness import witness_expectation
from core.formulas.measures.purity import purity
from core.formulas.measures.von_neumann import von_neumann_entropy
from core.formulas.measures.formation import entanglement_of_formation
from core.formulas.measures.fidelity import state_fidelity
from core.formulas.measures.coherence import l1_coherence
from core.formulas.measures.geometric import geometric_measure
from core.formulas.measures.linear_entropy import linear_entropy
from core.formulas.criteria.ccnr import ccnr_trace_norm
from core.formulas.criteria.reduction import reduction_min_eigenvalues
from core.formulas.criteria.chsh_horodecki import max_chsh_horodecki
from core.results import AnalysisResult

def analyze_schmidt(a, b, c, d):
    psi = np.array([[a, b], [c, d]], dtype=float)
    result = run_schmidt_pipeline(psi)
    result.values = result.to_safe_dict()
    return result

def analyze_chsh(state, a, a_p, b, step=0.02, *, with_plot=False):
    result = run_chsh_pipeline(state, a, a_p, b, step)
    result.values = result.to_safe_dict()
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

# =========================================================
# 1D 分析与扫描路由支持
# =========================================================
def analyze_werner(p: float) -> AnalysisResult:
    rho = werner_state(p)
    ppt_min = ppt_min_eigenvalue(rho)
    neg = negativity(rho)
    conc = concurrence(rho)
    pur = purity(rho)
    vn_ent = von_neumann_entropy(rho)
    eof = entanglement_of_formation(rho)

    return AnalysisResult(
        values={
            "p": p,
            "ppt_min_eigenvalue": ppt_min,
            "ppt_entangled": ppt_min < 0,
            "negativity": neg,
            "concurrence": conc,
            "purity": pur,
            "von_neumann": vn_ent,
            "formation": eof
        },
        explanation="PPT 判据检测到纠缠态。" if ppt_min < 0 else "PPT 判据未检测到纠缠。"
    )

def analyze_werner_scan(step: float = 0.01):
    ppt_res = universal_1d_scan(werner_state, ppt_min_eigenvalue, 0.0, 1.0, step)
    neg_res = universal_1d_scan(werner_state, negativity, 0.0, 1.0, step)
    pur_res = universal_1d_scan(werner_state, purity, 0.0, 1.0, step)
    
    return {
        "p": ppt_res["x"],
        "ppt_min_eigenvalues": ppt_res["y"],
        "negativities": neg_res["y"],
        "purities": pur_res["y"]
    }

def analyze_concurrence(p: float) -> AnalysisResult:
    rho = werner_state(p)
    c = concurrence(rho)
    return AnalysisResult(
        values={"p": p, "concurrence": c, "entangled": c > 0},
        explanation="Concurrence 大于 0，系统处于纠缠态。" if c > 0 else "Concurrence 为 0，系统为可分态。"
    )

def analyze_concurrence_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, concurrence, 0.0, 1.0, step)
    return {"p": res["x"], "concurrence": res["y"]}

def analyze_witness(p: float) -> AnalysisResult:
    rho = werner_state(p)
    val = witness_expectation(rho)
    return AnalysisResult(
        values={"p": p, "witness": val, "entangled": val < 0},
        explanation="纠缠见证期望值为负，检测到纠缠态。" if val < 0 else "纠缠见证期望值为正，未检测到纠缠。"
    )

def analyze_witness_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, witness_expectation, 0.0, 1.0, step)
    return {"p": res["x"], "witness": res["y"]}

def analyze_ccnr(p: float) -> AnalysisResult:
    rho = werner_state(p)
    norm_1 = ccnr_trace_norm(rho)
    return AnalysisResult(
        values={
            "p": p,
            "ccnr_trace_norm": norm_1,
            "entangled": norm_1 > 1.0
        },
        explanation="CCNR trace norm > 1, entanglement detected." if norm_1 > 1.0 else "CCNR trace norm <= 1, no entanglement detected by CCNR."
    )

def analyze_ccnr_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, ccnr_trace_norm, 0.0, 1.0, step)
    return {"p": res["x"], "ccnr_trace_norm": res["y"]}

def analyze_reduction(p: float) -> AnalysisResult:
    rho = werner_state(p)
    min_a, min_b = reduction_min_eigenvalues(rho)
    is_separable = (min_a >= 0.0) and (min_b >= 0.0)
    return AnalysisResult(
        values={
            "p": p,
            "reduction_min_a": min_a,
            "reduction_min_b": min_b,
            "entangled": not is_separable
        },
        explanation="Reduction criterion violated, entanglement detected." if not is_separable else "Reduction criterion not violated."
    )

def analyze_reduction_scan(step: float = 0.01):
    p_list = []
    min_a_list = []
    min_b_list = []

    ps = np.arange(0.0, 1.0 + step / 2, step)
    for p in ps:
        p_val = round(float(p), 6)
        rho = werner_state(p_val)
        min_a, min_b = reduction_min_eigenvalues(rho)
        p_list.append(p_val)
        min_a_list.append(min_a)
        min_b_list.append(min_b)

    return {"p": p_list, "reduction_min_a": min_a_list, "reduction_min_b": min_b_list}

def analyze_horodecki(p: float) -> AnalysisResult:
    rho = werner_state(p)
    s_max, m_val, violation = max_chsh_horodecki(rho)
    margin = s_max - 2.0
    return AnalysisResult(
        values={
            "p": p,
            "chsh_max": s_max,
            "horodecki_m": m_val,
            "violation": violation,
            "margin": margin,
        },
        explanation="CHSH violated (S_max > 2)." if violation else "No CHSH violation (S_max <= 2)."
    )

def analyze_horodecki_scan(step: float = 0.01):
    p_list = []
    s_list = []
    margin_list = []
    ps = np.arange(0.0, 1.0 + step / 2, step)
    for p in ps:
        p_val = round(float(p), 6)
        rho = werner_state(p_val)
        s_max, _, _ = max_chsh_horodecki(rho)
        p_list.append(p_val)
        s_list.append(float(s_max))
        margin_list.append(float(s_max - 2.0))
    return {"p": p_list, "chsh_max": s_list, "margin": margin_list}

def analyze_horodecki_map(resolution: int = 30):
    p_step = 1.0 / resolution
    theta_step = (np.pi / 2) / resolution
    p_vals = np.arange(0.0, 1.0 + p_step / 2, p_step)
    theta_vals = np.arange(0.0, float(np.pi / 2) + theta_step / 2, theta_step)

    s_grid = np.zeros((len(theta_vals), len(p_vals)))
    margin_grid = np.zeros((len(theta_vals), len(p_vals)))
    mask_grid = np.zeros((len(theta_vals), len(p_vals)))

    for j, theta in enumerate(theta_vals):
        for i, p in enumerate(p_vals):
            rho = generalized_werner(float(p), float(theta))
            s_max, _, violation = max_chsh_horodecki(rho)
            s_grid[j, i] = s_max
            margin_grid[j, i] = s_max - 2.0
            mask_grid[j, i] = 1.0 if violation else 0.0

    return {
        "x": [round(float(v), 4) for v in p_vals],
        "y": [round(float(v), 4) for v in theta_vals],
        "chsh_max": s_grid.tolist(),
        "margin": margin_grid.tolist(),
        "violation_mask": mask_grid.tolist(),
    }

def analyze_purity(p: float) -> AnalysisResult:
    rho = werner_state(p)
    pur = purity(rho)
    return AnalysisResult(
        values={"p": p, "purity": pur, "is_pure": pur >= 0.9999},
        explanation="系统为纯态 (Purity = 1)。" if pur >= 0.9999 else f"系统为混合态，纯度为 {pur:.4f}。"
    )

def analyze_purity_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, purity, 0.0, 1.0, step)
    return {"p": res["x"], "purity": res["y"]}

def analyze_linear_entropy(p: float) -> AnalysisResult:
    rho = werner_state(p)
    s_l = linear_entropy(rho)
    return AnalysisResult(
        values={"p": p, "linear_entropy": s_l, "is_pure": s_l <= 1e-10},
        explanation="State is pure (S_L ~= 0)." if s_l <= 1e-10 else f"State is mixed with S_L = {s_l:.4f}."
    )

def analyze_linear_entropy_scan(step: float = 0.01):
    s_res = universal_1d_scan(werner_state, linear_entropy, 0.0, 1.0, step)
    c_res = universal_1d_scan(werner_state, concurrence, 0.0, 1.0, step)
    return {
        "p": s_res["x"],
        "linear_entropy": s_res["y"],
        "concurrence": c_res["y"],
    }

def analyze_linear_entropy_phase(resolution: int = 30):
    p_step = 1.0 / resolution
    theta_step = (np.pi / 2) / resolution

    p_vals = np.arange(0.0, 1.0 + p_step / 2, p_step)
    theta_vals = np.arange(0.0, float(np.pi / 2) + theta_step / 2, theta_step)

    s_grid = np.zeros((len(theta_vals), len(p_vals)))
    c_grid = np.zeros((len(theta_vals), len(p_vals)))

    for j, theta in enumerate(theta_vals):
        for i, p in enumerate(p_vals):
            rho = generalized_werner(float(p), float(theta))
            s_grid[j, i] = linear_entropy(rho)
            c_grid[j, i] = concurrence(rho)

    # Werner curve in phase portrait (S_L, C) parameterized by p
    werner_ps = np.arange(0.0, 1.0 + 0.01 / 2, 0.01)
    werner_s = []
    werner_c = []
    for p in werner_ps:
        rho = werner_state(float(p))
        werner_s.append(float(linear_entropy(rho)))
        werner_c.append(float(concurrence(rho)))

    return {
        "x": [round(float(v), 4) for v in p_vals],
        "y": [round(float(v), 4) for v in theta_vals],
        "linear_entropy": s_grid.tolist(),
        "concurrence": c_grid.tolist(),
        "werner_curve": {
            "p": [round(float(v), 4) for v in werner_ps],
            "linear_entropy": werner_s,
            "concurrence": werner_c,
        },
    }

def analyze_von_neumann(p: float) -> AnalysisResult:
    rho = werner_state(p)
    ent = von_neumann_entropy(rho)
    return AnalysisResult(
        values={"p": p, "von_neumann": ent},
        explanation=f"冯·诺依曼熵为 {ent:.4f}。"
    )

def analyze_von_neumann_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, von_neumann_entropy, 0.0, 1.0, step)
    return {"p": res["x"], "von_neumann": res["y"]}

def analyze_formation_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, entanglement_of_formation, 0.0, 1.0, step)
    return {"p": res["x"], "formation": res["y"]}

def analyze_fidelity_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, state_fidelity, 0.0, 1.0, step)
    return {"p": res["x"], "fidelity": res["y"]}

def analyze_coherence_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, l1_coherence, 0.0, 1.0, step)
    return {"p": res["x"], "coherence": res["y"]}

def analyze_geometric_scan(step: float = 0.01):
    res = universal_1d_scan(werner_state, geometric_measure, 0.0, 1.0, step)
    return {"p": res["x"], "geometric": res["y"]}

# =========================================================
# 广义 Werner 态 3D 分析支持 (2D Scan)
# =========================================================
def analyze_advanced_3d_scan(resolution: int = 15):
    """
    生成 3D 曲面图所需的数据。
    """
    p_step = 1.0 / resolution
    theta_step = (np.pi / 2) / resolution
    
    p1_range = (0.0, 1.0, p_step)
    p2_range = (0.0, float(np.pi/2), theta_step)
    
# 定义执行扫描的辅助闭包，减少代码重复
    scan = lambda func: universal_2d_scan(generalized_werner, func, p1_range, p2_range)
    
    return {
            "concurrence": scan(concurrence),
            "formation": scan(entanglement_of_formation),
            "purity": scan(purity),
            "von_neumann": scan(von_neumann_entropy),
            "fidelity": scan(state_fidelity),
            "coherence": scan(l1_coherence),
            "geometric": scan(geometric_measure), # 新增
            "ppt": scan(ppt_min_eigenvalue),
            "negativity": scan(negativity)
        }

def analyze_criteria_compare_scan(resolution: int = 30):
    """
    Build p-theta heatmap data for PPT / CCNR / Reduction criteria.
    Returns criterion margins and a consensus count map (0..3).
    """
    p_step = 1.0 / resolution
    theta_step = (np.pi / 2) / resolution

    p_vals = np.arange(0.0, 1.0 + p_step / 2, p_step)
    theta_vals = np.arange(0.0, float(np.pi / 2) + theta_step / 2, theta_step)

    ppt_margin = np.zeros((len(theta_vals), len(p_vals)))
    ccnr_margin = np.zeros((len(theta_vals), len(p_vals)))
    reduction_margin = np.zeros((len(theta_vals), len(p_vals)))
    consensus = np.zeros((len(theta_vals), len(p_vals)))

    for j, theta in enumerate(theta_vals):
        for i, p in enumerate(p_vals):
            rho = generalized_werner(float(p), float(theta))

            ppt_min = ppt_min_eigenvalue(rho)
            ccnr_norm = ccnr_trace_norm(rho)
            red_a, red_b = reduction_min_eigenvalues(rho)
            red_min = min(red_a, red_b)

            ppt_detect = 1 if ppt_min < 0.0 else 0
            ccnr_detect = 1 if ccnr_norm > 1.0 else 0
            red_detect = 1 if red_min < 0.0 else 0

            ppt_margin[j, i] = -ppt_min
            ccnr_margin[j, i] = ccnr_norm - 1.0
            reduction_margin[j, i] = -red_min
            consensus[j, i] = ppt_detect + ccnr_detect + red_detect

    return {
        "x": [round(float(v), 4) for v in p_vals],
        "y": [round(float(v), 4) for v in theta_vals],
        "ppt_margin": ppt_margin.tolist(),
        "ccnr_margin": ccnr_margin.tolist(),
        "reduction_margin": reduction_margin.tolist(),
        "consensus": consensus.tolist()
    }

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
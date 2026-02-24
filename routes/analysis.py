from flask import Blueprint, render_template, request, jsonify, abort
from services.analysis_service import (analyze_schmidt, analyze_chsh, analyze_werner_scan, 
                                       analyze_concurrence, analyze_concurrence_scan, 
                                       analyze_witness, analyze_witness_scan, 
                                       analyze_advanced_3d_scan, analyze_purity_scan,
                                       analyze_von_neumann_scan, analyze_formation_scan,
                                       analyze_fidelity_scan, analyze_coherence_scan,
                                       analyze_geometric_scan
)
from core.formulas.measures.concurrence import concurrence
from core.states.generalized import generalized_werner
from services.pipeline import universal_1d_scan
from core.states.bell import psi_minus

from services.analysis_service import (
    analyze_schmidt,
    analyze_chsh,
    analyze_werner,     # ⭐ 新增
)


analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")


# ===============================
# 1️⃣ 实验大厅（左列表 + iframe）
# ===============================
@analysis_bp.route("/", methods=["GET"])
def analysis_hall():
    return render_template("analysis.html")


# ==========================================
# 2️⃣ 单个公式页面（iframe HTML，只负责展示）
# ==========================================
@analysis_bp.route("/formula/<formula_id>", methods=["GET", "POST"])
def formula_page(formula_id):
    """
    iframe 内页面
    - Schmidt: GET + POST
    - CHSH: 仅 GET（JS 调 API）
    - Werner: 仅 GET（JS 调 API）
    """
    result = None
    error = None

    try:
        # ---------- Schmidt ----------
        if formula_id == "schmidt":
            if request.method == "POST":
                a = float(request.form.get("a", 0))
                b = float(request.form.get("b", 0))
                c = float(request.form.get("c", 0))
                d = float(request.form.get("d", 0))

                result = analyze_schmidt(a, b, c, d)

            return render_template(
                "formulas/schmidt.html",
                result=result,
                error=error,
            )

        # ---------- CHSH ----------
        elif formula_id == "chsh":
            # ⚠️ CHSH 页面不处理 POST
            return render_template("formulas/chsh.html")

        # ---------- Werner ----------
        elif formula_id == "werner":
            # ⚠️ Werner 页面不处理 POST
            return render_template("formulas/werner.html")
        elif formula_id == "concurrence":
            # Concurrence 页面只负责展示，JS 调 API
            return render_template("formulas/concurrence.html")
        else:
            abort(404)

    except ValueError:
        error = "请输入合法的数值参数"
    except Exception as e:
        error = str(e)

    return render_template(
        f"formulas/{formula_id}.html",
        result=result,
        error=error,
    )


# ==========================================
# 3️⃣ CHSH API（前端可视化专用）
# ==========================================
@analysis_bp.route("/api/chsh", methods=["GET"])
def chsh_api():
    """
    /analysis/api/chsh?a=...&a_p=...&b=...
    """
    try:
        def q(x, step=0.02):
            return round(float(x) / step) * step

        a = q(request.args.get("a", 0))
        a_p = q(request.args.get("a_p", 0))
        b = q(request.args.get("b", 0))

        state = psi_minus()

        result = analyze_chsh(state, a, a_p, b)

        return jsonify({
            **result.values,
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================================
# 4️⃣ Werner API（PPT + Negativity）
# ==========================================
@analysis_bp.route("/api/werner", methods=["GET"])
def werner_api():
    """
    /analysis/api/werner?p=0.4
    """
    try:
        p = float(request.args.get("p", 0.0))

        if not (0.0 <= p <= 1.0):
            raise ValueError("p must be in [0, 1]")

        result = analyze_werner(p)

        return jsonify({
            **result.values,
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/werner/scan", methods=["GET"])
def werner_scan_api():
    """
    /analysis/api/werner/scan?step=0.01
    """
    try:
        step = float(request.args.get("step", 0.01))
        if step <= 0 or step > 0.1:
            raise ValueError("step must be in (0, 0.1]")

        data = analyze_werner_scan(step)

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@analysis_bp.route("/api/concurrence", methods=["GET"])
def concurrence_api():
    """
    /analysis/api/concurrence?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        result = analyze_concurrence(p)

        return jsonify({
            **result.values,
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@analysis_bp.route("/api/concurrence/scan", methods=["GET"])
def concurrence_scan_api():
    try:
        data = analyze_concurrence_scan(step=0.01)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@analysis_bp.route('/api/concurrence_dynamic_scan')
def concurrence_dynamic_scan_data():
    # 从前端获取滑块传来的 theta 值，默认为 pi/4
    theta_val = request.args.get('theta', default=np.pi/4, type=float)
    
    # 构造一个偏函数：固定 theta，只让 p 变化
    def target_state_func(p):
        return generalized_werner(p, theta=theta_val)
        
    # 扫描 p 从 0 到 1
    data = universal_1d_scan(target_state_func, concurrence, 0.0, 1.0, step=0.02)
    return jsonify({"p": data["x"], "concurrence": data["y"], "theta": theta_val})

@analysis_bp.route("/api/witness", methods=["GET"])
def witness_api():
    """
    /analysis/api/witness?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        result = analyze_witness(p)

        return jsonify({
            **result.values,
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/witness/scan", methods=["GET"])
def witness_scan_api():
    try:
        data = analyze_witness_scan(step=0.01)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 渲染独立的 Purity 页面
@analysis_bp.route('/purity')
def purity_page():
    return render_template('formulas/purity.html')

# 提供 Purity 1D 扫描数据
@analysis_bp.route('/api/purity_scan')
def purity_scan_data():
    data = analyze_purity_scan(step=0.01)
    return jsonify(data)

# 渲染 3D 页面
@analysis_bp.route('/advanced_3d')
def advanced_3d_page():
    return render_template('formulas/advanced_3d.html')

# 提供 3D 渲染所需的数据接口
@analysis_bp.route('/api/advanced_3d_data')
def advanced_3d_data():
    # resolution=20 表示生成一个 20x20 的网格
    data = analyze_advanced_3d_scan(resolution=20)
    return jsonify(data)

# 渲染独立的 Von Neumann Entropy 页面
@analysis_bp.route('/von_neumann')
def von_neumann_page():
    return render_template('formulas/von_neumann.html')

# 提供 Von Neumann 1D 扫描数据
@analysis_bp.route('/api/von_neumann_scan')
def von_neumann_scan_data():
    data = analyze_von_neumann_scan(step=0.01)
    return jsonify(data)

@analysis_bp.route('/formation')
def formation_page():
    return render_template('formulas/formation.html')

@analysis_bp.route('/api/formation_scan')
def formation_scan_data():
    data = analyze_formation_scan(step=0.01)
    return jsonify(data)

@analysis_bp.route('/fidelity')
def fidelity_page():
    return render_template('formulas/fidelity.html')

@analysis_bp.route('/api/fidelity_scan')
def fidelity_scan_data():
    data = analyze_fidelity_scan(step=0.01)
    return jsonify(data)

@analysis_bp.route('/coherence')
def coherence_page():
    return render_template('formulas/coherence.html')

@analysis_bp.route('/api/coherence_scan')
def coherence_scan_data():
    data = analyze_coherence_scan(step=0.01)
    return jsonify(data)

@analysis_bp.route('/geometric')
def geometric_page():
    return render_template('formulas/geometric.html')

@analysis_bp.route('/api/geometric_scan')
def geometric_scan_data():
    data = analyze_geometric_scan(step=0.01)
    return jsonify(data)
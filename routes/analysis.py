from flask import Blueprint, render_template, request, jsonify, abort
from services.analysis_service import analyze_schmidt, analyze_chsh, analyze_werner_scan, analyze_concurrence, analyze_concurrence_scan, analyze_witness, analyze_witness_scan

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

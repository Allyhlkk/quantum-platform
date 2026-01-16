from flask import Blueprint, render_template, request, jsonify, abort
from services.analysis_service import analyze_schmidt, analyze_chsh
from core.states.bell import psi_minus

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
            **result.values,                 # theta / S_vals / S_max / violation
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

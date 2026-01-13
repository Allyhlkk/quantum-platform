# routes/chsh.py
from flask import Blueprint, render_template, request, jsonify
from services.chsh_service import analyze_chsh

chsh_bp = Blueprint("chsh", __name__, url_prefix="/chsh")


@chsh_bp.route("/", methods=["GET"])
def chsh():
    return render_template("chsh.html", module_name="chsh")


@chsh_bp.route("/api", methods=["GET"])
def chsh_api():
    # 参数量化：防止缓存爆炸 + 抖动
    def q(x, step=0.02):
        return round(float(x) / step) * step

    a = q(request.args.get("a", 0))
    a_p = q(request.args.get("a_p", 0))
    b = q(request.args.get("b", 0))

    result = analyze_chsh(a, a_p, b)
    return jsonify(result)

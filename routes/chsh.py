from flask import Blueprint, render_template, request
from services.chsh_service import analyze_chsh

chsh_bp = Blueprint("chsh", __name__, url_prefix="/chsh")


@chsh_bp.route("/", methods=["GET", "POST"])
def chsh():
    if request.method == "POST":
        a = float(request.form["a"])
        a_p = float(request.form["a_p"])
        b = float(request.form["b"])

        result = analyze_chsh(a, a_p, b)

        return render_template(
            "chsh.html",
            module_name="chsh",
            result=result
        )

    return render_template("chsh.html", module_name="chsh")

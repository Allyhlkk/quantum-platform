from flask import Blueprint, render_template, request
from services.schmidt_service import analyze_schmidt

schmidt_bp = Blueprint("schmidt", __name__)


@schmidt_bp.route("/", methods=["GET", "POST"])
def schmidt():
    result = None
    error = None

    if request.method == "POST":
        try:
            a = float(request.form.get("a", 0))
            b = float(request.form.get("b", 0))
            c = float(request.form.get("c", 0))
            d = float(request.form.get("d", 0))

            result = analyze_schmidt(a, b, c, d)
        except ValueError:
            error = "请输入合法的数值参数"

    return render_template(
    "schmidt.html",
    module_name="schmidt",
    result=result
    )



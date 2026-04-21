from flask import Blueprint, render_template, request, jsonify, abort, Response
import numpy as np
from werkzeug.exceptions import HTTPException
from services.analysis_service import (analyze_schmidt, analyze_chsh, analyze_werner_scan, 
                                       analyze_concurrence, analyze_concurrence_scan,
                                       analyze_log_negativity, analyze_log_negativity_scan,
                                       analyze_tangle, analyze_tangle_scan,
                                       analyze_witness, analyze_witness_scan, 
                                       analyze_advanced_3d_scan, analyze_purity_scan,
                                       analyze_von_neumann_scan, analyze_formation_scan,
                                       analyze_fidelity_scan, analyze_coherence_scan,
                                       analyze_geometric_scan, analyze_ccnr, analyze_ccnr_scan,
                                       analyze_reduction, analyze_reduction_scan,
                                       analyze_criteria_compare_scan,
                                       analyze_horodecki, analyze_horodecki_scan, analyze_horodecki_map,
                                       analyze_linear_entropy, analyze_linear_entropy_scan, analyze_linear_entropy_phase,
                                       analyze_werner
)
from core.formulas.measures.concurrence import concurrence
from core.states.generalized import generalized_werner
from services.pipeline import universal_1d_scan
from core.states.bell import psi_minus
from core.states.factory import vector_state
from services.ml_service import run_ml_benchmark
from services.record_service import (
    create_record,
    list_records,
    get_record,
    delete_record,
    clear_records,
    update_record_note,
    export_records_csv,
)

analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")

def _state_args(default_type: str = "werner"):
    state_type = str(request.args.get("state_type", default_type)).strip() or default_type
    theta = request.args.get("theta", None, type=float)
    return state_type, theta


# ===============================
# 1️⃣ 实验大厅（左列表 + iframe）
# ===============================
@analysis_bp.route("/", methods=["GET"])
def analysis_hall():
    return render_template("analysis.html", module_name="analysis")


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
        elif formula_id == "log_negativity":
            return render_template("formulas/log_negativity.html")
        elif formula_id == "tangle":
            return render_template("formulas/tangle.html")
        elif formula_id == "ccnr":
            return render_template("formulas/ccnr.html")
        elif formula_id == "ppt":
            return render_template("formulas/ppt.html")
        elif formula_id == "reduction":
            return render_template("formulas/reduction.html")
        elif formula_id == "witness":
            return render_template("formulas/witness.html")
        elif formula_id == "chsh_horodecki":
            return render_template("formulas/chsh_horodecki.html")
        elif formula_id == "linear_entropy":
            return render_template("formulas/linear_entropy.html")
        else:
            abort(404)

    except HTTPException:
        raise
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

        state_type, theta = _state_args(default_type="bell")
        state = vector_state(state_type, theta=theta)
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

        state_type, theta = _state_args(default_type="werner")
        result = analyze_werner(p, state_type=state_type, theta=theta)

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

        state_type, theta = _state_args(default_type="werner")
        data = analyze_werner_scan(step, state_type=state_type, theta=theta)

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
        state_type, theta = _state_args(default_type="werner")
        result = analyze_concurrence(p, state_type=state_type, theta=theta)

        return jsonify({
            **result.values,
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@analysis_bp.route("/api/concurrence/scan", methods=["GET"])
def concurrence_scan_api():
    try:
        state_type, theta = _state_args(default_type="werner")
        data = analyze_concurrence_scan(step=0.01, state_type=state_type, theta=theta)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@analysis_bp.route("/api/log_negativity", methods=["GET"])
def log_negativity_api():
    """
    /analysis/api/log_negativity?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        state_type, theta = _state_args(default_type="werner")
        result = analyze_log_negativity(p, state_type=state_type, theta=theta)
        return jsonify({
            **result.values,
            "explanation": result.explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/log_negativity/scan", methods=["GET"])
def log_negativity_scan_api():
    try:
        state_type, theta = _state_args(default_type="werner")
        data = analyze_log_negativity_scan(step=0.01, state_type=state_type, theta=theta)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/tangle", methods=["GET"])
def tangle_api():
    """
    /analysis/api/tangle?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        state_type, theta = _state_args(default_type="werner")
        result = analyze_tangle(p, state_type=state_type, theta=theta)
        return jsonify({
            **result.values,
            "explanation": result.explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/tangle/scan", methods=["GET"])
def tangle_scan_api():
    try:
        state_type, theta = _state_args(default_type="werner")
        data = analyze_tangle_scan(step=0.01, state_type=state_type, theta=theta)
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
        state_type, theta = _state_args(default_type="werner")
        result = analyze_witness(p, state_type=state_type, theta=theta)

        return jsonify({
            **result.values,
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/witness/scan", methods=["GET"])
def witness_scan_api():
    try:
        state_type, theta = _state_args(default_type="werner")
        data = analyze_witness_scan(step=0.01, state_type=state_type, theta=theta)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/ccnr", methods=["GET"])
def ccnr_api():
    """
    /analysis/api/ccnr?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        state_type, theta = _state_args(default_type="werner")
        result = analyze_ccnr(p, state_type=state_type, theta=theta)
        return jsonify({
            **result.values,
            "explanation": result.explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/ccnr/scan", methods=["GET"])
def ccnr_scan_api():
    try:
        state_type, theta = _state_args(default_type="werner")
        data = analyze_ccnr_scan(step=0.01, state_type=state_type, theta=theta)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/reduction", methods=["GET"])
def reduction_api():
    """
    /analysis/api/reduction?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        state_type, theta = _state_args(default_type="werner")
        result = analyze_reduction(p, state_type=state_type, theta=theta)
        return jsonify({
            **result.values,
            "explanation": result.explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/reduction/scan", methods=["GET"])
def reduction_scan_api():
    try:
        state_type, theta = _state_args(default_type="werner")
        data = analyze_reduction_scan(step=0.01, state_type=state_type, theta=theta)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/chsh_horodecki", methods=["GET"])
def chsh_horodecki_api():
    """
    /analysis/api/chsh_horodecki?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        state_type, theta = _state_args(default_type="werner")
        result = analyze_horodecki(p, state_type=state_type, theta=theta)
        return jsonify({
            **result.values,
            "explanation": result.explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/chsh_horodecki/scan", methods=["GET"])
def chsh_horodecki_scan_api():
    try:
        step = float(request.args.get("step", 0.01))
        if step <= 0 or step > 0.1:
            raise ValueError("step must be in (0, 0.1]")
        state_type, theta = _state_args(default_type="werner")
        data = analyze_horodecki_scan(step=step, state_type=state_type, theta=theta)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/chsh_horodecki/map", methods=["GET"])
def chsh_horodecki_map_api():
    try:
        resolution = int(request.args.get("resolution", 30))
        if resolution < 10 or resolution > 100:
            raise ValueError("resolution must be in [10, 100]")
        data = analyze_horodecki_map(resolution=resolution)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/linear_entropy", methods=["GET"])
def linear_entropy_api():
    """
    /analysis/api/linear_entropy?p=0.5
    """
    try:
        p = float(request.args.get("p", 0.0))
        state_type, theta = _state_args(default_type="werner")
        result = analyze_linear_entropy(p, state_type=state_type, theta=theta)
        return jsonify({
            **result.values,
            "explanation": result.explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/linear_entropy/scan", methods=["GET"])
def linear_entropy_scan_api():
    try:
        step = float(request.args.get("step", 0.01))
        if step <= 0 or step > 0.1:
            raise ValueError("step must be in (0, 0.1]")
        state_type, theta = _state_args(default_type="werner")
        data = analyze_linear_entropy_scan(step=step, state_type=state_type, theta=theta)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route("/api/linear_entropy/phase", methods=["GET"])
def linear_entropy_phase_api():
    try:
        resolution = int(request.args.get("resolution", 30))
        if resolution < 10 or resolution > 100:
            raise ValueError("resolution must be in [10, 100]")
        data = analyze_linear_entropy_phase(resolution=resolution)
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
    state_type, theta = _state_args(default_type="werner")
    data = analyze_purity_scan(step=0.01, state_type=state_type, theta=theta)
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

@analysis_bp.route('/criteria_compare')
def criteria_compare_page():
    return render_template('formulas/criteria_compare.html')

@analysis_bp.route('/beginner_guide')
def beginner_guide_page():
    return render_template('formulas/beginner_guide.html')

@analysis_bp.route('/api/criteria_compare_data')
def criteria_compare_data():
    try:
        resolution = int(request.args.get("resolution", 30))
        if resolution < 10 or resolution > 80:
            raise ValueError("resolution must be in [10, 80]")
        data = analyze_criteria_compare_scan(resolution=resolution)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route('/ml_classifier')
def ml_classifier_page():
    return render_template('formulas/ml_classifier.html')

@analysis_bp.route('/api/ml/train', methods=['GET'])
def ml_train_api():
    try:
        n_samples = int(request.args.get("n_samples", 1200))
        seed = int(request.args.get("seed", 42))
        result = run_ml_benchmark(n_samples=n_samples, seed=seed)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 渲染独立的 Von Neumann Entropy 页面
@analysis_bp.route('/von_neumann')
def von_neumann_page():
    return render_template('formulas/von_neumann.html')

# 提供 Von Neumann 1D 扫描数据
@analysis_bp.route('/api/von_neumann_scan')
def von_neumann_scan_data():
    state_type, theta = _state_args(default_type="werner")
    data = analyze_von_neumann_scan(step=0.01, state_type=state_type, theta=theta)
    return jsonify(data)

@analysis_bp.route('/formation')
def formation_page():
    return render_template('formulas/formation.html')

@analysis_bp.route('/api/formation_scan')
def formation_scan_data():
    state_type, theta = _state_args(default_type="werner")
    data = analyze_formation_scan(step=0.01, state_type=state_type, theta=theta)
    return jsonify(data)

@analysis_bp.route('/fidelity')
def fidelity_page():
    return render_template('formulas/fidelity.html')

@analysis_bp.route('/api/fidelity_scan')
def fidelity_scan_data():
    state_type, theta = _state_args(default_type="werner")
    data = analyze_fidelity_scan(step=0.01, state_type=state_type, theta=theta)
    return jsonify(data)

@analysis_bp.route('/coherence')
def coherence_page():
    return render_template('formulas/coherence.html')

@analysis_bp.route('/api/coherence_scan')
def coherence_scan_data():
    state_type, theta = _state_args(default_type="werner")
    data = analyze_coherence_scan(step=0.01, state_type=state_type, theta=theta)
    return jsonify(data)

@analysis_bp.route('/geometric')
def geometric_page():
    return render_template('formulas/geometric.html')

@analysis_bp.route('/api/geometric_scan')
def geometric_scan_data():
    state_type, theta = _state_args(default_type="werner")
    data = analyze_geometric_scan(step=0.01, state_type=state_type, theta=theta)
    return jsonify(data)


@analysis_bp.route("/api/records", methods=["GET", "POST"])
def records_api():
    if request.method == "POST":
        try:
            payload = request.get_json(silent=True) or {}
            page_url = str(payload.get("page_url", "")).strip()
            page_title = str(payload.get("page_title", "")).strip()
            params = payload.get("params", {})
            explanation = str(payload.get("explanation", "")).strip()
            note = str(payload.get("note", "")).strip()

            if not isinstance(params, dict):
                raise ValueError("params must be an object")

            record = create_record(
                page_url=page_url,
                page_title=page_title,
                params=params,
                explanation=explanation,
                note=note,
            )
            return jsonify({"ok": True, "record": record})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    try:
        limit = int(request.args.get("limit", 100))
        query = str(request.args.get("q", "")).strip()
        records = list_records(limit=limit, query=query)
        return jsonify({"ok": True, "records": records})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@analysis_bp.route("/api/records/<int:record_id>", methods=["GET"])
def record_detail_api(record_id: int):
    try:
        record = get_record(record_id)
        if record is None:
            return jsonify({"ok": False, "error": "record not found"}), 404
        return jsonify({"ok": True, "record": record})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@analysis_bp.route("/api/records/<int:record_id>", methods=["DELETE"])
def record_delete_api(record_id: int):
    try:
        ok = delete_record(record_id)
        if not ok:
            return jsonify({"ok": False, "error": "record not found"}), 404
        return jsonify({"ok": True, "deleted_id": record_id})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@analysis_bp.route("/api/records/clear", methods=["POST"])
def records_clear_api():
    try:
        deleted_count = clear_records()
        return jsonify({"ok": True, "deleted_count": deleted_count})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@analysis_bp.route("/api/records/<int:record_id>/note", methods=["PATCH"])
def record_note_api(record_id: int):
    try:
        payload = request.get_json(silent=True) or {}
        note = str(payload.get("note", "")).strip()
        record = update_record_note(record_id, note)
        if record is None:
            return jsonify({"ok": False, "error": "record not found"}), 404
        return jsonify({"ok": True, "record": record})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@analysis_bp.route("/api/records/export.csv", methods=["GET"])
def records_export_csv_api():
    try:
        limit = int(request.args.get("limit", 1000))
        csv_text = export_records_csv(limit=limit)
        return Response(
            csv_text,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=experiment_records.csv"},
        )
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

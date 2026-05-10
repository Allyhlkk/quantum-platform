import numpy as np

from core.formulas.criteria.ccnr import ccnr_trace_norm
from core.formulas.criteria.ppt import ppt_min_eigenvalue
from core.formulas.criteria.reduction import reduction_min_eigenvalues
from core.formulas.criteria.witness import witness_expectation
from core.formulas.measures.concurrence import concurrence
from core.formulas.measures.negativity import negativity
from core.formulas.measures.purity import purity
from core.formulas.measures.von_neumann import von_neumann_entropy
from core.states.generalized import generalized_werner
from core.states.werner import werner_state


def _random_density_matrix(dim: int, rng: np.random.Generator) -> np.ndarray:
    a = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    rho = a @ a.conj().T
    return rho / np.trace(rho)


def _extract_features(rho: np.ndarray) -> list:
    ccnr_norm = ccnr_trace_norm(rho)
    red_a, red_b = reduction_min_eigenvalues(rho)
    red_min = min(red_a, red_b)
    neg = negativity(rho)
    pur = purity(rho)
    vn = von_neumann_entropy(rho)
    wit = witness_expectation(rho)
    return [ccnr_norm, red_min, neg, pur, vn, wit]


def _make_dataset(n_samples: int, seed: int):
    rng = np.random.default_rng(seed)

    feature_names = [
        "ccnr_trace_norm",
        "reduction_min_eig",
        "negativity",
        "purity",
        "von_neumann",
        "witness_expectation",
    ]

    x_rows = []
    y_rows = []

    n_werner = n_samples // 3
    n_generalized = n_samples // 3
    n_random = n_samples - n_werner - n_generalized

    for _ in range(n_werner):
        p = float(rng.uniform(0.0, 1.0))
        rho = werner_state(p)
        y = 1 if (ppt_min_eigenvalue(rho) < 0.0 or concurrence(rho) > 1e-10) else 0
        x_rows.append(_extract_features(rho))
        y_rows.append(y)

    for _ in range(n_generalized):
        p = float(rng.uniform(0.0, 1.0))
        theta = float(rng.uniform(0.0, np.pi / 2))
        rho = generalized_werner(p, theta)
        y = 1 if (ppt_min_eigenvalue(rho) < 0.0 or concurrence(rho) > 1e-10) else 0
        x_rows.append(_extract_features(rho))
        y_rows.append(y)

    for _ in range(n_random):
        rho = _random_density_matrix(4, rng)
        y = 1 if (ppt_min_eigenvalue(rho) < 0.0 or concurrence(rho) > 1e-10) else 0
        x_rows.append(_extract_features(rho))
        y_rows.append(y)

    x = np.asarray(x_rows, dtype=float)
    y = np.asarray(y_rows, dtype=int)
    dataset_meta = {
        "n_werner": int(n_werner),
        "n_generalized_werner": int(n_generalized),
        "n_random_density": int(n_random),
    }
    return x, y, feature_names, dataset_meta


def _safe_metrics(y_true, y_pred):
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    total = max(1, tp + tn + fp + fn)
    accuracy = (tp + tn) / total
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-12, precision + recall)

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": [[tn, fp], [fn, tp]],
    }


def _roc_payload(y_true, score, roc_curve_fn, auc_fn):
    fpr, tpr, _ = roc_curve_fn(y_true, score)
    return {
        "fpr": [float(v) for v in fpr],
        "tpr": [float(v) for v in tpr],
        "auc": float(auc_fn(fpr, tpr)),
    }


def _decision_projection_payload(
    logreg_model,
    svm_model,
    x_ref: np.ndarray,
    x_points: np.ndarray,
    y_points: np.ndarray,
    feature_names,
    x_idx: int = 0,
    y_idx: int = 3,
    grid_n: int = 80,
):
    """
    Build a 2D decision map by varying two selected features
    and fixing other features to reference mean.
    """
    x_min = float(np.min(x_ref[:, x_idx]))
    x_max = float(np.max(x_ref[:, x_idx]))
    y_min = float(np.min(x_ref[:, y_idx]))
    y_max = float(np.max(x_ref[:, y_idx]))

    x_pad = 0.08 * (x_max - x_min + 1e-12)
    y_pad = 0.08 * (y_max - y_min + 1e-12)
    xv = np.linspace(x_min - x_pad, x_max + x_pad, grid_n)
    yv = np.linspace(y_min - y_pad, y_max + y_pad, grid_n)
    xx, yy = np.meshgrid(xv, yv)

    base = np.mean(x_ref, axis=0)
    mesh = np.tile(base, (grid_n * grid_n, 1))
    mesh[:, x_idx] = xx.ravel()
    mesh[:, y_idx] = yy.ravel()

    lr_prob = logreg_model.predict_proba(mesh)[:, 1].reshape(grid_n, grid_n)
    svm_prob = svm_model.predict_proba(mesh)[:, 1].reshape(grid_n, grid_n)

    max_points = min(len(y_points), 700)
    pts_idx = np.arange(len(y_points))
    if len(y_points) > max_points:
        rng = np.random.default_rng(0)
        pts_idx = rng.choice(len(y_points), size=max_points, replace=False)

    x_pts = x_points[pts_idx, x_idx]
    y_pts = x_points[pts_idx, y_idx]
    l_pts = y_points[pts_idx]

    return {
        "x_feature": feature_names[x_idx],
        "y_feature": feature_names[y_idx],
        "x_grid": [float(v) for v in xv],
        "y_grid": [float(v) for v in yv],
        "logreg_prob": lr_prob.tolist(),
        "svm_prob": svm_prob.tolist(),
        "points": {
            "x": [float(v) for v in x_pts],
            "y": [float(v) for v in y_pts],
            "label": [int(v) for v in l_pts],
        },
    }


def run_ml_benchmark(n_samples: int = 1200, seed: int = 42) -> dict:
    if n_samples < 200:
        raise ValueError("n_samples must be >= 200")
    if n_samples > 20000:
        raise ValueError("n_samples must be <= 20000")

    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import auc, roc_curve
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC
    except Exception as exc:
        raise RuntimeError("scikit-learn is required for ML module. Please install scikit-learn.") from exc

    x, y, feature_names, dataset_meta = _make_dataset(n_samples=n_samples, seed=seed)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=seed, stratify=y
    )

    logreg = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, random_state=seed)),
        ]
    )
    svm = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", gamma="scale", C=2.0, probability=True, random_state=seed)),
        ]
    )

    logreg.fit(x_train, y_train)
    svm.fit(x_train, y_train)

    pred_logreg = logreg.predict(x_test)
    pred_svm = svm.predict(x_test)
    score_logreg = logreg.decision_function(x_test)
    score_svm = svm.decision_function(x_test)

    ent_ratio = float(np.mean(y))
    sep_ratio = float(1.0 - ent_ratio)

    coef = logreg.named_steps["clf"].coef_[0]
    feature_importance = sorted(
        (
            {
                "feature": name,
                "coef": float(c),
                "abs_coef": float(abs(c)),
            }
            for name, c in zip(feature_names, coef)
        ),
        key=lambda x: x["abs_coef"],
        reverse=True,
    )

    decision_projection = _decision_projection_payload(
        logreg_model=logreg,
        svm_model=svm,
        x_ref=x,
        x_points=x_test,
        y_points=y_test,
        feature_names=feature_names,
        x_idx=0,  # ccnr_trace_norm
        y_idx=2,  # negativity
        grid_n=80,
    )

    return {
        "meta": {
            "n_samples": int(n_samples),
            "n_train": int(len(y_train)),
            "n_test": int(len(y_test)),
            "entangled_ratio": ent_ratio,
            "separable_ratio": sep_ratio,
            "feature_names": feature_names,
            "label_rule": "entangled iff (ppt_min < 0) OR (concurrence > 0)",
            "dataset_sources": dataset_meta,
        },
        "logreg": {
            **_safe_metrics(y_test, pred_logreg),
            "roc": _roc_payload(y_test, score_logreg, roc_curve, auc),
        },
        "svm_rbf": {
            **_safe_metrics(y_test, pred_svm),
            "roc": _roc_payload(y_test, score_svm, roc_curve, auc),
        },
        "feature_importance": feature_importance,
        "decision_projection": decision_projection,
    }

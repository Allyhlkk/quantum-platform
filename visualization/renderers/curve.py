# visualization/renderers/curve.py
import matplotlib.pyplot as plt
import numpy as np

from typing import Callable, Tuple, List
from visualization.base import export_figure
from visualization.styles.default import STYLE as DEFAULT_STYLE
from visualization.styles import chsh as chsh_style
from visualization.overlays import bell_bound


STYLE_REGISTRY = {
    "default": DEFAULT_STYLE,
    "chsh": chsh_style.STYLE
}

OVERLAY_REGISTRY = {
    "bell_bound": bell_bound
}


def render_curve(
    x,
    y,
    *,
    title="",
    xlabel="",
    ylabel="",
    theme="default",
    overlays=None
):
    """
    通用一维曲线渲染器
    """
    colors = STYLE_REGISTRY.get(theme, DEFAULT_STYLE)
    overlays = overlays or []

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    # ===== 发光层 =====
    for lw, alpha in [(10, 0.04), (6, 0.08)]:
        ax.plot(
            x, y,
            color=colors["glow"],
            linewidth=lw,
            alpha=alpha
        )

    # ===== 主曲线 =====
    ax.plot(
        x, y,
        color=colors["main"],
        linewidth=2.5,
        label="value"
    )

    # ===== overlays（物理语义）=====
    for name in overlays:
        overlay = OVERLAY_REGISTRY.get(name)
        if overlay:
            overlay.draw(
                ax,
                color=colors.get("bound", "#CC3333")
            )

    # ===== 标注 =====
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    plt.tight_layout()
    return export_figure(fig)

def scan_1d(
    param_range: Tuple[float, float],
    step: float,
    generator: Callable[[float], np.ndarray],
    analyzer: Callable[[np.ndarray], float]
):
    """
    Generic 1D scan utility.

    Returns:
        params: list[float]
        values: list[float]
    """
    p_min, p_max = param_range
    params = np.arange(p_min, p_max + step, step)

    values: List[float] = []
    for p in params:
        state = generator(float(p))
        val = analyzer(state)
        values.append(float(val))

    return params, values
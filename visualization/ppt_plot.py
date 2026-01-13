import matplotlib
matplotlib.use("Agg")  # ✅ 非 GUI 后端，Flask 必须

import matplotlib.pyplot as plt
import numpy as np
import io
import base64


def plot_ppt_spectrum(p_vals, min_eigs, p_current):
    """
    绘制 PPT 判据谱线图

    参数
    ----
    p_vals : list[float]
        扫描的 p 值
    min_eigs : list[float]
        对应的最小特征值
    p_current : float
        当前实验点
    """

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    # ===== 主谱线 =====
    ax.plot(
        p_vals,
        min_eigs,
        color="#1f77b4",
        linewidth=2,
        label="min eigenvalue"
    )

    # ===== PPT 判据界线 =====
    ax.axhline(
        0,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label="PPT boundary"
    )

    # ===== 当前点 =====
    idx = np.argmin(np.abs(np.array(p_vals) - p_current))
    ax.scatter(
        [p_current],
        [min_eigs[idx]],
        color="orange",
        s=80,
        zorder=5,
        label=f"current p = {p_current:.2f}"
    )

    # ===== 美化 =====
    ax.set_xlabel("Noise parameter p")
    ax.set_ylabel("Minimum eigenvalue of ρ^{T_B}")
    ax.set_title("PPT Criterion Spectrum (Werner State)")

    ax.legend()
    ax.grid(alpha=0.3)

    # ===== 输出为 base64 =====
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)

    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return img_base64

import matplotlib.pyplot as plt
import io
import base64


def plot_chsh_curve(theta_range, S_vals, theme="chsh"):
    """
    绘制 CHSH 曲线并返回 base64 编码图片

    参数
    ----
    theta_range : array-like
        扫描的测量角度
    S_vals : array-like
        对应的 |S| 值
    theme : str
        配色主题（与前端 module_name 对应）
    """

    # === 1. 主题配色（统一视觉语言）===
    THEMES = {
        "chsh": {
            "main": "#7B6CF6",   # 刻晴紫
            "glow": "#C8C0FF",
            "bound": "#FF6A6A"
        },
        "default": {
            "main": "#444444",
            "glow": "#AAAAAA",
            "bound": "#CC3333"
        }
    }

    colors = THEMES.get(theme, THEMES["default"])

    # === 2. 创建画布 ===
    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    # === 3. 发光层（先画，粗、透明）===
    for lw, alpha in [(10, 0.04), (6, 0.08)]:
        ax.plot(
            theta_range,
            S_vals,
            color=colors["glow"],
            linewidth=lw,
            alpha=alpha
        )

    # === 4. 主曲线（后画，清晰）===
    ax.plot(
        theta_range,
        S_vals,
        color=colors["main"],
        linewidth=2.5,
        label="|S|"
    )

    # === 5. Bell 经典界限 ===
    ax.axhline(
        2,
        linestyle="--",
        linewidth=1,
        color=colors["bound"],
        label="Classical bound"
    )

    # === 6. 图形标注 ===
    ax.set_xlabel("θ (rad)")
    ax.set_ylabel("|S|")
    ax.set_title("CHSH Inequality Violation")

    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    plt.tight_layout()

    # === 7. 导出为 base64（给 Flask / AJAX 用）===
    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)

    return base64.b64encode(buf.getvalue()).decode("utf-8")

import numpy as np
from quantum.chsh import chsh_value
from visualization.chsh_plot import plot_chsh_curve
from utils.explain import explain_chsh


def analyze_chsh(a, a_p, b, step=0.02, theme="chsh"):
    """
    CHSH 实验分析服务
    - 计算完整 CHSH 曲线
    - 提取最大值
    - 生成可视化
    """

    #1. 参数扫描（实验本质）
    theta_range = np.arange(0, 2 * np.pi, step)

    S_vals = []
    for b_p in theta_range:
        S = abs(chsh_value(a, a_p, b, b_p))
        S_vals.append(S)

    S_max = max(S_vals)

    #2. 可视化（发光风格）
    plot = plot_chsh_curve(
        theta_range,
        S_vals,
        theme=theme
    )

    #3. 组织实验结果
    return {
        "S_max": round(S_max, 4),
        "violation": S_max > 2,
        "explanation": explain_chsh(S_max),
        "plot": plot,
    }

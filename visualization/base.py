# visualization/base.py
import io
import base64
import matplotlib.pyplot as plt


def export_figure(fig) -> str:
    """
    将 matplotlib Figure 导出为 base64 PNG
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, transparent=True)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

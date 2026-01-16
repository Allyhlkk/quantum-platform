# visualization/overlays/bell_bound.py
def draw(ax, *, bound=2, color="#FF6A6A"):
    """
    Bell 不等式经典上界 S <= 2
    """
    ax.axhline(
        bound,
        linestyle="--",
        linewidth=1,
        color=color,
        label="Classical bound"
    )

# core/formulas/__init__.py
from core.registry import register_formula, FormulaMeta

# ===== Schmidt =====
register_formula(
    FormulaMeta(
        id="schmidt",
        name="Schmidt 分解",
        category="纠缠结构分析",
        description="用于判断两比特纯态是否存在纠缠",
    )
)

# ===== CHSH =====
register_formula(
    FormulaMeta(
        id="chsh",
        name="CHSH 不等式",
        category="非定域性判据",
        description="通过 Bell 不等式检测量子非定域性",
    )
)

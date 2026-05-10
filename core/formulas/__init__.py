# core/formulas/__init__.py
from core.registry import FormulaMeta, register_formula


# ===== Schmidt =====
register_formula(
    FormulaMeta(
        id="schmidt",
        name="Schmidt 分解",
        category="量子态结构与基础性质",
        description="用于判断两比特纯态是否存在纠缠",
    )
)


# ===== CHSH =====
register_formula(
    FormulaMeta(
        id="chsh",
        name="CHSH 不等式",
        category="量子非定域性",
        description="通过 Bell 不等式检测量子非定域性",
    )
)


# ===== PPT =====
register_formula(
    FormulaMeta(
        id="ppt",
        name="PPT 判据",
        category="可分性判据",
        description="通过部分转置正定性检测混合态的纠缠",
    )
)


register_formula(
    FormulaMeta(
        id="concurrence",
        name="Concurrence",
        category="纠缠度量",
        description="基于纠缠量的混合态纠缠度量（Werner 态）",
    )
)


register_formula(
    FormulaMeta(
        id="witness",
        name="Entanglement Witness",
        category="可分性判据",
        description="通过纠缠见证算符的期望值检测量子纠缠",
    )
)

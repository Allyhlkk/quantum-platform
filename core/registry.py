# core/registry.py
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FormulaMeta:
    """
    单个公式在平台中的“注册信息”
    """
    id: str                 # 用于 URL / analysis_type
    name: str               # 展示名
    category: str           # 分类（纠缠结构 / 非定域性）
    description: str        # 简短说明
    enabled: bool = True    # 是否启用（规划中的可以 False）


# ========== 全局注册表 ==========
_FORMULA_REGISTRY: Dict[str, FormulaMeta] = {}


def register_formula(meta: FormulaMeta):
    if meta.id in _FORMULA_REGISTRY:
        raise ValueError(f"Formula '{meta.id}' already registered")
    _FORMULA_REGISTRY[meta.id] = meta


def get_all_formulas() -> List[FormulaMeta]:
    return list(_FORMULA_REGISTRY.values())


def get_formulas_by_category() -> Dict[str, List[FormulaMeta]]:
    """
    按 category 分组，供前端左侧列表使用
    """
    grouped: Dict[str, List[FormulaMeta]] = {}
    for meta in _FORMULA_REGISTRY.values():
        grouped.setdefault(meta.category, []).append(meta)
    return grouped

# core/results.py
from dataclasses import dataclass
from typing import Any, Dict
import numpy as np


def _to_safe(obj: Any):
    """
    递归地将 numpy / 非 JSON-safe 对象转为 Python 原生类型
    """
    # numpy scalar
    if isinstance(obj, np.generic):
        return obj.item()

    # numpy array
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # dict：⚠️ 强制 key 为 str
    if isinstance(obj, dict):
        return {
            str(k): _to_safe(v)
            for k, v in obj.items()
        }

    # list / tuple
    if isinstance(obj, (list, tuple)):
        return [_to_safe(x) for x in obj]

    # 其它类型（float / int / str / bool / None）
    return obj


@dataclass
class AnalysisResult:
    """
    ⭐ 统一分析结果对象
    """
    values: Dict[str, Any]
    explanation: str = ""

    def to_safe_dict(self) -> Dict[str, Any]:
        """
        ⭐ 核心出口：
        - 保证 dict key 全是 str
        - 保证 value 不含 numpy 对象
        """
        return _to_safe(self.values)

    def web_safe(self):
        """
        就地转换，供 service 层调用
        """
        self.values = self.to_safe_dict()
        return self

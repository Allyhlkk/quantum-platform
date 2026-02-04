import numpy as np

from core.states.werner import werner_state
from core.formulas.criteria.ppt import partial_transpose


def negativity_werner(p: float) -> float:
    """
    Negativity of 2-qubit Werner state.

    N(ρ) = sum_{λ_i < 0} |λ_i|
    where λ_i are eigenvalues of the partial transpose.
    """
    # 1. 构造 Werner 态
    rho = werner_state(p)

    # 2. 对第二个子系统做偏转置
    rho_pt = partial_transpose(rho, sys=1)

    # 3. 求偏转置的特征值
    eigvals = np.linalg.eigvals(rho_pt)

    # 4. Negativity = 负特征值的绝对值之和
    negativity = sum(abs(l) for l in eigvals if l.real < 0)

    return float(np.real_if_close(negativity))

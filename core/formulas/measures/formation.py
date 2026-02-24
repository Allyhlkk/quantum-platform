import numpy as np
from core.formulas.measures.concurrence import concurrence

def entanglement_of_formation(rho: np.ndarray) -> float:
    """
    计算两量子比特系统的形成纠缠度 (Entanglement of Formation)
    利用 Wootters 公式，通过 Concurrence 计算。
    值域为 [0, 1]，1 表示最大纠缠态。
    """
    c = concurrence(rho)
    
    if c <= 1e-12:
        return 0.0
    if c >= 0.999999:
        return 1.0
        
    x = (1 + np.sqrt(1 - c**2)) / 2.0
    
    # 计算二元香农熵
    eof = -x * np.log2(x) - (1 - x) * np.log2(1 - x)
    return float(eof)
import numpy as np

def von_neumann_entropy(rho: np.ndarray) -> float:
    """
    计算量子态的冯·诺依曼熵 (Von Neumann Entropy): S(rho) = -Tr(rho log2 rho)
    利用特征值计算：S = -sum(lambda_i * log2(lambda_i))
    纯态的熵为 0，最大混合态的熵为 log2(d)（两比特系统 d=4，最大熵为 2）
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (4, 4):
        raise ValueError("Von Neumann Entropy currently configured for 2-qubit (4x4) states.")
        
    eigvals = np.linalg.eigvals(rho).real
    
    # 过滤掉小于等于 0 的特征值（由于数值精度可能出现极小负数，且 log(0) 无定义）
    eigvals = eigvals[eigvals > 1e-12]
    
    entropy = -np.sum(eigvals * np.log2(eigvals))
    return float(entropy)
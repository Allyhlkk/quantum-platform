import numpy as np

def generalized_werner(p: float, theta: float) -> np.ndarray:
    """
    广义 Werner 态，受两个参数控制：
    p (0.0 ~ 1.0): 纯态部分的权重
    theta (0.0 ~ pi/2): 纯态的纠缠角度
    当 theta = pi/4 (45度) 且 p=1 时，为最大纠缠态。
    """
    # 构造态 |psi> = cos(theta)|00> + sin(theta)|11>
    psi = np.array([np.cos(theta), 0, 0, np.sin(theta)], dtype=complex)
    projector = np.outer(psi, psi.conj())
    
    identity = np.eye(4, dtype=complex) / 4.0
    rho = p * projector + (1 - p) * identity
    
    return rho
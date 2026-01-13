import numpy as np

# ===============================
# 基础工具
# ===============================

def is_hermitian(rho, tol=1e-10):
    """检查矩阵是否为厄米矩阵"""
    return np.allclose(rho, rho.conj().T, atol=tol)


def is_trace_one(rho, tol=1e-10):
    """检查迹是否为 1"""
    return abs(np.trace(rho) - 1.0) < tol


# ===============================
# 部分转置（PPT 核心）
# ===============================

def partial_transpose(rho, sys=1):
    """
    对两比特密度矩阵做部分转置

    参数
    ----
    rho : np.ndarray
        4x4 密度矩阵
    sys : int
        对哪个子系统转置
        sys = 0 → 对 A 转置
        sys = 1 → 对 B 转置（常用）

    返回
    ----
    rho_PT : np.ndarray
        部分转置后的矩阵
    """

    rho = np.asarray(rho)
    if rho.shape != (4, 4):
        raise ValueError("ρ must be a 4×4 matrix for two-qubit system.")

    # 重塑为 (i_A, i_B, j_A, j_B)
    rho_reshaped = rho.reshape(2, 2, 2, 2)

    if sys == 0:
        # 对 A 做转置：i_A <-> j_A
        rho_PT = rho_reshaped.transpose(2, 1, 0, 3)
    elif sys == 1:
        # 对 B 做转置：i_B <-> j_B
        rho_PT = rho_reshaped.transpose(0, 3, 2, 1)
    else:
        raise ValueError("sys must be 0 (A) or 1 (B)")

    return rho_PT.reshape(4, 4)


# ===============================
# PPT 判据
# ===============================

def ppt_eigenvalues(rho, sys=1):
    """
    计算部分转置后的特征值谱
    """
    rho_PT = partial_transpose(rho, sys=sys)
    eigvals = np.linalg.eigvalsh(rho_PT)
    return np.real_if_close(eigvals)


def is_entangled_ppt(rho, sys=1, tol=1e-10):
    """
    使用 PPT 判据判断是否纠缠

    返回
    ----
    entangled : bool
    min_eigenvalue : float
    eigvals : np.ndarray
    """
    eigvals = ppt_eigenvalues(rho, sys=sys)
    min_eig = np.min(eigvals)

    return (min_eig < -tol), float(min_eig), eigvals


# ===============================
# Werner 态（实验主角）
# ===============================

def bell_singlet():
    """
    |ψ^-> = (|01> - |10>) / sqrt(2)
    """
    psi = np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
    return np.outer(psi, psi.conj())


def werner_state(p):
    """
    Werner 态：
    ρ(p) = p |ψ^->⟨ψ^-| + (1-p) I/4

    参数
    ----
    p : float, 0 ≤ p ≤ 1
    """
    if not (0 <= p <= 1):
        raise ValueError("p must be in [0, 1]")

    rho_pure = bell_singlet()
    rho_mix = np.eye(4) / 4.0

    rho = p * rho_pure + (1 - p) * rho_mix
    return rho

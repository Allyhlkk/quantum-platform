def explain_schmidt(rank: int) -> str:
    if rank >= 2:
        return "Schmidt 秩为 2，系统处于纠缠态。"
    else:
        return "Schmidt 秩为 1，系统为可分态。"


def explain_chsh(S):
    if S > 2:
        return "CHSH 不等式被违反，系统表现出量子非定域性。"
    else:
        return "CHSH 不等式未被违反，结果符合局域隐变量理论。"


def explain_ppt(min_eig: float) -> str:
    """
    PPT 判据解释：
    根据偏转置最小特征值判断是否纠缠
    """
    if min_eig < 0:
        return "PPT 判据被违反，偏转置出现负特征值，系统为纠缠态。"
    else:
        return "PPT 判据未被违反，偏转置为半正定，系统为可分态。"

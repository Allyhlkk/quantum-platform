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

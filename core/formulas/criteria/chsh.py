import numpy as np
from core.observables.measurement import spin_measurement


def correlation(state, theta_a, theta_b):
    A = spin_measurement(theta_a)
    B = spin_measurement(theta_b)
    return np.vdot(state, np.kron(A, B) @ state).real


def chsh_value(state, a, a_p, b, b_p):
    return (
        correlation(state, a, b)
        + correlation(state, a, b_p)
        + correlation(state, a_p, b)
        - correlation(state, a_p, b_p)
    )


def chsh_scan(state, a, a_p, b, step=0.02):
    theta = np.arange(0, 2 * np.pi, step)
    S_vals = [abs(chsh_value(state, a, a_p, b, bp)) for bp in theta]
    return theta, S_vals, max(S_vals)

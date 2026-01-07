import numpy as np

# Pauli matrices
SIGMA_X = np.array([[0, 1], [1, 0]])
SIGMA_Z = np.array([[1, 0], [0, -1]])

# singlet state |psi->
psi_minus = (1 / np.sqrt(2)) * np.array([0, 1, -1, 0])


def measurement_operator(theta):
    return np.cos(theta) * SIGMA_Z + np.sin(theta) * SIGMA_X


def correlation(theta_a, theta_b):
    A = measurement_operator(theta_a)
    B = measurement_operator(theta_b)
    operator = np.kron(A, B)

    return np.vdot(psi_minus, operator @ psi_minus).real


def chsh_value(a, a_p, b, b_p):
    return (
        correlation(a, b)
        + correlation(a, b_p)
        + correlation(a_p, b)
        - correlation(a_p, b_p)
    )

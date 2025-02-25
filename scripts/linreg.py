import numpy as np


def estimate_coef(x, y):
    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x = np.mean(x)
    m_y = np.mean(y)

    # calculating cross-deviation and deviation about x
    ss_xy = np.sum(y * x) - n * m_y * m_x
    ss_xx = np.sum(x * x) - n * m_x * m_x

    # calculating regression coefficients
    b_1 = ss_xy / ss_xx
    b_0 = m_y - b_1 * m_x

    return b_0, b_1

def interpolate(x, x_list : list, y_list : list):
    return y_list[0] + (y_list[1] - y_list[0]) * (x - x_list[0]) / (x_list[1] - x_list[0])

import numpy as np

def vol_to_lgm(vol, const):
    """Converts volume to lgm"""
    return const[0] + const[1] * vol + const[2] * vol ** 2 + const[3] * vol ** 3

def gauss(x, amp, cen, sigma):
    """Gaussian function"""
    return amp * np.exp(-((x - cen) ** 2) / (2 * sigma ** 2))

def multi_gauss(x, *params):
    """
    Multi-Gaussian function: params = [amp1, cen1, sigma1, amp2, cen2, sigma2, ...]
    """
    n = len(params) // 3  # Number of Gaussians
    y = np.zeros_like(x)

    for i in range(n):
        amp = params[3 * i]
        cen = params[3 * i + 1]
        sigma = params[3 * i + 2]
        y += amp * np.exp(-((x - cen) ** 2) / (2 * sigma ** 2))

    return y
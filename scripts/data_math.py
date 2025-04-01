import numpy as np

def sort_data(x, y):
    """Combine x and y into pairs, sort by x, and unzip the result"""
    sorted_x, sorted_y = zip(*sorted(zip(x, y)))
    return list(sorted_x), list(sorted_y)

def normalize_second_by_point(x1, y1, x2, y2, x_target):
    """Normalize the second dataset by the intensity at a target point in the first dataset."""
    sorted_x1, sorted_y1 = zip(*sorted(zip(x1, y1)))
    sorted_x2, sorted_y2 = zip(*sorted(zip(x2, y2)))

    # Interpolate y-values at the target x value
    y1_target = np.interp(x_target, sorted_x1, sorted_y1)
    y2_target = np.interp(x_target, sorted_x2, sorted_y2)

    print(f"Target x: {x_target}, y1_target: {y1_target}, y2_target: {y2_target}")

    # Check if the second dataset intensity at the target point is zero
    if y2_target == 0:
        raise ValueError("Target intensity in the second dataset is 0, normalization is impossible.")

    # Calculate the scaling factor
    scale = y1_target / y2_target

    # Normalize the second dataset
    y2_norm = [y * scale for y in sorted_y2]

    return y2_norm


def subtract(x1, y1, x2, y2):
    """
    Subtracts the second dataset from the first by corresponding x-values.

    :param x1: List of x-values for the first dataset
    :param y1: List of y-values for the first dataset
    :param x2: List of x-values for the second dataset
    :param y2: List of y-values for the second dataset
    :return: A new list of y-values representing the difference between the first and second datasets at corresponding x
    """
    # Interpolate y2 to match the x-values of the first dataset (x1)
    y2_interpolated = np.interp(x1, x2, y2)

    # Subtract the y-values
    y_diff = [y1_i - y2_i for y1_i, y2_i in zip(y1, y2_interpolated)]

    return y_diff


def second_derivative(x, y, smooth_level=0):
    """
    Calculate the second derivative of the data points, optionally applying smoothing.

    :param x: List or array of x-values (independent variable)
    :param y: List or array of y-values (dependent variable)
    :param smooth_level: Number of points to smooth before computing the derivative. Default is 0 (no smoothing).
    :return: Tuple (new_x, new_y), where new_x is the same as input x and new_y is the second derivative of y.
    """

    # Apply smoothing if requested
    if smooth_level > 0:
        y = np.convolve(y, np.ones(smooth_level) / smooth_level, mode='same')

    # Compute the second derivative
    second_derivative_y = [y[i + 1] - 2 * y[i] + y[i - 1] for i in range(1, len(x) - 1)]

    # Return the result with x values as they are
    new_x = x[2 + smooth_level:-2 - smooth_level]  # Adjust x to match the range of the second derivative
    new_y = second_derivative_y[1 + smooth_level:-1 - smooth_level]

    return new_x, new_y
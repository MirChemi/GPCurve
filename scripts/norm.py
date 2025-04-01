def norm_0_1(data):
    """Normalize data to the range [0, 1]."""
    min_val, max_val = min(data), max(data)
    return [(y - min_val) / (max_val - min_val) for y in data]


def norm_1(data):
    """Normalize data to the maximum y-value of 1."""
    max_y = max(data)  # Find the maximum y-value

    if max_y == 0:  # Prevent division by zero
        raise ValueError("Maximum y-value is zero, cannot normalize.")

    return [y_i / max_y for y_i in data]

def normalize(data):
    min_val, max_val = min(data), max(data)
    return [(y - min_val) / (max_val - min_val) for y in data]
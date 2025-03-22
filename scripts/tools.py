def safe_float(value, default=None):
    return float(value.replace(',', '.')) if value else default

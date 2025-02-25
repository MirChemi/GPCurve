def safe_float(value):
    return float(value.replace(',', '.')) if value else None
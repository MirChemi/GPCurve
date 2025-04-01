def safe_float(value, default=None):
    """Converts a string to a float, or returns a default value if the conversion fails."""
    return float(value.replace(',', '.')) if value else default

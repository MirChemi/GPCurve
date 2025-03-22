def safe_float(value):
    return float(value.replace(',', '.')) if value else None

def vol_to_lgm(vol, const):
    return const[0] + const[1] * vol + const[2] * vol ** 2 + const[3] * vol ** 3
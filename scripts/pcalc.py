def calculate_peak(lgm, lgm_y):
    """Calculate peak parameters"""
    m_avg = []
    slice_start = []
    slice_end = []
    slice_avg = []
    i_start = []
    i_end = []
    i_avg = []
    slice_area = []
    sa_m = []
    sa_d_m = []

    for sl in range(len(lgm) - 1):
        m_avg.append((10 ** lgm[sl] + 10 ** lgm[sl + 1]) / 2)
        slice_start.append(lgm[sl])
        slice_end.append(lgm[sl + 1])
        slice_avg.append((slice_start[sl] + slice_end[sl]) / 2)
        i_start.append(lgm_y[sl])
        i_end.append(lgm_y[sl + 1])
        i_avg.append((i_start[sl] + i_end[sl]) / 2)
        slice_area.append(i_avg[sl] * abs(slice_end[sl] - slice_start[sl]))
        sa_m.append(slice_area[sl] * m_avg[sl])
        sa_d_m.append(slice_area[sl] / m_avg[sl])

    m_n = sum(slice_area) / sum(sa_d_m)
    m_w = sum(sa_m) / sum(slice_area)
    p_area = sum(slice_area)

    return m_n, m_w, p_area

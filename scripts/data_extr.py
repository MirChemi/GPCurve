from scripts import norm


def extract_data(data_filename, flag1, flag2):
    with open(data_filename, encoding="utf8") as f:
        data = f.readlines()
    while data and not data[0].startswith(flag1):
        data.pop(0)
    while data and not data[-1].startswith(flag2):
        data.pop(-1)
    vol = []
    vol_y = []
    vol_wt = []
    for i in range(len(data)):
        data_line = data[i].replace('\n', '').replace(',', '.').split('\t')
        vol.append(float(data_line[0]))
        vol_y.append(float(data_line[2]))

    for i in range(1,len(vol)):
        vol_wt.append((vol[i] - vol[i-1]) * (vol_y[i] + vol_y[i-1]) / 2)

    return vol, vol_y, vol_wt
import sys
import os
import configparser
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

import gpcurve
from scripts import linreg, norm, const_extr, data_extr, data_math, pcalc
from scripts.tools import safe_float, vol_to_lgm
from plot import Plot, Plot_vol

_debug = True
_pl = []

base_color = 'blue', 'red', 'green', 'black', 'yellow', 'magenta', 'cyan'
gauss_color = 'cyan', 'magenta', 'yellow', 'black', 'green', 'red', 'blue'

def main(*args):
    '''Main entry point for the application.'''
    global root, _top1, _w1, _use, _amp, _cen, _lock_cen, _sigma, _config

    root = TkinterDnD.Tk()
    root.protocol( 'WM_DELETE_WINDOW' , root.destroy)
    # Creates a toplevel widget.
    _config = configparser.ConfigParser()
    _config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    _top1 = root
    _w1 = gpcurve.Toplevel1(_top1)
    _w1.lb1.insert(1, "drag GPC txt data file")
    _w1.lb1.drop_target_register(DND_FILES)
    _w1.lb1.dnd_bind('<<Drop>>', lambda e: drop_file(_w1.lb1, e.data))
    _w1.lb2.insert(1, "drag constants pdf data file or folder")
    _w1.lb2.drop_target_register(DND_FILES)
    _w1.lb2.dnd_bind('<<Drop>>', lambda e: drop_file(_w1.lb2, e.data))
    if _config['conf']['const_path'] != '':
        _w1.lb2.insert(2, _config['conf']['const_path'])

    _w1.e_ff.insert(0, _config['conf']['flag1'])
    _w1.e_sf.insert(0, _config['conf']['flag2'])

    _use = [_w1.use1, _w1.use2, _w1.use3, _w1.use4, _w1.use5, _w1.use6]
    _amp = [_w1.a1, _w1.a2, _w1.a3, _w1.a4, _w1.a5, _w1.a6]
    _cen = [_w1.cn1, _w1.cn2, _w1.cn3, _w1.cn4, _w1.cn5, _w1.cn6]
    _lock_cen = [_w1.lock1, _w1.lock2, _w1.lock3, _w1.lock4, _w1.lock5, _w1.lock6]
    _sigma = [_w1.s1, _w1.s2, _w1.s3, _w1.s4, _w1.s5, _w1.s6]

    root.mainloop()

def drop_file(listbox, data):
    listbox.insert(1, data)
    listbox.delete(2)


def start():

    global _top1, _w1, _use, _amp, _cen, _lock_cen, _sigma, _config

    _config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    input1 = str(_w1.lb1.get(1))
    input2 = str(_w1.lb2.get(1))
    flag1 = str(_w1.e_ff.get())
    flag2 = str(_w1.e_sf.get())
    ex_name = input1.split("/")[-1].split(".")[0]

    if input2 != '':
        _config.set('conf', 'const_path', input2)
    _config.set('conf', 'flag1', flag1)
    _config.set('conf', 'flag2', flag2)
    with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w') as configfile:
        _config.write(configfile)

    if all([_w1.e_c0.get(), _w1.e_c1.get(), _w1.e_c2.get(), _w1.e_c3.get()]):
        const = [float(_w1.e_c0.get()), float(_w1.e_c1.get()), float(_w1.e_c2.get()), float(_w1.e_c3.get())]
    else:
        const = const_extr.extract_const(input2, input1)
    print('C0 - C3 = ' + str(const))

    vol, vol_y, vol_wt = data_extr.extract_data(input1, flag1, flag2)

    if not _w1.vol_plt.get():
        lgm, lgm_y = [], []
        for i in range(len(vol)):
            if _config.getboolean('conf', 'lin_calc'):
                c_lgm1 = float(_config['conf']['lin_lgm1'])
                c_lgm2 = float(_config['conf']['lin_lgm2'])
                c_vol1 = float(_config['conf']['lin_vol1'])
                c_vol2 = float(_config['conf']['lin_vol2'])
                lgm.append(linreg.interpolate(vol[i], [c_vol1, c_vol2], [c_lgm1, c_lgm2]))
            else:
                lgm.append(vol_to_lgm(vol[i], const))
            if i == 1:
                lgm_y.append(vol_wt[i - 1] / abs(lgm[i] - lgm[i - 1]))
                lgm_y.append(vol_wt[i - 1] / abs(lgm[i] - lgm[i - 1]))
            elif i > 1:
                lgm_y.append(2 * vol_wt[i - 1] / abs(lgm[i] - lgm[i - 1]) - lgm_y[i - 1])
        if _config.get('conf', 'norm_mode') == '01':
            lgm_y = norm.norm_0_1(lgm_y)
            print("Norm_0_1")
        elif _config.get('conf', 'norm_mode') == '1':
            lgm_y = norm.norm_1(lgm_y)
            print("Norm_1")

        lgm, lgm_y = data_math.sort_data(lgm, lgm_y)

        if not bool(_w1.reuse_fig.get()):
            _pl.append(Plot(lgm, lgm_y, ex_name, _w1.clean.get()))
        else:
            _pl[-1].add(lgm, lgm_y, ex_name, _w1.clean.get())

        if not _w1.clean.get():
            pk_lgm_p = [safe_float(_w1.e_sl.get()), safe_float(_w1.e_el.get())]
            pk_lgm_p_y = [safe_float(_w1.e_sb.get()), safe_float(_w1.e_eb.get())]
            if _w1.calc_type.get() == 1:
                pk_lgm_p[:2] = [vol_to_lgm(v, const) if v else v for v in pk_lgm_p[:2]]
                print('Recalculating peak position to lgm')
            _pl[-1].peak(pk_lgm_p, pk_lgm_p_y)
            _w1.Text1.insert(tk.END, f'peak position = {round(_pl[-1].pk_max, 4)}\t')
            _w1.Text1.insert(tk.END, f'Mn = {round(_pl[-1].m_n)}\t')
            _w1.Text1.insert(tk.END, f'Mw = {round(_pl[-1].m_w)}\t')
            _w1.Text1.insert(tk.END, f'Mw/Mn = {round(_pl[-1].m_w / _pl[-1].m_n, 4)}\n')
            _w1.Text1.insert(tk.END, f'peak area = {round(_pl[-1].p_area, 4)}\n')
    else:
        if bool(_w1.reuse_fig.get()):
            _pl.append(Plot_vol(vol, vol_y, ex_name, _w1.clean.get()))
        else:
            _pl[-1].add(vol, vol_y, ex_name, _w1.clean.get())

    _pl[-1].show()


def uncheck_gauss(*args):
    if _debug:
        print('main_support.uncheck_gauss')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

if __name__ == '__main__':
    gpcurve.start_up()





import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib import pyplot
from matplotlib.widgets import Button as bt
import numpy as np
import pdfplumber
from scipy.optimize import curve_fit
import clipboard
from colorama import just_fix_windows_console
from termcolor import cprint
import csv
from itertools import zip_longest
from statistics import mean

import config

base_color = 'blue', 'red', 'green', 'black'
gauss_color = 'cyan', 'magenta', 'yellow'
plot_number = 0


def main():
    try:
        just_fix_windows_console()
    except:
        print("Can't fix windows console for colored text")

    def clear_c():
        nonlocal number_gauss, amp, cen, lock_cen, sigma
        listbox_data.delete(1, END)
        entry_flag1.delete(0, END)
        entry_flag1.insert(0, config.flag1)
        entry_flag2.delete(0, END)
        entry_flag2.insert(0, config.flag2)
        entry_point1.delete(0, END)
        entry_point1.insert(0, 'auto')
        entry_point2.delete(0, END)
        entry_point2.insert(0, 'auto')
        entry_baseline1.delete(0, END)
        entry_baseline1.insert(0, 'auto')
        entry_baseline2.delete(0, END)
        entry_baseline2.insert(0, 'auto')
        number_gauss = 0
        button_gauss.config(text=f"ADD GAUSS({number_gauss})")
        amp = []
        cen = []
        lock_cen = []
        sigma = []

    def clear():
        clear_c()
        listbox_const.delete(1, END)

    def start():
        def copy_all(event):
            to_copy = ''
            for i in range(len(x)):
                to_copy += str(x[i])
                to_copy += '\t'
                to_copy += str(y[i])
                to_copy += '\n'
            clipboard.copy(to_copy)

        def copy_peak(event):
            to_copy = ''
            for i in range(len(x_peak)):
                to_copy += str(x_peak[i])
                to_copy += '\t'
                to_copy += str(y_peak[i])
                to_copy += '\n'
            clipboard.copy(to_copy)

        def all_to_csv(event):
            data_filename = str(listbox_data.get(1))
            csv_filename = data_filename.replace('.txt', '_GPCurve.csv')
            csv_data = [x, y, x_peak, y_peak]
            header_list = ['x_spectra', 'y_spectra', 'x_peak', 'y_peak']
            if len(amp) > 0:
                csv_data.append(x_peak)
                header_list.append('x_fit')
                csv_data.append(fit)
                header_list.append('y_fit')
                for gauss_number in range(len(amp)):
                    csv_data.append(x_peak)
                    header_list.append('x_gauss_' + str(gauss_number + 1))
                    csv_data.append(gac[gauss_number])
                    header_list.append('y_gauss_' + str(gauss_number + 1))

            csv_data = zip_longest(*csv_data, fillvalue='')
            with open(csv_filename, 'w', ) as f:
                writer = csv.writer(f)
                writer.writerow(header_list)
                writer.writerows(csv_data)

        def show_sec_der(event):
            x_der = []
            y_der = []
            for i in range(1, len(x) - 1):
                x_der.append(x[i])
                dy1 = (y[i] - y[i - 1]) / (x[i] - x[i - 1])
                dy2 = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
                y_der.append((dy2 - dy1) / ((x[i + 1] - x[i - 1]) / 2))
            x_der_smoothed = []
            y_der_smoothed = []
            step = config.der_smoothing_level
            for i in range(0, len(x_der), step):
                x_der_smoothed.append(mean(x_der[i:i + step - 1]))
                y_der_smoothed.append(mean(y_der[i:i + step - 1]))
            x_der_smoothed = np.array(x_der_smoothed)
            y_der_smoothed = np.array(y_der_smoothed)
            fig_d, axes_d = pyplot.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
            ax1_d = axes_d
            ax1_d.scatter(x_der_smoothed, y_der_smoothed)
            pyplot.show()

        def estimate_coef(x, y):
            # number of observations/points
            n = np.size(x)

            # mean of x and y vector
            m_x = np.mean(x)
            m_y = np.mean(y)

            # calculating cross-deviation and deviation about x
            SS_xy = np.sum(y * x) - n * m_y * m_x
            SS_xx = np.sum(x * x) - n * m_x * m_x

            # calculating regression coefficients
            b_1 = SS_xy / SS_xx
            b_0 = m_y - b_1 * m_x

            return b_0, b_1

        nonlocal amp, cen, lock_cen, sigma
        global ax1, plot_number
        flag1 = str(entry_flag1.get())
        flag2 = str(entry_flag2.get())
        input1 = str(listbox_data.get(1))
        input2 = str(listbox_const.get(1))
        if input2 != '':
            with open('const.txt', 'w') as fi:
                fi.write(input2)

        if '.pdf' not in input2:
            input1_pdf = input1.replace('.txt', '.pdf')
            print(input1_pdf)
            print(input1)
            with pdfplumber.open(input1_pdf) as pdf:
                page = pdf.pages[0]
                dt = page.extract_tables(table_settings={})
            dt = dt[0]
            for i in range(len(dt)):
                for j in range(len(dt[i])):
                    test = str(dt[i][j])
                    if 'Sequence' in test:
                        prefix = test
            prefix = prefix.split('\n')
            for i in range(len(prefix)):
                if 'Sequence' in str(prefix[i]):
                    prefix1 = str(prefix[i])
                    break
            prefix1 = prefix1.split(' ')
            for i in range(len(prefix1)):
                if '(' in str(prefix1[i]):
                    pr = str(prefix1[i])
                    break
            prefix = pr[6] + pr[7] + pr[8] + pr[9] + pr[3] + pr[4] + pr[0] + pr[1] + pr[-3] + pr[-2]
            name2 = input2 + '/' + prefix + '.pdf'
        else:
            name2 = input2
        print(name2)

        with pdfplumber.open(name2) as pdf:
            page = pdf.pages[0]
            ct = page.extract_tables(table_settings={})
        pre_const = []
        const = []
        for i in range(len(ct)):
            for j in range(len(ct[i])):
                if ct[i][j] == ['C0', 'C1', 'C2', 'C3']:
                    pre_const = ct[i][j + 1]
        for i in range(len(pre_const)):
            pre_const[i] = pre_const[i].replace(' ', '')
            pre_const[i] = pre_const[i].replace(',', '.')
            const.append(float(pre_const[i]))
        print('C0 - C3 = ' + str(const))

        with open(listbox_data.get(1), encoding="utf8") as f:
            print(str(f))
            data = f.readlines()

        finished = False
        while not finished:
            if flag1 in data[0]:
                finished = True
            else:
                data.pop(0)
        finished = False
        while not finished:
            if flag2 in data[-1]:
                finished = True
            else:
                data.pop(-1)
        x = []
        vol = []
        y = []
        if bool(do_fix.get()):
            print('lg intensity fixed')
        if config.lin_calc:
            print('lin_calc')
        for i in range(len(data)):
            data[i] = data[i].replace('\n', '')
            data[i] = data[i].replace(',', '.')
            li = data[i].split('\t')
            vl = float(li[0])
            vol.append(vl)
            if config.lin_calc:
                b1 = (config.lgm2 - config.lgm1) / (config.vol2 - config.vol1)
                b0 = config.lgm1 - b1 * config.vol1
                # b0 = (config.vol2 * config.lgm1 - config.vol1 * config.lgm2) / (config.lgm2 - config.lgm1)
                lgm = b0 + vl * b1
            else:
                lgm = const[0] + const[1] * vl + const[2] * vl * vl + const[3] * vl ** 3
            x.append(lgm)
            y.append(float(li[2]))

        for i in range(len(y)):
            y_fix = 1
            if bool(do_fix.get()) and i > 0:
                y_fix = (abs(vol[i] - vol[i - 1]) / abs(x[i] - x[i - 1])) ** 1
            y[i] = y[i] * y_fix

        y_min = min(y)
        for i in range(len(y)):
            y[i] = y[i] - y_min

        y_max = max(y)
        for i in range(len(y)):
            y[i] = y[i] / y_max

        if config.lin_approx:
            vol_for_lin = []
            lg_for_lin = []
            for i in range(len(x)):
                if y[i] > 0.1:
                    vol_for_lin.append(vol[i])
                    lg_for_lin.append(x[i])
            b0, b1 = estimate_coef(np.array(vol_for_lin), np.array(lg_for_lin))
            x = []
            for i in range(len(vol)):
                x.append(b0 + b1 * vol[i])

        index_max = y.index(max(y))
        plot_number += 1
        if bool(do_new_fig.get()):
            fig, axes = pyplot.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
            ax1 = axes
            plot_number = 0
        ax1.plot(x, y, 'k--', label='original')
        if bool(do_new_fig.get()):
            ax1.set_xlim(ax1.get_xlim()[::-1])
            ax_copy = fig.add_axes([0.9, 0.2, 0.1, 0.075])
            b_copy = bt(ax_copy, 'Copy\nspectra')
            b_copy.on_clicked(copy_all)

            ax_copy_p = fig.add_axes([0.9, 0.3, 0.1, 0.075])
            b_copy_p = bt(ax_copy_p, 'Copy\npeak')
            b_copy_p.on_clicked(copy_peak)

            ax_copy_a = fig.add_axes([0.9, 0.4, 0.1, 0.075])
            b_copy_a = bt(ax_copy_a, 'Save\nto csv')
            b_copy_a.on_clicked(all_to_csv)

            ax_der = fig.add_axes([0.9, 0.5, 0.1, 0.075])
            b_der = bt(ax_der, 'Show\n2nd der')
            b_der.on_clicked(show_sec_der)
        x_np = np.array(x)
        y_np = np.array(y)

        point1 = str(entry_point1.get())
        point2 = str(entry_point2.get())
        count = 0
        if 'auto' in point1:
            index_left_min = index_max
            flag = True
            while flag:
                if y[index_left_min - 2] <= y[index_left_min]:
                    index_left_min -= 1
                else:
                    flag = False
        else:
            count = 1
            index_left_min = x.index(min(x, key=lambda xx: abs(xx - float(point1))))

        if 'auto' in point2:
            index_right_min = index_max
            flag = True
            while flag:
                if y[index_right_min + 2] <= y[index_right_min]:
                    index_right_min += 1
                else:
                    flag = False
        else:
            if count == 1 and point1 <= point2:
                raise 'start lgM must be greater then end lgM'
            index_right_min = x.index(min(x, key=lambda xx: abs(xx - float(point2))))

        x_line = x_np[index_left_min], x_np[index_right_min]
        y_base = min(y_np[index_left_min], y_np[index_right_min])
        y_line = [y_base, y_base]

        baseline1 = str(entry_baseline1.get())
        baseline2 = str(entry_baseline2.get())
        if 'auto' not in baseline1:
            y_line[0] = float(baseline1)
        if 'auto' not in baseline2:
            y_line[1] = float(baseline2)

        k_line = -(y_line[1] - y_line[0]) / (x_line[0] - x_line[1])
        b_line = y_line[0] - k_line * x_line[0]
        ax1.plot(x_line, y_line, color=base_color[plot_number % len(base_color)], linestyle='dashdot', marker='x')

        x_peak = []
        vol_peak = []
        y_peak = []
        m_peak = []

        for i in range(index_right_min - index_left_min + 1):
            x_peak.append(x[i + index_left_min])
            vol_peak.append(vol[i + index_left_min])
            m_peak.append(10 ** x[i + index_left_min])
            y_peak.append(y[i + index_left_min] - (k_line * x[i + index_left_min] + b_line))

        def calculate_peak(x_pe, y_pe, text_color, back_color):

            if text_color == 'magenta':
                text_color = 'light_magenta'

            if text_color == 'cyan':
                text_color = 'light_cyan'

            if text_color == 'yellow':
                text_color = 'light_yellow'

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

            for ci in range(len(x_pe) - 1):
                m_avg.append((10 ** x_pe[ci] + 10 ** x_pe[ci + 1]) / 2)
                slice_start.append(x_pe[ci])
                slice_end.append(x_pe[ci + 1])
                slice_avg.append((slice_start[ci] + slice_end[ci]) / 2)
                i_start.append(y_pe[ci])
                i_end.append(y_pe[ci + 1])
                i_avg.append((i_start[ci] + i_end[ci]) / 2)
                slice_area.append(i_avg[ci] * abs(slice_end[ci] - slice_start[ci]))
                sa_m.append(slice_area[ci] * m_avg[ci])
                sa_d_m.append(slice_area[ci] / m_avg[ci])

            m_n = sum(slice_area) / sum(sa_d_m)
            m_w = sum(sa_m) / sum(slice_area)
            mwd = m_w / m_n

            cprint('Mn = ' + str(round(m_n)), text_color, back_color)
            cprint('Mw = ' + str(round(m_w)), text_color, back_color)
            cprint('Mw/Mn = ' + str(round(mwd, 3)), text_color, back_color)
            cprint('peak area = ' + str(round(sum(slice_area), 4)), text_color, back_color)
            cprint('number of slices = ' + str(len(x_pe) - 1), text_color, back_color)

        calculate_peak(x_peak, y_peak, base_color[plot_number % len(base_color)], 'on_white')
        ax1.plot(x_peak, y_peak, color=base_color[plot_number % len(base_color)])
        if len(amp) > 0:

            def func(x1, *params):
                y1 = np.zeros_like(x1)
                for i in range(0, len(params), 3):
                    ctr1 = params[i]
                    amp1 = params[i + 1]
                    wid1 = params[i + 2]
                    y1 = y1 + amp1 * np.exp(-0.5 * ((x1 - ctr1) / wid1) ** 2)
                return y1

            guess = []
            down_bounds = []
            up_bounds = []
            eps = 0.000000000000001
            for i in range(len(amp)):
                guess.append(cen[i])
                if lock_cen[i]:
                    down_bounds.append(cen[i] - eps)
                    up_bounds.append(cen[i] + eps)
                else:
                    down_bounds.append(-np.inf)
                    up_bounds.append(np.inf)

                guess.append(amp[i])
                down_bounds.append(0)
                up_bounds.append(np.inf)

                guess.append(sigma[i])
                down_bounds.append(-np.inf)
                up_bounds.append(np.inf)

            popt, pcov = curve_fit(func, x_peak, y_peak, p0=guess, bounds=[down_bounds, up_bounds], maxfev=100000)
            fit = func(x_peak, *popt)
            ax1.plot(x_peak, fit, color='orange')
            calculate_peak(x_peak, fit, 'light_red', 'on_black')
            gac = []
            print('center--amplitude--sigma')
            for ii in range(len(amp)):
                a = []
                a.append(float(popt[ii * 3]))
                a.append(float(popt[ii * 3 + 1]))
                a.append(float(popt[ii * 3 + 2]))
                a = np.array(a)
                print(a)
                gac.append(func(x_peak, *a))
                calculate_peak(x_peak, gac[ii], gauss_color[ii % len(gauss_color)], 'on_black')
                ax1.plot(x_peak, gac[ii], color=gauss_color[ii % len(gauss_color)])
        pyplot.show()

    root = TkinterDnD.Tk()  # instead of tk.Tk()
    root.geometry("400x300")

    for i in range(3):
        root.columnconfigure(index=i, weight=1)
    for i in range(10):
        root.rowconfigure(index=i, weight=1)

    listbox_data = tk.Listbox(root, width=10, height=1)
    listbox_data.insert(1, "drag GPC txt data file")
    listbox_data.drop_target_register(DND_FILES)
    listbox_data.dnd_bind('<<Drop>>', lambda e: listbox_data.insert(tk.END, e.data))
    listbox_data.grid(column=0, row=0, columnspan=3, rowspan=2, sticky="news")

    listbox_const = tk.Listbox(root, width=10, height=1)
    listbox_const.insert(1, "drag constants pdf data file or folder")
    try:
        with open('const.txt') as f:
            const_line = f.read()
        listbox_const.insert(2, const_line)
    except:
        print("no const.txt file")

    listbox_const.drop_target_register(DND_FILES)
    listbox_const.dnd_bind('<<Drop>>', lambda e: listbox_const.insert(tk.END, e.data))
    listbox_const.grid(column=0, row=2, columnspan=3, rowspan=2, sticky="news")

    button_start = Button(root, text="START", command=start)
    button_start.grid(column=0, row=4, sticky="news")

    button_clear = Button(root, text="CLEAR", command=clear)
    button_clear.grid(column=0, row=5, sticky="news")

    button_clear_c = Button(root, text="CLEAR -C", command=clear_c)
    button_clear_c.grid(column=0, row=6, sticky="news")

    number_gauss = 0

    amp = []
    cen = []
    lock_cen = []
    sigma = []

    def del_gauss(top):
        nonlocal number_gauss, amp, cen, lock_cen, sigma
        top.destroy()
        amp = []
        cen = []
        lock_cen = []
        sigma = []
        number_gauss = 0
        button_gauss.config(text=f"ADD GAUSS({number_gauss})")

    def popup_gauss():

        def close_gauss(top):
            nonlocal number_gauss, amp, cen, lock_cen, sigma
            amp.append(float(entry_amp.get()))
            cen.append(float(entry_cen.get()))
            lock_cen.append(bool(is_locked.get()))
            sigma.append(float(entry_sigma.get()))
            top.destroy()
            number_gauss += 1
            button_gauss.config(text=f"ADD GAUSS({number_gauss})")

        # Create a Toplevel window
        top = Toplevel(root)
        top.geometry("250x150")

        for i1 in range(3):
            top.columnconfigure(index=i1, weight=1)
        for i1 in range(4):
            top.rowconfigure(index=i1, weight=1)

        label_amp = ttk.Label(top, text="amplitude")
        label_amp.configure(anchor="center")
        label_amp.grid(column=0, row=0, sticky="news")

        entry_amp = Entry(top, width=10)
        entry_amp.insert(0, '1.0')
        entry_amp.grid(column=1, row=0)

        label_cen = ttk.Label(top, text="center")
        label_cen.configure(anchor="center")
        label_cen.grid(column=0, row=1, sticky="news")

        entry_cen = Entry(top, width=10)
        entry_cen.insert(0, '5.0')
        entry_cen.grid(column=1, row=1)

        label_sigma = ttk.Label(top, text="sigma")
        label_sigma.configure(anchor="center")
        label_sigma.grid(column=0, row=2, sticky="news")

        entry_sigma = Entry(top, width=10)
        entry_sigma.insert(0, '0.1')
        entry_sigma.grid(column=1, row=2)

        is_locked = IntVar(value=0)
        checkbutton_lock = ttk.Checkbutton(top, text="lock", variable=is_locked)
        checkbutton_lock.grid(column=2, row=1, sticky="news")

        button_ok = Button(top, text="Ok", command=lambda: close_gauss(top))
        button_ok.grid(column=0, row=3, sticky="news")

        button_del = Button(top, text="Del gauss", command=lambda: del_gauss(top))
        button_del.grid(column=1, row=3, sticky="news")

        top.mainloop()

    button_gauss = Button(root, text="ADD GAUSS(0)", command=popup_gauss)
    button_gauss.grid(column=0, row=7, sticky="news")

    do_fix = IntVar(value=0)
    checkbutton_fix = ttk.Checkbutton(text="fix lg intensity", variable=do_fix)
    checkbutton_fix.grid(column=0, row=8, sticky="news")

    do_new_fig = IntVar(value=1)
    checkbutton_new = ttk.Checkbutton(text="new figure", variable=do_new_fig)
    checkbutton_new.grid(column=0, row=9, sticky="news")

    label_flag1 = ttk.Label(text="first flag")
    label_flag1.configure(anchor="center")
    label_flag1.grid(column=1, row=4, sticky="news")

    entry_flag1 = Entry(root, width=10)
    entry_flag1.insert(0, config.flag1)
    entry_flag1.grid(column=2, row=4)

    label_flag2 = ttk.Label(text="second flag")
    label_flag2.configure(anchor="center")
    label_flag2.grid(column=1, row=5, sticky="news")

    entry_flag2 = Entry(root, width=10)
    entry_flag2.insert(0, config.flag2)
    entry_flag2.grid(column=2, row=5)

    label_point1 = ttk.Label(text="start lgM(.)")
    label_point1.configure(anchor="center")
    label_point1.grid(column=1, row=6, sticky="news")

    entry_point1 = Entry(root, width=10)
    entry_point1.insert(0, 'auto')
    entry_point1.grid(column=2, row=6)

    label_point2 = ttk.Label(text="end lgM(.)")
    label_point2.configure(anchor="center")
    label_point2.grid(column=1, row=7, sticky="news")

    entry_point2 = Entry(root, width=10)
    entry_point2.insert(0, 'auto')
    entry_point2.grid(column=2, row=7)

    label_baseline1 = ttk.Label(text="start base(.)")
    label_baseline1.configure(anchor="center")
    label_baseline1.grid(column=1, row=8, sticky="news")

    entry_baseline1 = Entry(root, width=10)
    entry_baseline1.insert(0, 'auto')
    entry_baseline1.grid(column=2, row=8)

    label_baseline2 = ttk.Label(text="end base(.)")
    label_baseline2.configure(anchor="center")
    label_baseline2.grid(column=1, row=9, sticky="news")

    entry_baseline2 = Entry(root, width=10)
    entry_baseline2.insert(0, 'auto')
    entry_baseline2.grid(column=2, row=9)

    root.mainloop()


if __name__ == '__main__':
    main()

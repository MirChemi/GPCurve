import tkinter as tk
from tkinter import ttk
import csv
import configparser
from itertools import zip_longest
from statistics import mean
import os

import clipboard
import pdfplumber
import numpy as np
from matplotlib import pyplot, widgets
from scipy.optimize import curve_fit
from tkinterdnd2 import DND_FILES, TkinterDnD

import linreg

base_color = 'blue', 'red', 'green', 'black', 'yellow', 'magenta', 'cyan'
gauss_color = 'cyan', 'magenta', 'yellow', 'black', 'green', 'red', 'blue'
plot_number = 0


def main():
    def clear():
        nonlocal number_gauss, amp, cen, lock_cen, sigma
        entry_point1.delete(0, tk.END)
        entry_point1.insert(0, 'auto')
        entry_point2.delete(0, tk.END)
        entry_point2.insert(0, 'auto')
        entry_baseline1.delete(0, tk.END)
        entry_baseline1.insert(0, 'auto')
        entry_baseline2.delete(0, tk.END)
        entry_baseline2.insert(0, 'auto')
        text_console.delete(1.0, tk.END)
        number_gauss = 0
        button_gauss.config(text=f"ADD GAUSS({number_gauss})")
        amp = []
        cen = []
        lock_cen = []
        sigma = []

    def start():
        def copy_spectra(event):
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
                    csv_data.append(gauss_curve[gauss_number])
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
            x_der_smoothed = np.empty(0)
            y_der_smoothed = np.empty(0)
            step = int(config['conf']['der_smoothing_level'])
            for i in range(0, len(x_der), step):
                x_der_smoothed = np.append(x_der_smoothed, mean(x_der[i:i + step - 1]))
                y_der_smoothed = np.append(y_der_smoothed, mean(y_der[i:i + step - 1]))
            fig_d, axes_d = pyplot.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
            ax1_d = axes_d
            ax1_d.scatter(x_der_smoothed, y_der_smoothed)
            pyplot.show()

        nonlocal amp, cen, lock_cen, sigma
        global ax1, plot_number

        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        flag1 = str(entry_flag1.get())
        flag2 = str(entry_flag2.get())
        input1 = str(listbox_data.get(1))
        ex_name = input1.split("/")[-1]
        ex_name = ex_name.split(".")[0]
        input2 = str(listbox_const.get(1))

        if input2 != '':
            config.set('conf', 'const_path', input2)
        config.set('conf', 'flag1', flag1)
        config.set('conf', 'flag2', flag2)
        with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w') as configfile:
            config.write(configfile)

        if '.pdf' not in input2:
            input1_pdf = input1.replace('.txt', '.pdf')
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
            prefix1 = prefix1.split(': ')
            for i in range(len(prefix1)):
                if '(' in str(prefix1[i]):
                    pr = str(prefix1[i])
                    if "RI" in pr:
                        gpc_type = "RI"
                    else:
                        gpc_type = "UV"
                    break
            prefix = pr[6] + pr[7] + pr[8] + pr[9] + pr[3] + pr[4] + pr[0] + pr[1] + gpc_type
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
        if config.getboolean('conf', 'lin_calc'):
            print('lin_calc')
        for i in range(len(data)):
            data[i] = data[i].replace('\n', '')
            data[i] = data[i].replace(',', '.')
            li = data[i].split('\t')
            vl = float(li[0])
            vol.append(vl)
            if config.getboolean('conf', 'lin_calc'):
                c_lgm1 = float(config['conf']['lgm2'])
                c_lgm2 = float(config['conf']['lgm2'])
                c_vol1 = float(config['conf']['vol1'])
                c_vol2 = float(config['conf']['vol2'])

                b1 = (c_lgm2 - c_lgm1) / (c_vol2 - c_vol1)
                b0 = c_lgm1 - b1 * c_vol1
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

        # to change cubic dependence between vol and lgM to linear one
        if config.getboolean('conf', 'lin_approx'):
            vol_for_lin = []
            lg_for_lin = []
            for i in range(len(x)):
                if y[i] > 0.1:
                    vol_for_lin.append(vol[i])
                    lg_for_lin.append(x[i])
            b0, b1 = linreg.estimate_coef(np.array(vol_for_lin), np.array(lg_for_lin))
            x = []
            for i in range(len(vol)):
                x.append(b0 + b1 * vol[i])

        index_max = y.index(max(y))
        plot_number += 1
        if bool(do_new_fig.get()):
            fig, ax1 = pyplot.subplots(figsize=(9.0, 7.0), sharex=True)
            ax1.set_position([0.07, 0.1, 0.8, 0.8])
            ax1.set_xlabel('lgM')
            plot_number = 0
        if bool(clear_plot.get()):
            ax1.plot(x, y, color=base_color[plot_number % len(base_color)], label=ex_name)
            ax1.legend()
        else:
            ax1.plot(x, y, 'k--', label=ex_name)
        if bool(do_new_fig.get()):
            ax1.set_xlim(ax1.get_xlim()[::-1])
            ax_copy = fig.add_axes([0.9, 0.2, 0.1, 0.075])
            b_copy = widgets.Button(ax_copy, 'Copy\nspectra')
            b_copy.on_clicked(copy_spectra)

            ax_copy_p = fig.add_axes([0.9, 0.3, 0.1, 0.075])
            b_copy_p = widgets.Button(ax_copy_p, 'Copy\npeak')
            b_copy_p.on_clicked(copy_peak)

            ax_copy_a = fig.add_axes([0.9, 0.4, 0.1, 0.075])
            b_copy_a = widgets.Button(ax_copy_a, 'Save\nto csv')
            b_copy_a.on_clicked(all_to_csv)

            ax_der = fig.add_axes([0.9, 0.5, 0.1, 0.075])
            b_der = widgets.Button(ax_der, 'Show\n2nd der')
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
        if not bool(clear_plot.get()):
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

        def calculate_peak(x_pe, y_pe, text_color):

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

            for sl in range(len(x_pe) - 1):
                m_avg.append((10 ** x_pe[sl] + 10 ** x_pe[sl + 1]) / 2)
                slice_start.append(x_pe[sl])
                slice_end.append(x_pe[sl + 1])
                slice_avg.append((slice_start[sl] + slice_end[sl]) / 2)
                i_start.append(y_pe[sl])
                i_end.append(y_pe[sl + 1])
                i_avg.append((i_start[sl] + i_end[sl]) / 2)
                slice_area.append(i_avg[sl] * abs(slice_end[sl] - slice_start[sl]))
                sa_m.append(slice_area[sl] * m_avg[sl])
                sa_d_m.append(slice_area[sl] / m_avg[sl])

            m_n = sum(slice_area) / sum(sa_d_m)
            m_w = sum(sa_m) / sum(slice_area)
            mwd = m_w / m_n

            text_console.insert(tk.END, 'Mn = ' + str(round(m_n)) + '\t', text_color)
            text_console.insert(tk.END, 'Mw = ' + str(round(m_w)) + '\t', text_color)
            text_console.insert(tk.END, 'Mw/Mn = ' + str(round(mwd, 3)) + '\n', text_color)
            text_console.insert(tk.END, 'peak area = ' + str(round(sum(slice_area), 4)) + '\n', text_color)
            text_console.insert(tk.END, 'number of slices = ' + str(len(x_pe) - 1) + '\n', text_color)

        calculate_peak(x_peak, y_peak, base_color[plot_number % len(base_color)])
        if not bool(clear_plot.get()):
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
            calculate_peak(x_peak, fit, 'orange')
            gauss_curve = []
            print('center--amplitude--sigma')
            for i in range(len(amp)):
                a = [float(popt[i * 3]), float(popt[i * 3 + 1]), float(popt[i * 3 + 2])]
                a = np.array(a)
                print(a)
                gauss_curve.append(func(x_peak, *a))
                calculate_peak(x_peak, gauss_curve[i], gauss_color[i % len(gauss_color)])
                ax1.plot(x_peak, gauss_curve[i], color=gauss_color[i % len(gauss_color)])
        pyplot.show()

    root = TkinterDnD.Tk()  # instead of tk.Tk()
    root.geometry("700x300")
    root.title('GPCurve')

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

    for i in range(6):
        root.columnconfigure(index=i, weight=1)
    for i in range(10):
        root.rowconfigure(index=i, weight=1)

    def drop_file(listbox, data):
        listbox.insert(1, data)
        listbox.delete(2)

    listbox_data = tk.Listbox(root, width=1, height=1)
    listbox_data.insert(1, "drag GPC txt data file")
    listbox_data.drop_target_register(DND_FILES)
    listbox_data.dnd_bind('<<Drop>>', lambda e: drop_file(listbox_data, e.data))
    listbox_data.grid(column=0, row=0, columnspan=3, rowspan=2, sticky="news")

    listbox_const = tk.Listbox(root, width=1, height=1)
    listbox_const.insert(1, "drag constants pdf data file or folder")

    if config['conf']['const_path'] != '':
        listbox_const.insert(2, config['conf']['const_path'])

    listbox_const.drop_target_register(DND_FILES)
    listbox_const.dnd_bind('<<Drop>>', lambda e: drop_file(listbox_const, e.data))
    listbox_const.grid(column=0, row=2, columnspan=3, rowspan=2, sticky="news")

    button_start = tk.Button(root, text="START", command=start)
    button_start.grid(column=0, row=4, sticky="news")

    button_clear = tk.Button(root, text="CLEAR", command=clear)
    button_clear.grid(column=0, row=5, sticky="news")

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
        top = tk.Toplevel(root)
        top.geometry("250x150")

        for i in range(3):
            top.columnconfigure(index=i, weight=1)
        for i in range(4):
            top.rowconfigure(index=i, weight=1)

        label_amp = tk.Label(top, text="amplitude")
        label_amp.configure(anchor="center")
        label_amp.grid(column=0, row=0)

        entry_amp = tk.Entry(top, width=10)
        entry_amp.insert(0, '1.0')
        entry_amp.grid(column=1, row=0)

        label_cen = tk.Label(top, text="center")
        label_cen.configure(anchor="center")
        label_cen.grid(column=0, row=1)

        entry_cen = tk.Entry(top, width=10)
        entry_cen.insert(0, '5.0')
        entry_cen.grid(column=1, row=1)

        label_sigma = tk.Label(top, text="sigma")
        label_sigma.configure(anchor="center")
        label_sigma.grid(column=0, row=2)

        entry_sigma = tk.Entry(top, width=10)
        entry_sigma.insert(0, '0.1')
        entry_sigma.grid(column=1, row=2)

        is_locked = tk.IntVar(value=0)
        checkbutton_lock = tk.Checkbutton(top, text="lock", variable=is_locked)
        checkbutton_lock.grid(column=2, row=1, sticky="news")

        button_ok = tk.Button(top, text="Ok", command=lambda: close_gauss(top))
        button_ok.grid(column=0, row=3, sticky="news")

        button_del = tk.Button(top, text="Del gauss", command=lambda: del_gauss(top))
        button_del.grid(column=1, row=3, sticky="news")

        top.mainloop()

    button_gauss = tk.Button(root, text="ADD GAUSS(0)", command=popup_gauss)
    button_gauss.grid(column=0, row=6, sticky="news")

    do_fix = tk.IntVar(value=0)
    checkbutton_fix = ttk.Checkbutton(text="fix lg intensity", variable=do_fix)
    checkbutton_fix.grid(column=0, row=7, sticky="news")

    do_new_fig = tk.IntVar(value=1)
    checkbutton_new = ttk.Checkbutton(text="new figure", variable=do_new_fig)
    checkbutton_new.grid(column=0, row=8, sticky="news")

    clear_plot = tk.IntVar(value=1)
    checkbutton_clear = ttk.Checkbutton(text="clear plot", variable=clear_plot)
    checkbutton_clear.grid(column=0, row=9, sticky="news")

    label_flag1 = tk.Label(text="first flag")
    label_flag1.configure(anchor="center")
    label_flag1.grid(column=1, row=4)

    entry_flag1 = tk.Entry(root, width=10)
    entry_flag1.insert(0, config['conf']['flag1'])
    entry_flag1.grid(column=2, row=4)

    label_flag2 = tk.Label(text="second flag")
    label_flag2.configure(anchor="center")
    label_flag2.grid(column=1, row=5)

    entry_flag2 = tk.Entry(root, width=10)
    entry_flag2.insert(0, config['conf']['flag2'])
    entry_flag2.grid(column=2, row=5)

    label_point1 = tk.Label(text="start lgM(.)")
    label_point1.configure(anchor="center")
    label_point1.grid(column=1, row=6)

    entry_point1 = tk.Entry(root, width=10)
    entry_point1.insert(0, 'auto')
    entry_point1.grid(column=2, row=6)

    label_point2 = tk.Label(text="end lgM(.)")
    label_point2.configure(anchor="center")
    label_point2.grid(column=1, row=7)

    entry_point2 = tk.Entry(root, width=10)
    entry_point2.insert(0, 'auto')
    entry_point2.grid(column=2, row=7)

    label_baseline1 = tk.Label(text="start base(.)")
    label_baseline1.configure(anchor="center")
    label_baseline1.grid(column=1, row=8)

    entry_baseline1 = tk.Entry(root, width=10)
    entry_baseline1.insert(0, 'auto')
    entry_baseline1.grid(column=2, row=8)

    label_baseline2 = tk.Label(text="end base(.)")
    label_baseline2.configure(anchor="center")
    label_baseline2.grid(column=1, row=9)

    entry_baseline2 = tk.Entry(root, width=10)
    entry_baseline2.insert(0, 'auto')
    entry_baseline2.grid(column=2, row=9)

    label_console = tk.Label(text="Console:")
    label_baseline2.configure(anchor="n")
    label_console.grid(column=3, row=0, sticky="n")

    text_console = tk.Text(root, width=20, height=1)
    text_console.grid(column=3, row=1, columnspan=3, rowspan=9, sticky="news")
    text_console.tag_config('blue', foreground="blue")
    text_console.tag_config('red', foreground="red")
    text_console.tag_config('green', foreground="green")
    text_console.tag_config('black', foreground="black")
    text_console.tag_config('cyan', foreground="cyan", background="black")
    text_console.tag_config('magenta', foreground="magenta", background="black")
    text_console.tag_config('yellow', foreground="yellow", background="black")
    text_console.tag_config('orange', foreground="orange", background="black")

    root.mainloop()


if __name__ == '__main__':
    main()

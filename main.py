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

base_color = 'blue', 'red', 'green', 'black'
gauss_color = 'cyan', 'magenta', 'yellow'
plot_number = 0
just_fix_windows_console()


def main():
    def clear_noc():
        nonlocal number_gauss, amp, cen, sigma
        lb1.delete(1, END)
        entry_ff.delete(0, END)
        entry_ff.insert(0, '6,00')
        entry_sf.delete(0, END)
        entry_sf.insert(0, '10,00')
        entry_sp.delete(0, END)
        entry_sp.insert(0, 'auto')
        entry_ep.delete(0, END)
        entry_ep.insert(0, 'auto')
        entry_sb.delete(0, END)
        entry_sb.insert(0, 'auto')
        entry_eb.delete(0, END)
        entry_eb.insert(0, 'auto')
        number_gauss = 0
        button_gauss.config(text=f"ADD GAUSS({number_gauss})")
        amp = []
        cen = []
        sigma = []

    def clear():
        nonlocal number_gauss, amp, cen, sigma
        clear_noc()
        lb2.delete(1, END)

    def start():
        def copy_all(event):
            to_copy = ''
            for k in range(len(x)):
                to_copy += str(x[k])
                to_copy += '\t'
                to_copy += str(y[k])
                to_copy += '\n'
            clipboard.copy(to_copy)

        def copy_peak(event):
            to_copy = ''
            for k in range(len(x_peak)):
                to_copy += str(x_peak[k])
                to_copy += '\t'
                to_copy += str(y_peak[k])
                to_copy += '\n'
            clipboard.copy(to_copy)

        nonlocal amp, cen, sigma
        global ax1, plot_number
        flag1 = str(entry_ff.get())
        flag2 = str(entry_sf.get())
        input1 = str(lb1.get(1))
        input2 = str(lb2.get(1))
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

        with open(lb1.get(1)) as f:
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
        for i in range(len(data)):
            data[i] = data[i].replace('\n', '')
            data[i] = data[i].replace(',', '.')
            li = data[i].split('\t')
            vl = float(li[0])
            vol.append(vl)
            lgm = const[0] + const[1] * vl + const[2] * vl * vl + const[3] * vl ** 3
            x.append(lgm)
            y.append(float(li[2]))

        for i in range(len(y)):
            y_fix = 1
            if bool(do_fix.get()) and i > 0:
                y_fix = abs(vol[i] - vol[i - 1]) / abs(x[i] - x[i - 1])
            y[i] = y[i] * y_fix

        y_min = min(y)
        for i in range(len(y)):
            y[i] = y[i] - y_min

        y_max = max(y)
        for i in range(len(y)):
            y[i] = y[i] / y_max

        index_max = y.index(max(y))
        plot_number += 1
        if bool(do_new.get()):
            fig, axes = pyplot.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
            ax1 = axes
            plot_number = 0
        ax1.plot(x, y, 'k--', label='original')
        if bool(do_new.get()):
            ax1.set_xlim(ax1.get_xlim()[::-1])
            ax_copy = fig.add_axes([0.9, 0.2, 0.1, 0.075])
            b_copy = bt(ax_copy, 'Copy all')
            b_copy.on_clicked(copy_all)
            ax_copy_p = fig.add_axes([0.9, 0.3, 0.1, 0.075])
            b_copy_p = bt(ax_copy_p, 'Copy peak')
            b_copy_p.on_clicked(copy_peak)
        x_np = np.array(x)
        y_np = np.array(y)

        sp = str(entry_sp.get())
        ep = str(entry_ep.get())
        count = 0
        if 'auto' in sp:
            index_left_min = index_max
            flag = True
            while flag:
                if y[index_left_min - 2] <= y[index_left_min]:
                    index_left_min -= 1
                else:
                    flag = False
        else:
            count = 1
            index_left_min = x.index(min(x, key=lambda xx: abs(xx - float(sp))))

        if 'auto' in ep:
            index_right_min = index_max
            flag = True
            while flag:
                if y[index_right_min + 2] <= y[index_right_min]:
                    index_right_min += 1
                else:
                    flag = False
        else:
            if count == 1 and sp <= ep:
                raise 'start lgM must be greater then end lgM'
            index_right_min = x.index(min(x, key=lambda xx: abs(xx - float(ep))))

        x_line = x_np[index_left_min], x_np[index_right_min]
        y_base = min(y_np[index_left_min], y_np[index_right_min])
        y_line = [y_base, y_base]

        sb = str(entry_sb.get())
        eb = str(entry_eb.get())
        if 'auto' not in sb:
            y_line[0] = float(sb)
        if 'auto' not in eb:
            y_line[1] = float(eb)

        k_line = -(y_line[1] - y_line[0]) / (x_line[0] - x_line[1])
        b_line = y_line[0] - k_line * x_line[0]
        ax1.plot(x_line, y_line, color=base_color[plot_number % len(base_color)])
        # ax1.fill_between(x, y, y_base, where=(x >= x[index_right_min]) & (x <= x[index_left_min]), color='red')

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

            cprint('Mn = ' + str(m_n), text_color, back_color)
            cprint('Mw = ' + str(m_w), text_color, back_color)
            cprint('Mw/Mn = ' + str(mwd), text_color, back_color)
            cprint('peak area = ' + str(sum(slice_area)), text_color, back_color)
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
            for i in range(len(amp)):
                guess.append(cen[i])
                guess.append(amp[i])
                guess.append(sigma[i])
            print(guess)

            popt, pcov = curve_fit(func, x_peak, y_peak, p0=guess, maxfev=100000)
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

    for c in range(3):
        root.columnconfigure(index=c, weight=1)
    for r in range(10):
        root.rowconfigure(index=r, weight=1)

    lb1 = tk.Listbox(root, width=10, height=1)
    lb1.insert(1, "drag GPC txt data file")
    lb1.drop_target_register(DND_FILES)
    lb1.dnd_bind('<<Drop>>', lambda e: lb1.insert(tk.END, e.data))
    lb1.grid(column=0, row=0, columnspan=3, rowspan=2, sticky="news")

    lb2 = tk.Listbox(root, width=10, height=1)
    lb2.insert(1, "drag constants pdf data file or folder")
    try:
        with open('const.txt') as f:
            const_line = f.read()
        lb2.insert(2, const_line)
    except:
        print("no const.txt file")
    lb2.drop_target_register(DND_FILES)
    lb2.dnd_bind('<<Drop>>', lambda e: lb2.insert(tk.END, e.data))
    lb2.grid(column=0, row=2, columnspan=3, rowspan=2, sticky="news")

    button_start = Button(root, text="START", command=start)
    button_start.grid(column=0, row=4, sticky="news")

    button_clear = Button(root, text="CLEAR", command=clear)
    button_clear.grid(column=0, row=5, sticky="news")

    button_clear_noc = Button(root, text="CLEAR -C", command=clear_noc)
    button_clear_noc.grid(column=0, row=6, sticky="news")

    number_gauss = 0

    amp = []
    cen = []
    sigma = []

    def del_gauss(top):
        nonlocal number_gauss, amp, cen, sigma
        top.destroy()
        amp = []
        cen = []
        sigma = []
        number_gauss = 0
        button_gauss.config(text=f"ADD GAUSS({number_gauss})")

    def popup_gauss():

        def close_gauss(top):
            nonlocal number_gauss, amp, cen, sigma
            amp.append(float(entry_amp.get()))
            cen.append(float(entry_cen.get()))
            sigma.append(float(entry_sigma.get()))
            top.destroy()
            number_gauss += 1
            button_gauss.config(text=f"ADD GAUSS({number_gauss})")

        # Create a Toplevel window
        top = Toplevel(root)
        top.geometry("200x200")

        for gc in range(2):
            top.columnconfigure(index=gc, weight=1)
        for gr in range(4):
            top.rowconfigure(index=gr, weight=1)

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

        button = Button(top, text="Ok", command=lambda: close_gauss(top))
        button.grid(column=0, row=3, sticky="news")

        button = Button(top, text="Del gauss", command=lambda: del_gauss(top))
        button.grid(column=1, row=3, sticky="news")

    button_gauss = Button(root, text="ADD GAUSS(0)", command=popup_gauss)
    button_gauss.grid(column=0, row=7, sticky="news")

    do_fix = IntVar()
    fix_cb = ttk.Checkbutton(text="fix lg intensity", variable=do_fix)
    fix_cb.grid(column=0, row=8, sticky="news")

    do_new = IntVar()
    new_cb = ttk.Checkbutton(text="new figure", variable=do_new)
    new_cb.grid(column=0, row=9, sticky="news")

    label_first_flag = ttk.Label(text="first flag")
    label_first_flag.configure(anchor="center")
    label_first_flag.grid(column=1, row=4, sticky="news")

    entry_ff = Entry(root, width=10)
    entry_ff.insert(0, '6,00')
    entry_ff.grid(column=2, row=4)

    label_second_flag = ttk.Label(text="second flag")
    label_second_flag.configure(anchor="center")
    label_second_flag.grid(column=1, row=5, sticky="news")

    entry_sf = Entry(root, width=10)
    entry_sf.insert(0, '10,00')
    entry_sf.grid(column=2, row=5)

    label_sp = ttk.Label(text="start lgM(.)")
    label_sp.configure(anchor="center")
    label_sp.grid(column=1, row=6, sticky="news")

    entry_sp = Entry(root, width=10)
    entry_sp.insert(0, 'auto')
    entry_sp.grid(column=2, row=6)

    label_ep = ttk.Label(text="end lgM(.)")
    label_ep.configure(anchor="center")
    label_ep.grid(column=1, row=7, sticky="news")

    entry_ep = Entry(root, width=10)
    entry_ep.insert(0, 'auto')
    entry_ep.grid(column=2, row=7)

    label_sb = ttk.Label(text="start base(.)")
    label_sb.configure(anchor="center")
    label_sb.grid(column=1, row=8, sticky="news")

    entry_sb = Entry(root, width=10)
    entry_sb.insert(0, 'auto')
    entry_sb.grid(column=2, row=8)

    label_eb = ttk.Label(text="end base(.)")
    label_eb.configure(anchor="center")
    label_eb.grid(column=1, row=9, sticky="news")

    entry_eb = Entry(root, width=10)
    entry_eb.insert(0, 'auto')
    entry_eb.grid(column=2, row=9)

    root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

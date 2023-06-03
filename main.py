import tkinter as tk
from tkinter import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib import pyplot
from matplotlib.widgets import Button as bt
import numpy as np
import pdfplumber
import pandas as pd

flag1 = "6,00"
flag2 = "10,00"


def main():
    def clear():
        lb1.delete(1, END)
        lb2.delete(1, END)

    def copy(event):
        print("doing copy")

    def start():
        with pdfplumber.open(lb2.get(1)) as pdf:
            page = pdf.pages[0]
            ct = page.extract_tables(table_settings={})
        for i in range(len(ct)):
            for j in range(len(ct[i])):
                if ct[i][j] == ['C0', 'C1', 'C2', 'C3']:
                    const = ct[i][j + 1]
        for i in range(len(const)):
            const[i] = const[i].replace(' ', '')
            const[i] = const[i].replace(',', '.')
            const[i] = float(const[i])
        print(const)
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
        y = []
        for i in range(len(data)):
            data[i] = data[i].replace('\n', '')
            data[i] = data[i].replace(',', '.')
            li = data[i].split('\t')
            vl = float(li[0])
            lgm = const[0] + const[1] * vl + const[2] * vl * vl + const[3] * vl ** 3
            x.append(lgm)
            y.append(float(li[2]))

        y_min = min(y)
        for i in range(len(y)):
            y[i] = y[i] - y_min
        y_max = max(y)
        for i in range(len(y)):
            y[i] = y[i] / y_max

        index_max = y.index(max(y))
        fig, axes = pyplot.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
        ax1 = axes
        ax1.plot(x, y, 'k--', label='original')
        ax1.set_xlim(ax1.get_xlim()[::-1])
        ax_copy = fig.add_axes([0.9, 0.2, 0.1, 0.075])
        b_copy = bt(ax_copy, 'Copy')
        b_copy.on_clicked(copy)
        x_np = np.array(x)
        y_np = np.array(y)

        index_left_min = index_max
        flag = True
        while flag:
            if y[index_left_min - 1] <= y[index_left_min]:
                index_left_min -= 1
            else:
                flag = False
        index_right_min = index_max
        flag = True
        while flag:
            if y[index_right_min + 1] <= y[index_right_min]:
                index_right_min += 1
            else:
                flag = False
        x_line = x_np[index_left_min], x_np[index_right_min]
        y_base = min(y_np[index_left_min], y_np[index_right_min])
        y_line = y_base, y_base
        k_line = -(y_line[1]-y_line[0])/(x_line[0]-x_line[1])
        b_line = y_line[0]-k_line*x_line[0]
        ax1.plot(x_line, y_line, 'xr-')
        #ax1.fill_between(x, y, y_base, where=(x >= x[index_right_min]) & (x <= x[index_left_min]), color='red')

        x_peak = []
        y_peak = []
        print(index_left_min)
        print(index_right_min)

        for i in range(index_right_min - index_left_min + 1):
            x_peak.append(x[i + index_left_min])
            y_peak.append(y[i + index_left_min] - (k_line*x[i + index_left_min] + b_line))

        print('len_peak = ' + str(len(x_peak)))
        ax1.plot(x_peak, y_peak, 'b-')




        pyplot.show()

    root = TkinterDnD.Tk()  # instead of tk.Tk()
    root.geometry("300x300")

    lb1 = tk.Listbox(root, width=50, height=4)
    lb1.insert(1, "drag GPC txt data file")
    lb1.drop_target_register(DND_FILES)
    lb1.dnd_bind('<<Drop>>', lambda e: lb1.insert(tk.END, e.data))
    lb1.pack()

    lb2 = tk.Listbox(root, width=50, height=4)
    lb2.insert(1, "drag constants pdf data file")
    lb2.drop_target_register(DND_FILES)
    lb2.dnd_bind('<<Drop>>', lambda e: lb2.insert(tk.END, e.data))
    lb2.pack()

    button_start = Button(root, text="START", padx=30, pady=20, command=start)
    button_start.pack()

    button_clear = Button(root, text="CLEAR", padx=30, pady=20, command=clear)
    button_clear.pack()

    root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

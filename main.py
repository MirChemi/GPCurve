import tkinter as tk
from tkinter import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib import pyplot
from matplotlib.widgets import Button as bt
import numpy as np
import pdfplumber
import pandas as pd

flag1 = "6,0"
flag2 = "10,0"


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
            lgm = const[0] + const[1] * vl + const[2] * vl * vl + const[3] * vl**3
            x.append(lgm)
            y.append(float(li[2]))
        y_min = min(y)
        for i in range(len(y)):
            y[i] = y[i] - y_min
        y_max = max(y)
        for i in range(len(y)):
            y[i] = y[i] / y_max
        fig, axes = pyplot.subplots(1, 1, figsize=(9.0, 8.0), sharex=True)
        ax1 = axes
        ax1.plot(x, y, 'k--', label='original')
        ax_copy = fig.add_axes([0.7, 0.05, 0.1, 0.075])
        b_copy = bt(ax_copy, 'Copy')
        b_copy.on_clicked(copy)
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

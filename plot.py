import clipboard
import os
import configparser
from statistics import mean
from matplotlib import pyplot, widgets
import numpy as np

from scripts import norm, linreg
from scripts.pcalc import calculate_peak


base_color = 'blue', 'red', 'green', 'black', 'magenta', 'cyan', 'yellow'

class Plot:
    def __init__(self, lgm, lgm_i, ex_name, clean):
        self.fig, self.ax1 = pyplot.subplots(figsize=(9.0, 7.0), sharex=True)
        self.ax1.set_position([0.07, 0.1, 0.8, 0.8])
        self.ax1.set_xlabel('lgM')
        self.lgm = [lgm]
        self.lgm_i = [lgm_i]
        self.pk_lgm = [lgm]
        self.pk_lgm_y = [lgm_i]
        self.ex_name = [ex_name]
        self.m_n = 0
        self.m_w = 0
        self.p_area = 0
        self.pk_max = 0
        if clean:
            self.ax1.plot(lgm, lgm_i, color=base_color[0], label=ex_name)
        else:
            self.ax1.plot(lgm, lgm_i, '--', color=base_color[0], label=ex_name)
        self.ax1.legend()

        self.ax1.set_xlim(self.ax1.get_xlim()[::-1])
        self.ax_copy = self.fig.add_axes([0.9, 0.2, 0.1, 0.075])
        self.b_copy = widgets.Button(self.ax_copy, 'Copy\nspectra')
        self.b_copy.on_clicked(self.copy_spectra)

        self.ax_der = self.fig.add_axes([0.9, 0.5, 0.1, 0.075])
        self.b_der = widgets.Button(self.ax_der, 'Show\n2nd der')
        self.b_der.on_clicked(self.show_sec_der)

        self.ax_copy_p = self.fig.add_axes([0.9, 0.3, 0.1, 0.075])
        self.b_copy_p = widgets.Button(self.ax_copy_p, 'Copy\npeak')
        self.b_copy_p.on_clicked(self.copy_peak)

    def show(self):
        pyplot.show()

    def add(self, lgm, lgm_i, ex_name, clean):
        self.lgm.append(lgm)
        self.lgm_i.append(lgm_i)
        self.ex_name.append(ex_name)
        if clean:
            self.ax1.plot(lgm, lgm_i, color=base_color[len(self.lgm) % len(base_color)], label=ex_name)
        else:
            self.ax1.plot(lgm, lgm_i, 'k--', color=base_color[len(self.lgm) % len(base_color)], label=ex_name)
        self.ax1.legend()

    def update_last_legend_entry(self, extra_text):
        handles, labels = self.ax1.get_legend_handles_labels()

        if labels:
            labels[-1] += f" {extra_text}"
        self.ax1.legend(handles, labels)

    def peak(self, pk_lgm_p: list, pk_lgm_p_y: list):
        if pk_lgm_p[0] and pk_lgm_p[1]:
            pk_lgm_p.sort()
        if pk_lgm_p[1]:
            while self.pk_lgm[-1][0] > pk_lgm_p[1]:
                self.pk_lgm[-1].pop(0)
                self.pk_lgm_y[-1].pop(0)
        else:
            pk_lgm_i_max = self.pk_lgm_y[-1].index(max(self.pk_lgm_y[-1]))
            pk_lgm_i_left = 0
            for i in range(pk_lgm_i_max, 0, -1):
                if self.pk_lgm_y[-1][i - 2] > self.pk_lgm_y[-1][i]:
                    pk_lgm_i_left = i
                    break
            self.pk_lgm[-1] = self.pk_lgm[-1][pk_lgm_i_left:]
            self.pk_lgm_y[-1] = self.pk_lgm_y[-1][pk_lgm_i_left:]

        if pk_lgm_p[0]:
            while self.pk_lgm[-1][-1] < pk_lgm_p[0]:
                self.pk_lgm[-1].pop()
                self.pk_lgm_y[-1].pop()
        else:
            pk_lgm_i_max = self.pk_lgm_y[-1].index(max(self.pk_lgm_y[-1]))
            pk_lgm_i_right = len(self.pk_lgm_y[-1]) - 2
            for i in range(pk_lgm_i_max, len(self.pk_lgm_y[-1]) - 2):
                if self.pk_lgm_y[-1][i + 2] > self.pk_lgm_y[-1][i]:
                    pk_lgm_i_right = i
                    break
            self.pk_lgm[-1] = self.pk_lgm[-1][:pk_lgm_i_right]
            self.pk_lgm_y[-1] = self.pk_lgm_y[-1][:pk_lgm_i_right]

        if not pk_lgm_p_y[0] and not pk_lgm_p_y[1]:
            pk_lgm_y_min = min(self.pk_lgm_y[-1])
            for i in range(len(self.pk_lgm_y[-1])):
                self.pk_lgm_y[-1][i] -= pk_lgm_y_min
        elif pk_lgm_p_y[0] and not pk_lgm_p_y[1]:
            for i in range(len(self.pk_lgm_y[-1])):
                self.pk_lgm_y[-1][i] -= pk_lgm_p_y[0]
        elif not pk_lgm_p_y[0] and pk_lgm_p_y[1]:
            for i in range(len(self.pk_lgm_y[-1])):
                self.pk_lgm_y[-1][i] -= pk_lgm_p_y[1]
        else:
            for i in range(len(self.pk_lgm_y[-1])):
                self.pk_lgm_y[-1][i] -= linreg.interpolate(self.pk_lgm[-1][i], pk_lgm_p, pk_lgm_p_y)

        self.m_n, self.m_w, self.p_area = calculate_peak(self.pk_lgm[-1], self.pk_lgm_y[-1])
        self.pk_max = self.pk_lgm[-1][self.pk_lgm_y[-1].index(max(self.pk_lgm_y[-1]))]
        self.ax1.plot(self.pk_lgm[-1], self.pk_lgm_y[-1], color=base_color[len(self.lgm) % len(base_color)])
        self.ax1.legend()
        self.update_last_legend_entry(f'Mn={round(self.m_n)} Mw/Mn={round(self.m_w/self.m_n, 2)}')

    def copy_spectra(self, event):
        to_copy = ''
        for i in range(len(self.lgm[-1])):
            to_copy += f'{self.lgm[-1][i]}\t{self.lgm_i[-1][i]}\n'
        clipboard.copy(to_copy)

    def copy_peak(self, event):
        to_copy = ''
        for i in range(len(self.pk_lgm[-1])):
            to_copy += f'{self.pk_lgm[-1][i]}\t{self.pk_lgm_y[-1][i]}\n'
        clipboard.copy(to_copy)

    def show_sec_der(self, event):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        x_der = []
        y_der = []
        for i in range(1, len(self.lgm[-1]) - 1):
            x_der.append(self.lgm[-1][i])
            dy1 = (self.lgm_i[-1][i] - self.lgm_i[-1][i - 1]) / (self.lgm[-1][i] - self.lgm[-1][i - 1])
            dy2 = (self.lgm_i[-1][i + 1] - self.lgm_i[-1][i]) / (self.lgm[-1][i + 1] - self.lgm[-1][i])
            y_der.append((dy2 - dy1) / ((self.lgm[-1][i + 1] - self.lgm[-1][i - 1]) / 2))
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



class Plot_vol:
    def __init__(self, vol, vol_y, ex_name, clean):
        self.fig, self.ax1 = pyplot.subplots(figsize=(9.0, 7.0), sharex=True)
        self.ax1.set_position([0.07, 0.1, 0.8, 0.8])
        self.ax1.set_xlabel('vol')
        self.vol = [vol]
        self.vol_y = [vol_y]
        self.pk_vol = [vol]
        self.pk_vol_y = [vol_y]
        self.ex_name = [ex_name]
        self.m_n = 0
        self.m_w = 0
        self.mwd = 0
        self.p_area = 0
        self.pk_max = 0
        if clean:
            self.ax1.plot(vol, vol_y, color=base_color[0], label=ex_name)
        else:
            self.ax1.plot(vol, vol_y, '--', color=base_color[0], label=ex_name)
        self.ax1.legend()

        self.ax_copy = self.fig.add_axes([0.9, 0.2, 0.1, 0.075])
        self.b_copy = widgets.Button(self.ax_copy, 'Copy\nspectra')
        self.b_copy.on_clicked(self.copy_spectra)

        self.ax_der = self.fig.add_axes([0.9, 0.5, 0.1, 0.075])
        self.b_der = widgets.Button(self.ax_der, 'Show\n2nd der')
        self.b_der.on_clicked(self.show_sec_der)

    def show(self):
        pyplot.show()

    def add(self, lgm, lgm_i, ex_name, clean):
        self.vol.append(lgm)
        self.vol_y.append(lgm_i)
        self.ex_name.append(ex_name)
        if clean:
            self.ax1.plot(lgm, lgm_i, color=base_color[len(self.vol) % len(base_color)], label=ex_name)
        else:
            self.ax1.plot(lgm, lgm_i, 'k--', color=base_color[len(self.vol) % len(base_color)], label=ex_name)
        self.ax1.legend()

    def copy_spectra(self, event):
        to_copy = ''
        for i in range(len(self.vol[-1])):
            to_copy += f'{self.vol[-1][i]}\t{self.vol_y[-1][i]}\n'
        clipboard.copy(to_copy)

    def show_sec_der(self, event):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        x_der = []
        y_der = []
        for i in range(1, len(self.vol[-1]) - 1):
            x_der.append(self.vol[-1][i])
            dy1 = (self.vol_y[-1][i] - self.vol_y[-1][i - 1]) / (self.vol[-1][i] - self.vol[-1][i - 1])
            dy2 = (self.vol_y[-1][i + 1] - self.vol_y[-1][i]) / (self.vol[-1][i + 1] - self.vol[-1][i])
            y_der.append((dy2 - dy1) / ((self.vol[-1][i + 1] - self.vol[-1][i - 1]) / 2))
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

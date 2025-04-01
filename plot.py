# MIT License
# Copyright (c) 2025 MirChemi (mirekchemis@gmail.com)

import clipboard
import os
import configparser
import csv
from itertools import zip_longest
from statistics import mean

from scipy.optimize import curve_fit
from matplotlib import pyplot, widgets
import numpy as np

from scripts import norm, linreg, data_math
from scripts.pcalc import calculate_peak
from scripts.data_math import normalize_second_by_point, second_derivative
from scripts.func import gauss, multi_gauss
from ui.matplotlib_widget import MatplotlibWidget


base_color = 'blue', 'red', 'green', 'black', 'magenta', 'cyan', 'yellow'

class Plot:
    def __init__(self, x, y, ex_name):
        self.widget = MatplotlibWidget()
        self.widget.setWindowTitle(ex_name)
        self.ax1 = self.widget.figure.add_subplot()
        self.ax1.set_position([0.08, 0.1, 0.8, 0.87])

        self.derivative_widget = MatplotlibWidget()
        self.derivative_widget.setWindowTitle(ex_name)
        self.ax_d = self.derivative_widget.figure.add_subplot()
        self.ax_d.set_position([0.08, 0.1, 0.8, 0.87])

        self.x = [x]
        self.y = [y]
        self.ex_name = [ex_name]

        self.ax_der = self.widget.figure.add_axes((0.9, 0.7, 0.1, 0.075))
        self.b_der = widgets.Button(self.ax_der, 'Show\n2nd der')
        self.b_der.on_clicked(self.show_sec_der)

        self.ax_copy = self.widget.figure.add_axes((0.9, 0.6, 0.1, 0.075))
        self.b_copy = widgets.Button(self.ax_copy, 'Copy\nspectra')
        self.b_copy.on_clicked(self.copy_spectra)

        self.ax_save_fig = self.widget.figure.add_axes((0.9, 0.5, 0.1, 0.075))
        self.b_save_fig = widgets.Button(self.ax_save_fig, 'Save\nfigure')
        self.b_save_fig.on_clicked(self.save_fig)

    def copy_spectra(self, event):
        to_copy = ''
        for i in range(len(self.x[-1])):
            to_copy += f'{self.x[-1][i]}\t{self.y[-1][i]}\n'
        clipboard.copy(to_copy)

    def show_sec_der(self, event):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        x_der, y_der = second_derivative(self.x[-1],
                                         self.y[-1],
                                         config.getint('derivative', 'smoothing_level'))

        self.ax_d.scatter(x_der, y_der)
        self.ax_d.set_xlim(self.ax_d.get_xlim()[::-1])

        self.derivative_widget.show()
        self.derivative_widget.canvas.draw()

    def show(self):
        self.widget.show()
        self.widget.canvas.draw()

    def save_fig(self, event):
        # Ensure the output directory exists
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)  # Creates the directory if it doesn't exist

        ex_names = "_".join(self.ex_name)
        fig_filename = os.path.join(output_dir, f'{ex_names}.png')

        extent = self.ax1.get_tightbbox(self.widget.figure.canvas.get_renderer()).transformed(
            self.widget.figure.dpi_scale_trans.inverted())
        self.widget.figure.savefig(fig_filename, bbox_inches=extent, dpi=300)


class Plot_lgm(Plot):
    def __init__(self, x, y, ex_name, clean):
        super().__init__(x, y, ex_name)

        self.ax1.set_xlabel('lgM')
        self.exp_lines = []
        self.pk_lgm = []
        self.pk_lgm_y = []
        self.gauss_cum_lgm = []
        self.gauss_cum_lgm_y = []
        self.gauss_lgm = []
        self.gauss_lgm_y = []
        self.pk_ex_name = []
        self.m_n = 0
        self.m_w = 0
        self.p_area = 0
        self.pk_max = 0

        if clean:
            self.exp_lines.append(self.ax1.plot(x, y, color=base_color[0], label=ex_name)[0])
        else:
            self.exp_lines.append(self.ax1.plot(x, y, '--', color=base_color[0], label=ex_name)[0])

        self.ax1.legend()

        self.ax1.set_xlim(self.ax1.get_xlim()[::-1])

        self.ax_csv = self.widget.figure.add_axes((0.9, 0.4, 0.1, 0.075))
        self.b_csv = widgets.Button(self.ax_csv, 'All to\ncsv')
        self.b_csv.on_clicked(self.all_to_csv)

        self.ax_copy_p = self.widget.figure.add_axes((0.9, 0.3, 0.1, 0.075))
        self.b_copy_p = widgets.Button(self.ax_copy_p, 'Copy\npeak')
        self.b_copy_p.on_clicked(self.copy_peak)

        self.ax_subtract = self.widget.figure.add_axes((0.9, 0.2, 0.1, 0.075))
        self.b_subtract = widgets.Button(self.ax_subtract, 'Subtract\nfirst')
        self.b_subtract.on_clicked(self.subtract_first)

    def add(self, x, y, ex_name, clean):
        self.exp_lines.append(None)
        self.x.append(x)
        self.y.append(y)
        self.ex_name.append(ex_name)
        if clean:
            self.exp_lines[-1], = self.ax1.plot(x, y,
                                                color=base_color[(len(self.x) - 1) % len(base_color)], label=ex_name)
        else:
            self.exp_lines[-1], = self.ax1.plot(x, y, 'k--',
                                                color=base_color[(len(self.x) - 1) % len(base_color)], label=ex_name)
        self.ax1.legend()

    def peak(self, pk_lgm_p: list, pk_lgm_p_y: list):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        self.pk_lgm.append(self.x[-1])
        self.pk_lgm_y.append(self.y[-1])
        self.pk_ex_name.append(self.ex_name[-1])

        if pk_lgm_p[0] and pk_lgm_p[1]:
            pk_lgm_p.sort()
        if pk_lgm_p[1]:
            while self.pk_lgm[-1][-1] > pk_lgm_p[1]:
                self.pk_lgm[-1].pop()
                self.pk_lgm_y[-1].pop()
        else:
            pk_lgm_i_max = self.pk_lgm_y[-1].index(max(self.pk_lgm_y[-1]))
            pk_lgm_i_right = len(self.pk_lgm_y[-1]) - 2
            for i in range(pk_lgm_i_max, len(self.pk_lgm_y[-1]) - 2):
                if self.pk_lgm_y[-1][i + 2] > self.pk_lgm_y[-1][i] and self.pk_lgm_y[-1][i] < config.getfloat(
                        'peak', 'baseline_threshold'):
                    pk_lgm_i_right = i
                    break
            self.pk_lgm[-1] = self.pk_lgm[-1][:pk_lgm_i_right]
            self.pk_lgm_y[-1] = self.pk_lgm_y[-1][:pk_lgm_i_right]

        if pk_lgm_p[0]:
            while self.pk_lgm[-1][0] < pk_lgm_p[0]:
                self.pk_lgm[-1].pop(0)
                self.pk_lgm_y[-1].pop(0)
        else:
            pk_lgm_i_max = self.pk_lgm_y[-1].index(max(self.pk_lgm_y[-1]))
            pk_lgm_i_left = 1
            for i in range(pk_lgm_i_max, 0, -1):
                if self.pk_lgm_y[-1][i - 2] > self.pk_lgm_y[-1][i] and self.pk_lgm_y[-1][i] < config.getfloat(
                        'peak', 'baseline_threshold'):
                    pk_lgm_i_left = i
                    break
            self.pk_lgm[-1] = self.pk_lgm[-1][pk_lgm_i_left:]
            self.pk_lgm_y[-1] = self.pk_lgm_y[-1][pk_lgm_i_left:]

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
        self.ax1.plot(self.pk_lgm[-1],
                      self.pk_lgm_y[-1],
                      color=base_color[(len(self.ex_name) - 1) % len(base_color)])
        self.exp_lines[-1].set_label(
            f'{self.ex_name[-1]} Mn={round(self.m_n)} '
            f'Mw/Mn={round(self.m_w / self.m_n, 2)}\n'
            f'area={round(self.p_area, 3)}'
        )
        self.ax1.legend()

    def gauss(self, guess, guess_bounds):
        # Perform Gaussian fitting
        popt, _ = curve_fit(multi_gauss, self.pk_lgm[-1], self.pk_lgm_y[-1], p0=guess, bounds=guess_bounds)

        # Extract parameters
        fitted_params = np.array(popt).reshape(-1, 3)  # [amp, cen, sigma] for each gaussian

        self.gauss_cum_lgm = self.pk_lgm[-1]
        self.gauss_cum_lgm_y = multi_gauss(self.pk_lgm[-1], *popt)
        m_n, m_w, area = calculate_peak(self.gauss_cum_lgm, self.gauss_cum_lgm_y)
        self.ax1.plot(self.gauss_cum_lgm, self.gauss_cum_lgm_y, color=base_color[-1],
                      label=f'gauss Mn={round(m_n)} Mw/Mn={round(m_w / self.m_n, 2)}\narea={round(area, 3)}')

        self.gauss_lgm = []
        self.gauss_lgm_y = []
        for i in range(len(fitted_params)):
            self.gauss_lgm.append(self.pk_lgm[-1])
            self.gauss_lgm_y.append(gauss(self.pk_lgm[-1], *fitted_params[i]))
            m_n, m_w, area = calculate_peak(self.gauss_lgm[-1], self.gauss_lgm_y[-1])
            self.ax1.plot(self.gauss_lgm[-1], self.gauss_lgm_y[-1], color=base_color[-2 - i],
                          label=f'gauss{i} Mn={round(m_n)} Mw/Mn={round(m_w / self.m_n, 2)}\narea={round(area, 3)}')

        self.ax1.legend()

    def copy_peak(self, event):
        to_copy = ''
        for i in range(len(self.pk_lgm[-1])):
            to_copy += f'{self.pk_lgm[-1][i]}\t{self.pk_lgm_y[-1][i]}\n'
        clipboard.copy(to_copy)

    def all_to_csv(self, event):

        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)  # Creates the directory if it doesn't exist

        ex_names = "_".join(self.ex_name)
        csv_filename = os.path.join(os.path.dirname(__file__), 'output', f'{ex_names}.csv')
        with open(csv_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            header = []
            data = []
            for i in range(len(self.ex_name)):
                header.append(f'{self.ex_name[i]}_lgm')
                header.append(f'{self.ex_name[i]}_intensity')
                data.append(self.x[i])
                data.append(self.y[i])
            for i in range(len(self.pk_ex_name)):
                header.append(f'{self.pk_ex_name[i]}_peak_lgm')
                header.append(f'{self.pk_ex_name[i]}_peak_intensity')
                data.append(self.pk_lgm[i])
                data.append(self.pk_lgm_y[i])
            if self.gauss_cum_lgm:
                header.append(f'{self.pk_ex_name[-1]}_gauss_cum_lgm')
                header.append(f'{self.pk_ex_name[-1]}gauss_cum_intensity')
                data.append(self.gauss_cum_lgm)
                data.append(self.gauss_cum_lgm_y)
            for i in range(len(self.gauss_lgm)):
                header.append(f'{self.pk_ex_name[-1]}_gauss{i}_lgm')
                header.append(f'{self.pk_ex_name[-1]}_gauss{i}_intensity')
                data.append(self.gauss_lgm[i])
                data.append(self.gauss_lgm_y[i])
            writer.writerow(header)
            writer.writerows(zip_longest(*data, fillvalue="0"))

    def subtract_first(self, event):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        lgm0_y_norm = normalize_second_by_point(self.x[-1], self.y[-1], self.x[0], self.y[0],
                                                config.getfloat('subtract','lgm_norm'))
        self.ax1.plot(self.x[0], lgm0_y_norm, color='yellow')

        lgm_y = data_math.subtract(self.x[-1], self.y[-1], self.x[0], lgm0_y_norm)
        lgm_y = norm.norm_0_1(lgm_y)
        self.subtracted = Plot_lgm(self.x[-1], lgm_y, self.ex_name[-1], False)
        self.subtracted.peak([None, None], [None, None])
        self.subtracted.show()


class Plot_vol(Plot):
    def __init__(self, x, y, ex_name):
        super().__init__(x, y, ex_name)
        self.ax1.set_xlabel('vol')
        self.ax1.plot(x, y, color=base_color[0], label=ex_name)
        self.ax1.legend()

    def add(self, x, y, ex_name):
        self.x.append(x)
        self.y.append(y)
        self.ex_name.append(ex_name)
        self.ax1.plot(x, y, color=base_color[(len(self.x) - 1) % len(base_color)], label=ex_name)
        self.ax1.legend()

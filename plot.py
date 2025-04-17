# MIT License
# Copyright (c) 2025 MirChemi (mirekchemis@gmail.com)

import clipboard
import os
import configparser
import csv
from itertools import zip_longest

import numpy as np

from scripts import norm, linreg, data_math
from scripts.pcalc import calculate_peak
from scripts.data_math import normalize_second_by_point, second_derivative, gauss_fit
from scripts.func import gauss, multi_gauss
from ui.matplotlib_widget import MatplotlibWidget
from ui.custom_elements import Button


base_color = 'blue', 'red', 'green', 'black', 'magenta', 'cyan', 'yellow'
config = configparser.ConfigParser()

class Plot:
    def __init__(self, x, y, ex_name):
        self.widget = MatplotlibWidget()
        self.widget.setWindowTitle(ex_name)
        self.ax1 = self.widget.figure.add_subplot()
        self.ax1.set_position([0.1, 0.1, 0.85, 0.87])

        self.csv_headers = []
        self.csv_columns = []
        self.x = [x]
        self.y = [y]
        self.ex_names = [ex_name]

        self.second_der_plot = None
        self.b_der = Button(text="D", tooltip="Show 2nd derivatives")
        self.b_der.setObjectName("D")

        self.b_copy = Button(text="C", tooltip="Copy last raw curve to clipboard")
        self.b_copy.setObjectName("C")
        self.b_copy.clicked.connect(self.copy_spectra)
        self.widget.add_custom_button(self.b_copy)

        self.b_sf = Button(text="SF", tooltip="Save figure")
        self.b_sf.setObjectName("SF")
        self.b_sf.clicked.connect(self.save_fig)
        self.widget.add_custom_button(self.b_sf)

        self.b_csv = Button(text="CSV", tooltip="Export all to csv to output folder")
        self.b_csv.setObjectName("CSV")
        self.b_csv.clicked.connect(self.all_to_csv)
        self.widget.add_custom_button(self.b_csv)

    def init_second_der(self):
        self.b_der.clicked.connect(self.show_sec_der)
        self.widget.add_custom_button(self.b_der)

        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        x_der2, y_der2 = second_derivative(self.x[0],
                                           self.y[0],
                                           config.getint("derivative", "smoothing_level"))

        self.second_der_plot = Plot_der(x_der2,
                                        y_der2,
                                        f"{self.ex_names[0]}_2nd_der",
                                        self.ax1.get_xlabel())

    def add_second_der(self, x, y):
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        x_der2, y_der2 = second_derivative(x,
                                           y,
                                           config.getint('derivative', 'smoothing_level'))

        self.second_der_plot.add(x_der2, y_der2, f"{self.ex_names[-1]}_2nd_der")

    def copy_spectra(self, event):
        to_copy = ''
        for i in range(len(self.x[-1])):
            to_copy += f'{self.x[-1][i]}\t{self.y[-1][i]}\n'
        clipboard.copy(to_copy)


    def show_sec_der(self, event):
        self.second_der_plot.show()

    def show(self):
        self.widget.show()
        self.widget.canvas.draw()

    def save_fig(self, event):
        # Ensure the output directory exists
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)  # Creates the directory if it doesn't exist

        ex_names = "_".join(self.ex_names)
        fig_filename = os.path.join(output_dir, f'{ex_names}.png')

        extent = self.ax1.get_tightbbox(self.widget.figure.canvas.get_renderer()).transformed(
            self.widget.figure.dpi_scale_trans.inverted())
        self.widget.figure.savefig(fig_filename, bbox_inches=extent, dpi=300)


    def all_to_csv(self, event):

        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)  # Creates the directory if it doesn't exist

        ex_names = "_".join(self.ex_names)
        csv_filename = os.path.join(os.path.dirname(__file__), 'output', f'{ex_names}.csv')
        with open(csv_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.csv_headers)
            writer.writerows(zip_longest(*self.csv_columns, fillvalue="0"))


class Plot_lgm(Plot):
    def __init__(self, x, y, ex_name, clean):
        super().__init__(x, y, ex_name)
        self.csv_headers.extend([f"{ex_name}_lgM", f"{ex_name}_lgM_y"])
        self.csv_columns.extend([x, y])
        self.ax1.set_xlabel('lgM')
        self.init_second_der()
        self.exp_lines = []
        self.pk_lgm = []
        self.pk_lgm_y = []
        self.gauss_cum_lgm = []
        self.gauss_cum_lgm_y = []
        self.gauss_lgm = []
        self.gauss_lgm_y = []
        self.g_residual_plot = None
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

        self.b_copy_p = Button(text="CP", tooltip="Copy last peak to clipboard")
        self.b_copy_p.setObjectName("CP")
        self.b_copy_p.clicked.connect(self.copy_peak)
        self.widget.add_custom_button(self.b_copy_p)

        self.b_subtract = Button(text="S", tooltip="Subtract first curve from last (normalization point in config.ini)")
        self.b_subtract.setObjectName("S")
        self.b_subtract.clicked.connect(self.subtract_first)

        self.b_subtract_g = Button(text="SG", tooltip="Subtract gaussian sum from last peak")
        self.b_subtract_g.setObjectName("SG")
        self.b_subtract_g.clicked.connect(self.subtract_gauss)

    def add(self, x, y, ex_name, clean):
        self.exp_lines.append(None)
        self.x.append(x)
        self.y.append(y)
        self.ex_names.append(ex_name)
        self.csv_headers.extend([f"{ex_name}_lgM", f"{ex_name}_lgM_y"])
        self.csv_columns.extend([x, y])
        self.add_second_der(x, y)

        self.widget.add_custom_button(self.b_subtract)

        if clean:
            self.exp_lines[-1], = self.ax1.plot(x, y,
                                                color=base_color[(len(self.x) - 1) % len(base_color)], label=ex_name)
        else:
            self.exp_lines[-1], = self.ax1.plot(x, y, 'k--',
                                                color=base_color[(len(self.x) - 1) % len(base_color)], label=ex_name)
        self.ax1.legend()

    def peak(self, pk_lgm_p: list, pk_lgm_p_y: list):
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        self.pk_lgm.append(self.x[-1])
        self.pk_lgm_y.append(self.y[-1])
        self.pk_ex_name.append(self.ex_names[-1])

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
        self.csv_headers.extend([f"{self.ex_names[-1]}_peak_lgM", f"{self.ex_names[-1]}_peak_lgM_y"])
        self.csv_columns.extend([self.pk_lgm[-1], self.pk_lgm_y[-1]])
        self.ax1.plot(self.pk_lgm[-1],
                      self.pk_lgm_y[-1],
                      color=base_color[(len(self.ex_names) - 1) % len(base_color)])
        self.exp_lines[-1].set_label(f'{self.ex_names[-1]} Mn={round(self.m_n)} Mw/Mn={round(self.m_w / self.m_n, 2)}\n'
                                     f'area={round(self.p_area, 3)}')
        self.ax1.legend()

    def gauss(self, guess, lower_bounds, upper_bounds):
        self.widget.add_custom_button(self.b_subtract_g)

        # Perform Gaussian fitting
        popt = gauss_fit(self.pk_lgm[-1], self.pk_lgm_y[-1], guess, lower_bounds, upper_bounds)

        # Extract parameters
        fitted_params = np.array(popt).reshape(-1, 3)  # [amp, cen, sigma] for each gaussian

        self.gauss_cum_lgm = self.pk_lgm[-1]
        self.gauss_cum_lgm_y = multi_gauss(self.pk_lgm[-1], *popt)
        self.csv_headers.extend([f"{self.ex_names[-1]}_g_lgM", f"{self.ex_names[-1]}_g_lgM_y"])
        self.csv_columns.extend([self.gauss_cum_lgm, self.gauss_cum_lgm_y])
        m_n, m_w, total_area = calculate_peak(self.gauss_cum_lgm, self.gauss_cum_lgm_y)
        self.ax1.plot(self.gauss_cum_lgm, self.gauss_cum_lgm_y, color=base_color[-1],
                      label=(f'gauss Mn={round(m_n)} Mw/Mn={round(m_w / self.m_n, 2)}\n'
                             f'area={round(total_area, 3)}'))

        self.gauss_lgm = []
        self.gauss_lgm_y = []
        for i in range(len(fitted_params)):
            self.gauss_lgm.append(self.pk_lgm[-1])
            self.gauss_lgm_y.append(gauss(self.pk_lgm[-1], *fitted_params[i]))
            self.csv_headers.extend([f"{self.ex_names[-1]}_g{i+1}_lgM", f"{self.ex_names[-1]}_g{i+1}_lgM_y"])
            self.csv_columns.extend([self.gauss_lgm[-1], self.gauss_lgm_y[-1]])
            m_n, m_w, area = calculate_peak(self.gauss_lgm[-1], self.gauss_lgm_y[-1])
            self.ax1.plot(self.gauss_lgm[-1], self.gauss_lgm_y[-1], color=base_color[-2 - i],
                          label=(f'gauss{i+1} Mn={round(m_n)} Mw/Mn={round(m_w / m_n, 2)}\n'
                                 f'area={round(area, 3)} ({round(area / total_area * 100)}%)'))

        self.ax1.legend()

    def copy_peak(self, event):
        to_copy = ''
        for i in range(len(self.pk_lgm[-1])):
            to_copy += f'{self.pk_lgm[-1][i]}\t{self.pk_lgm_y[-1][i]}\n'
        clipboard.copy(to_copy)

    def subtract_first(self, event):
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        lgm0_y_norm = normalize_second_by_point(self.x[-1], self.y[-1], self.x[0], self.y[0],
                                                config.getfloat('subtract','lgm_norm'))

        self.ax1.plot(self.x[0], lgm0_y_norm, color='yellow', label=f"{self.ex_names[0]}_norm")
        self.ax1.legend()
        self.show()

        lgm_y = data_math.subtract(self.x[-1], self.y[-1], self.x[0], lgm0_y_norm)
        lgm_y = norm.norm_0_1(lgm_y)
        self.subtracted = Plot_lgm(self.x[-1], lgm_y, self.ex_names[-1], False)
        self.subtracted.peak([None, None], [None, None])
        self.subtracted.show()

    def subtract_gauss(self, event):
        lgm_y = data_math.subtract(self.pk_lgm[-1], self.pk_lgm_y[-1], self.gauss_cum_lgm, self.gauss_cum_lgm_y)
        self.g_residual_plot = Plot_lgm(self.pk_lgm[-1], lgm_y, f"{self.ex_names[-1]}_residual", False)
        self.g_residual_plot.show()


class Plot_vol(Plot):
    def __init__(self, x, y, ex_name):
        super().__init__(x, y, ex_name)
        self.ax1.set_xlabel('vol')
        self.init_second_der()
        self.csv_headers.extend([f"{ex_name}_vol", f"{ex_name}_vol_y"])
        self.csv_columns.extend([x, y])
        self.ax1.plot(x, y, color=base_color[0], label=ex_name)
        self.ax1.legend()

    def add(self, x, y, ex_name):
        self.x.append(x)
        self.y.append(y)
        self.ex_names.append(ex_name)
        self.csv_headers.extend([f"{ex_name}_vol", f"{ex_name}_vol_y"])
        self.csv_columns.extend([x, y])
        self.add_second_der(x, y)
        self.ax1.plot(x, y, color=base_color[(len(self.x) - 1) % len(base_color)], label=ex_name)
        self.ax1.legend()

class Plot_der(Plot):
    def __init__(self, x, y, ex_name, units):
        super().__init__(x, y, ex_name)
        self.units = units
        self.csv_headers.extend([f"{ex_name}_{units}", f"{ex_name}_{units}_y"])
        self.csv_columns.extend([x, y])
        self.ax1.set_xlabel(units)
        self.ax1.scatter(x, y, color=base_color[0], label=ex_name)
        if units == "lgM":
            self.ax1.set_xlim(self.ax1.get_xlim()[::-1])

        self.ax1.legend()

    def add(self, x, y, ex_name):
        self.x.append(x)
        self.y.append(y)
        self.ex_names.append(ex_name)
        self.csv_headers.extend([f"{ex_name}_{self.units}", f"{ex_name}_{self.units}_y"])
        self.csv_columns.extend([x, y])
        self.ax1.scatter(x, y, color=base_color[(len(self.x) - 1) % len(base_color)], label=ex_name)
        self.ax1.legend()

    def init_second_der(self):
        pass


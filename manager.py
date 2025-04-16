# MIT License
# Copyright (c) 2025 MirChemi (mirekchemis@gmail.com)

import os
import configparser

from PySide6.QtWidgets import QMainWindow

from ui.draggable_window import Draggable_window
from scripts import linreg, norm, const_extr, data_extr, data_math
from scripts.tools import safe_float
from scripts.func import vol_to_lgm
from plot import Plot_lgm, Plot_vol


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize the UI with our custom list widget behavior
        self.ui = Draggable_window(self)


class Manager:
    def __init__(self):
        self.app = MyApp()
        self.plots_lgm = []
        self.plots_vol = []
        self.config = configparser.ConfigParser()

        self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        if self.config.get('auto_save', 'const_path') != '':
            self.app.ui.list_const.insertItem(2, self.config.get('auto_save', 'const_path'))

        self.app.ui.lineEdit_v1.setText(self.config.get('auto_save', 'vol1'))
        self.app.ui.lineEdit_v2.setText(self.config.get('auto_save', 'vol2'))

        self.app.ui.pushButton_start.clicked.connect(self.start)

        self.app.show()

    def start(self):
        self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        input_data = self.app.ui.list_data.item(1).text()
        input_const = self.app.ui.list_const.item(1).text()

        flag1 = self.app.ui.lineEdit_v1.text()
        flag2 = self.app.ui.lineEdit_v2.text()

        ex_name = input_data.split("/")[-1].split(".")[0]

        if input_const != '':
            self.config.set('auto_save', 'const_path', input_const)
        self.config.set('auto_save', 'vol1', flag1)
        self.config.set('auto_save', 'vol2', flag2)
        with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w') as configfile:
            self.config.write(configfile)

        c_inputs = [self.app.ui.lineEdit_c0.text(),
                    self.app.ui.lineEdit_c1.text(),
                    self.app.ui.lineEdit_c2.text(),
                    self.app.ui.lineEdit_c3.text()]

        if all(c_inputs):
            const = [safe_float(c_inputs[i]) for i in range(len(c_inputs))]
        else:
            const = const_extr.extract_const(input_const, input_data)
        print('C0 - C3 = ' + str(const))

        vol, vol_y, vol_wt = data_extr.extract_data(input_data, flag1, flag2)

        if not self.app.ui.checkBox_vol.isChecked():
            lgm, lgm_y = [], []
            for i in range(len(vol)):
                if self.config.getboolean('vol_to_lgm', 'lin_approx'):
                    c_lgm1 = self.config.getfloat('lin_approx', 'lin_lgm1')
                    c_lgm2 = self.config.getfloat('lin_approx', 'lin_lgm2')
                    c_vol1 = self.config.getfloat('lin_approx', 'lin_vol1')
                    c_vol2 = self.config.getfloat('lin_approx', 'lin_vol2')
                    lgm.append(linreg.interpolate(vol[i], [c_vol1, c_vol2], [c_lgm1, c_lgm2]))
                else:
                    lgm.append(vol_to_lgm(vol[i], const))
                if i == 1:
                    lgm_y.append(vol_wt[i - 1] / abs(lgm[i] - lgm[i - 1]))
                    lgm_y.append(vol_wt[i - 1] / abs(lgm[i] - lgm[i - 1]))
                elif i > 1:
                    lgm_y.append(2 * vol_wt[i - 1] / abs(lgm[i] - lgm[i - 1]) - lgm_y[i - 1])
            if self.config.get('data', 'norm_mode') == '01':
                lgm_y = norm.norm_0_1(lgm_y)
                print("Norm_0_1")
            elif self.config.get('data', 'norm_mode') == '1':
                lgm_y = norm.norm_1(lgm_y)
                print("Norm_1")

            lgm, lgm_y = data_math.sort_data(lgm, lgm_y)

            if not self.app.ui.checkBox_reuse.isChecked():
                self.plots_lgm.append(Plot_lgm(lgm, lgm_y, ex_name, self.app.ui.checkBox_clean.isChecked()))
            else:
                self.plots_lgm[-1].add(lgm, lgm_y, ex_name, self.app.ui.checkBox_clean.isChecked())

            if not self.app.ui.checkBox_clean.isChecked():
                pk_points = [safe_float(self.app.ui.lineEdit_p1.text()),
                            safe_float(self.app.ui.lineEdit_p2.text())]
                pk_baseline_intensities = [safe_float(self.app.ui.lineEdit_b1.text()),
                              safe_float(self.app.ui.lineEdit_b2.text())]

                if self.app.ui.radioButton_vol.isChecked():
                    pk_points[:2] = [vol_to_lgm(v, const) if v else v for v in pk_points[:2]]
                    print('Recalculating peak position to lgm')
                self.plots_lgm[-1].peak(pk_points, pk_baseline_intensities)

            eps = 0.000001
            gauss_guess = []
            gauss_lower_bounds = []
            gauss_upper_bounds = []

            gauss_use = [self.app.ui.checkBox_enable1.isChecked(),
                         self.app.ui.checkBox_enable2.isChecked(),
                         self.app.ui.checkBox_enable3.isChecked(),
                         self.app.ui.checkBox_enable4.isChecked(),
                         self.app.ui.checkBox_enable5.isChecked(),
                         self.app.ui.checkBox_enable6.isChecked(),
                         self.app.ui.checkBox_enable7.isChecked(),
                         self.app.ui.checkBox_enable8.isChecked()]

            gauss_amp = [
                item.text() if (item := self.app.ui.tableWidget.item(0, i)) else ''
                for i in range(8)
            ]

            gauss_cen = [
                item.text() if (item := self.app.ui.tableWidget.item(1, i)) else ''
                for i in range(8)
            ]

            gauss_sigma = [
                item.text() if (item := self.app.ui.tableWidget.item(2, i)) else ''
                for i in range(8)
            ]

            gauss_lock_cen = [self.app.ui.checkBox_lock1.isChecked(),
                              self.app.ui.checkBox_lock2.isChecked(),
                              self.app.ui.checkBox_lock3.isChecked(),
                              self.app.ui.checkBox_lock4.isChecked(),
                              self.app.ui.checkBox_lock5.isChecked(),
                              self.app.ui.checkBox_lock6.isChecked(),
                              self.app.ui.checkBox_lock7.isChecked(),
                              self.app.ui.checkBox_lock8.isChecked()]
            if any(gauss_use):
                for i in range(len(gauss_use)):
                    if bool(gauss_use[i]):
                        gauss_guess.append(safe_float(gauss_amp[i],
                                                      self.config.getfloat('gauss', 'basic_amp')))
                        gauss_lower_bounds.append(self.config.getfloat('gauss', 'amp_lower_bound'))
                        gauss_upper_bounds.append(self.config.getfloat('gauss', 'amp_upper_bound'))

                        gauss_guess.append(safe_float(gauss_cen[i], -1))
                        if gauss_lock_cen[i]:
                            gauss_lower_bounds.append(gauss_guess[-1] - eps)
                            gauss_upper_bounds.append(gauss_guess[-1] + eps)
                        else:
                            gauss_lower_bounds.append(self.config.getfloat('gauss', 'cen_lower_bound'))
                            gauss_upper_bounds.append(self.config.getfloat('gauss', 'cen_upper_bound'))

                        gauss_guess.append(safe_float(gauss_sigma[i],
                                                      self.config.getfloat('gauss', 'basic_sigma')))
                        gauss_lower_bounds.append(self.config.getfloat('gauss', 'sigma_lower_bound'))
                        gauss_upper_bounds.append(self.config.getfloat('gauss', 'sigma_upper_bound'))

                if gauss_guess:
                    self.plots_lgm[-1].gauss(gauss_guess, gauss_lower_bounds, gauss_upper_bounds)

            self.plots_lgm[-1].show()

        else:
            if not self.app.ui.checkBox_reuse.isChecked():
                self.plots_vol.append(Plot_vol(vol, vol_y, ex_name))
            else:
                self.plots_vol[-1].add(vol, vol_y, ex_name)

            self.plots_vol[-1].show()

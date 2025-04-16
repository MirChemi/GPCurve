import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.addWidget(self.toolbar)

        layout = QVBoxLayout()
        layout.addLayout(self.toolbar_layout)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.resize(750, 600)

    def add_custom_button(self, button: QPushButton):
        self.toolbar_layout.insertWidget(0, button)

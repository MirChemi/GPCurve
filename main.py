# MIT License
# Copyright (c) 2025 MirChemi (mirekchemis@gmail.com)

import sys

from PySide6.QtWidgets import QApplication

from manager import Manager


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = Manager()
    sys.exit(app.exec())

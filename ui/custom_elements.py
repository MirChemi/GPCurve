from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QSize

class Button(QPushButton):
    def __init__(self, text = "", tooltip = "", color = "blue"):
        super().__init__(text)
        self.setToolTip(tooltip)
        self.setFixedSize(24, 24)
        color_map = {
            "blue": ("#3498db", "#5dade2"),
            "red": ("#e74c3c", "#ec7063"),
            "green": ("#2ecc71", "#58d68d"),
        }
        self.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color_map[color][0]};
                        border: none;
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: {color_map[color][1]};
                    }}
                """)

# MIT License
# Copyright (c) 2025 MirChemi (mirekchemis@gmail.com)

from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PySide6.QtCore import Qt

from ui.main_window import Ui_MainWindow  # Import UI from Qt Designer


class Draggable_window(Ui_MainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(main_window)  # Setup the UI on the main window

        # Configure list_data and list_const for external file drops only:
        self.list_data.setAcceptDrops(True)        # Allow dropping items in list_data
        self.list_const.setAcceptDrops(True)         # Allow dropping items in list_const
        self.list_data.setDragEnabled(False)         # Disable internal dragging for list_data
        self.list_const.setDragEnabled(False)        # Disable internal dragging for list_const
        self.list_data.setDropIndicatorShown(True)   # Show drop indicator for list_data
        self.list_const.setDropIndicatorShown(True)    # Show drop indicator for list_const

        # Override drag and drop event handlers with lambda wrappers
        # to pass the correct list widget to our custom dropEvent method.
        self.list_data.dragEnterEvent = self.dragEnterEvent
        self.list_const.dragEnterEvent = self.dragEnterEvent
        self.list_data.dragMoveEvent = self.dragMoveEvent
        self.list_const.dragMoveEvent = self.dragMoveEvent
        self.list_data.dropEvent = lambda event: self.dropEvent(event, self.list_data)
        self.list_const.dropEvent = lambda event: self.dropEvent(event, self.list_const)

    def dragEnterEvent(self, event):
        """
        Accept the drag event if it contains URLs (files).
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Accept the drag move event if it contains URLs.
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event, list_widget):
        """
        Handle external file drops.
        Insert each dropped file path as a new item at the second position of the given list widget.
        """
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()  # Convert URL to local file path
                if file_path:
                    new_item = QListWidgetItem(file_path)
                    list_widget.insertItem(1, new_item)  # Insert at second position (index 1)
                while list_widget.count() > 2:
                    list_widget.takeItem(2)
            event.acceptProposedAction()
        else:
            event.ignore()
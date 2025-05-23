from PyQt5 import QtWidgets as QW
from PyQt5 import QtCore as QC

import qfluentwidgets as QFW

class ApplicationMainWindow(QFW.FluentWindow):
    def __init__(self, title: str, parent = None) -> None:
        super(QFW.FluentWindow, self).__init__(parent)

        self.setWindowTitle(title)
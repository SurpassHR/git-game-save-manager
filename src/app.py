import sys
from PyQt5 import QtWidgets as QW
from PyQt5 import QtCore as QC

from src.uiFrame.mainWindow import ApplicationMainWindow


class App:
    def __init__(self, title: str = "Default Main Window.") -> None:
        self._title = title

    def start(self) -> None:
        QW.QApplication.setHighDpiScaleFactorRoundingPolicy(QC.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QW.QApplication.setAttribute(QC.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QW.QApplication.setAttribute(QC.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        self._app = QW.QApplication(sys.argv)
        self._mainWindow = ApplicationMainWindow(self._title)
        self._mainWindow.show()
        self._app.exec()
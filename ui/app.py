import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

rootPath = str(Path(__file__).resolve().parent.parent)
sys.path.append(rootPath)

from ui.components.mainWindow import MainWindow
from core.gitManager import GitManager


def start():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    git_manager = GitManager("./saves")  # 默认存档目录
    mainWindow = MainWindow(git_manager)
    mainWindow.show()
    app.exec()
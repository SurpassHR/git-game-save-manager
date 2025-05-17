import sys
from core.gitManager import GitManager
from ui.graphView import MyMainWindow

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    git_manager = GitManager("./saves")  # 默认存档目录
    window = MyMainWindow(git_manager)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
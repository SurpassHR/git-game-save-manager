import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from pathlib import Path

from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets.common.style_sheet import setThemeColor
from qfluentwidgets.common.icon import FluentIcon

rootPath = str(Path(__file__).resolve().parent.parent)
sys.path.append(rootPath)

from ui.components.pages.mainPage import MainPage
from ui.components.utils.uiFunctionBase import UIFunctionBase


class MainWindow(FluentWindow, UIFunctionBase):
    APP_WIDTH = 1920
    APP_HEIGHT = 1080
    THEME_COLOR = "#8A95A9"

    def __init__(self, git_manager) -> None:
        super().__init__()

        self.git_manager = git_manager
        self.setWindowTitle("PyQt5 GraphicsView Test")
        self.resize(self.APP_WIDTH, self.APP_HEIGHT)

        setThemeColor(self.THEME_COLOR)

        # 隐藏标题栏图标
        self.titleBar.iconLabel.hide()

        # 隐藏导航栏
        # self.navigationInterface.hide()

        # 设置侧边栏宽度
        self.navigationInterface.setExpandWidth(192)

        # 侧边栏默认展开
        self.navigationInterface.setMinimumExpandWidth(self.APP_WIDTH)
        self.navigationInterface.expand(useAni = False)

        # 设置启动位置
        desktop = QApplication.desktop()
        if desktop:
            desktop = desktop.availableGeometry()
            self.move(desktop.width()//2 - self.width()//2, desktop.height()//2 - self.height()//2)
        else:
            exit(-1)

        self._mainPage = MainPage("_mainPage", self)
        self._mainPage.git_manager = git_manager
        self.addSubInterface(self._mainPage, FluentIcon.SETTING, "配置执行", NavigationItemPosition.SCROLL)

        self.uiSetMainWindow(self)

        self.show()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    mainWindow = MainWindow(None)
    app.exec()
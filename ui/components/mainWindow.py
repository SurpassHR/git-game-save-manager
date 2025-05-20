import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from pathlib import Path

from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets.common.style_sheet import setThemeColor
from qfluentwidgets.common.icon import FluentIcon

rootPath = str(Path(__file__).resolve().parent.parent)
sys.path.append(rootPath)

from ui.components.pages.eventGraphPage import EventGraphPage
from ui.components.pages.configPage import ConfigPage
from ui.components.utils.uiFunctionBase import UIFunctionBase


class MainWindow(FluentWindow, UIFunctionBase):
    THEME_COLOR = "#8A95A9"

    def __init__(self) -> None:
        super().__init__()

        self.wWidth: int = 1280
        self.wHeight: int = 720

        self.setWindowTitle("PyQt5 GraphicsView Test")

        setThemeColor(self.THEME_COLOR)

        # 设置启动位置
        self.setWindowPosAndSize()

        # 配置标题栏
        self.configTitleBar()

        # 配置导航栏
        self.configNaviBar()

        # 添加页面
        self.addPages()

        # 绑定主窗口
        self.uiSetMainWindow(self)

        self.show()

    def setWindowPosAndSize(self):
        desktop = QApplication.desktop()
        if not desktop:
            exit(-1)
        desktop = desktop.availableGeometry()

        self.wWidth = int(desktop.width() * 2 / 3)
        self.wHeight = int(desktop.height() * 2 / 3)
        self.resize(self.wWidth, self.wHeight)
        self.setMinimumSize(self.wWidth, self.wHeight)
        self.move(desktop.width() // 2 - self.width() // 2, desktop.height() // 2 - self.height() // 2)

    def configTitleBar(self):
        # 隐藏标题栏图标
        self.titleBar.iconLabel.hide()

    def configNaviBar(self):
        # 设置侧边栏宽度
        self.navigationInterface.setExpandWidth(192)

        # 侧边栏默认展开
        self.navigationInterface.setMinimumExpandWidth(self.wWidth)
        print(self.wWidth)
        self.navigationInterface.expand(useAni = False)

        # 隐藏返回按钮
        self.navigationInterface.panel.setReturnButtonVisible(False)

    def addPages(self):
        self._configPage = ConfigPage("_configPage", self)
        self.addSubInterface(self._configPage, FluentIcon.SETTING, "配置管理", NavigationItemPosition.SCROLL)

        self._eventGraphPage = EventGraphPage("_eventGraphPage", self)
        self.addSubInterface(self._eventGraphPage, FluentIcon.BROOM, "事件视图", NavigationItemPosition.SCROLL)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    app.exec()
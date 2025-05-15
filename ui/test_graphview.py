import sys
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QVBoxLayout, QFrame
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt
from pathlib import Path

from qfluentwidgets import FluentWindow, NavigationItemPosition
from qfluentwidgets.common.style_sheet import setThemeColor
from qfluentwidgets.common.icon import FluentIcon

rootPath = str(Path(__file__).resolve().parent.parent)
sys.path.append(rootPath)

from ui.components.infiniteCanvasView import InfiniteCanvasView
from ui.components.gridScene import SmartGridScene


class MainPage(QFrame):
    def __init__(self, text: str, window) -> None:
        super().__init__(window)
        self.setObjectName(text.replace(" ", "-"))

        self.window = window

        self.createUI()

    def createUI(self):
        viewContainer = QVBoxLayout()

        scene = SmartGridScene(self)

        # greenBrush = QBrush(Qt.GlobalColor.green)
        blueBrush = QBrush(Qt.GlobalColor.blue)

        blackPen = QPen(Qt.GlobalColor.black)
        blackPen.setWidth(5)

        rect = scene.addEllipse(-100, -100, 200, 200, blackPen, blueBrush)
        if not rect:
            return
        rect.setBrush(blueBrush)
        rect.setPen(blackPen)
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        view = InfiniteCanvasView(scene, self)
        view.setGeometry(0, 0, 1280, 720)

        viewContainer.addWidget(view)
        self.setLayout(viewContainer)

class MyMainWindow(FluentWindow):
    APP_WIDTH = 1280
    APP_HEIGHT = 720
    THEME_COLOR = "#8A95A9"

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("PyQt5 GraphicsView Test")
        self.resize(self.APP_WIDTH, self.APP_HEIGHT)

        setThemeColor(self.THEME_COLOR)

        self.titleBar.iconLabel.hide()
        # 设置启动位置
        desktop = QApplication.desktop()
        if desktop:
            desktop = desktop.availableGeometry()
            self.move(desktop.width()//2 - self.width()//2, desktop.height()//2 - self.height()//2)
        else:
            exit(-1)

        self._mainPage = MainPage("_mainPage", self)
        self.addSubInterface(self._mainPage, FluentIcon.SETTING, "配置执行", NavigationItemPosition.SCROLL)

        # self.createUI()

        self.show()

    def createUI(self):
        viewContainer = QVBoxLayout()

        scene = SmartGridScene(self)

        # greenBrush = QBrush(Qt.GlobalColor.green)
        blueBrush = QBrush(Qt.GlobalColor.blue)

        blackPen = QPen(Qt.GlobalColor.black)
        blackPen.setWidth(5)

        rect = scene.addEllipse(-100, -100, 200, 200, blackPen, blueBrush)
        if not rect:
            return
        rect.setBrush(blueBrush)
        rect.setPen(blackPen)
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        view = InfiniteCanvasView(scene, self)
        view.setGeometry(0, 0, 1280, 720)

        viewContainer.addWidget(view)
        self.setLayout(viewContainer)

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    mainWindow = MyMainWindow()
    app.exec()
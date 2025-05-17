import sys
import uuid
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QFrame, QBoxLayout
from PyQt5.QtCore import Qt
from pathlib import Path

from qfluentwidgets import FluentWindow, NavigationItemPosition, PrimaryPushButton
from qfluentwidgets.common.style_sheet import setThemeColor
from qfluentwidgets.common.icon import FluentIcon

rootPath = str(Path(__file__).resolve().parent.parent)
sys.path.append(rootPath)

from ui.components.widgets.infiniteCanvasView import InfiniteCanvasView
from ui.components.widgets.gridScene import SmartGridScene
from ui.tools.styleDefs import NODE_BORDER_DEFAULT_PEN, NODE_FILL_DEFAULT_BRUSH, NODE_VERTICAL_SPACING


class MainPage(QFrame):
    def __init__(self, text: str, window) -> None:
        super().__init__(window)
        self.setObjectName(text.replace(" ", "-"))

        self.window = window

        self.createUI()

    def addScene(self, container: QBoxLayout) -> None:
        self.scene = SmartGridScene(self)

        view = InfiniteCanvasView(self.scene, self)
        view.setGeometry(0, 0, 1280, 720)

        container.addWidget(view)

    def createUI(self) -> None:
        container = QVBoxLayout()

        def addCtrlBtn(container: QBoxLayout):
            btnContainer = QHBoxLayout()

            btn1 = PrimaryPushButton(
                text="增加节点",
                icon=FluentIcon.ADD,
            )
            btn1.clicked.connect(self.addStandardNode)

            btn2 = PrimaryPushButton(
                text="删除节点",
                icon=FluentIcon.REMOVE,
            )
            btn2.clicked.connect(self.removeSelectedNode)

            btnContainer.addWidget(btn1, 1)
            btnContainer.addWidget(btn2, 1)

            container.addLayout(btnContainer)

        addCtrlBtn(container)
        self.addScene(container)
        self.setLayout(container)

    def addStandardNode(self) -> None:
        selectedNode = self.scene.getSelected()
        isSceneEmpty = self.scene.isEmpty()

        # 当前没有选中的节点，且场景内已有节点，不添加新节点
        if selectedNode is None and not isSceneEmpty:
            return

        # 当前没有选中的节点，但是场景内没有节点，此时添加一个首节点
        if selectedNode is None and isSceneEmpty:
            self.scene.createDragableRound(
                x=0,
                y=0,
                r=30,
                border=NODE_BORDER_DEFAULT_PEN,
                fill=NODE_FILL_DEFAULT_BRUSH,
                id="root",
                parentId="",
            )

        # 当前有选中的节点，给该节点添加一个子节点
        if selectedNode:
            pos = self.scene.getGraphicPosition(selectedNode.id)
            if pos is None:
                return
            self.scene.createDragableRound(
                x=pos.x(),
                y=pos.y() + NODE_VERTICAL_SPACING,
                r=30,
                border="#000",
                fill="#FC5531",
                id=str(uuid.uuid4()),
                parentId=selectedNode.id,
            )

    def removeSelectedNode(self) -> None:
        selectedNode = self.scene.getSelected()
        if not selectedNode:
            return
        self.scene.removeGraphic(selectedNode.id)


class MainWindow(FluentWindow):
    APP_WIDTH = 1280
    APP_HEIGHT = 720
    THEME_COLOR = "#8A95A9"

    def __init__(self, sth) -> None:
        super().__init__()

        self.setWindowTitle("PyQt5 GraphicsView Test")
        self.resize(self.APP_WIDTH, self.APP_HEIGHT)

        setThemeColor(self.THEME_COLOR)

        # 隐藏标题栏图标
        self.titleBar.iconLabel.hide()

        # 隐藏导航栏
        self.navigationInterface.hide()

        # 设置启动位置
        desktop = QApplication.desktop()
        if desktop:
            desktop = desktop.availableGeometry()
            self.move(desktop.width()//2 - self.width()//2, desktop.height()//2 - self.height()//2)
        else:
            exit(-1)

        self._mainPage = MainPage("_mainPage", self)
        self.addSubInterface(self._mainPage, FluentIcon.SETTING, "配置执行", NavigationItemPosition.SCROLL)

        self.show()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    mainWindow = MainWindow(None)
    app.exec()
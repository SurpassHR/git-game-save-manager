import sys
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QMenu, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
# from PyQt5.QtWebChannel import QWebChannel

class MainWindow(QWidget):
    APP_WIDTH = 1280
    APP_HEIGHT = 720

    def __init__(self) -> None:
        super().__init__()


        layout = QVBoxLayout()
        self.webView = QWebEngineView()
        self.webView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.webView.customContextMenuRequested.connect(self.showContextMenu)
        # 创建独立的开发者工具视图
        self.devToolsView = QWebEngineView()
        self.webView.page().setDevToolsPage(self.devToolsView.page())
        self.webView.loadFinished.connect(self.onLoadFinished)

        layout.addWidget(self.webView)

        htmlPath = os.path.join(os.path.dirname(__file__), '..', 'static', 'test_qwebchannel.html')
        self.webView.load(QUrl.fromLocalFile(htmlPath))
        self.setLayout(layout)
        self.resize(self.APP_WIDTH, self.APP_HEIGHT)
        self.show()

    def showContextMenu(self, pos):
        menu = QMenu(self)
        inspectAction = QAction("Open developer tools", self)
        inspectAction.triggered.connect(self.openDevTools)
        menu.addAction(inspectAction)
        menu.exec(self.webView.mapToGlobal(pos))

    def openDevTools(self):
        try:
            # 确保开发者工具视图可见
            self.devToolsView.show()
            # 触发开发者工具
            self.webView.page().triggerAction(QWebEnginePage.WebAction.InspectElement) # type: ignore
        except Exception as e:
            print(f"打开开发者工具失败: {e}")

    def onLoadFinished(self, ok):
        if ok:
            self.webView.page().runJavaScript("console.log('页面加载完成');")

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    # 必须设置此属性才能启用开发者工具
    # QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # 显示开发者工具窗口
    # mainWindow.devToolsView.show()
    app.exec()
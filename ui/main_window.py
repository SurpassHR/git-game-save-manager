from PyQt5.QtCore import pyqtSignal, QObject, Qt, pyqtSlot
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QInputDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import json

from core.gitManager import GitManager

class Bridge(QObject):
    """JavaScript-Python通信桥"""
    nodeClicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    @pyqtSlot(str)
    def send_node_click(self, node_id):
        """处理来自JS的节点点击事件"""
        self.nodeClicked.emit(node_id)
    nodeClicked = pyqtSignal(str)

    def send_node_click(self, node_id):
        self.nodeClicked.emit(node_id)

class MainWindow(QMainWindow):
    def __init__(self, git_manager):
        super().__init__()
        self.git_manager: GitManager = git_manager
        self.bridge = Bridge()
        self.init_ui()
        self.load_visualization()

    def init_ui(self):
        self.setWindowTitle('Git 存档管理系统')
        self.setGeometry(100, 100, 1200, 800)

        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 操作按钮面板
        control_panel = QHBoxLayout()
        self.btn_init = QPushButton('初始化仓库')
        self.btn_commit = QPushButton('创建决策点')
        self.btn_branch = QPushButton('新建分支')
        self.btn_load = QPushButton('加载仓库')

        control_panel.addWidget(self.btn_init)
        control_panel.addWidget(self.btn_commit)
        control_panel.addWidget(self.btn_branch)
        control_panel.addWidget(self.btn_load)

        # Web视图初始化
        self.web_view = QWebEngineView()
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)

        # 页面加载完成后初始化WebChannel
        def init_webchannel():
            self.web_view.page().setWebChannel(self.channel)
            self.web_view.page().runJavaScript("""
                if (typeof qt !== 'undefined') {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        window.bridge = channel.objects.bridge;
                        console.log('WebChannel initialized');
                        // 确保方法存在
                        if (!window.bridge.send_node_click) {
                            window.bridge.send_node_click = function(id) {
                                console.log('Fallback send_node_click:', id);
                            };
                        }
                    });
                }
            """)

        self.web_view.loadFinished.connect(init_webchannel)

        main_layout.addLayout(control_panel)
        main_layout.addWidget(self.web_view, 1)  # 添加伸缩因子1使webview随窗口缩放
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 连接信号
        self.btn_init.clicked.connect(self.init_repo)
        self.btn_commit.clicked.connect(self.create_commit)
        self.btn_branch.clicked.connect(self.create_branch)
        self.btn_load.clicked.connect(self.load_repo)
        self.bridge.nodeClicked.connect(self.handle_node_click)

    def handle_node_click(self, node_id):
        """处理节点点击事件，回退到对应commit"""
        try:
            if self.git_manager.checkout_commit(node_id):
                QMessageBox.information(self, "成功", f"已回退到版本: {node_id[:7]}")
                self.update_graph()  # 刷新视图
            else:
                QMessageBox.warning(self, "警告", "回退失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def load_visualization(self):
        self.web_view.setHtml(open('static/d3_graph.html').read())

    def update_graph(self):
        data = self.git_manager.get_graph_data()
        self.web_view.page().runJavaScript(f"updateGraph({json.dumps(data)})")

    def init_repo(self):
        path = QFileDialog.getExistingDirectory(self, '选择存档目录')
        if path:
            self.git_manager.repo_path = path
            self.git_manager.initialize()
            self.update_graph()

    def create_commit(self):
        """创建决策点commit"""
        try:
            text, ok = QInputDialog.getText(self, '创建决策点', '输入决策描述:')
            if ok and text.strip():
                commit_hash = self.git_manager.create_decision_point(text.strip())
                QMessageBox.information(self, "成功", f"决策点已创建\nCommit: {commit_hash[:7]}")
                self.update_graph()
            else:
                QMessageBox.warning(self, "提示", "请输入有效的决策描述")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def create_branch(self):
        # 实际应弹出输入对话框
        self.git_manager.create_branch("new_branch", "分支说明")
        self.update_graph()

    def load_repo(self):
        path = QFileDialog.getExistingDirectory(self, '选择已有仓库')
        if path:
            self.git_manager.repo_path = path
            self.git_manager.initialize()
            self.update_graph()

    def handle_node_click(self, node_id):
        print(f"节点被点击: {node_id}")
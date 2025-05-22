import sys
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QFileDialog
from pathlib import Path

from qfluentwidgets import FluentIcon

rootPath = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.configLoader import getConfig, setConfig

from ui.components.utils.uiFunctionBase import UIFunctionBase
from ui.components.widgets.frames.pushButtonCard import PushButtonCard

class ConfigPage(QFrame, UIFunctionBase):
    def __init__(self, text: str, window) -> None:
        QFrame.__init__(self, window)

        self.setObjectName(text.replace(" ", "-"))

        # 主容器
        container = QVBoxLayout()
        container.setSpacing(8)

        container.addWidget(self.createSelectRepoCard())
        container.addStretch(1)

        self.window = window

        self.setLayout(container)

    def createSelectRepoCard(self) -> PushButtonCard:
        def selectRepoCardInit(widget: PushButtonCard):
            selectedRepo = "当前管理存档目录: " + f"{getConfig("repo")}"
            widget.setDescription(f"{selectedRepo}")
            widget.setText("选择文件夹")
            widget.setIcon(FluentIcon.FOLDER_ADD)

        def selectRepoCardClicked(widget: PushButtonCard):
            # 选择文件夹
            path = QFileDialog.getExistingDirectory(
                parent=None,
                caption="选择目录",
            )
            path = path.strip()
            if path is None or path == "":
                return
            setConfig("repo", path)
            selectedRepo = "当前管理存档目录: " + f"{getConfig("repo")}"
            widget.setDescription(f"{selectedRepo}")

        return PushButtonCard(
            title="选择存档目录",
            description="选择存档目录",
            init=selectRepoCardInit,
            clicked=selectRepoCardClicked,
        )
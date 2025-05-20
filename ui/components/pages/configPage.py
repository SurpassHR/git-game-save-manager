import sys
import uuid
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QBoxLayout
from pathlib import Path

from qfluentwidgets import PrimaryPushButton
from qfluentwidgets.common.icon import FluentIcon

from ui.components.utils.eventManager import EventEnum

rootPath = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(rootPath)

from core.getGitInfo import CommitObj
from ui.components.utils.uiFunctionBase import UIFunctionBase
from ui.components.widgets.infiniteCanvasView import InfiniteCanvasView
from ui.components.widgets.gridScene import SmartGridScene
from ui.publicDefs.styleDefs import NODE_VERTICAL_SPACING

class ConfigPage(QFrame, UIFunctionBase):
    def __init__(self, text: str, window) -> None:
        QFrame.__init__(self, window)

        self.setObjectName(text.replace(" ", "-"))

        self.window = window
import sys
from pathlib import Path
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF
from typing import Callable

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint
from core.getGitInfo import CommitObj
from ui.components.graphics.graphicsInterface import EdgeLineBase, RoundNodeBase

class RoundNodeGraphic(RoundNodeBase, CommitObj):
    def __init__(self, rect: QRectF, selectCb: Callable, level: int):
        super().__init__(rect)

        self.selectCb: Callable = selectCb
        self.level = level # 表示从根节点到本节点的距离
        self.connections: list[EdgeLineBase] = []

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def setCommitInfo(self, commitObj: CommitObj):
        for k, v in commitObj.__dict__.items():
            self.setItem(k, v)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if self.isSelected() and self.selectCb:
            self.selectCb(self.hexSha, True)
        if not event:
            return
        self.posBeforeMove = self.scenePos()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if not event:
            return
        loggerPrint(f"move '{self.hexSha}': {self.posBeforeMove} -> {self.scenePos()}, parent: {self.parentItem()}")

    def setSelected(self, selected: bool) -> None:
        super().setSelected(selected)
        if self.selectCb:
            self.selectCb(self.hexSha, selected)

    def mouseMoveEvent(self, event):
        old_pos = self.pos()
        super().mouseMoveEvent(event)
        if old_pos != self.pos():
            for edges in self.connections:
                edges.updatePosition()

    def addConnection(self, connection):
        self.connections.append(connection)
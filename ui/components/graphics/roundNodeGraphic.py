import sys
from pathlib import Path
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QRectF
from typing import Callable, Optional

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint


class RoundNodeGrphic(QGraphicsEllipseItem):
    def __init__(self, rect: QRectF, selectCb: Callable, id: str, parentId: Optional[str]):
        super().__init__(rect)

        self.selectCb: Callable = selectCb
        self.id: str = id
        self.parentId: Optional[str] = parentId

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if self.isSelected() and self.selectCb:
            self.selectCb(self.id, True)
        if not event:
            return
        self.posBeforeMove = self.scenePos()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if not event:
            return
        loggerPrint(f"move {self.id}: {self.posBeforeMove} -> {self.scenePos()}, parent: {self.parentItem()}")

    def setSelected(self, selected: bool) -> None:
        super().setSelected(selected)

        if self.selectCb:
            self.selectCb(self.id, selected)

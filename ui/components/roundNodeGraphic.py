import sys
from pathlib import Path
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from PyQt5.QtCore import QRectF
from typing import Callable, Optional

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)


class RoundNodeGrphic(QGraphicsEllipseItem):
    def __init__(self, rect: QRectF, selectCb: Callable, id: str, parent: Optional[QGraphicsItem] = None):
        super().__init__(rect, parent)
        self.selectCb = selectCb
        self.id = id

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isSelected() and self.selectCb:
            self.selectCb(self.id, True)

    def setSelected(self, selected: bool) -> None:
        if self.selectCb:
            self.selectCb(self.id, False)

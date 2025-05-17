import sys
from pathlib import Path
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QAbstractGraphicsShapeItem, QGraphicsScene
from PyQt5.QtCore import QRectF, QPointF
from typing import Optional

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint
from ui.components.roundNodeGraphic import RoundNodeGrphic

class GraphicManager:
    def __init__(self) -> None:
        self.graphics: dict[str, QAbstractGraphicsShapeItem] = {}
        self.selected: Optional[QAbstractGraphicsShapeItem] = None

    def boundToScene(self, scene: QGraphicsScene) -> None:
        self.scene = scene

    def setSelected(self, graphicId: str, isSelected: bool):
        if isSelected:
            self.selected = self.getGraphic(graphicId)
            loggerPrint(f"graphic selected: {graphicId} obj: {self.selected}")
        else:
            self.selected = None
            loggerPrint(f"graphic diselected: {graphicId}")

    def getSelected(self):
        pass

    def createDragableRound(
        self,
        x: float,
        y: float,
        r: float,
        border: str | QPen,
        fill: str | QBrush,
        id: str,
    ):
        round = RoundNodeGrphic(
            rect=QRectF(x, y, r, r),
            selectCb=self.setSelected,
            id=id,
        )
        if not round:
            return None

        round.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        round.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        pen: QPen = QPen()
        brush: QBrush = QBrush()
        if isinstance(border, str) and isinstance(fill, str):
            brush: QBrush = QBrush(QColor(fill))
            pen: QPen = QPen(QColor(border))
        elif isinstance(border, QPen) and isinstance(fill, QBrush):
            brush: QBrush= fill
            pen: QPen = border

        round.setBrush(brush)
        round.setPen(pen)

        self.graphics[id] = round
        if self.scene:
            self.scene.addItem(round)
        loggerPrint(f"created round graphic borderColor: {pen.color().name()}, fillColor: {brush.color().name()}, pos: ({x}, {y}), radius: {r}")
        return round

    def getGraphic(self, id: str) -> Optional[QAbstractGraphicsShapeItem]:
        graphic = self.graphics.get(id)
        if not graphic:
            return None
        return graphic

    def getGraphicPosition(self, id: str) -> Optional[QPointF]:
        graphic = self.graphics.get(id)
        if not graphic:
            return None
        return graphic.pos()

    # 获取图形的外接矩形的大小
    def getGraphicSize(self, id: str) -> Optional[QRectF]:
        graphic = self.graphics.get(id)
        if not graphic:
            return None
        return graphic.boundingRect()

    def removeGraphic(self, id: str) -> None:
        graphic = self.graphics.get(id)
        if not graphic:
            return None

        graphic.hide()
        self.scene.removeItem(graphic)
        _ = self.graphics.pop(id)

    def destroyAll(self) -> None:
        for graphic in self.graphics.values():
            self.scene.removeItem(graphic)
        self.graphics.clear()

    def clearAllSelectedGraphic(self) -> None:
        for graphic in self.graphics.values():
            if graphic.isSelected():
                graphic.setSelected(False)
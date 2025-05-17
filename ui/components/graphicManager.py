import sys
from pathlib import Path
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene
from PyQt5.QtCore import QRectF, QPointF, QSizeF
from typing import Optional

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint
from ui.components.graphics.roundNodeGraphic import RoundNodeGrphic

class NodeManager:
    def __init__(self) -> None:
        self.nodes: dict[str, RoundNodeGrphic] = {}
        self.selected: Optional[RoundNodeGrphic] = None

    def boundToScene(self, scene: QGraphicsScene) -> None:
        self.scene = scene

    def setSelected(self, graphicId: str, isSelected: bool):
        if isSelected:
            self.selected = self.getGraphic(graphicId)
            loggerPrint(f"graphic selected: {graphicId}")
        else:
            self.selected = None
            loggerPrint(f"graphic diselected: {graphicId}")

    def getSelected(self) -> Optional[RoundNodeGrphic]:
        return self.selected

    def isEmpty(self):
        return len(self.nodes) == 0

    def createDragableRound(
        self,
        x: float,
        y: float,
        r: float,
        border: str | QPen,
        fill: str | QBrush,
        id: str,
        parentId: Optional[str],
    ):
        round = RoundNodeGrphic(
            rect=QRectF(0, 0, r, r),
            selectCb=self.setSelected,
            id=id,
            parentId=parentId,
        )
        round.setPos(x, y)

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

        self.nodes[id] = round
        if self.scene:
            self.scene.addItem(round)
        loggerPrint(fr"created node {id} graphic, parent {parentId if parentId else 'none'}, pos: ({x}, {y}), radius: {r}")
        return round

    def getGraphic(self, id: str) -> Optional[RoundNodeGrphic]:
        graphic = self.nodes.get(id)
        if not graphic:
            return None
        return graphic

    def getGraphicPosition(self, id: str) -> Optional[QPointF]:
        graphic = self.nodes.get(id)
        if not graphic:
            return None
        loggerPrint(f"get node {id} position: {graphic.scenePos()}")
        return graphic.scenePos()

    # 获取图形的外接矩形的大小
    def getGraphicSize(self, id: str) -> Optional[QSizeF]:
        graphic = self.nodes.get(id)
        if not graphic:
            return None
        loggerPrint(f"get node {id} size: {graphic.boundingRect().size()}")
        return graphic.boundingRect().size()

    def removeGraphic(self, id: str) -> None:
        graphic = self.nodes.get(id)
        if not graphic:
            return None

        loggerPrint(f"remove node {id} graphic, pos: ({graphic.pos().x()}, {graphic.pos().y()}), radius: {graphic.rect().width()}")
        graphic.hide()
        self.scene.removeItem(graphic)
        _ = self.nodes.pop(id)

    def destroyAll(self) -> None:
        for graphic in self.nodes.values():
            self.scene.removeItem(graphic)
        self.nodes.clear()

    def clearAllSelectedGraphic(self) -> None:
        for graphic in self.nodes.values():
            if graphic.isSelected():
                graphic.setSelected(False)
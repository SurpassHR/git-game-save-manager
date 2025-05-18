import sys
from pathlib import Path
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene
from PyQt5.QtCore import QRectF, QPointF, QSizeF
from typing import Optional

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.getGitInfo import CommitObj
from core.tools.utils.simpleLogger import loggerPrint
from ui.components.graphics.roundNodeGraphic import RoundNodeGrphic
from ui.components.graphics.connectionLineGraphic import ConnectionLineGraphic
from ui.tools.styleDefs import NODE_BORDER_DEFAULT_PEN, NODE_FILL_DEFAULT_BRUSH

class NodeManager:
    def __init__(self) -> None:
        self.nodes: dict[str, RoundNodeGrphic] = {}
        self.connections: dict[str, ConnectionLineGraphic] = {}
        self.selected: Optional[RoundNodeGrphic] = None

    def boundToScene(self, scene: QGraphicsScene) -> None:
        self.scene = scene

    def setSelected(self, graphicId: str, isSelected: bool):
        if isSelected:
            self.selected = self.getNode(graphicId)
            loggerPrint(f"node selected: {graphicId}")
        else:
            self.selected = None
            loggerPrint(f"node diselected: {graphicId}")

    def getSelected(self) -> Optional[RoundNodeGrphic]:
        return self.selected

    def isEmpty(self):
        return len(self.nodes) == 0

    def createDragableNode(
        self,
        x: float,
        y: float,
        r: float,
        commitObj: CommitObj,
        level: int,
        border: str | QPen = NODE_BORDER_DEFAULT_PEN,
        fill: str | QBrush = NODE_FILL_DEFAULT_BRUSH,
    ) -> Optional[RoundNodeGrphic]:
        isNodeExisted = self.nodes.get(commitObj.hexSha, '') != ''
        if isNodeExisted:
            return

        # 创建图形
        round = RoundNodeGrphic(
            rect=QRectF(0, 0, r, r),
            selectCb=self.setSelected,
            level=level,
        )
        round.setCommitInfo(commitObj)
        round.setPos(x, y)

        # 设置图形属性: 可拖动、可选中
        round.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        round.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # 设置图形样式
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

        # 将图形添加到场景
        self.nodes[round.hexSha] = round
        if self.scene:
            self.scene.addItem(round)

        # 连接父节点与子节点
        loggerPrint(fr"created node {round.hexSha} graphic, parents {round.parents}, pos: ({x}, {y}), radius: {r}")

        # 判断是否根节点
        if len(round.parents) == 0:
            self.rootNode = round.hexSha

        return round

    def getNode(self, hexSha: str) -> Optional[RoundNodeGrphic]:
        node = self.nodes.get(hexSha)
        if not node:
            return None
        return node

    def getRootNode(self) -> Optional[RoundNodeGrphic]:
        node = self.nodes.get(self.rootNode)
        if not node:
            return None
        return node

    def getNodePosition(self, hexSha: str) -> Optional[QPointF]:
        node = self.nodes.get(hexSha)
        if not node:
            return None
        loggerPrint(f"get node {hexSha} graphic position: {node.scenePos()}")
        return node.scenePos()

    # 获取图形的外接矩形的大小
    def getNodeGraphicSize(self, hexSha: str) -> Optional[QSizeF]:
        node = self.nodes.get(hexSha)
        if not node:
            return None
        loggerPrint(f"get node {hexSha} graphic size: {node.boundingRect().size()}")
        return node.boundingRect().size()

    def removeGraphic(self, hexSha: str) -> None:
        node = self.nodes.get(hexSha)
        if not node:
            return None

        loggerPrint(f"remove node {hexSha} graphic, pos: ({node.pos().x()}, {node.pos().y()}), radius: {node.rect().width()}")
        node.hide()
        self.scene.removeItem(node)
        _ = self.nodes.pop(hexSha)

    def destroyAll(self) -> None:
        for node in self.nodes.values():
            self.scene.removeItem(node)
        self.nodes.clear()

    def clearAllSelectedGraphic(self) -> None:
        for node in self.nodes.values():
            if node.isSelected():
                node.setSelected(False)

    def getAllLeafNodes(self) -> None:
        nodeIdList: list[str] = []
        for node in self.nodes.values():
            if len(node.children) == 0:
                nodeIdList.append(node.hexSha)
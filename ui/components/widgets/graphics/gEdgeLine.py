import sys
from pathlib import Path
from PyQt5.QtCore import QLineF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsLineItem

rootPath = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(rootPath)

from ui.components.widgets.interfaces import ICommitNode


class EdgeLineGraphic(QGraphicsLineItem):
    def __init__(self, startNode: ICommitNode, endNode: ICommitNode) -> None:
        super().__init__()

        startPoint = startNode.getNodeGraphicCenter()
        endPoint = endNode.getNodeGraphicCenter()

        self.setLine(QLineF(startPoint, endPoint))
        self.setPen(QPen(QColor("#000")))
        self.setZValue(-1)
        self.show()

        self.start: ICommitNode = startNode
        self.end: ICommitNode = endNode

    def updatePosition(self):
        # 计算两个椭圆中心之间的连线
        line = QLineF(self.start.getNodeGraphicCenter(), self.end.getNodeGraphicCenter())
        self.setLine(line)
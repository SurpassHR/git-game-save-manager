import sys
from pathlib import Path
from PyQt5.QtCore import QLineF, QRectF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsEllipseItem

rootPath = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(rootPath)


class RoundNodeBase(QGraphicsEllipseItem):
    def __init__(self, rect: QRectF) -> None:
        super().__init__(rect)

class EdgeLineBase(QGraphicsLineItem):
    def __init__(self, startNode: RoundNodeBase, endNode: RoundNodeBase) -> None:
        super().__init__()

        self.start: RoundNodeBase = startNode
        self.end: RoundNodeBase = endNode

        startPoint = startNode.sceneBoundingRect().center()
        endPoint = endNode.sceneBoundingRect().center()

        self.setLine(QLineF(startPoint, endPoint))
        self.setPen(QPen(QColor("#000")))
        self.setZValue(-1)
        self.show()

    def updatePosition(self):
        # 计算两个椭圆中心之间的连线
        line = QLineF(self.start.sceneBoundingRect().center(),
                      self.end.sceneBoundingRect().center())
        self.setLine(line)
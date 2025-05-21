from PyQt5.QtCore import QLineF, QPointF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsLineItem


class EdgeLineGraphic(QGraphicsLineItem):
    def __init__(self, start: QPointF, end: QPointF) -> None:
        super().__init__()

        self.setLine(QLineF(start, end))
        self.setPen(QPen(QColor("#000")))
        self.setZValue(-1)
        self.show()

    def updatePosition(self, start: QPointF, end: QPointF):
        # 计算两个椭圆中心之间的连线
        line = QLineF(start, end)
        self.setLine(line)
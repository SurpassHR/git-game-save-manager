from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtCore import QPointF

class ConnectionLineGraphic(QGraphicsLineItem):
    def __init__(self, startPoint: QPointF, endPoint: QPointF) -> None:
        super().__init__()
        self.start: QPointF = startPoint
        self.end: QPointF = endPoint
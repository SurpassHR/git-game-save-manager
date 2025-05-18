import sys
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QLineF
from pathlib import Path

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from ui.components.utils.graphicManager import NodeManager

class GridScene(NodeManager, QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        repoPath = "F:\\Games\\25-05-03\\克莱尔的任务Claire's Quest 0.28.1\\www\\save"
        NodeManager.__init__(self, repoPath)

        self.grid_size = 20  # 网格基础大小（像素）
        self.grid_color = QColor(220, 220, 220)  # 浅灰色网格
        self.boundToScene(self)

    def drawBackground(self, painter, rect):
        """ 重写背景绘制方法 """
        if not painter:
            return
        painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))

        # 计算可见区域的网格线范围
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)

        # 绘制垂直线
        x = left
        while x < rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += self.grid_size

        # 绘制水平线
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += self.grid_size


class SmartGridScene(GridScene):
    def __init__(self, parent=None):
        super().__init__(parent)

    def drawBackground(self, painter, rect):
        # 根据视图缩放级别动态调整网格密度
        views = self.views()
        if views:
            view = views[0]  # 获取第一个关联视图
            transform = view.transform()
            scale_x = transform.m11()  # 获取水平缩放因子

            # 动态调整网格大小（缩放时网格不会太密或太疏）
            effective_size = max(20, self.grid_size * (1.0 / scale_x))
            if scale_x > 5:  # 放大时显示更密的次级网格
                painter.setPen(QPen(self.grid_color.lighter(120), 0.5))
                sub_size = effective_size / 5
                self._drawGrid(painter, rect, sub_size)

            # 主网格
            painter.setPen(QPen(self.grid_color, 1))
            self._drawGrid(painter, rect, effective_size)

    def _drawGrid(self, painter, rect, size):
        """ 通用网格绘制方法 """
        left = int(rect.left()) - (int(rect.left()) % size)
        top = int(rect.top()) - (int(rect.top()) % size)

        lines = []
        # 垂直线
        x = left
        while x < rect.right():
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += size
        # 水平线
        y = top
        while y < rect.bottom():
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += size

        painter.drawLines(lines)
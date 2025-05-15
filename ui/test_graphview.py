import sys
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QMainWindow, QGraphicsItem
from PyQt5.QtGui import QBrush, QPen, QPainter, QColor
from PyQt5.QtCore import Qt, QRectF, QPoint, QLineF

class InfiniteCanvasView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setScene(scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # 视图控制参数
        self._pan_start = QPoint()
        self._panning = False
        self.scale_factor = 1.0

        # 强制显示滚动条（视觉上更一致）
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 初始场景范围
        scene = self.scene()
        if not scene:
            return
        scene.setSceneRect(QRectF(-1e6, -1e6, 2e6, 2e6))

    def wheelEvent(self, event):
        # 缩放控制（保持之前实现）
        zoom_in_factor = 1.2
        zoom_out_factor = 1 / zoom_in_factor

        if event and event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)
        self.scale_factor *= zoom_factor

    def mousePressEvent(self, event):
        if not event:
            return
        clickedItem = self.itemAt(event.pos())
        if clickedItem and (clickedItem.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable != 0):
            # 如果点击了可移动项，交给默认处理
            self._dragging_item = clickedItem
            super().mousePressEvent(event)
        else:
            # 否则处理为画布拖拽
            if event.button() == Qt.MouseButton.LeftButton:
                self._panning = True
                self._pan_start = event.pos()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()

    def mouseMoveEvent(self, event):
        if self._panning and event:
            # 计算移动距离
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()

            # 直接移动视图内容（不依赖滚动条）
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            if not h_bar or not v_bar:
                return
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())

            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event and event.button() == Qt.MouseButton.LeftButton and self._panning:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def showEvent(self, event):
        # 确保视图初始化后滚动条可用
        self.centerOn(0, 0)
        super().showEvent(event)

class GridScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_size = 20  # 网格基础大小（像素）
        self.grid_color = QColor(220, 220, 220)  # 浅灰色网格

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

class MyMainWindow(QMainWindow):
    WIDTH = 1280
    HEIGHT = 720

    def __init__(self) -> None:

        super().__init__()

        self.setWindowTitle("PyQt5 GraphicsView Test")
        self.setGeometry(200, 300, 1280, 720)

        self.createUI()

        self.show()

    def createUI(self):
        scene = SmartGridScene(self)

        # greenBrush = QBrush(Qt.GlobalColor.green)
        blueBrush = QBrush(Qt.GlobalColor.blue)

        blackPen = QPen(Qt.GlobalColor.black)
        blackPen.setWidth(5)

        rect = scene.addEllipse(-100, -100, 200, 200, blackPen, blueBrush)
        if not rect:
            return
        rect.setBrush(blueBrush)
        rect.setPen(blackPen)
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.view = InfiniteCanvasView(scene, self)
        self.view.setGeometry(0, 0, 1280, 720)

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    # 必须设置此属性才能启用开发者工具
    # QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    mainWindow = MyMainWindow()
    # 显示开发者工具窗口
    # mainWindow.devToolsView.show()
    app.exec()
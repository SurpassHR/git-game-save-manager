from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QRectF, QPoint

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
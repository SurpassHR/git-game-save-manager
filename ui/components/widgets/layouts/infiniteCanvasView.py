import sys
from pathlib import Path
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsScene
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QRectF, QPoint
from typing import override

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from ui.components.widgets.layouts.gridScene import SmartGridScene
from ui.components.utils.uiFunctionBase import UIFunctionBase, EventEnum

class InfiniteCanvasView(QGraphicsView, UIFunctionBase):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(parent)
        self.setScene(scene)
        self.setRenderHints(QPainter.RenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform))

        # 视图控制参数
        self._pan_start = QPoint()
        self._panning = False
        self._draggingItem = False
        self.scale_factor = 1.0

        # 强制显示滚动条（视觉上更一致）
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QGraphicsView {
                border: none;
                border-radius: 10px;
                padding: 0;
                margin: 0;
            }
        """)

        # 初始场景范围
        if not scene:
            return
        scene.setSceneRect(QRectF(-1e6, -1e6, 2e6, 2e6))

    @override
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

    def procItemPress(self, event):
        super().mousePressEvent(event)
        # 如果点击了可移动项，交给默认处理
        if event.button() == Qt.MouseButton.LeftButton:
            self._draggingItem = True

    def procScenePress(self, event):
        # 否则处理为画布拖拽
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            scene = self.scene()
            if not scene:
                return
            if isinstance(scene, SmartGridScene):
                scene.clearAllSelectedGraphic()
                scene.clearSelection()
            event.accept()

    @override
    def mousePressEvent(self, event):
        if not event:
            return

        clickedItem = self.itemAt(event.pos())
        if clickedItem and (clickedItem.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable != 0):
            self.procItemPress(event)
        else:
            self.procScenePress(event)

    def procSceneMove(self, event):
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

    def procItemMove(self, event):
        super().mouseMoveEvent(event)
        if self._draggingItem:
            self.uiEmit(EventEnum.UI_GRAPHIC_MGR_MOUSE_MOVE_NODE, {})

    @override
    def mouseMoveEvent(self, event):
        if self._panning and event:
            self.procSceneMove(event)
        else:
            self.procItemMove(event)

    def procSceneRelease(self, event):
        self._panning = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        event.accept()

    def procItemRelease(self, event):
        self._draggingItem = False
        super().mouseReleaseEvent(event)

    @override
    def mouseReleaseEvent(self, event):
        if event and event.button() == Qt.MouseButton.LeftButton and self._panning:
            self.procSceneRelease(event)
        else:
            self.procItemRelease(event)

    @override
    def showEvent(self, event):
        # 确保视图初始化后滚动条可用
        self.centerOn(0, 0)
        super().showEvent(event)
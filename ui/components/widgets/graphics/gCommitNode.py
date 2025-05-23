import sys
from pathlib import Path
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsEllipseItem
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QBrush, QPen, QColor, QFont, QPainter
from typing import Callable, override, Any, no_type_check

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint
from core.gitManager import CommitObj
from ui.components.utils.uiFunctionBase import UIFunctionBase, EventEnum


class GCommitNode(QGraphicsEllipseItem, CommitObj):
    def __init__(self, rect: QRectF, selectCb: Callable, level: int):
        QGraphicsEllipseItem.__init__(self, rect)
        CommitObj.__init__(self)

        self.selectCb: Callable = selectCb
        self.level = level # 表示从根节点到本节点的距离

    def setCommitInfo(self, commitObj: CommitObj):
        for k, v in commitObj.__dict__.items():
            self.setItem(k, v)


class GLabeledCommitNode(QGraphicsItemGroup):
    def __init__(self, rect: QRectF, selectCb: Callable, level: int):
        super().__init__()

        # 创建图形项（例如一个矩形）
        self.rectItem = GCommitNode(rect, selectCb, level)
        self.rectItem.setBrush(QBrush(QColor(200, 200, 255)))

        # 创建文本项
        self.font = QFont("微软雅黑")
        self.textItem = QGraphicsTextItem()
        self.textItem.setFont(self.font)
        self.textItem.setDefaultTextColor(QColor("#000"))
        self.textItem.show()

        # 将两者添加到组中
        self.addToGroup(self.rectItem)
        self.addToGroup(self.textItem)

        # 设置可移动
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    @override
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if self.isSelected() and self.rectItem.selectCb:
            self.rectItem.selectCb(self.hexSha(), True)
        if not event:
            return
        self.posBeforeMove = self.scenePos()

    @override
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if not event:
            return
        loggerPrint(f"move '{self.hexSha()}': ({self.posBeforeMove.x():.1f}, {self.posBeforeMove.y():.1f}) -> ({self.scenePos().x():.1f}, {self.scenePos().y():.1f}), parent: {self.parents()}")

    @override
    def setSelected(self, selected: bool) -> None:
        super().setSelected(selected)
        if self.rectItem.selectCb:
            self.rectItem.selectCb(self.hexSha(), selected)

    @override
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    @override
    def boundingRect(self):
        # 获取所有子项的边界矩形(在组坐标系中)
        children_rect = QRectF()
        for child in self.childItems():
            # 将子项的边界矩形映射到组坐标系
            child_rect = child.mapRectToParent(child.boundingRect())
            children_rect = children_rect.united(child_rect)
        return children_rect

    @override
    def paint(self, painter: QPainter, option, widget=None):
        # 调用父类绘制
        super().paint(painter, option, widget)

        # 调试绘制边界矩形(可选)
        painter.setPen(Qt.GlobalColor.red)
        painter.drawRect(self.boundingRect())

    @no_type_check
    def setPos(self, *args):
        if len(args) == 1:
            super().setPos(args[0])
        elif len(args) == 2:
            super().setPos(QPointF(args[0], args[1]))
        else:
            raise TypeError("setPos() takes 1 or 2 arguments")
        self.uiEmit(EventEnum.UI_GRAPHIC_MGR_MOUSE_MOVE_NODE, {})

    def updateTextPosition(self):
        # 获取当前尺寸
        rect = self.rectItem.rect()
        text_rect = self.textItem.boundingRect()

        # 计算居中位置
        x = (rect.width() - text_rect.width()) / 2
        # y = (rect.height() - text_rect.height()) / 2
        y = rect.height()

        self.textItem.setPos(x, y)

    def setCommitInfo(self, commitObj: CommitObj):
        self.rectItem.setCommitInfo(commitObj)
        self.textItem.setPlainText(commitObj.message)
        self.updateTextPosition()

    def setBrush(self, brush: QBrush):
        self.rectItem.setBrush(brush)

    def setPen(self, pen: QPen):
        self.rectItem.setPen(pen)

    def parents(self) -> list:
        return self.rectItem.parents

    def hexSha(self) -> str:
        return self.rectItem.hexSha

    def level(self) -> int:
        return self.rectItem.level

    def message(self) -> str:
        return self.rectItem.message

    def rect(self) -> QRectF:
        return self.rectItem.rect()

    # 获取节点图形的中心
    def getNodeGraphicCenter(self) -> QPointF:
        x = self.rectItem.scenePos().x() + self.rectItem.boundingRect().width() / 2
        y = self.rectItem.scenePos().y() + self.rectItem.boundingRect().height() / 2
        return QPointF(x, y)


class GLabeledColliDetectCommitNode(GLabeledCommitNode, UIFunctionBase):
    def __init__(self, rect: QRectF, selectCb: Callable[..., Any], level: int):
        super().__init__(rect, selectCb, level)

        # 设置发送图形变化消息
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # 状态信息
        self.originalPos = self.pos()
        self.isDragging = False

    @override
    def mouseReleaseEvent(self, event):
        self.isDragging = False
        super().mouseReleaseEvent(event)

    @override
    def mousePressEvent(self, event):
        self.isDragging = True
        super().mousePressEvent(event)

    @override
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # 只处理由拖动引起的位置变化
            self.originalPos = self.scenePos()
            if self.isDragging:
                # self.originalPos = self.scenePos()
                newPos = value
                # 如果拖动的是当前项，立即通知场景处理碰撞
                data = {
                    "draggedItem": self,
                    "newPos": newPos,
                }
                self.uiEmit(EventEnum.UI_COLLISION_SCENE_PROC_DETECT, data)

        # 始终按正常方式更新位置
        return super().itemChange(change, value)
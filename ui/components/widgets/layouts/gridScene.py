import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QLineF, QPointF
from pathlib import Path

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from ui.components.utils.graphicManager import NodeManager
from ui.components.utils.uiFunctionBase import UIFunctionBase
from ui.components.widgets.interfaces import ICommitNode


class GridScene(NodeManager, QGraphicsScene, UIFunctionBase):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        NodeManager.__init__(self, self.uiGetConfig("repo"))

        self.grid_size = 20  # 网格基础大小（像素）
        self.grid_color = QColor(220, 220, 220)  # 浅灰色网格
        self.boundToScene(self)

    # 重写背景绘制方法
    def drawBackground(self, painter, rect):
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
            self._drawGrid(painter, rect, effective_size / 2)

    # 通用网格绘制方法
    def _drawGrid(self, painter, rect, size):
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


class ColliDetectSmartScene(SmartGridScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.isProcessingCollision = False

    # 处理拖动项的碰撞
    def handleCollisionForDraggedItem(self, draggedItem, newPos):
        if self.isProcessingCollision:
            return

        self.isProcessingCollision = True
        try:
            # 保存原始位置并模拟移动
            originalPos = draggedItem.pos()
            draggedItem.setPos(newPos)

            # 一次性处理所有碰撞
            self.resolveAllCollisions(draggedItem)

            # 还原拖动项的位置，让系统继续处理正常的拖动
            draggedItem.setPos(originalPos)

        finally:
            self.isProcessingCollision = False

    def distanceSquare(self, item: ICommitNode, draggedItem: ICommitNode):
        item1Center = item.getNodeGraphicRect().center()
        item2Center = draggedItem.getNodeGraphicRect().center()

        return int(item1Center.x() - item2Center.x()) ** 2 + int(item1Center.y() - item2Center.y()) ** 2

    # 迭代解决场景中所有碰撞
    def resolveAllCollisions(self, draggedItem):
        maxIterations = 3  # 限制最大迭代次数

        # 创建要处理的项列表
        itemsToCheck: list[QGraphicsItem] = list(self.items())
        itemsToCheck = [item for item in itemsToCheck if isinstance(item, ICommitNode)]

        # 主循环
        for iteration in range(maxIterations):
            collisionFound = False

            # 检查每个项的碰撞
            for i, item1 in enumerate(itemsToCheck):
                # 只检查可移动的矩形项
                if not isinstance(item1, ICommitNode):
                    continue

                # 跳过被拖动的项（它不应该被推动）
                if item1 == draggedItem:
                    continue

                # 找出碰撞
                collidingItems = []
                for item2 in itemsToCheck:
                    if (item2 != item1 and isinstance(item2, ICommitNode) and item1.collidesWithItem(item2)):
                        collidingItems.append(item2)

                if not collidingItems:
                    continue

                collisionFound = True

                # 对于每个碰撞，计算和应用推动向量
                for item2 in collidingItems:
                    # 确定哪一个是固定的，哪一个应该移动
                    itemToMove, itemToFixed = self.determineMoveAndFixedItems(item1, item2, draggedItem)
                    if itemToMove is None or itemToFixed is None:
                        continue

                    # 计算推动向量
                    pushVector = self.calculatePushVector(itemToMove, itemToFixed)
                    if pushVector is not None:
                        # 应用推动向量
                        targetPos = itemToMove.pos() + pushVector
                        itemToMove.setPos(targetPos)

            # 如果没有找到碰撞，可以提前退出
            if not collisionFound:
                break

        # 结束处理

    # 确定哪个项应该移动，哪个应该保持固定
    def determineMoveAndFixedItems(self, item1: ICommitNode, item2: ICommitNode, draggedItem: ICommitNode):
        # 拖动的项始终是固定的
        if item1 == draggedItem:
            return item2, item1
        elif item2 == draggedItem:
            return item1, item2

        # 其他情况下，如果一个被选中一个没有，移动未选中的
        if item1.isSelected() and not item2.isSelected():
            return item2, item1
        elif item2.isSelected() and not item1.isSelected():
            return item1, item2

        # 两者都未被选中，与 draggedItem 接触的不移动，未接触的移动
        if item1.getNodeGraphicRect().intersects(draggedItem.getNodeGraphicRect()):
            return item2, item1
        elif item2.getNodeGraphicRect().intersects(draggedItem.getNodeGraphicRect()):
            return item1, item2

        # 两者都被选中或都未被选中，选择距离被选中者较远的移动
        dist1 = self.distanceSquare(item1, draggedItem)
        dist2 = self.distanceSquare(item2, draggedItem)
        if dist1 < dist2:
            return item2, item1
        else:
            return item1, item2

    # 计算推动向量
    def calculatePushVector(self, itemToMove: ICommitNode, itemToFixed: ICommitNode):
        itemToMoveRect = itemToMove.getNodeGraphicRect()
        itemToFixedRect = itemToFixed.getNodeGraphicRect()

        # 确保矩形实际重叠
        if not itemToMoveRect.intersects(itemToFixedRect):
            return None

        # 交集矩形
        intersection = itemToMoveRect.intersected(itemToFixedRect)

        # 如果交集无效，返回None
        if intersection.isEmpty() or intersection.width() <= 0 or intersection.height() <= 0:
            return None

        # 计算物体中心点
        movedItemCenter = itemToMoveRect.center()
        fixedItemCenter = itemToFixedRect.center()

        # 方向向量（从固定物体指向移动物体）
        dx = movedItemCenter.x() - fixedItemCenter.x()
        dy = movedItemCenter.y() - fixedItemCenter.y()

        # 避免除零错误
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            dx = 1.0
            dy = 0.0

        # 计算推动方向
        if intersection.width() < intersection.height():
            # 水平推动
            alphaX = intersection.width() * (1 if dx > 0 else -1)
            alphaY = 0
        else:
            # 垂直推动
            alphaX = 0
            alphaY = intersection.height() * (1 if dy > 0 else -1)

        return QPointF(alphaX, alphaY)
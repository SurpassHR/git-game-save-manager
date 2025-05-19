import sys
from pathlib import Path
from typing import override
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                           QGraphicsItem, QGraphicsRectItem,
                           QMainWindow)

rootPath = str(Path(__file__).resolve().parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint

class DraggableItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color=Qt.GlobalColor.blue, name=""):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.name = name
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
        scene: CollisionScene = self.scene() # type: ignore
        if scene is None:
            return super().itemChange(change, value)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # 只处理由拖动引起的位置变化
            if self.isDragging:
                self.originalPos = self.pos()
                newPos = value
                # 如果拖动的是当前项，立即通知场景处理碰撞
                scene.handleCollisionForDraggedItem(self, newPos)

        # 始终按正常方式更新位置
        return super().itemChange(change, value)


class CollisionScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.isProcessingCollision = False

    def handleCollisionForDraggedItem(self, draggedItem, newPos):
        """处理拖动项的碰撞"""
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
        # self.finalCheckIntersect(draggedItem)

    def distanceSquare(self, item: DraggableItem, draggedItem: DraggableItem):
        item1Center = item.sceneBoundingRect().center()
        item2Center = draggedItem.sceneBoundingRect().center()
        # print(f"itemCenter: {item1Center} draggedItemCenter: {item2Center}")

        return int(item1Center.x() - item2Center.x())**2 + int(item1Center.y() - item2Center.y())**2

    def finalCheckIntersect(self, draggedItem: DraggableItem):
        itersectDict = {}
        cnt = 0
        items_to_check: list[DraggableItem] = list(self.items()) # type: ignore
        checkedPair: list[tuple[DraggableItem, DraggableItem]] = []
        for i, item1 in enumerate(items_to_check):
            item1RectF = item1.sceneBoundingRect()
            for item2 in items_to_check:
                if item1.name == item2.name:
                    continue
                item2RectF = item2.sceneBoundingRect()
                intersectRect = item1RectF.intersected(item2RectF)
                if (item1, item2) in checkedPair or (item2, item1) in checkedPair:
                    continue
                if intersectRect.width() > 20 or intersectRect.height() > 20:
                    itersectDict[cnt] = [item1.name, item2.name]
                    cnt += 1
                    # moveItem, fixedItem = self.determineMoveAndFixedItems(item1, item2, draggedItem)
                    # targetPos = self.calculatePushVector(fixedItem, moveItem)
                    # moveItem.setPos(targetPos)
                    # checkedPair.append((item1, item2))
        if itersectDict != {}:
            print(itersectDict)

    def resolveAllCollisions(self, draggedItem):
        """迭代解决场景中所有碰撞"""
        maxIterations = 3  # 限制最大迭代次数

        # 创建要处理的项列表
        itemsToCheck: list[QGraphicsItem] = list(self.items())

        # 标记哪些项是被处理过的
        # processedItems = set()

        # 主循环
        for iteration in range(maxIterations):
            collisionFound = False

            # 检查每个项的碰撞
            for i, item1 in enumerate(itemsToCheck):
                # 只检查可移动的矩形项
                if not isinstance(item1, DraggableItem):
                    continue

                # 跳过被拖动的项（它不应该被推动）
                if item1 == draggedItem:
                    continue

                # 找出碰撞
                collidingItems = []
                for item2 in itemsToCheck:
                    if (item2 != item1 and
                        isinstance(item2, DraggableItem) and
                        item1.collidesWithItem(item2)):
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

    def determineMoveAndFixedItems(self, item1, item2, draggedItem):
        """确定哪个项应该移动，哪个应该保持固定"""
        # 拖动的项始终是固定的
        if item1 == draggedItem:
            # loggerPrint(f"move {item2.name} fixed {item1.name}")
            return item2, item1
        elif item2 == draggedItem:
            # loggerPrint(f"move {item1.name} fixed {item2.name}")
            return item1, item2

        # 其他情况下，如果一个被选中一个没有，移动未选中的
        if item1.isSelected() and not item2.isSelected():
            # loggerPrint(f"move {item2.name} fixed {item1.name}")
            return item2, item1
        elif item2.isSelected() and not item1.isSelected():
            # loggerPrint(f"move {item1.name} fixed {item2.name}")
            return item1, item2

        # 两者都被选中或都未被选中，选择索引较大的（更晚添加到场景中的）移动
        # allItems = self.items()
        # if allItems.index(item1) > allItems.index(item2):
        #     return item1, item2
        # else:
        #     return item2, item1

        # 两者都被选中或都未被选中，选择距离被选中者较远的移动
        dist1 = self.distanceSquare(item1, draggedItem)
        dist2 = self.distanceSquare(item2, draggedItem)
        if dist1 < dist2:
            # loggerPrint(f"item2 dist {dist2} item1 dist {dist1}")
            # loggerPrint(f"move {item2.name} fixed {item1.name}")
            return item2, item1
        else:
            # loggerPrint(f"move {item1.name} fixed {item2.name}")
            return item1, item2


    def calculatePushVector(self, itemToMove: DraggableItem, itemToFixed: DraggableItem):
        """计算推动向量"""
        # print(f"proc {itemToMove.name} {itemToFixed.name} collision")
        itemToMoveRect = itemToMove.sceneBoundingRect()
        itemToFixedRect = itemToFixed.sceneBoundingRect()

        # 确保矩形实际重叠
        if not itemToMoveRect.intersects(itemToFixedRect):
            # print(f"{itemToMove.name} not interset with {itemToFixed.name}")
            return None

        # 交集矩形
        intersection = itemToMoveRect.intersected(itemToFixedRect)

        # 如果交集无效，返回None
        if intersection.isEmpty() or intersection.width() <= 0 or intersection.height() <= 0:
            # print(f"{itemToMove.name} not interset with {itemToFixed.name}")
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

        # print(f"{itemToFixed.name} push {itemToMove.name} to {alphaX, alphaY}")
        return QPointF(alphaX, alphaY)


class CollisionTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('实时碰撞检测 - 无递归版本')
        self.setGeometry(100, 100, 1920, 1080)

        self.scene = CollisionScene()
        self.scene.setSceneRect(0, 0, 700, 500)

        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # 添加几个可拖动的矩形
        rect1 = DraggableItem(50, 50, 100, 100, QColor(255, 100, 100), "rect1") # 红
        rect2 = DraggableItem(200, 50, 100, 100, QColor(100, 255, 100), "rect2") # 绿
        rect3 = DraggableItem(350, 50, 100, 100, QColor(100, 100, 255), "rect3") # 紫
        rect4 = DraggableItem(50, 200, 80, 120, QColor(200, 200, 100), "rect4") # 棕
        rect5 = DraggableItem(200, 200, 120, 80, QColor(100, 200, 200), "rect5") # 青

        self.scene.addItem(rect1)
        self.scene.addItem(rect2)
        self.scene.addItem(rect3)
        self.scene.addItem(rect4)
        self.scene.addItem(rect5)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CollisionTestWindow()
    sys.exit(app.exec_())

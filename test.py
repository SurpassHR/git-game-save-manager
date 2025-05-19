import sys
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                           QGraphicsItem, QGraphicsRectItem,
                           QMainWindow)

from core.tools.utils.simpleLogger import loggerPrint
from rich import print

class DraggableItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, color=Qt.blue, name=""):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.name = name
        self.original_pos = self.pos()
        self.currently_dragged = False

    def mouseReleaseEvent(self, event):
        self.currently_dragged = False
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        self.currently_dragged = True
        super().mousePressEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # 只处理由拖动引起的位置变化
            if self.currently_dragged:
                self.original_pos = self.pos()
                new_pos = value
                # 如果拖动的是当前项，立即通知场景处理碰撞
                self.scene().handle_collision_for_dragged_item(self, new_pos)

        # 始终按正常方式更新位置
        return super().itemChange(change, value)


class CollisionScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.collision_in_progress = False

    def handleCollisionForDraggedItem(self, dragged_item, new_pos):
        """处理拖动项的碰撞"""
        if self.collision_in_progress:
            return

        self.collision_in_progress = True
        try:
            # 保存原始位置并模拟移动
            original_pos = dragged_item.pos()
            dragged_item.setPos(new_pos)

            # 一次性处理所有碰撞
            self.resolveAllCollisions(dragged_item)

            # 还原拖动项的位置，让系统继续处理正常的拖动
            dragged_item.setPos(original_pos)

        finally:
            self.collision_in_progress = False
        # self.finalCheckIntersect(dragged_item)

    def distanceSquare(self, item: DraggableItem, dragged_item: DraggableItem):
        item1Center = item.sceneBoundingRect().center()
        item2Center = dragged_item.sceneBoundingRect().center()
        # print(f"itemCenter: {item1Center} draggedItemCenter: {item2Center}")

        return int(item1Center.x() - item2Center.x())**2 + int(item1Center.y() - item2Center.y())**2

    def finalCheckIntersect(self, dragged_item: DraggableItem):
        itersectDict = {}
        cnt = 0
        items_to_check: list[QGraphicsItem] = list(self.items())
        checkedPair: list[tuple[QGraphicsItem, QGraphicsItem]] = []
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
                    # moveItem, fixedItem = self.determine_move_and_fixed_items(item1, item2, dragged_item)
                    # targetPos = self.calculate_push_vector(fixedItem, moveItem)
                    # moveItem.setPos(targetPos)
                    # checkedPair.append((item1, item2))
        from rich import print
        if itersectDict != {}:
            print(itersectDict)

    def resolveAllCollisions(self, dragged_item):
        """迭代解决场景中所有碰撞"""
        max_iterations = 3  # 限制最大迭代次数

        # 创建要处理的项列表
        items_to_check: list[QGraphicsItem] = list(self.items())

        # 标记哪些项是被处理过的
        processed_items = set()

        # 主循环
        for iteration in range(max_iterations):
            collision_found = False

            # 检查每个项的碰撞
            for i, item1 in enumerate(items_to_check):
                # 只检查可移动的矩形项
                if not isinstance(item1, DraggableItem):
                    continue

                # 跳过被拖动的项（它不应该被推动）
                if item1 == dragged_item:
                    continue

                # 找出碰撞
                colliding_items = []
                for item2 in items_to_check:
                    if (item2 != item1 and
                        isinstance(item2, DraggableItem) and
                        item1.collidesWithItem(item2)):
                        colliding_items.append(item2)

                if not colliding_items:
                    continue

                collision_found = True

                # 对于每个碰撞，计算和应用推动向量
                for item2 in colliding_items:
                    # 确定哪一个是固定的，哪一个应该移动
                    move_item, fixed_item = self.determine_move_and_fixed_items(item1, item2, dragged_item)
                    if move_item is None or fixed_item is None:
                        continue

                    # 计算推动向量
                    push_vector = self.calculate_push_vector(move_item, fixed_item)
                    if push_vector:
                        # 应用推动向量
                        new_pos = move_item.pos() + push_vector
                        move_item.setPos(new_pos)

            # 如果没有找到碰撞，可以提前退出
            if not collision_found:
                break

        # 结束处理

    def determine_move_and_fixed_items(self, item1, item2, dragged_item):
        """确定哪个项应该移动，哪个应该保持固定"""
        # 拖动的项始终是固定的
        if item1 == dragged_item:
            # loggerPrint(f"move {item2.name} fixed {item1.name}")
            return item2, item1
        elif item2 == dragged_item:
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
        # all_items = self.items()
        # if all_items.index(item1) > all_items.index(item2):
        #     return item1, item2
        # else:
        #     return item2, item1

        # 两者都被选中或都未被选中，选择距离被选中者较远的移动
        dist1 = self.distanceSquare(item1, dragged_item)
        dist2 = self.distanceSquare(item2, dragged_item)
        if dist1 < dist2:
            # loggerPrint(f"item2 dist {dist2} item1 dist {dist1}")
            # loggerPrint(f"move {item2.name} fixed {item1.name}")
            return item2, item1
        else:
            # loggerPrint(f"move {item1.name} fixed {item2.name}")
            return item1, item2


    def calculate_push_vector(self, move_item: DraggableItem, fixed_item: DraggableItem):
        """计算推动向量"""
        # print(f"proc {move_item.name} {fixed_item.name} collision")
        move_rect = move_item.sceneBoundingRect()
        fixed_rect = fixed_item.sceneBoundingRect()

        # 确保矩形实际重叠
        if not move_rect.intersects(fixed_rect):
            # print(f"{move_item.name} not interset with {fixed_item.name}")
            return None

        # 交集矩形
        intersection = move_rect.intersected(fixed_rect)

        # 如果交集无效，返回None
        if intersection.isEmpty() or intersection.width() <= 0 or intersection.height() <= 0:
            # print(f"{move_item.name} not interset with {fixed_item.name}")
            return None

        # 计算物体中心点
        move_center = move_rect.center()
        fixed_center = fixed_rect.center()

        # 方向向量（从固定物体指向移动物体）
        dx = move_center.x() - fixed_center.x()
        dy = move_center.y() - fixed_center.y()

        # 避免除零错误
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            dx = 1.0
            dy = 0.0

        # 计算推动方向
        if intersection.width() < intersection.height():
            # 水平推动
            push_x = intersection.width() * (1 if dx > 0 else -1) + 1
            push_y = 0
        else:
            # 垂直推动
            push_x = 0
            push_y = intersection.height() * (1 if dy > 0 else -1) + 1

        # print(f"{fixed_item.name} push {move_item.name} to {push_x, push_y}")
        return QPointF(push_x, push_y)


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

import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QLineF, QPointF, pyqtSlot, QRectF
from pathlib import Path
from typing import Optional

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint
from ui.components.utils.graphicManager import NodeManager
from ui.components.utils.uiFunctionBase import UIFunctionBase, EventEnum
from ui.components.widgets.graphics.gCommitNode import GLabeledColliDetectCommitNode


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
        self.subscribeEvt()

    # 处理拖动项的碰撞
    @pyqtSlot(EventEnum, dict)
    def _uiEvt_handleCollisionForDraggedItem(self, _: EventEnum, data: dict):
        if self.isProcessingCollision:
            return

        if len(data) != 2:
            return

        draggedItem: Optional[GLabeledColliDetectCommitNode] = data.get("draggedItem")
        newPos: Optional[QPointF] = data.get("newPos")

        if draggedItem is None or newPos is None:
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

    def distanceSquare(self, node: GLabeledColliDetectCommitNode, draggedNode: GLabeledColliDetectCommitNode):
        node1Center = node.sceneBoundingRect().center()
        node2Center = draggedNode.sceneBoundingRect().center()

        return int(node1Center.x() - node2Center.x()) ** 2 + int(node1Center.y() - node2Center.y()) ** 2

    # 迭代解决场景中所有碰撞
    def resolveAllCollisions(self, draggedNode):
        maxIterations = 3  # 限制最大迭代次数

        # 创建要处理的项列表
        nodesToCheck: list[QGraphicsItem] = list(self.items())
        nodesToCheck = [node for node in nodesToCheck if isinstance(node, GLabeledColliDetectCommitNode)]

        # 主循环
        for iteration in range(maxIterations):
            collisionFound = False

            # 检查每个项的碰撞
            for i, node1 in enumerate(nodesToCheck):
                # 只检查可移动的矩形项
                if not isinstance(node1, GLabeledColliDetectCommitNode):
                    continue

                # 跳过被拖动的项（它不应该被推动）
                if node1 == draggedNode:
                    continue

                # 找出碰撞
                collidingNodes = []
                for node2 in nodesToCheck:
                    if (node2 != node1 and isinstance(node2, GLabeledColliDetectCommitNode) and node1.collidesWithItem(node2)):
                        collidingNodes.append(node2)

                if not collidingNodes:
                    continue

                collisionFound = True

                # 对于每个碰撞，计算和应用推动向量
                for node2 in collidingNodes:
                    # 确定哪一个是固定的，哪一个应该移动
                    nodeToMove, nodeToFixed = self.determineMoveAndFixedNodes(node1, node2, draggedNode)
                    if nodeToMove is None or nodeToFixed is None:
                        continue

                    # 计算推动向量
                    pushVector = self.calculatePushVector(nodeToMove, nodeToFixed)
                    if pushVector is not None:
                        # 应用推动向量
                        targetPos = nodeToMove.pos() + pushVector
                        nodeToMove.setPos(targetPos)
                        data = { "nodeToMove": nodeToMove }
                        self.uiEmit(EventEnum.UI_GRAPHIC_MGR_MOUSE_MOVE_NODE, data)

            # 如果没有找到碰撞，可以提前退出
            if not collisionFound:
                break

        # 结束处理

    # 确定哪个项应该移动，哪个应该保持固定
    def determineMoveAndFixedNodes(self, node1: GLabeledColliDetectCommitNode, node2: GLabeledColliDetectCommitNode, draggedNode: GLabeledColliDetectCommitNode):
        # 拖动的项始终是固定的
        if node1 == draggedNode:
            return node2, node1
        elif node2 == draggedNode:
            return node1, node2

        # 其他情况下，如果一个被选中一个没有，移动未选中的
        if node1.isSelected() and not node2.isSelected():
            return node2, node1
        elif node2.isSelected() and not node1.isSelected():
            return node1, node2

        # 两者都未被选中，与 draggedItem 接触的不移动，未接触的移动
        node1Rect = QRectF(node1.originalPos.x(), node1.originalPos.y(), node1.sceneBoundingRect().width(), node1.sceneBoundingRect().height())
        node2Rect = QRectF(node2.originalPos.x(), node2.originalPos.y(), node2.sceneBoundingRect().width(), node2.sceneBoundingRect().height())
        draggedNodeRect = QRectF(draggedNode.scenePos().x(), draggedNode.scenePos().y(), draggedNode.sceneBoundingRect().width(), draggedNode.sceneBoundingRect().height())
        if node1Rect.intersects(draggedNodeRect):
            return node2, node1
        elif node2Rect.intersects(draggedNodeRect):
            return node1, node2

        # 两者都被选中或都未被选中，选择距离被选中者较远的移动
        dist1 = self.distanceSquare(node1, draggedNode)
        dist2 = self.distanceSquare(node2, draggedNode)
        if dist1 < dist2:
            return node2, node1
        else:
            return node1, node2

    # 计算推动向量
    def calculatePushVector(self, nodeToMove: GLabeledColliDetectCommitNode, nodeToFixed: GLabeledColliDetectCommitNode):
        nodeToMoveRect = nodeToMove.sceneBoundingRect()
        nodeToFixedRect = nodeToFixed.sceneBoundingRect()

        # 确保矩形实际重叠
        if not nodeToMoveRect.intersects(nodeToFixedRect):
            return None

        # 交集矩形
        intersection = nodeToMoveRect.intersected(nodeToFixedRect)

        # 如果交集无效，返回None
        if intersection.isEmpty() or intersection.width() <= 0 or intersection.height() <= 0:
            return None

        # 计算物体中心点
        movedNodeCenter = nodeToMoveRect.center()
        fixedNodeCenter = nodeToFixedRect.center()

        # 方向向量（从固定物体指向移动物体）
        dx = movedNodeCenter.x() - fixedNodeCenter.x()
        dy = movedNodeCenter.y() - fixedNodeCenter.y()

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

    def subscribeEvt(self):
        super().subscribeEvt()
        self.uiSubscribe(EventEnum.UI_COLLISION_SCENE_PROC_DETECT, self._uiEvt_handleCollisionForDraggedItem)
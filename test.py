from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QApplication
from PyQt5.QtCore import QPointF
import sys

class CustomItem(QGraphicsRectItem):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def mouseReleaseEvent(self, event):
        print(f"{self} 的 scenePos(): {self.scenePos()}")
        print(f"{self} 的 pos(): {self.pos()}")
        super().mouseReleaseEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    view = QGraphicsView(scene)

    # 两个 Item，大小不同但移动到同一位置
    item1 = CustomItem(0, 0, 50, 50)
    item2 = CustomItem(0, 0, 100, 100)
    scene.addItem(item1)
    scene.addItem(item2)

    # 手动移动它们到 (100, 100)
    item1.setPos(100, 100)
    item2.setPos(100, 100)

    # 检查坐标
    print("--- 初始坐标 ---")
    print("Item1 scenePos():", item1.scenePos())  # (100, 100)
    print("Item2 scenePos():", item2.scenePos())  # (100, 100)
    print("Item1 pos():", item1.pos())  # (100, 100)
    print("Item2 pos():", item2.pos())  # (100, 100)

    # 检查变换后的中心点
    center1 = item1.mapToScene(item1.boundingRect().center())
    center2 = item2.mapToScene(item2.boundingRect().center())
    print("Item1 中心点:", center1)  # (125, 125)（因为宽高50x50）
    print("Item2 中心点:", center2)  # (150, 150)（因为宽高100x100）

    view.show()
    sys.exit(app.exec_())
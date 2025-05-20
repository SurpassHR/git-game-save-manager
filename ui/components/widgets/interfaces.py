from PyQt5.QtCore import QRectF, Qt, QPointF
from PyQt5.QtWidgets import QGraphicsItem
from typing import Protocol, Optional, runtime_checkable


@runtime_checkable
class ICommitNode(Protocol):
    def sceneBoundingRect(self) -> QRectF:
        ...

    def boundingRect(self):
        ...

    def getNodeGraphicCenter(self) -> QPointF:
        ...

    def getNodeGraphicRect(self) -> QRectF:
        ...

    def hexSha(self) -> str:
        ...

    def message(self) -> str:
        ...

    def collidesWithItem(self, other: Optional['QGraphicsItem'], mode: Qt.ItemSelectionMode = ...) -> bool:
        ...

    def isSelected(self) -> bool:
        ...

    def setPos(self, *args):
        ...

    def pos(self) -> QPointF:
        ...


@runtime_checkable
class IEdgeLine(Protocol):
    def updatePosition(self):
        ...


@runtime_checkable
class IGraphScene(Protocol):
    def handleCollisionForDraggedItem(self, draggedItem, newPos):
        ...
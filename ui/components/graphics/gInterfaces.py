import sys
from pathlib import Path
from PyQt5.QtCore import QRectF
from typing import Protocol

rootPath = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(rootPath)


class ICommitNode(Protocol):
    def sceneBoundingRect(self) -> QRectF:
        ...

    def getNodeGraphicCenter(self) -> QRectF:
        ...

class IEdgeLine(Protocol):
    def updatePosition(self):
        ...
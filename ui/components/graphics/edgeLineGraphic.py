import sys
from pathlib import Path

rootPath = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(rootPath)

from ui.components.graphics.roundNodeGraphic import RoundNodeGraphic
from ui.components.graphics.graphicsInterface import EdgeLineBase, RoundNodeBase


class EdgeLineGraphic(EdgeLineBase):
    def __init__(self, startNode: RoundNodeBase, endNode: RoundNodeBase) -> None:
        super().__init__(startNode, endNode)
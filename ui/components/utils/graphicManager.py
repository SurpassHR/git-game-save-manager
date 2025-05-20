import sys
from pathlib import Path
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QRectF, QPointF, QSizeF, pyqtSlot
from typing import Optional

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.publicDef.levelDefs import LogLevels
from core.tools.utils.dataStructTools import listDedup
from core.getGitInfo import CommitObj, GitRepoInfoMgr
from core.tools.utils.simpleLogger import loggerPrint

from ui.components.widgets.graphics.gCommitNode import GLabeledCommitNode, GLabeledColliDetectCommitNode
from ui.components.widgets.graphics.gEdgeLine import EdgeLineGraphic
from ui.components.utils.eventManager import EventEnum
from ui.components.utils.uiFunctionBase import UIFunctionBase
from ui.publicDefs.styleDefs import NODE_BORDER_DEFAULT_PEN, NODE_FILL_DEFAULT_BRUSH, NODE_HORIZONTAL_SPACING, NODE_VERTICAL_SPACING


class NodeManager(GitRepoInfoMgr, UIFunctionBase):
    def __init__(self, repoPath: str) -> None:
        GitRepoInfoMgr.__init__(self, repoPath)

        self.nodes: dict[str, GLabeledCommitNode] = {}
        self.edges: dict[str, EdgeLineGraphic] = {}
        self.selected: Optional[GLabeledCommitNode] = None

        self.subscribeEvt()

    def boundToScene(self, scene: QGraphicsScene) -> None:
        self.scene = scene

    def setSelected(self, graphicHash: str, isSelected: bool):
        if isSelected:
            self.selected = self.getNode(graphicHash)
            loggerPrint(f"node selected: '{graphicHash}'")
        else:
            self.selected = None
            loggerPrint(f"node diselected: '{graphicHash}'")

    def getSelected(self) -> Optional[GLabeledCommitNode]:
        return self.selected

    def isEmpty(self):
        return len(self.nodes) == 0

    def createDragableNode(
        self,
        x: float,
        y: float,
        r: float,
        commitObj: CommitObj,
        level: int,
        border: str | QPen = NODE_BORDER_DEFAULT_PEN,
        fill: str | QBrush = NODE_FILL_DEFAULT_BRUSH,
    ) -> Optional[GLabeledCommitNode]:
        isNodeExisted = self.nodes.get(commitObj.hexSha, '') != ''
        if isNodeExisted:
            return

        # 创建图形
        round = GLabeledColliDetectCommitNode(
            rect=QRectF(0, 0, r, r),
            selectCb=self.setSelected,
            level=level,
        )
        round.setCommitInfo(commitObj)
        round.setPos(x, y)

        # 设置图形样式
        pen: QPen = QPen()
        brush: QBrush = QBrush()
        if isinstance(border, str) and isinstance(fill, str):
            brush: QBrush = QBrush(QColor(fill))
            pen: QPen = QPen(QColor(border))
        elif isinstance(border, QPen) and isinstance(fill, QBrush):
            brush: QBrush= fill
            pen: QPen = border

        round.setBrush(brush)
        round.setPen(pen)

        # 将图形添加到场景
        self.nodes[round.hexSha()] = round
        if self.scene:
            self.scene.addItem(round)

        # 连接父节点与子节点
        loggerPrint(fr"create node: {round.hexSha()} graphic, parents: {round.parents()}, level: {round.level()}, pos: ({x}, {y}), msg: {round.message()}")

        # 判断是否根节点
        if len(round.parents()) == 0:
            self.rootNode = round.hexSha()

        return round

    def createConnections(
            self,
            fromNodeHash: str,
            toNodeHash: str,
        ):
        fromNode = self.getNode(fromNodeHash)
        toNode = self.getNode(toNodeHash)
        if fromNode is None or toNode is None:
            return

        edge = EdgeLineGraphic(fromNode, toNode)
        fromNode.addConnection(edge)
        toNode.addConnection(edge)
        self.edges[f"{fromNodeHash}->{toNodeHash}"] = edge
        self.scene.addItem(edge)

    def getNode(self, hexSha: str) -> Optional[GLabeledCommitNode]:
        node = self.nodes.get(hexSha)
        if not node:
            return None
        return node

    def getRootNode(self) -> Optional[GLabeledCommitNode]:
        node = self.nodes.get(self.rootNode)
        if not node:
            return None
        return node

    def getNodePosition(self, hexSha: str) -> Optional[QPointF]:
        node = self.nodes.get(hexSha)
        if not node:
            return None
        loggerPrint(f"get node '{hexSha}' graphic position: {node.scenePos()}", level=LogLevels.DEBUG)
        return node.scenePos()

    # 获取图形的外接矩形的大小
    def getNodeGraphicSize(self, hexSha: str) -> Optional[QSizeF]:
        node = self.nodes.get(hexSha)
        if not node:
            return None
        loggerPrint(f"get node '{hexSha}' graphic size: {node.boundingRect().size()}", level=LogLevels.DEBUG)
        return node.boundingRect().size()

    def removeGraphic(self, hexSha: str) -> None:
        node = self.nodes.get(hexSha)
        if not node:
            return None

        loggerPrint(f"remove node '{hexSha}' graphic, pos: ({node.pos().x()}, {node.pos().y()}), radius: {node.rect().width()}")
        node.hide()
        self.scene.removeItem(node)
        _ = self.nodes.pop(hexSha)

    def destroyAll(self) -> None:
        for node in self.nodes.values():
            self.scene.removeItem(node)
        self.nodes.clear()

    def clearAllSelectedGraphic(self) -> None:
        for node in self.nodes.values():
            if node.isSelected():
                node.setSelected(False)

    def getNodesByLevel(self, level: int) -> list[str]:
        nodeList: list[str] = []
        for node in self.nodes.values():
            if node.level() == level:
                nodeList.append(node.hexSha())
        return nodeList

    def nodeMaxLevel(self) -> int:
        leafNodeList: list[str] = self.all_leaves()
        maxLevel = 0
        for nodeHash in leafNodeList:
            node = self.getNode(nodeHash)
            if not node:
                continue
            maxLevel = max(maxLevel, node.level())

        return maxLevel

    # dict.values: node, posX, posY
    @pyqtSlot(EventEnum, dict)
    def _uiEvt_moveNode(self, _: EventEnum, data: dict):
        if len(data) != 3:
            return

        node: Optional[GLabeledCommitNode] = data.get("node")
        posX: Optional[float] = data.get("posX")
        posY: Optional[float] = data.get("posY")

        if node is None or posX is None or posY is None:
            return

        node.setPos(posX, posY)
        self._forceUpdateAllEdges()

    @pyqtSlot(EventEnum, dict)
    def _logicEvt_arrangeNodeGraphics(self, _: EventEnum = EventEnum.EVENT_INVALID, data: dict = {}):
        def haveSameParent(nodeAHash: str, nodeBHash: str):
            nodeA = self.getNode(nodeAHash)
            nodeB = self.getNode(nodeBHash)
            if not nodeA or not nodeB:
                return False, None
            for nodeAParent in nodeA.parents():
                if nodeAParent in nodeB.parents():
                    return True, nodeAParent
            return False, None

        def groupByParent(sameLevelNodes: list[str]) -> dict:
            nodeDict: dict[str, list[str]] = {}
            for nodeA in sameLevelNodes:
                for nodeB in sameLevelNodes:
                    isHaveSameParent, parent = haveSameParent(nodeA, nodeB)
                    if isHaveSameParent and parent is not None:
                        if not nodeDict.get(parent):
                            nodeDict[parent] = [nodeA, nodeB]
                        else:
                            nodeDict[parent].extend([nodeA, nodeB])

            for parent, grp in nodeDict.items():
                nodeDict[parent] = listDedup(grp)

            return nodeDict

        def moveNodeList(nodeList: list[str], alphaX: float, alphaY: float):
            for nodeHash in nodeList:
                node = self.getNode(nodeHash)
                if not node:
                    continue
                data = {
                    "node": node,
                    "posX": node.scenePos().x() + alphaX,
                    "posY": node.scenePos().y() + alphaY,
                }
                self.uiEmit(EventEnum.UI_GRAPHIC_MANAGER_MOVE_NODE, data)

        def arrangeNodeList(nodeList: list[str]):
            baseNode = self.getNode(nodeList[0])
            baseNodePos = self.getNodePosition(nodeList[0])
            baseNodeSize = self.getNodeGraphicSize(nodeList[0])
            if baseNode is None or baseNodePos is None or baseNodeSize is None:
                return

            offsetX = baseNodePos.x() + baseNodeSize.width()
            for i, nodeHash in enumerate(nodeList[1:]):
                node = self.getNode(nodeHash)
                nodeSize = self.getNodeGraphicSize(nodeHash)
                if node is None or nodeSize is None:
                    continue
                data = {
                    "node": node,
                    "posX": offsetX + NODE_HORIZONTAL_SPACING * (i + 1),
                    "posY": baseNode.scenePos().y(),
                }
                offsetX += nodeSize.width()
                self.uiEmit(EventEnum.UI_GRAPHIC_MANAGER_MOVE_NODE, data)

        # 获取一组节点的外接矩形
        def getNodeListBoundingRect(nodeList: list[str]) -> QRectF:
            maxY = -1e6
            minY = 1e6
            maxX = -1e6
            minX = 1e6

            for nodeHash in nodeList:
                nodePos = self.getNodePosition(nodeHash)
                nodeSize = self.getNodeGraphicSize(nodeHash)
                if nodePos is None or nodeSize is None:
                    continue

                maxX = max(maxX, nodePos.x())
                minX = min(minX, nodePos.x())
                maxY = max(maxY, nodePos.y())
                minY = min(minY, nodePos.y())

            return QRectF(minX, maxY, maxX - minX, maxY - minY)

        # 将一个组内的节点进行排列
        def arrangeNodeInGroup(grpNodeDict: dict[str, list[str]]) -> QRectF:
            for parent, grp in grpNodeDict.items():
                parentNodePos = self.getNodePosition(parent)
                if parentNodePos is None:
                    continue

                arrangeNodeList(grp)
                boundingRect = getNodeListBoundingRect(grp)
                loggerPrint(f"parent: '{parent}', pos: ({parentNodePos.x()}, {parentNodePos.y()})", level=LogLevels.DEBUG)
                loggerPrint(f"xRange: ({boundingRect.x()}, {boundingRect.x() + boundingRect.width()}), yRange: ({boundingRect.y()}, {boundingRect.y() + boundingRect.height()}), children: {grp}", level=LogLevels.DEBUG)
                centerX = (boundingRect.x() + boundingRect.x() + boundingRect.width()) / 2
                alphaX = parentNodePos.x() - centerX
                alphaY = parentNodePos.y() + NODE_VERTICAL_SPACING - boundingRect.y()
                moveNodeList(grp, alphaX, alphaY)

                return getNodeListBoundingRect([node for node in grp] + [parent])

            raise RuntimeError("一个节点不能有两个直接上游节点!")

        # 将根节点与他的每一个子节点都移动相同的位移
        def moveNodeGroup(grpNodeDict: dict[str, list[str]], alphaX: float, alphaY: float):
            for parent, grp in grpNodeDict.items():
                moveNodeList(grp + [parent], alphaX, alphaY)
                return

            raise RuntimeError("一个节点不能有两个直接上游节点!")

        def arrangeNodeGrps(grpNodeDict: dict[str, list[str]]):
            for parent, _ in grpNodeDict.items():
                parentNode = self.getNode(parent)
                parentNodePos = self.getNodePosition(parent)
                if parentNode is None or parentNodePos is None:
                    continue
                if len(parentNode.parents()) == 0:
                    continue
                grandParent = parentNode.parents()[0]
                grandParentNodePos = self.getNodePosition(grandParent)
                if grandParentNodePos is None:
                    continue
                alphaY = grandParentNodePos.y() + NODE_VERTICAL_SPACING - parentNodePos.y()
                moveNodeGroup(grpNodeDict, 0, alphaY)
                break

        maxLevel = self.nodeMaxLevel()
        # 节点组居中对齐
        # TODO: 细节待优化，节点移动与边移动不同步
        for level in range(1, maxLevel + 1):
            levelNodes: list[str] = self.getNodesByLevel(level)
            levelGrpNodes = groupByParent(levelNodes)
            grpBoundingRect = arrangeNodeInGroup(levelGrpNodes)
            arrangeNodeGrps(levelGrpNodes)
            loggerPrint(
                msg=f"level: {level} - {levelGrpNodes} - left: {grpBoundingRect.x()}, right: {grpBoundingRect.x() + grpBoundingRect.width()}, top: {grpBoundingRect.y()}, bottom: {grpBoundingRect.y() + grpBoundingRect.height()}",
                level=LogLevels.DEBUG,
            )

    def _forceUpdateAllEdges(self):
        for edge in self.edges.values():
            edge.updatePosition()

    def subscribeEvt(self):
        self.uiSubscribe(EventEnum.LOGIC_GRAPHIC_MANAGER_ARRANGE_NODES, self._logicEvt_arrangeNodeGraphics)
        self.uiSubscribe(EventEnum.UI_GRAPHIC_MANAGER_MOVE_NODE, self._uiEvt_moveNode)
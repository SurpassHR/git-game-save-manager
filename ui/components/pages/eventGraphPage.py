import sys
import uuid
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QBoxLayout
from PyQt5.QtCore import pyqtSlot
from pathlib import Path

from qfluentwidgets import PrimaryPushButton
from qfluentwidgets.common.icon import FluentIcon

rootPath = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(rootPath)

from core.gitManager import CommitObj
from ui.components.utils.eventManager import EventEnum
from ui.components.utils.uiFunctionBase import UIFunctionBase, MsgBoxLevels
from ui.components.widgets.layouts.infiniteCanvasView import InfiniteCanvasView
from ui.components.widgets.layouts.gridScene import ColliDetectSmartScene
from ui.publicDefs.styleDefs import NODE_VERTICAL_SPACING


class EventGraphPage(QFrame, UIFunctionBase):
    def __init__(self, text: str, window) -> None:
        QFrame.__init__(self, window)

        self.setObjectName(text.replace(" ", "-"))

        self.window = window

        self.subscribeEvt()

        self.createUI()

    def addScene(self, container: QBoxLayout) -> None:
        self.scene = ColliDetectSmartScene(self)

        view = InfiniteCanvasView(self.scene, self)

        container.addWidget(view)

    @pyqtSlot(EventEnum, dict)
    def _uiEvt_nodeMgrRefreshCommits(self, event: EventEnum = EventEnum.EVENT_INVALID, data: dict = {}) -> None:
        commitDict: dict[str, CommitObj] = self.scene.getRepoRawCommitInfo(self.uiGetConfig("repo") if event != EventEnum.EVENT_INVALID else "")
        self.scene.destroyAll()
        for k in reversed(self.scene.graph.keys()):
            self.addNodeFromRelations(commitDict[k])
        self.addConnectionFromGitInfo()
        self.scene._logicEvt_arrangeNodeGraphics()

    def addConnectionFromGitInfo(self) -> None:
        edges = self.scene.get_all_edges()
        for edge in edges:
            self.scene.createConnections(edge[0], edge[1])

    def createUI(self) -> None:
        container = QVBoxLayout()

        def addCtrlBtn(container: QBoxLayout):
            btnContainer = QHBoxLayout()

            btn1 = PrimaryPushButton(
                text="增加节点",
                icon=FluentIcon.ADD,
            )
            btn1.clicked.connect(self.addStandardNode)

            btn2 = PrimaryPushButton(
                text="删除节点",
                icon=FluentIcon.REMOVE,
            )
            btn2.clicked.connect(self.removeSelectedNode)

            btn3 = PrimaryPushButton(
                text="整理节点",
                icon=FluentIcon.ROTATE,
            )
            btn3.clicked.connect(lambda: self.uiEmit(EventEnum.LOGIC_GRAPHIC_MANAGER_ARRANGE_NODES, {}))

            btnContainer.addWidget(btn1, 1)
            btnContainer.addWidget(btn2, 1)
            btnContainer.addWidget(btn3, 1)

            container.addLayout(btnContainer)

        addCtrlBtn(container)
        self.addScene(container)
        self._uiEvt_nodeMgrRefreshCommits()
        hasCircle = self.scene.isGraphHasCircle()
        if hasCircle:
            self.uiShowMsgBox(
                level=MsgBoxLevels.WARNING,
                msg="当前事件图中出现环，合并分支会导致不可预料的问题",
                acptCbk=None,
                rjctCbk=None,
            )
        self.setLayout(container)

    def addStandardNode(self) -> None:
        # 触发创建 commit 事件，并获取返回的 commitObj 数据
        return

        selectedNode = self.scene.getSelected()
        isSceneEmpty = self.scene.isEmpty()

        # 当前没有选中的节点，且场景内已有节点，不添加新节点
        if selectedNode is None and not isSceneEmpty:
            return

        # 当前没有选中的节点，但是场景内没有节点，此时添加一个首节点
        if selectedNode is None and isSceneEmpty:
            self.scene.createDragableNode(
                x=-100,
                y=-100,
                r=30,
                id="root",
                parents="",
                level=self.dis
            )

        # 当前有选中的节点，给该节点添加一个子节点
        if selectedNode:
            pos = self.scene.getNodePosition(selectedNode.id)
            if pos is None:
                return
            self.scene.createDragableNode(
                x=pos.x(),
                y=pos.y() + NODE_VERTICAL_SPACING,
                r=30,
                id=str(uuid.uuid4()),
                parents=selectedNode.id,
                level=self.distance("root", str(uuid.uuid4())),
            )

    def addNodeFromRelations(self, commitObj: CommitObj):
        parentNodes: list[str] = commitObj.parents
        if len(parentNodes) == 0:
            self.scene.createDragableNode(
                x=-100,
                y=-100,
                r=30,
                commitObj=commitObj,
                level=0,
            )
        else:
            rootNode = self.scene.getRootNode()
            if not rootNode:
                return
            pos = self.scene.getNodePosition(parentNodes[0])
            if pos is None:
                return
            self.scene.createDragableNode(
                x=pos.x(),
                y=pos.y() + NODE_VERTICAL_SPACING,
                r=30,
                commitObj=commitObj,
                level=self.scene.distance(rootNode.hexSha(), commitObj.hexSha),
            )

    def removeSelectedNode(self) -> None:
        selectedNode = self.scene.getSelected()
        if not selectedNode:
            return
        self.scene.removeGraphic(selectedNode.hexSha())

    def subscribeEvt(self):
        self.uiSubscribe(EventEnum.UI_GIT_MANAGER_REFRESH_COMMIT_INFO, self._uiEvt_nodeMgrRefreshCommits)
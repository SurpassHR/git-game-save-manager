import sys

from typing import Optional
from enum import IntEnum
from collections.abc import Callable

from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot,
    QRunnable,
    QThreadPool,
)
from PyQt5.QtWidgets import QWidget

from qfluentwidgets.components.dialog_box import MessageBox

from core.tools.publicDef.levelDefs import MsgBoxLevels
from core.tools.utils.simpleLogger import loggerPrint
from core.tools.publicDef.levelDefs import LogLevels


class EventEnum(IntEnum):
    EVENT_INVALID = 0

    # 逻辑事件线程
    # 耗时逻辑操作相关事件，可以在子线程中执行
    LOGIC_EVENT_START = 0x0000
    LOGIC_GRAPHIC_MANAGER_ARRANGE_NODES = 0x0001 # 图形管理整理节点图形
    LOGIC_EVENT_END = 0x0FFF

    # UI事件线程
    # UI 绘制相关事件，不能在子线程中执行
    UI_EVENT_START = 0x1000
    UI_GRAPHIC_MGR_MOVE_NODE = 0x1001 # 图形管理移动节点图形
    UI_GRAPHIC_MGR_MOUSE_MOVE_NODE = 0x1002 # 鼠标移动节点图形（由于图形管理维护所有的节点和边，所以在此进行处理）
    UI_COLLISION_SCENE_PROC_DETECT = 0x1003 # 场景处理节点碰撞
    UI_GIT_MANAGER_REFRESH_COMMIT_INFO = 0x1004 # git 管理刷新提交节点记录
    UI_EVENT_END = 0x1FFF


class EventTask(QRunnable):
    def __init__(self, handler: Callable, event: EventEnum, data: dict):
        super().__init__()
        self.handler = handler
        self.event = event
        self.data = data

    def run(self):
        try:
            self.handler(self.event, self.data)
        except Exception as e:
            EventManager.getSingleton().emitError(
                sys.exc_info()[2].tb_frame.f_code.co_filename,  # type: ignore
                str(sys.exc_info()[2].tb_lineno),  # type: ignore
                str(e),
            )


class EventManager(QObject):
    # 单一实例
    _singleton = None

    # 自定义信号
    # 字典类型或者其他复杂对象应该使用 object 作为信号参数类型，这样可以传递任意 Python 对象，包括 dict
    _signal = pyqtSignal(EventEnum, object)

    # 事件列表
    _eventCallbacks: dict[EventEnum, list[Callable]] = {}

    # 错误事件在这里统一处理（完全不处理，直接弹框提示到对应位置修改问题，只要保证例外出现时不会导致 UI 进程挂掉）
    _errorSignal = pyqtSignal(str, str, str)

    # 消息框事件
    _msgBoxSignal = pyqtSignal(MsgBoxLevels, str, object, object)

    # 主窗口
    _mainWindow: Optional[QWidget] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._signal.connect(self.processEvent)
        self._errorSignal.connect(self.processError)
        self._msgBoxSignal.connect(self.processMsgBox)

    # 获取单例
    @staticmethod
    def getSingleton():
        if EventManager._singleton is None:
            EventManager._singleton = EventManager()

        return EventManager._singleton

    # 处理事件
    def processEvent(self, event: EventEnum, data: dict):
        if event in self._eventCallbacks.keys():
            isUiEvent = event > EventEnum.UI_EVENT_START.value and event < EventEnum.UI_EVENT_END.value
            for handler in self._eventCallbacks[event]:
                if isUiEvent:
                    handler(event, data)
                else:
                    task = EventTask(handler, event, data)
                    QThreadPool.globalInstance().start(task)  # type: ignore

    @pyqtSlot(MsgBoxLevels, str, object, object)
    def processMsgBox(self, level: MsgBoxLevels, msg: str, acptCbk: Optional[Callable] = None, rejtCbk: Optional[Callable] = None):
        # 类型转换和检查
        if not isinstance(level, MsgBoxLevels):
            return
        msgBox = MessageBox(title=level.value, content=msg, parent=self._mainWindow)
        msgBox.yesButton.setText("确定")
        msgBox.cancelButton.setText("取消")
        if callable(acptCbk):
            msgBox.accepted.connect(acptCbk)
        if callable(rejtCbk):
            msgBox.rejected.connect(rejtCbk)
        msgBox.exec()

    def showMsgBox(self, level: MsgBoxLevels, msg: str, acptCbk: Optional[Callable] = None, rejtCbk: Optional[Callable] = None) -> None:
        self._msgBoxSignal.emit(level, msg, acptCbk, rejtCbk)

    @pyqtSlot(str, str, str)
    def processError(self, filename: str, lineno: str, error: str):
        msg = f"{filename}:{lineno} - ERROR: {error}"
        loggerPrint(msg, level=LogLevels.ERROR)
        self.showMsgBox(
            level=MsgBoxLevels.ERROR,
            msg=msg,
            acptCbk=None,
        )

    def emitError(self, filename: str, lineno: str, error: str):
        self._errorSignal.emit(filename, lineno, error)

    # 触发事件
    def emit(self, event: EventEnum, data: dict):
        self._signal.emit(event, data)

    # 订阅事件
    def subscribe(self, event: EventEnum, handler: Callable):
        if event not in self._eventCallbacks:
            self._eventCallbacks[event] = []
        self._eventCallbacks[event].append(handler)

    # 取消订阅事件
    def unsubscribe(self, event: EventEnum, handler: Callable):
        if event in self._eventCallbacks:
            self._eventCallbacks[event].remove(handler)

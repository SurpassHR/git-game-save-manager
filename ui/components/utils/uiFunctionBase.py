from typing import Callable, Optional

from PyQt5.QtWidgets import QWidget

from core.tools.utils.simpleLogger import loggerPrint
from core.tools.utils.configLoader import getConfig, setConfig
from core.tools.publicDef.levelDefs import LogLevels, MsgBoxLevels
from ui.components.utils.eventManager import EventManager, EventEnum


# 这里的全部信息都是每次从配置读取的，完全不使用缓存
class UIFunctionBase:
    _singleton = None

    def __init__(self) -> None:
        pass

    # UI 中读取配置
    def uiGetConfig(self, key: str, default: str = "") -> str:
        return getConfig(key, default)

    # UI 中写入配置
    def uiSetConfig(self, key: str, val: str) -> bool:
        return setConfig(key, val)

    # 主窗口弹窗
    def uiShowMsgBox(
        self,
        level: MsgBoxLevels,
        msg: str,
        acptCbk: Optional[Callable] = None,
        rjctCbk: Optional[Callable] = None,
    ) -> None:
        EventManager.getSingleton().showMsgBox(
            level=level,
            msg=msg,
            acptCbk=acptCbk,
            rejtCbk=rjctCbk,
        )

    def uiSetMainWindow(self, mainWindow: QWidget) -> None:
        EventManager._mainWindow = mainWindow

    # 触发错误处理
    def uiEmitError(self, filename: str, lineno: str, error: str) -> None:
        EventManager.getSingleton()._errorSignal.emit(filename, lineno, error)

    # 触发事件
    def uiEmit(self, event: EventEnum, data: dict) -> None:
        loggerPrint(f"触发事件: {event.name}", level=LogLevels.DEBUG)
        EventManager.getSingleton().emit(event, data)

    # 订阅事件
    def uiSubscribe(self, event: EventEnum, handler: Callable) -> None:
        loggerPrint(f"订阅事件: {event.name}", level=LogLevels.DEBUG)
        EventManager.getSingleton().subscribe(event, handler)

    # 取消订阅事件
    def uiUnsubscribe(self, event: EventEnum, handler: Callable) -> None:
        loggerPrint(f"取消订阅事件: {event.name}", level=LogLevels.DEBUG)
        EventManager.getSingleton().unsubscribe(event, handler)

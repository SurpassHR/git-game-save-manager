from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from qfluentwidgets import (
    CardWidget,
    PushButton,
    CaptionLabel,
    StrongBodyLabel,
    FluentIconBase,
)


class PushButtonCard(CardWidget):
    def __init__(self, title: str, description: str, init=None, clicked=None) -> None:
        super().__init__(None)

        # 设置容器
        self.setBorderRadius(4)
        self.container = QHBoxLayout(self)

        # 文本控件
        self.vbox = QVBoxLayout()

        self.titleLabel = StrongBodyLabel(title, self)
        self.titleLabel.setContentsMargins(4, 0, 0, 4)
        self.descriptionLabel = CaptionLabel(description, self)
        self.descriptionLabel.setContentsMargins(4, 0, 0, 4)
        self.descriptionLabel.setTextColor(QColor(96, 96, 96), QColor(160, 160, 160))

        self.vbox.addWidget(self.titleLabel)
        self.vbox.addWidget(self.descriptionLabel)
        self.container.addLayout(self.vbox)

        # 填充
        self.container.addStretch(1)

        # 添加控件
        self.pushButton = PushButton("", self)
        self.container.addWidget(self.pushButton)

        if init:
            init(self)

        if clicked:
            self.pushButton.clicked.connect(lambda: clicked(self))

    def setTitle(self, title: str) -> None:
        self.titleLabel.setText(title)

    def setDescription(self, description: str) -> None:
        self.descriptionLabel.setText(description)

    def setText(self, text: str) -> None:
        self.pushButton.setText(text)

    def setIcon(self, icon: FluentIconBase) -> None:
        self.pushButton.setIcon(icon)

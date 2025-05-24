from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtGui import QFont


NODE_BORDER_DEFAULT_PEN = QPen(QColor("#000"))

NODE_ORANGE_FILL_BRUSH = QBrush(QColor("#FC5531"))
NODE_FILL_DEFAULT_BRUSH = NODE_ORANGE_FILL_BRUSH

NODE_VERTICAL_SPACING = 100
NODE_HORIZONTAL_SPACING = 100

msYaheiFont: str = "微软雅黑"
# 全局标题字体
titleFont = QFont(None)
titleFont.setPointSize(15)
titleFont.setFamily(msYaheiFont)
# 全局正文字体
bodyFont = QFont(None)
bodyFont.setPointSize(11)
bodyFont.setFamily(msYaheiFont)
# 全局注释说明字体
commentFont = QFont(None)
commentFont.setPointSize(9)
commentFont.setFamily(msYaheiFont)

noBorderStyleSheet: str = """
    QGroupBox {
        border: 1px none #DCDCDC;
        border-radius: 10px;
    }
"""

roundBorderCornerStyleSheet: str = """
    QGroupBox {
        border: 1px solid #DCDCDC;
        border-radius: 10px;
    }
"""
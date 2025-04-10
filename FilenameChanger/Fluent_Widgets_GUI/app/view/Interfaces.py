from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl, QSize

from Fluent_Widgets_GUI.qfluentwidgets import SubtitleLabel, setFont


class HomeInterface(QFrame):
    """定义主页布局"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)  # 第三个参数设置对齐方式
        self.setObjectName(text.replace(' ', '-'))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel)


class HistoryListInterface(QFrame):
    """历史记录列表界面"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HistoryListInterface')

        """界面基本设置"""
        self.totalWidget = QWidget(self)
        self.interfaceLayout = QHBoxLayout(self)
        self.widgetLayout = QVBoxLayout(self.totalWidget)

        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 默认向上对齐

        self.interfaceLayout.addWidget(self.totalWidget)

        """标题标签"""
        self.titleLabel = SubtitleLabel(text=text, parent=self)

        self.widgetLayout.addWidget(self.titleLabel)

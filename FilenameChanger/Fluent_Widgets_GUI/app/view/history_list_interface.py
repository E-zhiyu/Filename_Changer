from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, PushButton, FluentIcon, setFont,
                                                               SmoothScrollArea)


class HistoryListInterface(QFrame):
    """历史记录列表界面"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HistoryListInterface')

        """界面基本设置"""
        self.totalWidget = QWidget(self)
        self.interfaceLayout = QHBoxLayout(self)
        self.widgetLayout = QVBoxLayout(self.totalWidget)

        self.setLayout(self.interfaceLayout)  # 设置界面主布局
        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 默认向上对齐

        self.interfaceLayout.addWidget(self.totalWidget)

        """标题标签"""
        self.titleLabel = SubtitleLabel(text=text, parent=self)

        setFont(self.titleLabel, 30)

        self.widgetLayout.addWidget(self.titleLabel)

        """历史记录编辑按钮"""
        self.delBtn = PushButton(FluentIcon.DELETE, '删除选中记录')
        self.clearBtn = PushButton(FluentIcon.BROOM, '清空所有记录')
        self.btnLayout = QHBoxLayout(self)

        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.btnLayout.addWidget(self.delBtn)
        self.btnLayout.addWidget(self.clearBtn)

        self.widgetLayout.addLayout(self.btnLayout)

        """历史记录展示区域"""
        self.historyWidget = QWidget(self)
        self.historyScrollArea = SmoothScrollArea(self)
        self.historyLayout = QVBoxLayout(self.historyWidget)

        self.historyLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.historyScrollArea.setWidget(self.historyWidget)
        self.widgetLayout.addWidget(self.historyScrollArea)

        self.addHistoryCards()  # 加载历史记录卡片

    def addHistoryCards(self):
        pass

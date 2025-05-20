from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (toggleTheme,FluentIcon, setFont, ScrollArea, SubtitleLabel,
                                                               OptionsSettingCard)
from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg


class SettingInterface(ScrollArea):
    """应用设置界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingInterface")
        self.enableTransparentBackground()

        """基本布局设置"""
        self.widget = QWidget()
        self.setWidget(self.widget)
        self.viewLayout = QVBoxLayout()
        self.setLayout(self.viewLayout)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 顶部对齐

        self.titleLabel = SubtitleLabel(text='设置', parent=self.widget)
        setFont(self.titleLabel, 30)
        self.viewLayout.addWidget(self.titleLabel)

        """修改应用主题"""
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            '应用主题',
            '修改你的应用主题',
            texts=[
                '浅色', '深色',
                '跟随系统'
            ],
            parent=self
        )
        self.viewLayout.addWidget(self.themeCard, 0, Qt.AlignmentFlag.AlignTop)



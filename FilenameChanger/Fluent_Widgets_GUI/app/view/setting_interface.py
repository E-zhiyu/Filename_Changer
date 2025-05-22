from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (FluentIcon, setFont, ScrollArea, SubtitleLabel,
                                                               OptionsSettingCard, PushSettingCard, SettingCardGroup,
                                                               InfoBar, InfoBarPosition)
from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg

from FilenameChanger.rename_rules.rule_manager import (import_rule, export_rule)


class SettingInterface(ScrollArea):
    """应用设置界面"""
    ruleChanged = pyqtSignal()

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
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.viewLayout.setSpacing(28)
        self.viewLayout.setContentsMargins(30, 10, 30, 0)

        self.viewLayout.addWidget(self.titleLabel)

        self.initView()

    def initView(self):
        """初始化布局"""

        """个性化设置项"""
        self.personalizationGroup = SettingCardGroup('个性化', self.widget)
        self.viewLayout.addWidget(self.personalizationGroup, 0, Qt.AlignmentFlag.AlignTop)

        # 修改应用主题
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
        self.personalizationGroup.addSettingCard(self.themeCard)

        """规则导入导出"""
        self.ruleIOGroup = SettingCardGroup('规则导入和导出', self.widget)
        self.viewLayout.addWidget(self.ruleIOGroup, 0, Qt.AlignmentFlag.AlignTop)

        # 规则导入
        self.ruleImportCard = PushSettingCard(
            text='选择文件',
            icon=FluentIcon.DOWNLOAD,
            title='规则导入',
            content='从外部json文件导入规则'
        )

        def importRule():
            """显示文件选择窗口并启动导入操作"""
            src_path = QFileDialog.getOpenFileName(
                self,
                '规则导入',
                '',
                'JSON文件 (*.json)'
            )[0]
            if src_path:
                flag, message = import_rule(src_path)
                if flag:
                    InfoBar.success(
                        '成功',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                else:
                    InfoBar.error(
                        '失败',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
            self.ruleChanged.emit()

        self.ruleImportCard.clicked.connect(importRule)
        self.ruleIOGroup.addSettingCard(self.ruleImportCard)

        # 规则导出
        self.ruleExportCard = PushSettingCard(
            text='选择位置',
            icon=FluentIcon.SHARE,
            title='规则导出',
            content='备份你的规则'
        )

        def exportRule():
            """显示文件夹选择窗口并启动导出操作"""
            dst_path = QFileDialog.getExistingDirectory(
                self,
                '规则导出',
                '',
                QFileDialog.Option.ShowDirsOnly
            )
            if dst_path:
                flag, message = export_rule(dst_path)
                if flag:
                    InfoBar.success(
                        '成功',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                else:
                    InfoBar.error(
                        '失败',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )

        self.ruleExportCard.clicked.connect(exportRule)
        self.ruleIOGroup.addSettingCard(self.ruleExportCard)

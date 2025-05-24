from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (FluentIcon, setFont, ScrollArea, SubtitleLabel,
                                                               OptionsSettingCard, PushSettingCard, SettingCardGroup,
                                                               InfoBar, InfoBarPosition, CustomColorSettingCard,
                                                               ExpandLayout)
from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg

from FilenameChanger.rename_rules.rule_manager import (import_rule, export_rule)
from FilenameChanger.log.log_recorder import *


class SettingInterface(QWidget):
    """应用设置界面"""
    ruleChanged = pyqtSignal()
    themeColorChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingInterface")

        """基本布局设置"""
        self.scrollArea = ScrollArea(parent=self)
        self.widget = QWidget()
        self.viewLayout = ExpandLayout(self.widget)
        self.interfaceLayout = QVBoxLayout()
        self.setLayout(self.interfaceLayout)
        self.scrollArea.setWidget(self.widget)
        self.scrollArea.setWidgetResizable(True)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 顶部对齐
        self.interfaceLayout.addWidget(self.scrollArea)

        cfg.themeColorChanged.connect(lambda: self.themeColorChanged.emit())

        # 将背景设置为透明
        self.scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.widget.setStyleSheet("background-color: transparent;")

        self.titleLabel = SubtitleLabel(text='设置', parent=self.widget)
        setFont(self.titleLabel, 30)
        self.viewLayout.setSpacing(28)
        self.viewLayout.setContentsMargins(30, 10, 30, 0)

        self.viewLayout.addWidget(self.titleLabel)

        self.initView()

    def initView(self):
        """初始化布局"""

        """个性化设置项"""
        self.personalizationGroup = SettingCardGroup('个性化', self.widget)
        self.viewLayout.addWidget(self.personalizationGroup)

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
            parent=self.personalizationGroup
        )
        self.personalizationGroup.addSettingCard(self.themeCard)

        # 修改主题颜色
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            '主题颜色',
            '调整应用的主题颜色',
            parent=self.personalizationGroup
        )
        self.personalizationGroup.addSettingCard(self.themeColorCard)

        """规则导入导出"""
        self.ruleIOGroup = SettingCardGroup('规则导入和导出', self.widget)
        self.viewLayout.addWidget(self.ruleIOGroup)

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
                    logging.info(f'用户从“{src_path}”导入规则成功')
                else:
                    InfoBar.error(
                        '失败',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    logging.info(f'用户从“{src_path}”导入规则失败')
                    logging.info(f'原因：{message}')
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
                    logging.info(f'用户导出规则至“{dst_path}”成功')
                else:
                    InfoBar.error(
                        '失败',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    logging.info(f'用户导出规则至“{dst_path}”失败')
                    logging.info(f'原因：{message}')

        self.ruleExportCard.clicked.connect(exportRule)
        self.ruleIOGroup.addSettingCard(self.ruleExportCard)

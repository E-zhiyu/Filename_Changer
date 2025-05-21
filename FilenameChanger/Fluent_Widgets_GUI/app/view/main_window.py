# coding:utf-8
from FilenameChanger import version

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import FluentIcon as FIF, setTheme, Theme, isDarkTheme
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (NavigationItemPosition, FluentWindow)

from FilenameChanger.Fluent_Widgets_GUI.app.view.home_interface import HomeInterface
from FilenameChanger.Fluent_Widgets_GUI.app.view.rule_list_interface import RuleListInterface
from FilenameChanger.Fluent_Widgets_GUI.app.view.info_interface import InfoInterface
from FilenameChanger.Fluent_Widgets_GUI.app.view.history_list_interface import HistoryListInterface
from FilenameChanger.Fluent_Widgets_GUI.app.view.setting_interface import SettingInterface


class MainWindow(FluentWindow):
    """定义主窗口"""

    def __init__(self):
        super().__init__()
        self.initWindow()

        # 设置界面亮暗主题
        setTheme(Theme.AUTO)

        # 实例化不同的子界面
        self.homeInterface = HomeInterface(self)
        self.ruleListInterface = RuleListInterface('规则列表', self)
        self.historyListInterface = HistoryListInterface('历史记录', self)
        self.settingInterface = SettingInterface(self)
        self.infoInterface = InfoInterface(self)

        # 初始化导航栏
        self.initNavigation()

        # 捕获themeChanged信号并连接至修改主题函数
        cfg.themeChanged.connect(self.setStyle)

        # 将各窗口的信号连接至对应方法
        self.homeInterface.refreshView_signal.connect(lambda: self.historyListInterface.initCardView())

    def initNavigation(self):
        """初始化导航栏"""
        self.navigationInterface.setExpandWidth(200)  # 设置导航栏展开宽度

        # 创建导航栏选项
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        self.addSubInterface(self.ruleListInterface, FIF.LAYOUT, '规则列表')
        self.addSubInterface(self.historyListInterface, FIF.HISTORY, '重命名记录')

        # 添加导航栏底部按钮
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.infoInterface, FIF.INFO, '关于软件', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        """初始化窗口"""
        self.resize(1100, 750)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle(f'FilenameChanger-v{version}')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()

    def setStyle(self, theme: Theme):
        """设置样式"""
        setTheme(theme)
        light_scrollBackground = 'QFrame{background-color:rgb(240, 240, 240)}'
        dark_scrollBackground = 'QFrame{background-color:rgb(24, 24, 24)}'
        if not isDarkTheme():
            self.homeInterface.setStyleSheet(light_scrollBackground)
            self.ruleListInterface.setStyleSheet(light_scrollBackground)
            self.historyListInterface.setStyleSheet(light_scrollBackground)
        else:
            self.homeInterface.setStyleSheet(dark_scrollBackground)
            self.ruleListInterface.setStyleSheet(dark_scrollBackground)
            self.historyListInterface.setStyleSheet(dark_scrollBackground)

# coding:utf-8

from FilenameChanger import version

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import FluentIcon as FIF, setTheme, Theme
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (NavigationItemPosition, MessageBox, FluentWindow,
                                               NavigationAvatarWidget, SystemThemeListener)

from FilenameChanger.Fluent_Widgets_GUI.app.view.home_interface import HomeInterface
from FilenameChanger.Fluent_Widgets_GUI.app.view.rule_list_interface import RuleListInterface


class MainWindow(FluentWindow):
    """定义主窗口"""

    def __init__(self):
        super().__init__()
        self.initWindow()

        # 设置界面亮暗主题
        setTheme(Theme.DARK)

        # 实例化不同的子界面
        self.homeInterface = HomeInterface('文件更名器', self)
        self.ruleListInterface = RuleListInterface('规则列表', self)

        self.initNavigation()

    def initNavigation(self):
        """初始化导航栏"""
        # 创建导航栏选项
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        self.addSubInterface(self.ruleListInterface, FIF.LAYOUT, '规则列表')

        # 添加导航栏底部按钮
        """self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)  # 添加导航栏设置按钮
        self.addSubInterface(self.infoInterface, FIF.INFO, '关于', NavigationItemPosition.BOTTOM)  # 添加应用详情界面"""

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

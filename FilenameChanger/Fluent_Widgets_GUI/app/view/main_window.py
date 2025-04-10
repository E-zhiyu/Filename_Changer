# coding:utf-8
from FilenameChanger import version

from PyQt6.QtGui import QIcon, QDesktopServices
from Fluent_Widgets_GUI.qfluentwidgets import FluentIcon as FIF
from Fluent_Widgets_GUI.qfluentwidgets import (NavigationItemPosition, MessageBox, FluentWindow,
                                               NavigationAvatarWidget, SystemThemeListener)

from Fluent_Widgets_GUI.app.view.Interfaces import *


class MainWindow(FluentWindow):
    """定义主窗口"""

    def __init__(self):
        super().__init__()
        self.initWindow()

        # 创建系统主题监听器
        self.themeListener = SystemThemeListener(self)

        # 实例化不同的子界面
        self.homeInterface = HomeInterface('主页', self)
        self.musicInterface = HomeInterface('这是规则列表', self)
        self.infoInterface = HomeInterface('这是应用详情界面', self)
        self.settingInterface = HomeInterface('这是设置界面', self)

        self.initNavigation()

        # 启动主题监听器
        self.themeListener.start()

    def closeEvent(self, event):
        """停止系统主题监听器进程"""
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(event)

    def initNavigation(self):
        """初始化导航栏"""
        # 创建导航栏选项
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        self.addSubInterface(self.musicInterface, FIF.LAYOUT, '规则列表')

        # 添加导航栏底部按钮
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('zhiyiYo', './app/resource/shoko.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)  # 添加导航栏设置按钮
        self.addSubInterface(self.infoInterface, FIF.INFO, '关于', NavigationItemPosition.BOTTOM)  # 添加应用详情界面

        # NOTE: enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

    def initWindow(self):
        """初始化窗口"""
        self.resize(900, 700)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle(f'FilenameChanger-v{version}')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()

        # 设置允许导航面板展开的最小窗口宽度
        # self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))

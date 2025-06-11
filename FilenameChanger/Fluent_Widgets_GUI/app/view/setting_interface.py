"""
软件设置界面
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QDialog, QHBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (FluentIcon, setFont, ScrollArea, SubtitleLabel,
                                                               OptionsSettingCard, PushSettingCard, SettingCardGroup,
                                                               InfoBar, InfoBarPosition, CustomColorSettingCard,
                                                               ExpandLayout, SwitchSettingCard, MessageBoxBase,
                                                               LineEdit, PasswordLineEdit, HeaderCardWidget)
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets.common.config import QConfig
from FilenameChanger.Fluent_Widgets_GUI.app.common.config import Config as cfg

from FilenameChanger.rename_rules.rule_manager import (import_rule, export_rule)
from FilenameChanger.log.log_recorder import *
from FilenameChanger.database.connection_recorder import saveConnectionInfos
from FilenameChanger.database.database_connector import loadConnectionInfos, create_connection


def testConnection(parentInterface):
    """测试数据库连接"""
    # 如果没有启用数据库模式直接结束运行
    if not cfg.get(cfg, cfg.databaseMode):
        return

    connection, flag, message = create_connection()
    if flag:
        InfoBar.success(
            '成功',
            message,
            duration=2000,
            position=InfoBarPosition.TOP,
            parent=parentInterface
        )
    else:
        InfoBar.error(
            '失败',
            message,
            duration=2000,
            position=InfoBarPosition.TOP,
            parent=parentInterface
        )

    if connection:  # 如果connection不是None则运行close方法
        connection.close()


def editDatabaseConnection(parentInterface):
    """编辑数据库连接参数"""
    connection_infos = loadConnectionInfos()

    class EditWindow(MessageBoxBase):
        """创建编辑连接参数的窗口"""
        connection_dict = {
            'host': '',
            'port': 3306,
            'user': '',
            'password': '',
            'database': ''
        }  # 存放数据库连接参数的字典

        def __init__(self, info_dict, parent):
            super().__init__(parent)
            self.info_dict = info_dict

            self.yesButton.setText('确定')
            self.cancelButton.setText('取消')

            self.widget.setFixedWidth(350)

            self.__initView__()

        def __initView__(self):
            """初始化界面布局"""
            # 主机
            hostLayout = QHBoxLayout(self.widget)
            hostLabel = SubtitleLabel(text='主机', parent=self.widget)
            hostLineEdit = LineEdit(self.widget)
            hostLineEdit.setPlaceholderText('请输入主机地址')
            hostLineEdit.setFixedWidth(175)
            hostLineEdit.textChanged.connect(lambda: self.recordConnection('host', hostLineEdit.text()))

            hostLayout.addWidget(hostLabel)
            hostLayout.addStretch(1)
            hostLayout.addWidget(hostLineEdit)
            self.viewLayout.addLayout(hostLayout)

            # 端口
            portLayout = QHBoxLayout(self.widget)
            portLabel = SubtitleLabel(text='端口', parent=self.widget)
            portLineEdit = LineEdit(self.widget)
            portLineEdit.setPlaceholderText('留空使用默认值3306')
            portLineEdit.setFixedWidth(175)
            portLineEdit.textChanged.connect(lambda: self.recordConnection('port', portLineEdit.text()))

            portLayout.addWidget(portLabel)
            portLayout.addStretch(1)
            portLayout.addWidget(portLineEdit)
            self.viewLayout.addLayout(portLayout)

            # 用户
            userLayout = QHBoxLayout(self.widget)
            userLabel = SubtitleLabel(text='用户', parent=self.widget)
            userLineEdit = LineEdit(self.widget)
            userLineEdit.setPlaceholderText('请输入用户名')
            userLineEdit.setFixedWidth(175)
            userLineEdit.textChanged.connect(lambda: self.recordConnection('user', userLineEdit.text()))

            userLayout.addWidget(userLabel)
            userLayout.addStretch(1)
            userLayout.addWidget(userLineEdit)
            self.viewLayout.addLayout(userLayout)

            # 密码
            passwordLayout = QHBoxLayout(self.widget)
            passwordLabel = SubtitleLabel(text='密码', parent=self.widget)
            passwordLineEdit = PasswordLineEdit(self.widget)
            passwordLineEdit.setPlaceholderText('请输入密码')
            passwordLineEdit.setFixedWidth(175)
            passwordLineEdit.textChanged.connect(lambda: self.recordConnection('password', passwordLineEdit.text()))

            passwordLayout.addWidget(passwordLabel)
            passwordLayout.addStretch(1)
            passwordLayout.addWidget(passwordLineEdit)
            self.viewLayout.addLayout(passwordLayout)

            # 数据库
            databaseLayout = QHBoxLayout(self.widget)
            databaseLabel = SubtitleLabel(text='数据库', parent=self.widget)
            databaseLineEdit = LineEdit(self.widget)
            databaseLineEdit.setPlaceholderText('请输入数据库')
            databaseLineEdit.setFixedWidth(175)
            databaseLineEdit.textChanged.connect(lambda: self.recordConnection('database', databaseLineEdit.text()))

            databaseLayout.addWidget(databaseLabel)
            databaseLayout.addStretch(1)
            databaseLayout.addWidget(databaseLineEdit)
            self.viewLayout.addLayout(databaseLayout)

            """设置输入框文本"""
            hostLineEdit.setText(self.info_dict['host'])
            portLineEdit.setText(str(self.info_dict['port']))
            userLineEdit.setText(self.info_dict['user'])
            passwordLineEdit.setText(self.info_dict['password'])
            databaseLineEdit.setText(self.info_dict['database'])

        def recordConnection(self, k, v):
            """将键值对保存至字典"""
            if k == 'port':
                self.connection_dict[k] = int(v)  # 端口号保存为整型
            else:
                self.connection_dict[k] = v

    window = EditWindow(connection_infos, parentInterface)
    if window.exec():
        connection_dict = window.connection_dict
        saveConnectionInfos(connection_dict)

        logging.info('数据库连接参数保存成功')

        # 编辑完成后如果启用了数据库模式则测试连接状态
        if cfg.get(cfg, cfg.databaseMode):
            testConnection(parentInterface)
        else:
            InfoBar.success(
                '成功',
                '数据库连接参数保存成功',
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=parentInterface
            )


class SettingInterface(QWidget):
    """应用设置界面"""
    ruleChanged = pyqtSignal()

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
            QConfig.themeMode,
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
            QConfig.themeColor,
            FluentIcon.PALETTE,
            '主题颜色',
            '调整应用的主题颜色',
            parent=self.personalizationGroup
        )
        self.personalizationGroup.addSettingCard(self.themeColorCard)

        """数据管理"""
        self.dataManagementGroup = SettingCardGroup('数据管理', self.widget)
        self.viewLayout.addWidget(self.dataManagementGroup)

        # 数据库模式开关
        self.databaseCard = SwitchSettingCard(
            FluentIcon.BOOK_SHELF,
            '数据库模式',
            '使用数据库管理规则和历史记录',
            cfg.databaseMode
        )
        self.dataManagementGroup.addSettingCard(self.databaseCard)
        self.databaseCard.checkedChanged.connect(lambda: testConnection(self))

        # 数据库连接参数设置
        self.databaseConnectionCard = PushSettingCard(
            '编辑参数',
            FluentIcon.LINK,
            '连接数据库',
            '设置数据库连接参数',
            self
        )
        self.dataManagementGroup.addSettingCard(self.databaseConnectionCard)
        self.databaseConnectionCard.clicked.connect(lambda: editDatabaseConnection(self))

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
        self.dataManagementGroup.addSettingCard(self.ruleImportCard)

        # 规则导出
        self.ruleExportCard = PushSettingCard(
            text='选择位置',
            icon=FluentIcon.SHARE,
            title='规则导出',
            content='备份你的规则'
        )

        def exportRule():
            """显示文件夹选择窗口并启动导出操作"""
            dialog = QFileDialog(
                self,
                '规则导出',
                '',
                'JSON文件 (*.json)',
            )
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)  # 对话框设置为保存文件模式
            file_name = datetime.now().strftime('%Y_%m_%d_') + 'FC_rule.json'
            dialog.selectFile(file_name)  # 设置默认文件名

            if dialog.exec() == QDialog.DialogCode.Accepted:
                dst_path = dialog.selectedFiles()[0]
                flag, message = export_rule(dst_path)
                if flag:
                    InfoBar.success(
                        '成功',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    logging.info(f'【成功】用户导出规则至“{dst_path}”')
                else:
                    InfoBar.error(
                        '失败',
                        message,
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    logging.info(f'【失败】用户导出规则至“{dst_path}”')
                    logging.info(f'原因：{message}')

        self.ruleExportCard.clicked.connect(exportRule)
        self.dataManagementGroup.addSettingCard(self.ruleExportCard)

        """重命名设置"""
        self.modeGroup = SettingCardGroup('重命名设置', self.widget)
        self.viewLayout.addWidget(self.modeGroup)

        # 扫描全部文件
        self.secureScanningCard = SwitchSettingCard(
            FluentIcon.VPN,
            '安全扫描模式（建议开启）',
            '扫描目标文件夹时忽略隐藏、只读、系统文件',
            cfg.secureScanning
        )
        self.modeGroup.addSettingCard(self.secureScanningCard)

        def secureScanning_log():
            """安全扫描模式值改变时写入日志"""
            if cfg.get(cfg, cfg.secureScanning):
                logging.info('设置项改变，安全扫描模式：开')
            else:
                logging.info('设置项改变，安全扫描模式：关')

        self.secureScanningCard.checkedChanged.connect(secureScanning_log)

        # 文件夹模式
        self.folderModeCard = SwitchSettingCard(
            FluentIcon.FOLDER,
            '文件夹模式',
            '重命名对象由文件更改为文件夹',
            cfg.folderMode
        )
        self.modeGroup.addSettingCard(self.folderModeCard)

        def folderMode_log():
            """文件夹模式改变时写入日志"""
            if cfg.get(cfg, cfg.folderMode):
                logging.info('设置项改变，文件夹模式：开')
            else:
                logging.info('设置项改变，文件夹模式：关')

        self.folderModeCard.checkedChanged.connect(folderMode_log)

from operator import index

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, BodyLabel, setFont, LineEdit, FluentIcon,
                                                               PrimaryPushButton, SmoothScrollArea, MessageBox,
                                                               ToolButton, CardWidget, CheckBox, MessageBoxBase,
                                                               TeachingTip, InfoBarIcon, TeachingTipTailPosition)

from FilenameChanger.file_history_operations.file_history_operations import (is_directory_usable, rename,
                                                                             cancel_rename_operation, scan_files)
from FilenameChanger.log.log_recorder import *


class FileCard(CardWidget):
    """文件卡片"""
    selectSignal = pyqtSignal()

    def __init__(self, file_name, selected: bool, index: int, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.file_name = file_name
        self.index = index

        """基本设置"""
        self.setFixedHeight(37)

        self.viewLayout = QHBoxLayout()
        self.setLayout(self.viewLayout)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.viewLayout.setSpacing(0)

        """是否选中复选框"""
        self.selectedCheckBox = CheckBox()
        self.selectedCheckBox.setFixedWidth(10)
        if selected:
            self.selectedCheckBox.setChecked(True)  # 默认所有文件都是选中状态
        self.viewLayout.addWidget(self.selectedCheckBox)
        self.selectedCheckBox.stateChanged.connect(self.modifySelectFileList)

        """文件名文本标签"""
        filenameLabel = BodyLabel(self.file_name, self)
        self.viewLayout.addWidget(filenameLabel)

    def modifySelectFileList(self):
        """文件选中状态改变时修改选中文件列表"""
        if self.selectedCheckBox.checkState() == Qt.CheckState.Checked:
            if self.file_name not in self.parent.selected_file_list:  # 只有文件名不在选中列表时才添加
                self.parent.selected_file_list.append(self.file_name)
        else:
            try:
                self.parent.selected_file_list.remove(self.file_name)
            except ValueError:
                print(f'{self.file_name}不在选中列表中')  # 仅用于调试

        self.selectSignal.emit()  # 发送信号切换全选复选框的状态

    def switchSelected(self):
        """切换文件选中状态"""
        if self.selectedCheckBox.isChecked():
            self.selectedCheckBox.setChecked(False)
        else:
            self.selectedCheckBox.setChecked(True)

    def setCardChecked(self, checked: bool):
        """设置文件选中状态"""
        if checked:
            self.selectedCheckBox.setChecked(True)
        else:
            self.selectedCheckBox.setChecked(False)


class SelectAllCheckBox(CheckBox):
    """文件列表的全选复选框"""

    def nextCheckState(self):
        """未选中和半选中时点击切换为选中，选中时点击切换为未选中"""
        if self.checkState() == Qt.CheckState.Unchecked:
            self.setCheckState(Qt.CheckState.Checked)
        elif self.checkState() == Qt.CheckState.PartiallyChecked:
            self.setCheckState(Qt.CheckState.Checked)
        else:
            self.setCheckState(Qt.CheckState.Unchecked)


class FileListInterface(MessageBoxBase):
    """文件列表界面"""

    def __init__(self, scan_file_list, selected_file_tuple, parent=None):
        super().__init__(parent)
        self.widget.setFixedHeight(700)
        self.widget.setFixedWidth(600)

        self.scan_file_list = scan_file_list
        self.selected_file_list = list(selected_file_tuple)
        self.file_card_list = []
        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')

        """标题标签"""
        self.titleLabel = SubtitleLabel(text='文件列表', parent=self.widget)
        self.viewLayout.addWidget(self.titleLabel)

        """全选复选框和文件数量标签"""
        self.checkBoxAndNumLabelLayout = QHBoxLayout()

        # 文件数量标签
        self.numLabel = BodyLabel(text=f'已选中：{len(self.selected_file_list)}/{len(self.scan_file_list)}',
                                  parent=self.widget)

        # 全选复选框
        self.selectAllCheckBox = SelectAllCheckBox('全选')
        self.selectAllCheckBox.setTristate(True)  # 复选框启用三态
        self.setCheckBoxState()

        self.selectAllCheckBox.stateChanged.connect(self.selectAllFile)

        # 控件添加至主布局
        self.checkBoxAndNumLabelLayout.addWidget(self.selectAllCheckBox, 0, Qt.AlignmentFlag.AlignLeft)
        self.checkBoxAndNumLabelLayout.addWidget(self.numLabel, 0, Qt.AlignmentFlag.AlignRight)
        self.viewLayout.addLayout(self.checkBoxAndNumLabelLayout)

        """文件展示区域"""
        self.fileScrollArea = SmoothScrollArea()
        self.fileWidget = QWidget(self)
        self.fileScrollArea.setWidget(self.fileWidget)
        self.fileScrollArea.setWidgetResizable(True)

        self.fileViewLayout = QVBoxLayout(self.fileWidget)
        self.fileViewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.viewLayout.addWidget(self.fileScrollArea)

        self.initView()

    def initView(self):
        """初始化文件展示"""
        index = 0
        for file_name in self.scan_file_list:
            if file_name in self.selected_file_list:
                selected = True
            else:
                selected = False
            card = FileCard(file_name, selected, index, self)
            card.selectSignal.connect(self.setCheckBoxState)
            self.file_card_list.append(card)
            card.clicked.connect(lambda card_index=card.index: self.file_card_list[card_index].switchSelected())
            self.fileViewLayout.addWidget(card)
            index += 1

    def setCheckBoxState(self):
        """设置全选复选框的状态和文件数量标签的文本"""
        if len(self.scan_file_list) == len(self.selected_file_list):
            self.selectAllCheckBox.setCheckState(Qt.CheckState.Checked)
        elif self.selected_file_list:
            self.selectAllCheckBox.setCheckState(Qt.CheckState.PartiallyChecked)
        else:
            self.selectAllCheckBox.setCheckState(Qt.CheckState.Unchecked)

        self.numLabel.setText(f'已选择：{len(self.selected_file_list)}/{len(self.scan_file_list)}')

    def selectAllFile(self):
        """文件全选或全不选"""
        if self.selectAllCheckBox.checkState() == Qt.CheckState.Checked:
            for card in self.file_card_list:
                card.setCardChecked(True)
        elif self.selectAllCheckBox.checkState() == Qt.CheckState.Unchecked:
            for card in self.file_card_list:
                card.setCardChecked(False)


class HomeInterface(QWidget):
    """定义主页布局"""

    # 定义触发历史记录列表刷新布局方法的信号
    refreshView_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HomeInterface')  # 设置全局唯一对象名，否则不能将该界面添加至导航栏
        self.scan_file = []
        self.selected_file_tuple = None

        """基本布局设置"""
        self.totalWidget = QWidget(self)  # 创建一个总容器存放所有控件，使得调整窗口大小的时候各控件不会相互分离
        self.interfaceLayout = QVBoxLayout(self)  # 界面总布局器，只存放一个总容器控件
        self.widgetLayout = QVBoxLayout(self.totalWidget)  # 总容器的垂直布局器
        self.setLayout(self.interfaceLayout)  # 设置界面主布局器

        self.interfaceLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 界面总布局器默认为居中对齐
        self.interfaceLayout.addWidget(self.totalWidget, 0, Qt.AlignmentFlag.AlignCenter)

        """标题标签"""
        self.label = SubtitleLabel(text='文件更名器', parent=self.totalWidget)
        setFont(self.label, 40)

        self.widgetLayout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)
        self.widgetLayout.addSpacing(15)

        """文件夹选择"""
        # 文本框
        self.folderLineEdit = LineEdit(self.totalWidget)
        self.lineEditAndBtnLayout = QHBoxLayout()  # 文件夹选择布局器（水平）
        self.lineEditLayout = QVBoxLayout()  # 文本框布局器（垂直）
        self.lineEditLayout.addLayout(self.lineEditAndBtnLayout)

        self.lineEditAndBtnLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.folderLineEdit.setFixedWidth(250)
        self.folderLineEdit.setClearButtonEnabled(True)
        self.folderLineEdit.setPlaceholderText('请选择一个文件夹')  # 设置文本框提示文本

        self.lineEditAndBtnLayout.addWidget(self.folderLineEdit)

        # 文件夹浏览按钮
        self.folderSelectBtn = ToolButton(FluentIcon.FOLDER)
        self.folderSelectBtn.setFixedHeight(34)
        self.lineEditAndBtnLayout.addWidget(self.folderSelectBtn)

        # 文件查看按钮
        self.fileListBtn = ToolButton(FluentIcon.ALIGNMENT)
        self.fileListBtn.setFixedHeight(34)
        self.lineEditAndBtnLayout.addWidget(self.fileListBtn)

        # 文件夹路径有效性提示标签
        self.tipLabel = BodyLabel(self.totalWidget)  # 提示用户是否输入正确的路径
        setFont(self.tipLabel, 17)
        self.lineEditLayout.addWidget(self.tipLabel, 0, Qt.AlignmentFlag.AlignCenter)

        # 将整体布局添加至主布局器
        self.widgetLayout.addLayout(self.lineEditLayout)
        self.widgetLayout.addSpacing(10)

        """功能按钮"""
        self.renameBtn = PrimaryPushButton(FluentIcon.PENCIL_INK, '文件重命名')
        self.cancelOperationBtn = PrimaryPushButton(FluentIcon.HISTORY, '撤销重命名')
        self.buttonHBoxLayout = QHBoxLayout()  # 按钮布局器（水平）

        self.renameBtn.setFixedWidth(175)
        self.renameBtn.setEnabled(False)  # 先将其禁用防止未输入路径就重命名
        self.cancelOperationBtn.setFixedWidth(175)

        self.buttonHBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonHBoxLayout.setSpacing(30)  # 设置布局器的默认控件间隔

        self.widgetLayout.addLayout(self.buttonHBoxLayout)
        self.buttonHBoxLayout.addWidget(self.renameBtn)
        self.buttonHBoxLayout.addWidget(self.cancelOperationBtn, 0)

        self.achieve_functions()  # 调用控件功能函数

    def achieve_functions(self):
        """实现各控件的功能"""

        def confirm_operation(with_warning=True):
            """弹出确认操作的提示框"""
            warning = """\
            【警告】您正在批量修改文件名，可能伴随以下风险：
            - 重命名后某些软件会因为路径依赖而无法定位到该文件！
            - 如果文件夹内有您不想重命名的文件，它们也会被重命名！
            - 重命名可能导致文件路径超出最大长度，导致文件无法使用！
            """
            if with_warning:
                message = f"{warning}{'\n确认进行操作吗？'}"
            else:
                message = '确认进行操作吗？'

            confirm_window = MessageBox('操作确认', content=message, parent=self)
            confirm_window.yesButton.setText('确认')
            confirm_window.cancelButton.setText('取消')

            if confirm_window.exec():
                return 1
            else:
                return 0

        def dirLineEdit_function():
            # 文本框功能实现
            targetDirectory = self.folderLineEdit.text().strip('\"')
            flag = is_directory_usable(targetDirectory)
            if flag == 1:
                logging.info('路径有效，进行下一步操作')
                self.renameBtn.setEnabled(True)
                self.tipLabel.setStyleSheet("""QLabel{color: rgb(72, 180, 72);
                                              text-shadow: 2px 2px 4px black;}""")
                self.tipLabel.setText('文件夹路径有效！')
            elif flag == 0:
                logging.warning('路径无效')
                self.renameBtn.setEnabled(False)
                self.tipLabel.setStyleSheet("""QLabel{color: rgb(255, 100, 100);
                                                text-shadow: 2px 2px 4px black;}""")
                self.tipLabel.setText('这不是一个有效的文件夹！')
            elif flag == -1:
                logging.info('用户清空输入框的路径')
                self.renameBtn.setEnabled(False)
                self.tipLabel.setText('')

        self.folderLineEdit.textChanged.connect(dirLineEdit_function)

        # 重命名按钮功能实现
        def rename_button_callback():
            logging.info('用户点击重命名按钮，确认操作中……')
            if confirm_operation():  # 弹出消息框确认操作
                logging.info('用户确认重命名')

                targetDirectory = self.folderLineEdit.text().strip('\"')
                self.scan_file = scan_files(targetDirectory)
                self.selected_file_tuple = tuple(self.scan_file)
                logging.info(f'已选择：{len(self.selected_file_tuple)}/{len(self.scan_file)}')
                flag = rename(targetDirectory, self.selected_file_tuple)
                # 显示一个消息提示框
                if flag == 1:
                    title = '成功'
                    message = '文件重命名完成！'
                elif flag == 0:
                    message = '文件夹为空或未选中任何文件！'
                    title = '失败'
                elif flag == -1:
                    title = '失败'
                    message = '规则列表为空！请先写入规则！'
                elif flag == -2:
                    title = '失败'
                    message = '所有文件的新旧文件名都相同'
                elif flag == -3:  # 仅用于调试
                    title = '严重错误'
                    message = '新文件名列表为空，请检查代码逻辑！'

                message_window = MessageBox(title=title, content=message, parent=self)
                message_window.cancelButton.hide()
                message_window.buttonLayout.insertStretch(1)
                message_window.yesButton.setText("确认")
                message_window.exec()

            else:
                logging.info('用户取消重命名')

            self.refreshView_signal.emit()

        self.renameBtn.clicked.connect(rename_button_callback)

        # 撤销重命名按钮功能实现
        def cancel_button_callback():
            logging.info('用户点击撤销重命名按钮，确认操作中……')
            if confirm_operation():  # 弹出消息框确认操作
                logging.info('用户确认撤销重命名')
                flag = cancel_rename_operation()

                if flag == 1:
                    message = '撤销重命名成功！'
                    title = '成功'
                elif flag == 0:
                    message = '历史记录为空，无法撤销重命名！'
                    title = '失败'
                elif flag == -1:
                    message = '上次重命名的文件夹不存在或已被移除！'
                    title = '失败'
                message_window = MessageBox(title=title, content=message, parent=self)
                message_window.cancelButton.hide()
                message_window.buttonLayout.insertStretch(1)
                message_window.yesButton.setText("确认")
                message_window.exec()

                # 撤销成功才将按钮点击的信号发送出去
                if flag == 1:
                    self.refreshView_signal.emit()
            else:
                logging.info('用户取消撤销重命名')

        self.cancelOperationBtn.clicked.connect(cancel_button_callback)

        # 文件夹浏览按钮功能实现
        def select_folder_callback():
            folder_path = QFileDialog.getExistingDirectory(
                self,
                '选择文件夹',
                '',
                QFileDialog.Option.ShowDirsOnly
            )
            if folder_path:
                self.folderLineEdit.setText(folder_path)

        self.folderSelectBtn.clicked.connect(select_folder_callback)

        # 文件列表按钮功能实现
        def file_list_callback():
            targetDirectory = self.folderLineEdit.text().strip('\"')
            if is_directory_usable(targetDirectory) == 1:
                self.scan_file = scan_files(targetDirectory)
                self.selected_file_tuple = tuple(self.scan_file)  # 类型为元组，防止传值时被外部变量修改
            else:
                self.scan_file.clear()

            if self.scan_file:
                fileListInterface = FileListInterface(self.scan_file, self.selected_file_tuple, self)
                if fileListInterface.exec():
                    self.selected_file_tuple = tuple(sorted(fileListInterface.selected_file_list))
            else:
                # 显示一个气泡弹窗
                TeachingTip.create(
                    target=self.fileListBtn,
                    icon=InfoBarIcon.ERROR,
                    title='错误',
                    content='请先输入有效文件夹路径',
                    isClosable=True,
                    tailPosition=TeachingTipTailPosition.LEFT,
                    duration=1500,
                    parent=self
                )

        self.fileListBtn.clicked.connect(file_list_callback)

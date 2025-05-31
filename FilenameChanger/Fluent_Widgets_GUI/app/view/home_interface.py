from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, BodyLabel, setFont, LineEdit, FluentIcon,
                                                               PrimaryPushButton, SmoothScrollArea, MessageBox, InfoBar,
                                                               ToolButton, CardWidget, CheckBox, MessageBoxBase,
                                                               InfoBarPosition, ToolTipPosition, ToolTipFilter)
from FilenameChanger.Fluent_Widgets_GUI.app.common.config import Config as cfg

from FilenameChanger.file_history_operations.file_history_operations import (is_directory_usable, rename_operation,
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
        self.fileWidget = QFrame(self)
        self.fileScrollArea.setWidget(self.fileWidget)
        self.fileScrollArea.setWidgetResizable(True)

        self.fileViewLayout = QVBoxLayout(self.fileWidget)
        self.fileViewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.viewLayout.addWidget(self.fileScrollArea)

        self.initView()

    def initView(self):
        """初始化文件展示"""
        if self.scan_file_list:
            self.fileViewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置为顶部对齐

            for index, file_name in enumerate(self.scan_file_list):
                if file_name in self.selected_file_list:
                    selected = True
                else:
                    selected = False
                card = FileCard(file_name, selected, index, self)
                card.selectSignal.connect(self.setCheckBoxState)
                self.file_card_list.append(card)
                card.clicked.connect(lambda card_index=card.index: self.file_card_list[card_index].switchSelected())
                self.fileViewLayout.addWidget(card)
        else:
            self.fileViewLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label = BodyLabel(text='该文件夹为空', parent=self.widget)
            setFont(label, 20)
            self.fileViewLayout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)

            # 将全选复选框设置为未选中
            self.selectAllCheckBox.setChecked(False)

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
    addNewHistory = pyqtSignal(dict)  # 定义触发历史记录列表刷新布局方法的信号
    cancelRename = pyqtSignal(int)  # 撤销重命名发送的信号
    filenameChanged = pyqtSignal()  # 重命名或者撤销重命名后发送的信号

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HomeInterface')  # 设置全局唯一对象名，否则不能将该界面添加至导航栏
        self.scanned_objects = None
        self.selected_object_tuple = None
        self.path_flag = -1  # 标记输入路径的有效性

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
        self.lineEditLayout = QHBoxLayout()  # 输入框布局器
        self.lineEditLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.folderLineEdit.setFixedWidth(250)
        self.folderLineEdit.setClearButtonEnabled(True)
        self.folderLineEdit.setPlaceholderText('请选择目标的父级文件夹')  # 设置文本框提示文本

        self.lineEditLayout.addWidget(self.folderLineEdit)

        # 文件夹浏览按钮
        self.folderSelectBtn = ToolButton(FluentIcon.FOLDER)
        self.folderSelectBtn.setToolTip('打开文件夹选择窗口')
        self.folderSelectBtn.installEventFilter(
            ToolTipFilter(self.folderSelectBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.folderSelectBtn.setFixedHeight(34)
        self.lineEditLayout.addWidget(self.folderSelectBtn)

        # 文件查看按钮
        self.fileListBtn = ToolButton(FluentIcon.ALIGNMENT)
        self.fileListBtn.setToolTip('选择需要重命名的对象')
        self.fileListBtn.installEventFilter(
            ToolTipFilter(self.fileListBtn, showDelay=300, position=ToolTipPosition.TOP))
        self.fileListBtn.setFixedHeight(34)
        self.lineEditLayout.addWidget(self.fileListBtn)

        # 将整体布局添加至主布局器
        self.widgetLayout.addLayout(self.lineEditLayout)
        self.widgetLayout.addSpacing(20)

        """功能按钮"""
        # 重命名按钮
        self.renameBtn = PrimaryPushButton(FluentIcon.PENCIL_INK, '文件重命名')
        self.renameBtn.setToolTip('开始文件重命名')
        self.renameBtn.installEventFilter(ToolTipFilter(self.renameBtn, showDelay=300, position=ToolTipPosition.BOTTOM))

        # 撤销重命名按钮
        self.cancelOperationBtn = PrimaryPushButton(FluentIcon.HISTORY, '撤销重命名')
        self.cancelOperationBtn.setToolTip('撤销上一次重命名')
        self.cancelOperationBtn.installEventFilter(
            ToolTipFilter(self.cancelOperationBtn, showDelay=300, position=ToolTipPosition.BOTTOM))

        self.buttonHBoxLayout = QHBoxLayout()  # 按钮布局器（水平）
        self.renameBtn.setFixedWidth(175)
        self.cancelOperationBtn.setFixedWidth(175)

        self.buttonHBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonHBoxLayout.setSpacing(30)  # 设置布局器的默认控件间隔

        self.widgetLayout.addLayout(self.buttonHBoxLayout)
        self.buttonHBoxLayout.addWidget(self.renameBtn)
        self.buttonHBoxLayout.addWidget(self.cancelOperationBtn, 0)

        self.achieve_functions()  # 调用控件功能函数

    def initFileList(self):
        """初始化文件列表"""
        # 扫描整个文件夹
        directory = self.folderLineEdit.text().strip('\"')
        flag, message = is_directory_usable(directory)
        if flag == 1:  # 路径有效才扫描
            self.scanned_objects = scan_files(directory)
            self.selected_object_tuple = tuple(self.scanned_objects)  # 类型为元组，防止传值时被外部变量修改

        return flag, message

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
            """文本框功能实现"""
            logging.info('判断路径有效性……')
            self.path_flag, message = self.initFileList()  # 扫描整个文件夹
            if cfg.get(cfg, cfg.folderMode):
                rename_object = '文件夹'
            else:
                rename_object = '文件'
            if self.path_flag:
                InfoBar.success(
                    '有效',
                    '文件夹路径有效，'f'对象：{rename_object}',
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                logging.info(message)
            else:
                InfoBar.error(
                    '无效',
                    '文件夹路径无效',
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                logging.info(message)

        self.folderLineEdit.textChanged.connect(dirLineEdit_function)

        def rename_button_callback():
            """重命名按钮功能实现"""
            if self.path_flag == 1:
                logging.info('用户点击重命名按钮，确认操作中……')
                if confirm_operation():  # 弹出消息框确认操作
                    if cfg.get(cfg, cfg.folderMode):
                        folder_mode = '文件夹模式：开'
                    else:
                        folder_mode = '文件夹模式：关'
                    logging.info(f'用户确认重命名，{folder_mode}')

                    # 如果还未扫描文件夹则进行扫描操作
                    if self.scanned_objects is None:
                        self.initFileList()
                    logging.info(f'已选择文件数：{len(self.selected_object_tuple)}/{len(self.scanned_objects)}')

                    targetDirectory = self.folderLineEdit.text().strip('\"')
                    flag, message, new_history_dict = rename_operation(targetDirectory, self.selected_object_tuple)

                    # 显示一个消息提示框
                    if flag:
                        InfoBar.success(
                            title='完成',
                            content=message,
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )
                        self.addNewHistory.emit(new_history_dict)
                        self.initFileList()  # 文件名改变后重新扫描目标文件夹
                        logging.info('文件重命名完成')
                    else:
                        InfoBar.error(
                            title='失败',
                            content=message,
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )
                        logging.error(f'{message}')
                else:
                    logging.info('用户取消重命名')
            else:
                InfoBar.error(
                    title='错误',
                    content='请输入有效的文件夹路径',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

        self.renameBtn.clicked.connect(rename_button_callback)

        def cancel_button_callback():
            """撤销重命名按钮功能实现"""
            logging.info('用户点击撤销重命名按钮，确认操作中……')
            if confirm_operation():  # 弹出消息框确认操作
                logging.info('用户确认撤销重命名')
                flag, message = cancel_rename_operation()

                if flag:
                    InfoBar.success(
                        title='成功',
                        content=message,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
                    self.initFileList()  # 文件名修改后重新扫描文件夹
                    self.cancelRename.emit(0)  # 将按钮点击的信号发送出去
                else:
                    InfoBar.error(
                        title='失败',
                        content=message,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )

            else:
                logging.info('用户取消撤销重命名')

        self.cancelOperationBtn.clicked.connect(cancel_button_callback)

        def select_folder_callback():
            """文件夹浏览按钮功能实现"""
            folder_path = QFileDialog.getExistingDirectory(
                self,
                '选择文件夹',
                '',
                QFileDialog.Option.ShowDirsOnly
            )
            if folder_path:
                self.folderLineEdit.setText(folder_path)

        self.folderSelectBtn.clicked.connect(select_folder_callback)

        def file_list_callback():
            """文件列表按钮功能实现"""
            if self.path_flag == 1:
                fileListInterface = FileListInterface(self.scanned_objects, self.selected_object_tuple, self)
                if fileListInterface.exec() and self.scanned_objects:  # 用户点击确认按钮并且文件夹内有文件才执行
                    self.selected_object_tuple = tuple(sorted(fileListInterface.selected_file_list))
                    InfoBar.success(
                        title='成功',
                        content='重命名作用域修改成功',
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
            else:
                # 显示一个气泡弹窗
                InfoBar.warning(
                    title='提示',
                    content='请先输入有效的文件夹路径',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

        self.fileListBtn.clicked.connect(file_list_callback)

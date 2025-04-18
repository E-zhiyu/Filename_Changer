from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PyQt6.QtCore import Qt

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, setFont, LineEdit, FluentIcon,
                                                               PrimaryPushButton,
                                                               MessageBox, ToolButton)
from FilenameChanger.file_operations.file_utils import is_directory_usable, rename
from FilenameChanger.file_operations.file_utils import cancel_rename_operation


class HomeInterface(QFrame):
    """定义主页布局"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HomeInterface')  # 设置全局唯一对象名，否则不能将该界面添加至导航栏

        """基本布局设置"""
        self.totalWidget = QWidget()  # 创建一个总容器存放所有控件，使得调整窗口大小的时候各控件不会相互分离
        self.interfaceTotalLayout = QVBoxLayout(self)  # 界面总布局器，只存放一个总容器控件
        self.totalWidgetVLayout = QVBoxLayout(self.totalWidget)  # 总容器内的垂直布局器
        self.setLayout(self.interfaceTotalLayout)  # 设置界面主布局器

        self.interfaceTotalLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 界面总布局器默认为居中对齐
        self.totalWidgetVLayout.setSpacing(10)  # 增加一个10像素的空隔
        self.totalWidgetVLayout.setContentsMargins(0, 180, 0, 200)  # 设置总容器布局器四周向内收缩距离
        self.interfaceTotalLayout.addWidget(self.totalWidget, 1, Qt.AlignmentFlag.AlignCenter)

        """标题标签"""
        self.label = SubtitleLabel(text, self.totalWidget)
        setFont(self.label, 40)

        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.totalWidgetVLayout.addWidget(self.label, 1)

        """文件夹路径文本框"""
        self.tipLabel = SubtitleLabel(self.totalWidget)  # 提示用户是否输入正确的路径
        self.folderLineEdit = LineEdit(self.totalWidget)
        self.folderSelectBtn = ToolButton(FluentIcon.FOLDER)

        self.folderSelectLayout = QHBoxLayout()  # 文件夹选择布局器（水平）
        self.lineEditLayout = QVBoxLayout()  # 文本框布局器（垂直）

        self.folderLineEdit.setFixedWidth(300)
        self.folderLineEdit.setClearButtonEnabled(True)
        self.folderLineEdit.setPlaceholderText('请选择一个文件夹')  # 设置文本框提示文本
        self.folderSelectBtn.setFixedHeight(34)

        self.folderSelectLayout.setContentsMargins(160, 10, 160, 0)

        self.totalWidgetVLayout.addLayout(self.lineEditLayout, 1)
        self.folderSelectLayout.addWidget(self.folderLineEdit, 1, Qt.AlignmentFlag.AlignCenter)
        self.folderSelectLayout.addWidget(self.folderSelectBtn, 1, Qt.AlignmentFlag.AlignCenter)
        self.lineEditLayout.addLayout(self.folderSelectLayout, 1)
        self.lineEditLayout.addWidget(self.tipLabel, 1, Qt.AlignmentFlag.AlignCenter)

        """功能按钮"""
        self.renameBtn = PrimaryPushButton(FluentIcon.PENCIL_INK, '文件重命名')
        self.cancelOperationBtn = PrimaryPushButton(FluentIcon.HISTORY, '撤销重命名')
        self.buttonHBoxLayout = QHBoxLayout()  # 按钮布局器（水平）

        self.renameBtn.setFixedWidth(200)
        self.renameBtn.setEnabled(False)  # 先将其禁用防止未输入路径就重命名
        self.cancelOperationBtn.setFixedWidth(200)

        self.buttonHBoxLayout.setContentsMargins(100, 0, 100, 0)

        self.totalWidgetVLayout.addLayout(self.buttonHBoxLayout, 1)
        self.buttonHBoxLayout.addWidget(self.renameBtn, 0)
        self.buttonHBoxLayout.addWidget(self.cancelOperationBtn, 0)

        self.achieve_functions()  # 调用控件功能函数

    def achieve_functions(self):
        """实现各控件的功能"""

        def confirm_operation(with_warning=True):
            """弹出确认操作的提示框"""
            warning = """\
            【警告】您正在批量修改文件名，可能伴随以下风险：
            - 重命名后某些软件会因为路径依赖而无法定位到该文件。
            - 如果文件夹内有您不想重命名的文件，它们也会被重命名！
            """
            if with_warning:
                message = f"{warning}{'\n确认进行操作吗？'}"
            else:
                message = '确认进行操作吗？'

            confirm_window = MessageBox('操作确认', content=message, parent=self)
            confirm_window.show()
            confirm_window.yesButton.setText('确认')
            confirm_window.cancelButton.setText('取消')

            if confirm_window.exec():
                return 1
            else:
                return 0

        def get_directory():
            # 文本框功能实现
            self.folderLineEdit.setFocus()

            targetDirectory = self.folderLineEdit.text()
            targetDirectory, flag = is_directory_usable(targetDirectory)
            if flag == 1:
                self.renameBtn.setEnabled(True)
                self.tipLabel.setStyleSheet("""QLabel{color: rgb(72, 180, 72);
                                              text-shadow: 2px 2px 4px black;}""")
                self.tipLabel.setText('文件夹路径有效！')
            elif flag == 0:
                self.renameBtn.setEnabled(False)
                self.tipLabel.setStyleSheet("""QLabel{color: rgb(255, 100, 100);
                                                text-shadow: 2px 2px 4px black;}""")
                self.tipLabel.setText('这不是一个有效的文件夹！')
            elif flag == -1:
                self.renameBtn.setEnabled(False)
                self.tipLabel.clear()

        self.folderLineEdit.textChanged.connect(get_directory)

        # 重命名按钮功能实现
        def rename_button_function():
            if confirm_operation():  # 弹出消息框确认操作
                targetDirectory = self.folderLineEdit.text()
                targetDirectory = targetDirectory.strip('\"')
                flag = rename(targetDirectory)
                # 显示一个消息提示框
                if flag == 1:
                    message = '文件重命名完成！'
                    title = '成功'
                elif flag == 0:
                    message = '文件夹为空！'
                    title = '失败'
                elif flag == -1:
                    message = '规则列表为空！请先写入规则！'
                    title = '失败'
                message_window = MessageBox(title=title, content=message, parent=self)
                message_window.cancelButton.hide()
                message_window.buttonLayout.insertStretch(1)
                message_window.yesButton.setText("确认")
                message_window.show()
                message_window.exec()

        self.renameBtn.clicked.connect(rename_button_function)

        # 撤销重命名按钮功能实现
        def cancel_button_function():
            if confirm_operation():  # 弹出消息框确认操作
                flag = cancel_rename_operation()

                if flag == 1:
                    message = '撤销重命名成功！'
                    title = '成功'
                elif flag == 0:
                    message = '历史记录为空，无法撤销重命名！'
                    title = '失败'
                elif flag == -1:
                    message = '历史记录文件不存在或已被删除！'
                    title = '失败'
                elif flag == -2:
                    message = '上次重命名的文件夹不存在或已被移除！'
                    title = '失败'
                message_window = MessageBox(title=title, content=message, parent=self)
                message_window.cancelButton.hide()
                message_window.buttonLayout.insertStretch(1)
                message_window.yesButton.setText("确认")
                message_window.show()
                message_window.exec()

        self.cancelOperationBtn.clicked.connect(cancel_button_function)

        # 文件夹浏览按钮功能实现
        def open_folder_dialog():
            folder_path = QFileDialog.getExistingDirectory(
                self,
                '选择文件夹',
                '',
                QFileDialog.Option.ShowDirsOnly
            )
            if folder_path:
                self.folderLineEdit.setText(folder_path)

        self.folderSelectBtn.clicked.connect(open_folder_dialog)

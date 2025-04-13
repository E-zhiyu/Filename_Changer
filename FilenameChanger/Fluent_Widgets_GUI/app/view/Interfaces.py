from PyQt6.QtWidgets import QApplication, QFrame, QVBoxLayout, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl, QSize
from pyexpat.errors import messages

from Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, setFont, LineEdit, FluentIcon, PrimaryPushButton, Dialog)
from cli.cli import is_directory_usable, rename
from file_operations.file_utils import cancel_rename_operation


class HomeInterface(QFrame):
    """定义主页布局"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        """实例化界面中的控件"""
        self.label = SubtitleLabel(text, self)
        self.warnLabel = SubtitleLabel(self)  # 提示用户是否输入正确的路径
        self.folderLineEdit = LineEdit(self)
        self.folderLineEdit.setPlaceholderText('请选择一个文件夹')
        self.renameButton = PrimaryPushButton(FluentIcon.PENCIL_INK, '文件重命名')
        self.cancelButton = PrimaryPushButton(FluentIcon.CANCEL, '撤销重命名')
        self.mainVBoxLayout = QVBoxLayout(self)  # 设置垂直布局器
        self.lineEditLayout = QVBoxLayout(self)  # 设置文本框布局器（垂直）
        self.buttonHBoxLayout = QHBoxLayout(self)  # 设置按钮布局器（水平）

        """设置控件属性"""
        setFont(self.label, 40)
        self.folderLineEdit.setFixedWidth(300)
        self.folderLineEdit.setClearButtonEnabled(True)
        self.renameButton.setFixedWidth(200)
        self.renameButton.setEnabled(False)  # 先将其禁用防止未输入路径就重命名
        self.cancelButton.setFixedWidth(200)

        """设置布局器中控件的间隔"""
        self.mainVBoxLayout.setSpacing(0)
        self.buttonHBoxLayout.setContentsMargins(0, 0, 0, 0)

        """设置控件位置"""
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        """将控件添加至布局器"""
        self.mainVBoxLayout.addWidget(self.label, 1)
        self.lineEditLayout.addWidget(self.folderLineEdit, 1, Qt.AlignmentFlag.AlignCenter)
        self.lineEditLayout.addWidget(self.warnLabel, 1, Qt.AlignmentFlag.AlignCenter)
        self.buttonHBoxLayout.addWidget(self.renameButton, 1)
        self.buttonHBoxLayout.addWidget(self.cancelButton, 1)
        self.mainVBoxLayout.addLayout(self.lineEditLayout, 1)  # 将文本框布局器添加至主布局器
        self.mainVBoxLayout.addLayout(self.buttonHBoxLayout, 1)  # 将按钮布局器加入主布局器
        self.setObjectName(text.replace(' ', '-'))

        self.achieve_functions()

    def achieve_functions(self):
        """实现控件功能"""

        def get_directory():
            # 文本框功能实现
            self.folderLineEdit.setFocus()

            targetDirectory = self.folderLineEdit.text()
            targetDirectory, flag = is_directory_usable(targetDirectory)
            if flag:
                self.renameButton.setEnabled(True)
                self.warnLabel.setStyleSheet("""QLabel{color: rgb(72, 180, 72);
                                              text-shadow: 2px 2px 4px black;}""")
                self.warnLabel.setText('文件夹路径有效！')
            else:
                self.renameButton.setEnabled(False)
                self.warnLabel.setStyleSheet("""QLabel{color: rgb(255, 100, 100);
                                                text-shadow: 2px 2px 4px black;}""")
                self.warnLabel.setText('这不是一个有效的文件夹！')

        self.folderLineEdit.textChanged.connect(get_directory)

        # 重命名按钮功能实现
        def rename_button_function():
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
            dialog = Dialog(title, message, self)
            dialog.cancelButton.hide()
            dialog.buttonLayout.insertStretch(1)
            dialog.yesButton.setText("确认")
            dialog.show()
            dialog.exec()

        self.renameButton.pressed.connect(rename_button_function)

        # 撤销重命名按钮功能实现
        def cancel_button_function():
            flag = cancel_rename_operation()

            if flag == 1:
                message = '撤销重命名成功！'
                title='成功'
            elif flag == 0:
                message = '历史记录为空，无法撤销重命名！'
                title = '失败'
            elif flag == -1:
                message = '历史记录文件不存在或已被删除！'
                title = '失败'
            elif flag == -2:
                message = '上次重命名的文件夹不存在或已被移除！'
                title = '失败'
            dialog = Dialog(title, message, self)
            dialog.cancelButton.hide()
            dialog.buttonLayout.insertStretch(1)
            dialog.yesButton.setText("确认")
            dialog.show()
            dialog.exec()

        self.cancelButton.pressed.connect(cancel_button_function)

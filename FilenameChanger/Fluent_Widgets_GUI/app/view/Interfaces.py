from PyQt6.QtWidgets import QApplication, QFrame, QVBoxLayout, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl, QSize

from Fluent_Widgets_GUI.qfluentwidgets import SubtitleLabel, setFont, LineEdit, PushButton, FluentIcon, \
    PrimaryPushButton


class HomeInterface(QFrame):
    """定义主页布局"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        """定义界面中的控件"""
        self.label = SubtitleLabel(text, self)
        self.folderLineEdit = LineEdit(self)
        self.folderLineEdit.setPlaceholderText('请选择一个文件夹')
        self.renameButton = PrimaryPushButton(FluentIcon.PENCIL_INK, '文件重命名')
        self.cancelButton = PrimaryPushButton(FluentIcon.CANCEL, '撤销重命名')
        self.mainVBoxLayout = QVBoxLayout(self)  # 设置垂直布局器
        self.secondaryHBoxLayout = QHBoxLayout(self)  # 设置次要布局器（水平）

        setFont(self.label, 40)
        self.folderLineEdit.setFixedWidth(150)  # 设置文本框长度

        """设置控件位置"""
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        """将控件添加至布局器"""
        self.secondaryHBoxLayout.addWidget(self.renameButton, 1)
        self.secondaryHBoxLayout.addWidget(self.cancelButton, 1)
        self.mainVBoxLayout.addWidget(self.label, 1)
        self.mainVBoxLayout.addWidget(self.folderLineEdit, 1, Qt.AlignmentFlag.AlignCenter)
        self.mainVBoxLayout.addStretch()
        self.mainVBoxLayout.addLayout(self.secondaryHBoxLayout, 1)  # 将水平布局器加入主布局器
        self.setObjectName(text.replace(' ', '-'))

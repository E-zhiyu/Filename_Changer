from PyQt6.QtCore import Qt
from PyQt6.QtSql import password
from PyQt6.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, BodyLabel, PushButton, FluentIcon,
                                                               setFont, SmoothScrollArea, CardWidget,
                                                               TransparentToolButton, MessageBoxBase)

from FilenameChanger.file_history_operations.file_history_operations import load_history


class InfoWindow(MessageBoxBase):
    """记录详情界面"""

    def __init__(self, old_name_list, new_name_list, parent=None):
        super().__init__(parent=parent)
        self.old_name_list = old_name_list
        self.new_name_list = new_name_list

        """基本设置"""
        self.yesButton.setText('确定')
        self.cancelButton.setHidden(True)

        self.widget.setMinimumWidth(700)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        """标题标签"""
        self.titleLabel = SubtitleLabel(text='历史记录详情', parent=self.widget)

        self.viewLayout.addWidget(self.titleLabel)

        """文件名更改的展示区域"""
        self.infoScrollArea = SmoothScrollArea(parent=self.widget)
        self.infoWidget = QWidget(self.widget)
        self.infoLayout = QVBoxLayout(self.infoWidget)  # 文件名变化从想到下排列

        self.infoLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.infoLayout.addSpacing(5)

        self.infoScrollArea.setWidget(self.infoWidget)
        self.infoScrollArea.setWidgetResizable(True)
        self.viewLayout.addWidget(self.infoScrollArea)

        self.initInfoView()

    def initInfoView(self):
        """初始化详情展示区域"""
        for index in range(len(self.old_name_list)):
            oldNameLabel = BodyLabel(text=f'原名：{self.old_name_list[index]}', parent=self.infoWidget)
            newNameLabel = BodyLabel(text=f'新名：{self.new_name_list[index]}', parent=self.infoWidget)

            self.infoLayout.addWidget(oldNameLabel)
            self.infoLayout.addWidget(newNameLabel)
            self.infoLayout.addSpacing(15)


class HistoryCard(CardWidget):
    """历史记录卡片"""

    def __init__(self, history_dict, parent=None):
        super().__init__(parent=parent)
        self.history_dict = history_dict
        self.parentInterface = parent  # 记录卡片的父亲容器
        self.selected = False  # 默认没有选中该卡片

        """基本布局设置"""
        self.setFixedHeight(75)
        self.cardLayout = QHBoxLayout()  # 卡片主布局（水平）

        self.setLayout(self.cardLayout)

        """卡片信息显示"""
        self.timeLabel = SubtitleLabel(history_dict['time'], self)
        self.directoryLabel = BodyLabel(history_dict['directory'], self)
        self.labelLayout = QVBoxLayout(self)

        setFont(self.timeLabel, 22)
        setFont(self.directoryLabel, 16)

        self.labelLayout.addWidget(self.timeLabel)
        self.labelLayout.addWidget(self.directoryLabel)
        self.cardLayout.addLayout(self.labelLayout)

        """卡片详情按钮"""
        self.infoBtn = TransparentToolButton(FluentIcon.INFO)

        self.infoBtn.setFixedSize(32, 32)

        self.cardLayout.addWidget(self.infoBtn)

        self.infoBtn.clicked.connect(self.showInfo)

    def setCardSelected(self, isSelected: bool):
        """切换卡片的选中状态"""
        if isSelected == self.selected:  # 如果带切换的状态与当前状态相同则不进行操作
            return

        self.selected = isSelected

        if not isSelected:
            self.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border-radius: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background: #ff009faa;
                    border-radius: 5px;
                }
            """)

    def showInfo(self):
        """显示记录详情"""
        infoWindow = InfoWindow(self.history_dict['old_name_list'], self.history_dict['new_name_list'],
                                self.parentInterface)
        infoWindow.exec()


class HistoryListInterface(QFrame):
    """历史记录列表界面"""
    history_list = []  # 定义类属性：历史记录列表

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HistoryListInterface')

        """界面基本设置"""
        self.totalWidget = QWidget(self)
        self.interfaceLayout = QHBoxLayout(self)
        self.widgetLayout = QVBoxLayout(self.totalWidget)

        self.setLayout(self.interfaceLayout)  # 设置界面主布局
        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 默认向上对齐

        self.interfaceLayout.addWidget(self.totalWidget)

        """标题标签"""
        self.titleLabel = SubtitleLabel(text=text, parent=self)

        setFont(self.titleLabel, 30)

        self.widgetLayout.addWidget(self.titleLabel)

        """历史记录编辑按钮"""
        self.delBtn = PushButton(FluentIcon.DELETE, '删除选中记录')
        self.clearBtn = PushButton(FluentIcon.BROOM, '清空所有记录')
        self.btnLayout = QHBoxLayout(self)

        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.btnLayout.addWidget(self.delBtn)
        self.btnLayout.addWidget(self.clearBtn)

        self.widgetLayout.addLayout(self.btnLayout)

        """历史记录展示区域"""
        self.historyWidget = QWidget(self)
        self.historyScrollArea = SmoothScrollArea(self)
        self.historyCardLayout = QVBoxLayout(self.historyWidget)

        self.historyCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.historyScrollArea.setWidget(self.historyWidget)
        self.widgetLayout.addWidget(self.historyScrollArea)

        """初始化卡片展示区域"""
        self.currentIndex = -1
        self.cardList = []
        self.initCardView()  # 加载历史记录卡片

    def initCardView(self):
        self.history_list = load_history()  # 加载历史记录
        pass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, BodyLabel, PushButton, FluentIcon,
                                                               setFont, SmoothScrollArea, CardWidget,
                                                               TransparentToolButton, MessageBoxBase, MessageBox)

from FilenameChanger.file_history_operations.file_history_operations import (load_history, history_del, history_clear)
from FilenameChanger.log.log_recorder import *


class InfoWindow(MessageBoxBase):
    """记录详情界面"""

    def __init__(self, history_dict, parent=None):
        super().__init__(parent=parent)
        self.old_name_list = history_dict['old_name_list']
        self.new_name_list = history_dict['new_name_list']
        self.error_files = history_dict['error_files']
        self.directory = history_dict['directory']
        self.time = history_dict.get('time', '未知时间')  # 由于老版本没有time关键字，所以用get方法防止KeyError

        """基本设置"""
        self.yesButton.setText('确定')
        self.cancelButton.setHidden(True)

        self.widget.setMinimumWidth(700)
        self.widget.setMinimumHeight(600)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.viewLayout.setSpacing(5)

        """标题标签"""
        self.titleLabel = SubtitleLabel(text='历史记录详情', parent=self.widget)

        self.viewLayout.addWidget(self.titleLabel)

        """路径和日期标签"""
        self.timeLabel = BodyLabel(text=self.time, parent=self.widget)
        self.directoryLabel = BodyLabel(text=f'路径：{self.directory}', parent=self.widget)

        setFont(self.timeLabel, 18)
        setFont(self.directoryLabel, 15)

        self.viewLayout.addWidget(self.timeLabel)
        self.viewLayout.addWidget(self.directoryLabel)

        """文件名更改详情的展示区域"""
        self.infoScrollArea = SmoothScrollArea(parent=self.widget)
        self.infoWidget = QWidget(self.widget)
        self.infoLayout = QVBoxLayout(self.infoWidget)  # 文件名变化从想到下排列

        self.infoLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.infoLayout.setSpacing(5)

        self.infoScrollArea.setWidget(self.infoWidget)
        self.infoScrollArea.setWidgetResizable(True)
        self.viewLayout.addWidget(self.infoScrollArea)

        self.initInfoView()

    def initInfoView(self):
        """初始化详情展示区域"""
        # 展示成功重命名的文件
        successLabel = SubtitleLabel(text='成功重命名的文件', parent=self.widget)
        setFont(successLabel, 20)
        self.infoLayout.addWidget(successLabel)

        for index in range(len(self.old_name_list)):
            oldNameLabel = BodyLabel(text=f'原名：{self.old_name_list[index]}', parent=self.infoWidget)
            newNameLabel = BodyLabel(text=f'新名：{self.new_name_list[index]}', parent=self.infoWidget)

            self.infoLayout.addWidget(oldNameLabel)
            self.infoLayout.addWidget(newNameLabel)
            self.infoLayout.addSpacing(15)

        # 展示重命名出错的文件
        errorLabel = SubtitleLabel(text='出错的文件', parent=self.widget)
        setFont(errorLabel, 20)
        self.infoLayout.addWidget(errorLabel)

        for error_file in self.error_files:
            errorLabel = BodyLabel(text=error_file, parent=self.infoWidget)

            self.infoLayout.addWidget(errorLabel)


class HistoryCard(CardWidget):
    """历史记录卡片"""

    def __init__(self, history_dict, index, parent=None):
        super().__init__(parent=parent)
        self.history_dict = history_dict
        self.index = index
        self.parentInterface = parent  # 记录卡片的父亲容器
        self.selected = False  # 默认没有选中该卡片

        time = history_dict.get('time', '未知时间')

        """基本布局设置"""
        self.setFixedHeight(75)
        self.cardLayout = QHBoxLayout()  # 卡片主布局（水平）

        self.setLayout(self.cardLayout)

        """卡片信息显示"""
        self.timeLabel = SubtitleLabel(text=time, parent=self)
        self.directoryLabel = BodyLabel(history_dict['directory'], self)
        self.labelLayout = QVBoxLayout(self)

        setFont(self.timeLabel, 22)
        setFont(self.directoryLabel, 16)
        self.timeLabel.setStyleSheet('background-color:transparent')
        self.directoryLabel.setStyleSheet('background-color:transparent')

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
        infoWindow = InfoWindow(self.history_dict, self.parentInterface)
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

        self.historyScrollArea.setWidget(self.historyWidget)
        self.historyScrollArea.setWidgetResizable(True)
        self.widgetLayout.addWidget(self.historyScrollArea)

        """初始化卡片展示区域"""
        self.currentIndex = -1
        self.cardList = []
        self.initCardView()  # 初始化布局

        """实现控件功能"""
        self.achieveFunctions()

    def initCardView(self):
        """刷新化卡片展示区域"""
        logging.info('开始更新历史记录卡片布局')
        self.currentIndex = -1  # 先将目前选中的卡片下标置为-1，否则会有下标越界风险
        self.history_list = load_history()  # 加载历史记录

        """删除旧的布局"""
        while self.historyCardLayout.count():
            item = self.historyCardLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cardList.clear()  # 清空卡片列表

        """添加新的布局"""
        if self.history_list:
            self.historyCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

            index = 0
            for history in self.history_list:
                card = HistoryCard(history, index, self)
                card.clicked.connect(lambda index=card.index: self.setSelected(index))
                self.cardList.append(card)
                self.historyCardLayout.addWidget(card)  # 将父亲设置为历史界面，以便历史详情界面正常显示

                index += 1
        else:
            self.historyCardLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tipLabel = SubtitleLabel(text='历史记录为空', parent=self.historyWidget)
            self.historyCardLayout.addWidget(tipLabel, 0, Qt.AlignmentFlag.AlignCenter)

    def setSelected(self, index):
        """
        功能：点击卡片时将对应卡片设置为选中
        参数 index：鼠标点击的卡片的下标
        """
        # 将原来的卡片设置为未选中
        if self.currentIndex > -1:
            self.cardList[self.currentIndex].setCardSelected(False)

        # 将鼠标点击的卡片设置为选中
        self.currentIndex = index
        self.cardList[self.currentIndex].setCardSelected(True)

    def achieveFunctions(self):
        """实现控件功能"""

        # 删除历史记录
        def delHistory():
            if self.currentIndex > -1:
                history_del(self.history_list, self.currentIndex)
                self.initCardView()  # （删除历史记录）刷新卡片布局
                self.currentIndex -= 1  # 将选中卡片的下标恢复为-1防止下标越界

        self.delBtn.clicked.connect(delHistory)

        # 清空历史记录
        def clearHistory():
            if self.history_list:  # 没有历史记录的时候不会产生任何效果
                confirmWindow = MessageBox(title='清空历史记录', content='确定要清空历史记录吗？', parent=self)
                confirmWindow.yesButton.setText('确认')
                confirmWindow.cancelButton.setText('取消')

                logging.info('正在确认操作：清空历史记录')
                if confirmWindow.exec():
                    logging.info('用户确认清空历史记录')
                    history_clear()
                    self.initCardView()  # （清空历史记录）刷新卡片布局
                    self.currentIndex -= 1
                else:
                    logging.info('用户取消清空历史记录')

        self.clearBtn.clicked.connect(clearHistory)

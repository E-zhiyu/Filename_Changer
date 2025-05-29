from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, BodyLabel, PushButton, FluentIcon,
                                                               setFont, SmoothScrollArea, CardWidget, themeColor,
                                                               TransparentToolButton, MessageBoxBase, MessageBox,
                                                               InfoBarPosition, InfoBar, ToolTipFilter, isDarkTheme,
                                                               setCustomStyleSheet)

from FilenameChanger.file_history_operations.file_history_operations import (load_history, history_del, history_clear)
from FilenameChanger.log.log_recorder import *


class InfoWindow(MessageBoxBase):
    """历史记录详情界面"""

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

        """重命名模式标签"""
        folder_mode = history_dict.get('folder_mode')
        if folder_mode:
            message = '文件夹'
        else:
            message = '文件'
        self.modeLabel = SubtitleLabel(text=f'重命名对象：{message}', parent=self.widget)
        setFont(self.modeLabel, 15)

        self.viewLayout.addWidget(self.modeLabel)

        """文件名更改详情的展示区域"""
        self.infoScrollArea = SmoothScrollArea(parent=self.widget)
        self.infoWidget = QFrame(self.widget)
        self.infoLayout = QVBoxLayout(self.infoWidget)  # 文件名变化从想到下排列

        self.infoLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.infoLayout.setSpacing(5)
        self.infoWidget.setStyleSheet('border-radius: 5px;')

        self.infoScrollArea.setWidget(self.infoWidget)
        self.infoScrollArea.setWidgetResizable(True)
        self.viewLayout.addWidget(self.infoScrollArea)

        self.initInfoView()

    def initInfoView(self):
        """初始化详情展示区域"""
        # 展示成功重命名的文件
        if self.new_name_list:
            successLabel = SubtitleLabel(text='成功重命名的文件', parent=self.widget)
            setFont(successLabel, 20)
            self.infoLayout.addWidget(successLabel)

        for index in range(len(self.old_name_list)):
            oldNameLabel = BodyLabel(text=f'原名：{self.old_name_list[index]}', parent=self.infoWidget)
            newNameLabel = BodyLabel(text=f'新名：{self.new_name_list[index]}', parent=self.infoWidget)

            self.infoLayout.addWidget(oldNameLabel)
            self.infoLayout.addWidget(newNameLabel)
            self.infoLayout.addSpacing(15)

        # 展示未重命名的文件
        if self.error_files:
            errorLabel = SubtitleLabel(text='未重命名的文件', parent=self.widget)
            setFont(errorLabel, 20)
            self.infoLayout.addWidget(errorLabel)

            for error_file in self.error_files:
                errorLabel = BodyLabel(text=error_file, parent=self.infoWidget)
                self.infoLayout.addWidget(errorLabel)


class HistoryCard(CardWidget):
    """历史记录卡片"""
    clicked = pyqtSignal(int)

    def __init__(self, history_dict, index, parent=None):
        super().__init__(parent=parent)
        self.history_dict = history_dict
        self.index = index  # 卡片在卡片列表中的下标
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

        """打开文件夹按钮"""
        self.openFolderBtn = PushButton(FluentIcon.FOLDER, '打开文件夹', self)
        self.cardLayout.addWidget(self.openFolderBtn, 0, Qt.AlignmentFlag.AlignRight)

        self.openFolderBtn.clicked.connect(self.openFolder)

        """卡片详情按钮"""
        self.infoBtn = TransparentToolButton(FluentIcon.INFO)
        self.infoBtn.setFixedSize(32, 32)

        self.infoBtn.setToolTip('查看重命名详情')
        self.infoBtn.installEventFilter(ToolTipFilter(self.infoBtn))

        self.cardLayout.addWidget(self.infoBtn)

        self.infoBtn.clicked.connect(self.showInfo)

        """设置卡片标签控件的样式"""
        self.setStyle()

    def setStyle(self):
        # 设置卡片中标签控件的样式
        if isDarkTheme():
            label_qss = """
                QLabel {
                    color: white;
                    background-color: transparent;
                }
            """
        else:
            label_qss = """
                QLabel {
                    color: black;
                    background-color: transparent;
                }
            """
        self.timeLabel.setStyleSheet(label_qss)
        self.directoryLabel.setStyleSheet(label_qss)

    def mouseReleaseEvent(self, e):
        """重写clicked信号触发逻辑，使其发送卡片位置"""
        super(CardWidget, self).mouseReleaseEvent(e)
        self.clicked.emit(self.index)

    def setCardSelected(self, isSelected: bool):
        """切换卡片的选中状态"""
        if isSelected == self.selected:  # 如果带切换的状态与当前状态相同则不进行操作
            return

        self.selected = isSelected
        color = themeColor()

        if isSelected:
            # 设置卡片背景颜色
            self.setStyleSheet("QWidget {background-color:" + f"{color.name()};" +
                               "border-radius: 5px;}")

            if isDarkTheme():
                label_qss = """
                    QLabel {
                        color: black;
                        background-color: transparent;
                    }"""
                btn_qss = 'QPushButton {color: black;}'  # 深色模式选中时文字为黑色
                self.openFolderBtn.setIcon(FluentIcon.FOLDER.icon(color='black'))
                self.infoBtn.setIcon(FluentIcon.INFO.icon(color='black'))

                self.timeLabel.setStyleSheet(label_qss)
                self.directoryLabel.setStyleSheet(label_qss)

            else:
                btn_qss = 'QPushButton {color: black;}'  # 浅色模式选中时文字不变仍为黑色
                self.openFolderBtn.setIcon(FluentIcon.FOLDER.icon(color='black'))
                self.infoBtn.setIcon(FluentIcon.INFO.icon(color='black'))

            setCustomStyleSheet(self.openFolderBtn, btn_qss, btn_qss)

        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border-radius: 5px;
                }""")  # 设置卡片背景颜色

            if isDarkTheme():
                label_qss = """
                    QLabel {
                        color: white;
                        background-color: transparent;
                    }"""
                btn_qss = 'QPushButton {color: white;}'  # 深色模式未选中时文字为白色
                self.openFolderBtn.setIcon(FluentIcon.FOLDER.icon(color='white'))
                self.infoBtn.setIcon(FluentIcon.INFO.icon(color='white'))

            else:
                label_qss = """
                    QLabel {
                        color: black;
                        background-color: transparent;
                    }"""
                btn_qss = 'QPushButton {color: black;}'  # 浅色模式未选中时文字为黑色
                self.openFolderBtn.setIcon(FluentIcon.FOLDER.icon(color='black'))
                self.infoBtn.setIcon(FluentIcon.INFO.icon(color='black'))

            self.timeLabel.setStyleSheet(label_qss)
            self.directoryLabel.setStyleSheet(label_qss)
            setCustomStyleSheet(self.openFolderBtn, btn_qss, btn_qss)

    def showInfo(self):
        """显示记录详情"""
        infoWindow = InfoWindow(self.history_dict, self.parentInterface)
        infoWindow.exec()

    def openFolder(self):
        """打开该记录对应的文件夹"""
        try:
            os.startfile(self.directoryLabel.text())
        except FileNotFoundError:
            errorWindow = MessageBox('失败', '文件夹不存在', parent=self.parentInterface)
            errorWindow.yesButton.setText('确定')
            errorWindow.cancelButton.setHidden(True)
            errorWindow.exec()


class HistoryListInterface(QWidget):
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
        # 删除单条历史记录按钮
        self.delBtn = PushButton(FluentIcon.DELETE, '删除选中记录')
        self.delBtn.setToolTip('删除选中的历史记录')
        self.delBtn.installEventFilter(ToolTipFilter(self.delBtn))

        # 清空历史记录按钮
        self.clearBtn = PushButton(FluentIcon.BROOM, '清空所有记录')
        self.clearBtn.setToolTip('清空所有历史记录')
        self.clearBtn.installEventFilter(ToolTipFilter(self.clearBtn))

        self.btnLayout = QHBoxLayout(self)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.btnLayout.addWidget(self.delBtn)
        self.btnLayout.addWidget(self.clearBtn)

        self.widgetLayout.addLayout(self.btnLayout)

        """历史记录展示区域"""
        self.historyWidget = QFrame(self)
        self.historyScrollArea = SmoothScrollArea(self)
        self.historyCardLayout = QVBoxLayout(self.historyWidget)

        self.historyScrollArea.setWidget(self.historyWidget)
        self.historyScrollArea.setWidgetResizable(True)
        self.widgetLayout.addWidget(self.historyScrollArea)

        """初始化卡片展示区域"""
        self.currentIndex = -1
        self.historyCardList = []
        self.initCardView()  # 初始化布局

        """实现控件功能"""
        self.achieveFunctions()

    def initCardView(self):
        """刷新化卡片展示区域"""
        logging.info('开始更新历史记录卡片布局……')
        self.currentIndex = -1  # 先将目前选中的卡片下标置为-1，否则会有下标越界风险
        self.history_list = load_history()  # 加载历史记录

        """删除旧的布局"""
        while self.historyCardLayout.count():
            item = self.historyCardLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.historyCardList.clear()  # 清空卡片列表

        """添加新的布局"""
        if self.history_list:
            self.historyCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

            for index, history in enumerate(self.history_list):
                card = HistoryCard(history, index, self)

                card.clicked.connect(self.setSelected)  # 将卡片点击动作连接至选中卡片方法
                self.historyCardList.append(card)
                self.historyCardLayout.addWidget(card)  # 将父亲设置为历史界面，以便历史详情界面正常显示
        else:
            self.historyCardLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tipLabel = SubtitleLabel(text='历史记录为空', parent=self.historyWidget)
            self.historyCardLayout.addWidget(tipLabel, 0, Qt.AlignmentFlag.AlignCenter)

    def setSelected(self, index):
        """
        功能：点击卡片时将对应卡片设置为选中
        参数 index：目标卡片的下标
        """
        # 将原来的卡片设置为未选中
        if self.currentIndex > -1:
            self.historyCardList[self.currentIndex].setCardSelected(False)

        # 将目标卡片设置为选中
        self.currentIndex = index
        if self.currentIndex > -1:
            self.historyCardList[self.currentIndex].setCardSelected(True)

    def addHistory(self, new_history: dict):
        """
        功能：界面中添加新增的历史记录卡片（仅从类外部调用时）
        参数 new_history：新增的历史记录字典
        """
        self.setSelected(-1)  # 先取消选中卡片

        if new_history.get('new_name_list') or new_history.get('error_files'):
            if self.history_list:  # 如果历史记录不为空，则将新卡片插入到列表首位
                self.history_list.insert(0, new_history)  # 将新历史记录插入到历史记录列表首位

                new_card = HistoryCard(new_history, 0, self)  # 创建新卡片实例对象
                new_card.clicked.connect(self.setSelected)  # 将点击动作连接至选中卡片方法

                for existing_card in self.historyCardList:  # 将现存的所有卡片所保存的下标加一
                    existing_card.index += 1

                self.historyCardList.insert(0, new_card)  # 将现存卡片下标加一后再将新卡片插入列表

                # 向界面中添加新卡片
                self.historyCardLayout.insertWidget(0, new_card)
            else:
                self.initCardView()  # 如果历史记录为空，则直接强制刷新界面

    def delHistory(self, index: int = -1):
        """
        功能：删除指定的历史记录
        参数 index：从外部调用时传递的下标值
        """
        if self.history_list:
            if index != -1:  # 外部参数优先级高于历史记录列表界面选择卡片的下标
                del_index = index
            else:
                del_index = self.currentIndex

            self.setSelected(-1)  # 取消选中卡片防止出现显示BUG

            if del_index != -1:
                history_del(self.history_list, del_index)  # 删除文件中的历史记录

                if self.history_list:  # 判断删除后是否还有历史记录
                    self.historyCardLayout.takeAt(del_index)  # 从界面中取出选中的卡片
                    for card in self.historyCardList[del_index:]:  # 其后的卡片的下标都减一
                        card.index -= 1
                    self.historyCardList[del_index].deleteLater()  # 将选中的卡片删除
                    del self.historyCardList[del_index]  # 删除列表中对应的卡片

                    self.currentIndex = -1  # 将选中规则的下标归位

                    # 设置滚动条位置为删除前的位置
                    v_pos = self.historyScrollArea.verticalScrollBar().value()
                    self.historyScrollArea.verticalScrollBar().setValue(v_pos)
                else:
                    self.initCardView()  # 若删除后没有历史记录，则直接刷新界面（以此显示历史记录为空的文本标签）

                # 创建操作成功的消息框
                if index == -1:  # 当该方法从外部调用并传值时不显示该消息
                    InfoBar.success(
                        title='成功',
                        content='已删除选中的历史记录',
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
            else:
                # 显示一个气泡弹窗
                InfoBar.warning(
                    title='提示',
                    content='请先选择一条历史记录',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
        else:
            InfoBar.error(
                title='错误',
                content='历史记录为空',
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def achieveFunctions(self):
        """实现控件功能"""

        # 删除历史记录
        self.delBtn.clicked.connect(lambda: self.delHistory())

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
                    self.setSelected(-1)

                    InfoBar.success(
                        title='成功',
                        content='已清除全部历史记录',
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
                else:
                    logging.info('用户取消清空历史记录')
            else:
                InfoBar.error(
                    title='错误',
                    content='历史记录为空',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

        self.clearBtn.clicked.connect(clearHistory)
